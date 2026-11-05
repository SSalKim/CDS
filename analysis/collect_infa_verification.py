"""Collect IN-FA raw forecasts for retrospective skill, without production QC."""
import argparse
import csv
import json
import os
from pathlib import Path
import sys
import time
from datetime import timedelta, datetime, timezone
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis.collect_track_verification import (
    STORMS, FIELDS, cycles, dt, stamp, record, valid_position,
    parse_kma, parse_deck, digest_text, fetch,
)
from vtg_sources import MODEL_SOURCES, INACTIVE_MODEL_IDS

STORM = 'IN-FA'
SPEC = STORMS[STORM]
COLLAPSE = {'KIM_3h': 'KIM', 'KIM_6h': 'KIM', 'KIM_GFDL_6h': 'KIM'}
SKIP = set(INACTIVE_MODEL_IDS) | {'UM', 'UM_GFDL_6h', 'UM_KEPS', 'FNUM_AI', 'PGUM_AI', 'GCUM_AI'}


def mappings(column):
    return {str(r[column]).upper(): COLLAPSE.get(r['name'], r['name'])
            for r in MODEL_SOURCES if r['name'] not in SKIP and r.get(column)}


def kma_models():
    result = {}
    for r in MODEL_SOURCES:
        if r['name'] not in SKIP and r.get('apihub'):
            result.setdefault(COLLAPSE.get(r['name'], r['name']), []).append(r['apihub'])
    extra = {'ECMWF': ['ECMWF_TIGGE', 'ECM_SPR_D'], 'ECMWF_EPS': ['ECM_SPR_E'],
             'GFS': ['GFS_TIGGE', 'NCEP_TIGGE'], 'CMC': ['CMSC'],
             'CMC_EPS': ['CMSC_EPS'], 'UKM': ['UKM', 'UKMO'],
             'IFEC_AI': ['IFEC'], 'IFKM_AI': ['IFKM'],
             'GCEC_AI': ['GCEC', 'GPEC'], 'GCKM_AI': ['GCKM', 'GPKM'],
             'FNEC_AI': ['FNEC'], 'FNKM_AI': ['FNKM'], 'PGEC_AI': ['PGEC'], 'PGKM_AI': ['PGKM']}
    for name, aliases in extra.items():
        result.setdefault(name, []).extend(aliases)
    return result


def parse_polar(payload, ref):
    cycle = str(payload.get('cycle', ''))
    if payload.get('atcf_id', '').upper() != SPEC['atcf'] or len(cycle) != 10:
        return []
    rows = []
    lookup = mappings('polarwx')
    digest = digest_text(json.dumps(payload, sort_keys=True))
    for raw, series in payload.get('models', {}).items():
        model = lookup.get(raw.upper())
        if not model:
            continue
        for i, lead in enumerate(series.get('fhr', [])):
            try:
                lat, lon = float(series['lat'][i]), float(series['lon'][i])
                if lon > 180:
                    lon -= 360
                valid = stamp(dt(cycle) + timedelta(hours=float(lead)))
                if str(series['time'][i]) != valid or not 0 <= float(lead) <= 240 or not valid_position(lat, lon):
                    continue
                rows.append(record(STORM, model, 'POLARWX', cycle, float(lead), lat, lon, raw, SPEC['atcf'], ref, digest))
            except (ValueError, IndexError, KeyError, TypeError):
                continue
    return rows


def parse_smca(payload, ref):
    data = payload.get('data', {})
    if str(payload.get('code')) != '200' or str(data.get('ident') or data.get('tfbh')) != '202631':
        return []
    rows = []
    lookup = mappings('smca')
    digest = digest_text(json.dumps(payload, sort_keys=True))
    for analysis in data.get('points', []):
        for forecast in analysis.get('forecast') or []:
            raw = str(forecast.get('sets', '')).upper()
            model = lookup.get(raw)
            if not model:
                continue
            try:
                cycle_dt = datetime.fromisoformat(forecast['init_time_utc'].replace('Z', '+00:00'))
                if cycle_dt.tzinfo is None:
                    cycle_dt = cycle_dt.replace(tzinfo=timezone.utc)
                cycle = stamp(cycle_dt.astimezone(timezone.utc))
            except (ValueError, KeyError, TypeError):
                continue
            for point in forecast.get('points') or []:
                try:
                    lead = float(point['forecastTime'])
                    lat, lon = float(point['lat']), float(point['lng'])
                    if lon > 180:
                        lon -= 360
                    if 0 <= lead <= 240 and valid_position(lat, lon):
                        rows.append(record(STORM, model, 'SMCA.FUN', cycle, lead, lat, lon, raw, '202631', ref, digest))
                except (ValueError, KeyError, TypeError):
                    continue
    return rows


def collect(output, offline=False):
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / 'raw'
    raw_dir.mkdir(exist_ok=True)
    folder = ROOT / 'data/2026/TYP_2631_IN-FA'
    history = json.loads((folder / 'metadata/track_history.json').read_text(encoding='utf-8'))
    observations = [p for p in history['points'] if SPEC['start'] <= p['time_utc'][:10] <= SPEC['end']]
    (output / 'observations.json').write_text(json.dumps(observations, indent=2), encoding='utf-8')
    audit, points = [], []
    valid_cycles = set(cycles(SPEC))
    def save():
        (output / 'audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
        with (output / 'forecasts.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(points)
    for path in sorted((ROOT / 'data/polarwx').glob('*/wp302026.json')):
        rows = parse_polar(json.loads(path.read_text(encoding='utf-8')), path.relative_to(ROOT).as_posix())
        points.extend(rows)
    # Prefer the per-cycle persisted provider snapshots to mutable live history.
    for path in sorted((folder / 'metadata/smca').glob('*/*.json')):
        points.extend(parse_smca(json.loads(path.read_text(encoding='utf-8')), path.relative_to(ROOT).as_posix()))
    audit.append(dict(source='ARCHIVED_SNAPSHOTS', status='ok', points=len(points)))
    save()
    if not offline:
        keys = [os.getenv('KMA_APIHUB_AUTH_KEY', '').strip(), os.getenv('KMA_APIHUB_FALLBACK_AUTH_KEY', '').strip()]
        for cycle in sorted(valid_cycles):
            numbers = [31]
            meta_path = folder / 'metadata/runs' / (cycle + '00_240h.json')
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding='utf-8'))
                if meta.get('canonical_typ_number') == 31 and meta.get('data_typ_number') not in (None, 31):
                    numbers.append(int(meta['data_typ_number']))
            for host, key in zip(['apihub-pub.kma.go.kr', 'apihub.kma.go.kr'], keys):
                if not key:
                    audit.append(dict(source='APIHUB', cycle=cycle, status='key_missing'))
                    continue
                params = dict(src='', tm=cycle+'00', mode='2', disp='1', help='0', authKey=key)
                text, status = fetch('https://'+host+'/api/typ01/url/typ_gts_now.php?'+urlencode(params), keys)
                ref = f'raw/apihub_{cycle}.txt'
                rows, conflicts = parse_kma(text, STORM, cycle, numbers, ref, digest_text(text), kma_models()) if text else ([], 0)
                audit.append(dict(source='APIHUB', cycle=cycle, endpoint=host, status=status if rows else status+'_no_rows', points=len(rows), conflicts=conflicts))
                if rows:
                    (output / ref).write_text(text, encoding='utf-8')
                    points.extend(rows)
                save()
                time.sleep(0.5)
                if rows:
                    break
            print(f'{cycle}: {len(points)} total points', flush=True)
        text, status = fetch('https://smca.fun/api/typhoon_msg/?typhoonId=202631')
        if text:
            (raw_dir / 'smca_history.json').write_text(text, encoding='utf-8')
            try:
                points.extend(parse_smca(json.loads(text), 'raw/smca_history.json'))
            except ValueError:
                status = 'invalid_json'
        audit.append(dict(source='SMCA.FUN', status=status))
        for source, url, column in [
            ('RAL.UCAR', 'https://hurricanes.ral.ucar.edu/realtime/plots/northwestpacific/2026/wp302026/awp302026.dat', 'ral_ucar'),
            ('EMC.NCEP', 'https://www.emc.ncep.noaa.gov/hurricane/DECKS_OPEN/awp302026.dat', 'emc')]:
            text, status = fetch(url)
            if text:
                ref = 'raw/'+source.lower()+'_adeck.txt'
                (output / ref).write_text(text, encoding='utf-8')
                for cycle in sorted(valid_cycles):
                    for raw, model in mappings(column).items():
                        rows, _ = parse_deck(text, STORM, cycle, raw, SPEC['atcf'], source, ref, digest_text(text))
                        for row in rows:
                            row['model'] = model
                        points.extend(rows)
            audit.append(dict(source=source, status=status))
            save()
        # The retired GDM collector still holds useful early-cycle research data.
        for cycle in sorted(valid_cycles):
            date = dt(cycle)
            for raw, model in [('GENC', 'GENC'), ('FNV3', 'WNC'), ('WNV3', 'WNV3')]:
                url = f'https://raw.githubusercontent.com/SSalKim/GDM/main/forecast_files/{date:%Y/%m/%d}/{raw}_{date:%Y_%m_%dT%H_00}_atcf_a_deck.txt'
                text, status = fetch(url)
                rows, _ = parse_deck(text, STORM, cycle, raw, SPEC['atcf'], 'RAW.GITHUB', url, digest_text(text)) if text else ([], 0)
                for row in rows:
                    row['model'] = model
                points.extend(rows)
                audit.append(dict(source='RAW.GITHUB', model=model, cycle=cycle, status=status, points=len(rows)))
                if rows:
                    (raw_dir / f'{raw}_{cycle}.txt').write_text(text, encoding='utf-8')
            save()
    points[:] = [p for p in points if p['cycle'] in valid_cycles]
    save()
    manifest = dict(storm=STORM, spec=SPEC, commit=os.getenv('GITHUB_SHA'),
                    collected_at=datetime.now(timezone.utc).isoformat(), cycles=sorted(valid_cycles),
                    points=len(points), observations=len(observations),
                    policy='Exact identity/cycle/time; raw coordinates, no motion/intensity QC; no interpolation')
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--offline', action='store_true')
    args = p.parse_args()
    collect(args.output, args.offline)
