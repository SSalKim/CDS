# CDS Private Usage Analytics

Dedicated Worker and D1; independent of chart production, Drive and VTG.
Only `/collect` and `/health` are public. `/admin` and every `/admin/*` API/asset
require a verified Cloudflare Access JWT with the configured audience, issuer
and exact administrator email. Missing configuration denies access.

## Configuration

- D1 binding `DB`; apply `migrations/0001_events.sql`.
- Secrets: `HMAC_SECRET` (stable random 32+ bytes), `ADMIN_EMAIL`,
  `ACCESS_AUD`, `ACCESS_TEAM_DOMAIN` (team.cloudflareaccess.com).
- Protect `cds-usage-analytics.kwj1407.workers.dev/admin` with a self-hosted
  Cloudflare Access application and an exact-email Allow policy.
- Leave `/collect` outside Access; `ALLOWED_ORIGINS` limits browser collection.
- After anonymous denial and owner login are verified, enable
  `cds-usage-config.js` with the HTTPS `/collect` endpoint.
- Keep Workers/D1 on their existing plan; no paid plan is required by this code.
  Monitor request and D1 row quotas. CORS is not proof of a human visitor;
  bounded batches and a rate limiter reduce, but do not eliminate, bogus events.

The client reuses GA's client/session IDs only when available and permitted.
The server stores keyed hashes, not raw IDs, email addresses or IPs. The rate
limiter uses a transient keyed IP hash. Logs are disabled in this configuration.
No visitor data is committed to Git or saved to chart Drive accounts.

TOP counts distinct browser + model + initialization + product + region + detail
within the selected KST date range, independent of forecast lead or comparison
layout. Raw history retains each distinct displayed lead. This is browser usage,
not an identity system. Data starts at activation; old missing GA parameters
cannot be reconstructed. Retention deletes records older than 90 days daily.
CSV exports are limited to 5,000 filtered rows and escape spreadsheet formulas.

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
