# CDS Pages Deployment

GitHub Pages publishes through `.github/workflows/pages.yml` with the repository
Pages build type set to `workflow`. The public URL and relative asset paths stay
unchanged. No Jekyll transformation is required for the static HTML/JS/CSS site.

- Pushes to `main` and manual dispatches can request publication.
- VTG generation, backfill, archive, Polarwx collection, and manual DMDW collection
  completions also request publication. This covers commits made by `GITHUB_TOKEN`,
  which do not trigger another push workflow.
- One production concurrency group finishes an active deployment before starting
  another; waiting requests collapse to the latest pending snapshot.
- A sparse checkout compares tracked public Git blobs with the last successful
  `github-pages` deployment. Unchanged public content skips packaging and upload.
- Packaging includes root web assets, `data/`, `fonts/`, `docs/`, and
  `special_images/`. Untracked files, hidden paths, operational Python code, tests,
  and local outputs are not published. Public files must be regular files.
- A failed publish cleans up only its own commit's deployment request and retries
  once. An unsuccessful or cancelled job also attempts the same bounded cleanup.
- `deployment.json` records the published commit and public-tree fingerprint.

To republish unchanged content, manually run **Deploy CDS Pages** with `force`
enabled. Do not re-enable branch-based Pages publishing alongside this workflow.
