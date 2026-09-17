# Polarwx source collection

Generate VTG never launches a browser or directly requests Polarwx JSON. It
first validates all other sources. If they cover every active Polarwx-supported
model, it skips Polarwx entirely. UKMO EPS without pressure remains incomplete,
unless an explicit source override was requested.

Otherwise VTG reads `data/polarwx/<UTC cycle>/<ATCF ID>.json`. Missing or stale
snapshots are queued as the `polarwx-requests` workflow artifact. After Generate
VTG or Backfill finishes, the independent **Prefetch Polarwx VTG source data**
workflow consumes that artifact and commits successful snapshots. The next
image-generation run sees them. The initial image does not wait for collection.

The collector uses a fresh, ordinary headless Chromium session, selects the
storm, Models, Raw and exact cycle through the public page controls, and reads
the response that the page loaded. It does not issue direct JSON requests,
reuse personal browser cookies, mask automation signals, or retry blocked
responses. Only the configured raw model arrays are saved, without ensemble
members or interpolated prior-cycle tracks.

- Snapshot identity and point valid times must match the requested cycle.
- Duplicate requests for one storm/cycle collapse into one artifact file.
- Successful snapshots are refreshed at most once per 15 minutes.
- Automatic requests cover the latest 48 hours only. The public active-storm UI
  is not an archive endpoint; older stored snapshots remain readable.
- Failed collections leave the previous successful snapshot untouched. Partial
  responses update usable models individually and retain absent/empty models
  from the same ATCF ID and cycle, with their original collection timestamps.
- Normal image updates retain the previous image and metadata while an absent
  snapshot would remove a previously selected Polarwx model. A first image with
  no previous output still renders from other sources without waiting.
- Missing snapshots do not stop other sources or image generation.

For a manual collection, dispatch `polarwx_prefetch.yml` with an active ATCF ID
and exact UTC cycle. `polarwx_browser_test.yml` additionally publishes a
screenshot, parsed tracks, pressure counts and separate cold/warm timings.
Install `requirements-polarwx.txt` only for collectors; normal rendering needs
only `requirements-vtg.txt`.
