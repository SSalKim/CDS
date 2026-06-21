from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DMDW_HOME_URL = "https://dmdw.kma.go.kr/"


ID_SELECTORS = [
    "#email",
    'input[id="email"]',
    'input[placeholder="ID"]',
    'input[name="userId"]',
    'input[name="loginId"]',
    'input[name="id"]',
    'input[name="userid"]',
    'input[name="username"]',
    'input[id="userId"]',
    'input[id="loginId"]',
    'input[id="id"]',
    'input[type="text"]',
]

PW_SELECTORS = [
    "#pwd",
    'input[id="pwd"]',
    'input[placeholder="PASSWORD"]',
    'input[name="password"]',
    'input[name="passwd"]',
    'input[name="pwd"]',
    'input[id="password"]',
    'input[id="passwd"]',
    'input[type="password"]',
]

LOGIN_BUTTON_SELECTORS = [
    "#btnLogin",
    'button[id="btnLogin"]',
    "button.login_btn",
    'button:has-text("로그인")',
    'button[type="submit"]',
    'input[type="submit"]',
    'a:has-text("로그인")',
    'input[value="로그인"]',
]


def first_visible(page, selectors: list[str], timeout: int = 1500) -> str | None:
    for selector in selectors:
        try:
            loc = page.locator(selector).first
            loc.wait_for(state="visible", timeout=timeout)
            return selector
        except Exception:
            continue
    return None


def dump_login_candidates(page) -> None:
    print("Login selector discovery failed. Dumping candidate controls.")
    try:
        candidates = page.evaluate(
            """
            () => {
              const els = [...document.querySelectorAll('input, button, a')];
              return els.slice(0, 200).map((el, i) => ({
                i,
                tag: el.tagName,
                type: el.getAttribute('type'),
                id: el.id,
                name: el.getAttribute('name'),
                value: el.getAttribute('value'),
                text: (el.innerText || el.textContent || '').trim().slice(0, 80),
                placeholder: el.getAttribute('placeholder'),
                className: el.className
              }));
            }
            """
        )
    except Exception as exc:
        print(f"Failed to inspect login page controls: {exc}")
        return

    for candidate in candidates:
        print(candidate)


def build_cookie_header(cookies) -> str:
    parts: list[str] = []
    for cookie in cookies:
        name = cookie.get("name")
        value = cookie.get("value")
        domain = cookie.get("domain", "")
        if not name or value is None:
            continue
        if "dmdw.kma.go.kr" in domain or domain in {".kma.go.kr", "dmdw.kma.go.kr"}:
            parts.append(f"{name}={value}")
    return "; ".join(parts)


def extract_csrf_from_page(page) -> str:
    js = """
    () => {
      const vals = [];
      const metas = [
        'meta[name="_csrf"]',
        'meta[name="csrf"]',
        'meta[name="csrf-token"]',
        'meta[name="X-CSRF-TOKEN"]',
        'meta[name="x-csrf-token"]'
      ];

      for (const sel of metas) {
        const el = document.querySelector(sel);
        if (el && el.content) vals.push(el.content);
      }

      const inputs = [
        'input[name="_csrf"]',
        'input[name="csrf"]',
        'input[name="csrf-token"]',
        'input[name="X-CSRF-TOKEN"]',
        'input[name="x-csrf-token"]'
      ];

      for (const sel of inputs) {
        const el = document.querySelector(sel);
        if (el && el.value) vals.push(el.value);
      }

      const regex = /(csrf|xsrf|token)/i;
      for (const store of [window.localStorage, window.sessionStorage]) {
        try {
          for (let i = 0; i < store.length; i++) {
            const k = store.key(i);
            const v = store.getItem(k);
            if (regex.test(k) && v) vals.push(v);
          }
        } catch (e) {}
      }

      for (const k of Object.keys(window)) {
        if (regex.test(k)) {
          try {
            const v = window[k];
            if (typeof v === "string" && v.length >= 8 && v.length < 300) {
              vals.push(v);
            }
          } catch (e) {}
        }
      }

      return [...new Set(vals)].filter(Boolean);
    }
    """
    try:
        vals = page.evaluate(js)
    except Exception:
        return ""
    return vals[0] if vals else ""


def looks_logged_in(page) -> bool:
    url = page.url.lower()
    if "login_expired" in url:
        return False

    try:
        body = page.locator("body").inner_text(timeout=3000)
    except Exception:
        body = ""

    try:
        if page.locator("#btnlogOut").count() > 0:
            return True
    except Exception:
        pass

    if "로그아웃" in body:
        return True

    logged_in_url_markers = [
        "/rsw/mfp/mfpmain",
        "/uwa/iwa/iwamain",
        "/uwa/iwa/wamain",
        "/mfp/mfpmain",
    ]
    if any(marker in url for marker in logged_in_url_markers):
        return True

    if "dmdw.kma.go.kr" in url and "login" not in url:
        try:
            visible_login_inputs = page.locator(
                "#email:visible, #pwd:visible, #btnLogin:visible"
            ).count()
            if visible_login_inputs >= 2:
                return False
        except Exception:
            pass
        return True

    return False



def save_page_debug(page, output_dir: Path, prefix: str) -> None:
    """Save non-secret page diagnostics for headless runner troubleshooting."""
    safe_prefix = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in prefix)
    try:
        screenshot_path = output_dir / f"{safe_prefix}.png"
        page.screenshot(path=str(screenshot_path), full_page=True, timeout=5000)
        print(f"Saved DMDW debug screenshot: {screenshot_path}")
    except Exception as exc:
        print(f"Could not save DMDW debug screenshot: {exc}")

    try:
        html_path = output_dir / f"{safe_prefix}.html"
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"Saved DMDW debug HTML: {html_path}")
    except Exception as exc:
        print(f"Could not save DMDW debug HTML: {exc}")


def dismiss_dmdw_overlays(page) -> None:
    """Dismiss DMDW main-page popups that can block the login button in headless mode."""
    selectors = [
        "#btnModlClose1",  # 계속(PC버전유지)
        "#btnModlClose2",
        "#btnNoticeClose",
        "#btnPopupClose",
        "#btnClose",
        "#closeBtn",
        'a:has-text("계속(PC버전유지)")',
        'button:has-text("계속(PC버전유지)")',
        'a:has-text("PC버전유지")',
        'button:has-text("PC버전유지")',
        'button:has-text("닫기")',
        'a:has-text("닫기")',
        'button:has-text("확인")',
        'a:has-text("확인")',
        ".ui-dialog-titlebar-close",
        ".btn_close",
        ".btn-close",
        ".close",
    ]

    for selector in selectors:
        try:
            loc = page.locator(selector).first
            if loc.count() > 0 and loc.is_visible(timeout=300):
                print(f"Dismissing DMDW popup/control: {selector}")
                loc.click(timeout=1500, force=True)
                page.wait_for_timeout(300)
        except Exception:
            pass

    # Some DMDW popups leave a jQuery UI overlay above the login panel.
    # Removing only overlay/dialog containers is safer than clicking arbitrary coordinates.
    try:
        removed = page.evaluate(
            """
            () => {
              let removed = 0;
              const remove = (el) => {
                if (!el) return;
                el.remove();
                removed += 1;
              };

              document.querySelectorAll(
                '.ui-widget-overlay, .modal-backdrop, .blockUI, .ui-front.ui-widget-overlay'
              ).forEach(remove);

              document.querySelectorAll('.ui-dialog, .ui-dialog-content, .modal, .popup, .pop_wrap, .layer_popup').forEach(el => {
                const text = (el.innerText || el.textContent || '').trim();
                const hasLogin = !!el.querySelector('#email, #pwd, #btnLogin, input[placeholder="ID"], input[placeholder="PASSWORD"]');
                const looksLikeBlockingNotice =
                  text.includes('모바일') ||
                  text.includes('PC버전') ||
                  text.includes('공지') ||
                  text.includes('안내') ||
                  text.includes('알림') ||
                  text.includes('팝업');
                if (!hasLogin && looksLikeBlockingNotice) {
                  remove(el);
                }
              });

              document.body.classList.remove('modal-open');
              document.documentElement.style.overflow = '';
              document.body.style.overflow = '';
              return removed;
            }
            """
        )
        if removed:
            print(f"Removed DMDW blocking overlay/dialog elements: {removed}")
            page.wait_for_timeout(300)
    except Exception as exc:
        print(f"DMDW overlay cleanup JS failed: {exc}")


def click_login_button(page, login_button: str, pw_selector: str) -> None:
    """Click DMDW login robustly even when a popup overlay intercepts pointer events."""
    dismiss_dmdw_overlays(page)

    if login_button:
        try:
            page.click(login_button, timeout=5000)
            return
        except Exception as exc:
            print(f"Normal login button click failed; retrying after popup cleanup. reason={exc}")

        dismiss_dmdw_overlays(page)

        try:
            page.click(login_button, timeout=5000, force=True)
            return
        except Exception as exc:
            print(f"Forced login button click failed; trying DOM click. reason={exc}")

        page.evaluate(
            """
            (selector) => {
              const el = document.querySelector(selector);
              if (!el) throw new Error(`Login button not found: ${selector}`);
              el.click();
            }
            """,
            login_button,
        )
        return

    page.press(pw_selector, "Enter")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh a DMDW login cookie for VTG source sync.")
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR)
    parser.add_argument("--cookie-file", type=Path, default=None)
    parser.add_argument("--csrf-file", type=Path, default=None)
    parser.add_argument("--home-url", default=DMDW_HOME_URL)
    parser.add_argument("--browser-channel", default=os.getenv("DMDW_BROWSER_CHANNEL", ""))
    parser.add_argument("--browser-executable", default=os.getenv("DMDW_BROWSER_EXECUTABLE", ""))
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction, default=bool(os.getenv("CI")))
    parser.add_argument("--show-cookie-preview", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dmdw_id = os.environ.get("DMDW_ID", "").strip()
    dmdw_pw = os.environ.get("DMDW_PW", "").strip()
    if not dmdw_id or not dmdw_pw:
        raise SystemExit("DMDW_ID and DMDW_PW environment variables are required.")

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("playwright is required. Install requirements-dmdw.txt first.") from exc

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = args.cookie_file or output_dir / "cookie.txt"
    csrf_file = args.csrf_file or output_dir / "csrf.txt"

    with sync_playwright() as playwright:
        launch_kwargs = {
            "headless": args.headless,
            "args": [
                "--disable-popup-blocking",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        }
        if args.browser_executable:
            launch_kwargs["executable_path"] = args.browser_executable
        elif args.browser_channel:
            launch_kwargs["channel"] = args.browser_channel

        launch_preview = {
            "headless": launch_kwargs.get("headless"),
            "executable_path": launch_kwargs.get("executable_path", ""),
            "channel": launch_kwargs.get("channel", ""),
        }
        print(f"Launching browser for DMDW login: {launch_preview}")

        try:
            browser = playwright.chromium.launch(**launch_kwargs)
        except Exception as exc:
            print("DMDW browser launch failed before login page was opened.", file=sys.stderr)
            print("On Linux/self-hosted runners this usually means Chromium shared libraries are missing.", file=sys.stderr)
            print("Install them with: python -m playwright install-deps chromium", file=sys.stderr)
            print(f"Original launch error: {exc}", file=sys.stderr)
            raise

        context = browser.new_context(
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        print("Opening DMDW login page.")
        page.goto(args.home_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login_expired" in page.url:
            page.goto(args.home_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)

        id_selector = first_visible(page, ID_SELECTORS)
        pw_selector = first_visible(page, PW_SELECTORS)
        if not id_selector or not pw_selector:
            dump_login_candidates(page)
            raise RuntimeError("Could not locate DMDW ID/PW fields.")

        dismiss_dmdw_overlays(page)
        page.fill(id_selector, dmdw_id)
        page.fill(pw_selector, dmdw_pw)
        dismiss_dmdw_overlays(page)

        login_button = first_visible(page, LOGIN_BUTTON_SELECTORS, timeout=1000)
        print(f"DMDW login selectors: id={id_selector} pw={pw_selector} button={login_button or 'ENTER'}")
        try:
            click_login_button(page, login_button or "", pw_selector)
        except Exception:
            save_page_debug(page, output_dir, "dmdw_login_click_failed")
            raise

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeoutError:
            pass
        time.sleep(3)

        print(f"DMDW post-login url: {page.url}")
        if not looks_logged_in(page):
            save_page_debug(page, output_dir, "dmdw_login_not_completed")
            dump_login_candidates(page)
            raise RuntimeError("DMDW login did not appear to complete.")

        cookies = context.cookies(["https://dmdw.kma.go.kr"])
        cookie_header = build_cookie_header(cookies)
        if not cookie_header:
            raise RuntimeError("Failed to extract DMDW cookies.")

        cookie_file.write_text(cookie_header, encoding="utf-8")
        print(f"DMDW cookie saved: {cookie_file}")

        csrf = extract_csrf_from_page(page)
        if csrf:
            csrf_file.write_text(csrf, encoding="utf-8")
            print(f"DMDW CSRF token saved: {csrf_file}")
        else:
            print("No DMDW CSRF token found; continuing with cookie-only session.")

        if args.show_cookie_preview:
            print(f"Cookie preview: {cookie_header[:80]}...")
        else:
            print(f"Cookie length: {len(cookie_header)} characters.")

        browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
