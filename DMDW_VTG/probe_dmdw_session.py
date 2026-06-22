from __future__ import annotations

import argparse
import sys
from pathlib import Path

from query_models import make_headers, read_optional_text, read_required_text


IWA_URL = "https://dmdw.kma.go.kr/uwa/iwa/iwaMain.kaf"


def looks_like_login_page(text: str, url: str) -> bool:
    lowered = (text or "").lower()
    lowered_url = (url or "").lower()
    login_markers = [
        "login_expired",
        "btnlogin",
        'id="email"',
        'id="pwd"',
        'name="password"',
        'type="password"',
    ]
    return "login" in lowered_url or any(marker in lowered for marker in login_markers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe whether a cached DMDW session cookie is still usable.")
    parser.add_argument("--cookie-file", type=Path, required=True)
    parser.add_argument("--csrf-file", type=Path, default=None)
    parser.add_argument("--timeout", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cookie = read_required_text(args.cookie_file, "DMDW_COOKIE", "DMDW cookie")
    csrf = read_optional_text(args.csrf_file)
    headers = make_headers(cookie, csrf)

    try:
        import requests

        response = requests.get(IWA_URL, headers=headers, timeout=args.timeout, allow_redirects=True)
    except Exception as exc:
        print(f"DMDW cached session probe failed before response: {type(exc).__name__}: {exc}")
        return 1

    text = response.text or ""
    print(
        "DMDW cached session probe: "
        f"http={response.status_code} "
        f"url={response.url} "
        f"bytes={len(text)}"
    )
    if response.status_code in {401, 403}:
        print("DMDW cached session is not usable: authorization rejected.")
        return 1
    if response.status_code >= 400:
        print("DMDW cached session is not usable: HTTP error.")
        return 1
    if looks_like_login_page(text, response.url):
        print("DMDW cached session is not usable: login page detected.")
        return 1

    print("DMDW cached session is usable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
