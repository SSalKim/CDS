"""Paced historical WMSH collection; one request per 15+ seconds across storms."""
import argparse
import csv
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from urllib.request import build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis.collect_track_verification import STORMS, FIELDS, cycles, parse_deck, digest_text
from windborne import NoRedirects, WindborneError, request_text, parse_time, summarize_deck


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    key = os.environ.get('WB_API_KEY', '').strip()
    if not key:
        raise SystemExit('WB_API_KEY missing')
    opener = build_opener(NoRedirects())
    last_request = 0.0
    audit, points = [], []

    def request(path, params=None):
        nonlocal last_request
        for attempt in range(3):
            time.sleep(max(0, 15 - (time.monotonic() - last_request)))
            last_request = time.monotonic()
            try:
                return request_text(opener, key, path, params, timeout=30)
            except WindborneError as error:
                if str(error) != 'HTTP 429' or attempt == 2:
                    raise
                print('Rate limit: pausing for 65 seconds before retry.', flush=True)
                time.sleep(65)

    def save():
        (output / 'audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
        with (output / 'forecasts.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(points)

    for storm, spec in STORMS.items():
        try:
            listing = request('/' + spec['atcf'] + '/init_times')
            payload = json.loads(listing)
            if payload.get('tropical_cyclone_id') != spec['atcf'] or not isinstance(payload.get('available'), list):
                raise WindborneError('Invalid initialization list identity or format')
            available = {parse_time(value).strftime('%Y%m%d%H') for value in payload['available']}
            (output / f'{storm}_init_times.json').write_text(listing, encoding='utf-8')
            audit.append(dict(storm=storm, source='WINDBORNE', cycle='index', status='ok', available_cycles=len(available)))
        except (WindborneError, ValueError) as error:
            status = str(error) if isinstance(error, WindborneError) else 'invalid_json'
            audit.append(dict(storm=storm, source='WINDBORNE', cycle='index', status=status))
            save()
            print(f'{storm}: initialization index unavailable ({status})', flush=True)
            continue
        for cycle in cycles(spec):
            if cycle not in available:
                audit.append(dict(storm=storm, source='WINDBORNE', cycle=cycle, status='not_in_available_index'))
                save()
                continue
            try:
                text = request('/' + spec['atcf'], dict(initialization_time=cycle, format='deck'))
                summary = summarize_deck(text, spec['atcf'], cycle)
                ref = f'{storm}_{cycle}.atcf'
                rows, conflicts = parse_deck(text, storm, cycle, 'WMSH', spec['atcf'], 'WINDBORNE', ref, digest_text(text))
                (output / ref).write_text(text, encoding='utf-8')
                points.extend(rows)
                audit.append(dict(storm=storm, source='WINDBORNE', cycle=cycle,
                    status='ok' if rows else 'no_mean_points', points=len(rows), conflicts=conflicts, summary=summary))
                print(f'{storm} {cycle}: WMSH={len(rows)}', flush=True)
            except WindborneError as error:
                audit.append(dict(storm=storm, source='WINDBORNE', cycle=cycle, status=str(error)))
                print(f'{storm} {cycle}: {error}', flush=True)
            save()
    (output / 'manifest.json').write_text(json.dumps(dict(collected_at=datetime.now(timezone.utc).isoformat(),
        commit=os.getenv('GITHUB_SHA'), policy='Exact ATCF identity/cycle; WMSH only; sequential requests spaced 15 seconds; 65-second 429 backoff'), indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    main(parser.parse_args().output)
