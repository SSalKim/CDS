# Paused VTG source collectors

As of 2026-10-28, `DMDW` and `RAW.GITHUB` are paused in
`vtg_sources.PAUSED_SOURCE_IDS` to reduce recurring Actions work.

- VTG does not read DMDW source files or request GDM raw files.
- Paused sources cannot be selected, even with `--source-override`, or restored
  from the short-lived source backup. New availability records exclude them.
- Model IDs, parsers, source mappings, existing data, and workflow files remain.
  Historical analysis can still explicitly parse an archived file.
- Other source priorities and UKMO cadence/intensity preferences are unchanged.
  GenCast and WeatherNext2/3 remain enabled through their other mapped providers.
  Availability and first-arrival time can differ without the paused backups.

## GitHub workflow state

The following workflows are disabled using GitHub's workflow disable API, not
deleted or reduced to a skipped job:

| Repository | Workflow | File |
| --- | --- | --- |
| `SSalKim/CDS` | Sync DMDW VTG source data | `.github/workflows/dmdw_vtg_sync.yml` |
| `SSalKim/GDM` | Fetch Typhoon Data | `.github/workflows/fetch.yml` |

Cloudflare's external scheduler is managed separately. Remove or pause only its
dispatch calls for these two workflows, keeping VTG and other scheduled work.
Handle a rejected dispatch independently so it cannot stop unrelated dispatches.
No Cloudflare scheduler configuration is stored or changed in this repository.

## Reactivation

1. Review credentials and provider availability, then enable the required
   workflow in that repository's Actions UI.
2. Restore its external scheduler dispatch if it was paused there.
3. Remove only the required source from `PAUSED_SOURCE_IDS`, run the source
   tests, and deploy that change to resume VTG ingestion and backup replay.

Disabling DMDW reduces CDS data-only commits and associated Pages builds.
Pausing GDM reduces its collector runs but does not directly prevent CDS Pages
builds. Concurrent Pages builds can still be superseded by newer commits from
the remaining collectors; their deployment policy has not been changed here.
