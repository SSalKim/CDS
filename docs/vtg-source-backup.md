# Short-lived VTG source backups

The regular `vtg.yml` workflow restores `vtg-source-backup-v1` before rendering.
This artifact is separate from Git: no source snapshots are committed or served
by GitHub Pages. Manual image runs and historical backfills do not publish it.

`VTG_SOURCE_BACKUP_DIR` enables backup handling in the renderer. The payload is a
compressed, normalized forecast table, not HTTP responses, URLs, credentials, or
ensemble-member archives. It is keyed by the KMA storm identity and exact forecast
initialization, independently of an ATCF INVEST-to-numbered-storm transition.
Explicit KMA TD/TYP links permit the same storm's backup to follow a promotion.

Every render still fetches current data. A usable fresh source/model track replaces
its entire previous track, even if shorter. Only missing or unusable tracks fall
back to the same source/model's saved track; cached tails are never appended to
fresh forecasts. Existing provider priorities and motion, gap, and dateline QC
still apply. Official KMA analysis rows and past tracks are not backed up here.

Backups are removed when the existing Drive-archive logic confirms official final
termination. A TYP's downgrade to an active linked TD, a TD's promotion to a TYP,
or absence from an API response is not final termination. Linked TD backups are
also removed once their TYP finally ends.

Additional bounds protect against stalled official lists and failed cleanup:

- Keep only cycles from the last 48 hours, measured from initialization, not upload.
- Limit each expanded snapshot to 8 MiB and the compressed local bundle to 64 MiB.
- Evict the oldest cycles first if the bundle exceeds the limit.
- Publish one rolling artifact with a two-day artifact retention period.
- Delete superseded artifacts only after the replacement upload succeeds.
- Publish an empty index when no cycles remain so ended-storm artifacts are removed.

All restore entries are checked against an index of SHA-256 hashes before writing.
A failed restore or upload does not delete the previous remote artifact and does
not block image generation. A corrupt newest artifact can fall back to an older
valid artifact if one remains. In the unusual event cleanup fails, duplicates may
remain temporarily until their retention period expires.

This is a best-effort production safeguard, not a permanent historical archive.
Data deleted by a provider before the first successful collection cannot be
recovered, nor can expired backups be used for historical reprocessing. Provider
access failures and GitHub storage/service limits can also prevent backup refresh.
