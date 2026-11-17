# CDS Private Usage Analytics

Dedicated Worker and D1; independent of chart production, Drive and VTG.
Only `/collect` and `/health` are public. `/admin` and every `/admin/*` API/asset
require a verified Cloudflare Access JWT with the configured audience, issuer
and exact administrator email. Missing configuration denies access.

## Configuration

- D1 binding `DB`; apply `migrations/0001_events.sql`.
- Secrets: `HMAC_SECRET` (stable random 32+ bytes), `ADMIN_EMAIL`,
  `ACCESS_AUD`, `ACCESS_TEAM_DOMAIN` (team.cloudflareaccess.com),
  `CONNECTION_DATA_KEY` (separate stable random 32-byte AES key, base64 encoded).
- Protect `cds-usage-analytics.kwj1407.workers.dev/admin` with a self-hosted
  Cloudflare Access application and an exact-email Allow policy.
- Leave `/collect` outside Access; `ALLOWED_ORIGINS` limits browser collection.
- After anonymous denial and owner login are verified, enable
  `cds-usage-config.js` with the HTTPS `/collect` endpoint.
- Keep Workers/D1 on their existing plan; no paid plan is required by this code.
  Monitor request and D1 row quotas. CORS is not proof of a human visitor;
  bounded batches and a rate limiter reduce, but do not eliminate, bogus events.

The client reuses GA's client/session IDs only when available and permitted.
The server stores keyed browser/session hashes, not raw GA IDs or visitor email
addresses. With `COLLECT_CONNECTION_INFO=true`, it additionally captures the
edge-provided `CF-Connecting-IP` and `request.cf.city/country`; it never trusts
client JSON or X-Forwarded-For for these values. City is approximate, not GPS.
The connection metadata is AES-GCM encrypted as one envelope under the separate
key. Only authenticated administrator APIs decrypt it; the public collector
does not return it. The rate limiter uses a separate transient keyed IP hash.
Logs are disabled. Connection details are not sent to GA. No collected visitor
records are committed to Git or saved to chart Drive accounts. Do not regenerate the connection key during ordinary
deployment: existing envelopes require the same key to remain readable.

TOP counts distinct browser + model + initialization + product + region + detail
within the selected KST date range, independent of forecast lead or comparison
layout. Raw history retains each distinct displayed lead. This is browser usage,
not an identity system. Data starts at activation; old missing GA parameters
cannot be reconstructed. Retention deletes records older than 90 days daily.
Connection metadata is hidden by the API after 30 days and removed at the next
daily cleanup, independently of 90-day chart history. Legacy rows remain blank;
their IP or city cannot be reconstructed. A browser can change IP, and multiple
browsers can share an IP. The user list takes connection metadata from its most
recent matching event, while detailed history retains each event's metadata.
CSV exports include administrator-only connection data, are limited to 5,000
filtered rows, and escape spreadsheet formulas. Export timestamps use UTC ISO.

## Local Verification

Use Node 24+, `pnpm install`, `pnpm run build`, `pnpm test`.
`wrangler d1 migrations apply cds-usage-analytics --local` prepares test storage.
`wrangler dev --local --ip 127.0.0.1 --port 8791 --var LOCAL_PREVIEW:true`
serves the owner preview at `http://127.0.0.1:8791/admin/`.
The local bypass also checks the request hostname; never configure it in
production. Local test events must not be sent to the production collector.

Build dependencies are pinned in `pnpm-lock.yaml`. Rebuild icons with
`pnpm run build` before deploying. The site packaging allowlist excludes this
directory; only the collector and opt-out assets are in the public site.
