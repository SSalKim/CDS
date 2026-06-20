# VTG Google Drive archive

VTG keeps active storm images in the repository so the page can load them
quickly through raw GitHub URLs. Older ended-storm images can be moved to
Google Drive while the site keeps a small per-system archive map.

## Data layout

VTG data is grouped by year and system:

```text
data/
  2026/
    TYP_2607_MEKKHALA/
      images/
      metadata/
        runs/
        source_availability/
        track_history.json
      manifest.json
      drive_archive.json
    index.json
  manifest.json
  status.json
```

`data/manifest.json` should stay small. It points to yearly indexes, each yearly
index points to system manifests, and the page loads a system manifest only when
that system is selected.

## Frontend contract

For archived images, `typhoon-guidance.js` loads the selected system's
`drive_archive.json` only when needed:

```text
data/2026/TYP_2607_MEKKHALA/drive_archive.json
```

Supported object form:

```json
{
  "updated_at_utc": "202606190415",
  "images": {
    "data/2026/TYP_2607_MEKKHALA/images/2026061900_120h.png": {
      "file_id": "google-drive-file-id",
      "url": "https://drive.google.com/thumbnail?id=google-drive-file-id&sz=w2400"
    }
  }
}
```

Supported list form:

```json
{
  "updated_at_utc": "202606190415",
  "images": [
    {
      "image_path": "data/2026/TYP_2607_MEKKHALA/images/2026061900_120h.png",
      "file_id": "google-drive-file-id",
      "url": "https://drive.google.com/thumbnail?id=google-drive-file-id&sz=w2400"
    }
  ]
}
```

## GitHub Actions connection

For a normal personal `My Drive` archive folder, use OAuth refresh-token auth.
Service accounts do not have personal Drive storage quota, so they can upload
only when the target is a Google Workspace shared drive or when domain-wide
delegation is configured.

1. Create a Google Cloud project.
2. Enable the Google Drive API.
3. Configure the OAuth consent screen.
4. Create an OAuth Client ID for a desktop app.
5. Use Google OAuth Playground with your OAuth Client ID and secret.
6. Authorize this scope:

```text
https://www.googleapis.com/auth/drive
```

7. Exchange the authorization code for tokens and copy the refresh token.
8. Create a Google Drive folder for the VTG archive.
9. Make the archive folder or uploaded files readable by anyone with the link.
10. Add these GitHub repository secrets:

```text
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_DRIVE_REFRESH_TOKEN
VTG_ARCHIVE_DRIVE_FOLDER_ID
```

`VTG_ARCHIVE_DRIVE_FOLDER_ID` is the folder ID from the Drive URL. The workflow
still accepts `GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON`, but that path is intended for
shared drives rather than a personal My Drive folder.

## Automation

The archive sync script is:

```text
vtg_drive_archive.py
```

The manual GitHub Actions workflow is:

```text
.github/workflows/vtg_archive.yml
```

Run `Archive VTG images to Google Drive` from the Actions tab. Suggested first
run:

```text
max_files: 100
delete_local_after_upload: true
dry_run: true
```

If the dry run candidate list looks right, run again with:

```text
max_files: 500
delete_local_after_upload: true
dry_run: false
```

`max_files` limits only new Drive uploads. Files already present in a system
`drive_archive.json` can still be removed from the repository when
`delete_local_after_upload` is true. Use `max_files: 0` only when a one-shot
large migration is acceptable.

The script follows the same live-image rule as `typhoon-guidance.js`: active
window images and images from roughly the last 30 hours stay in the repository
for raw GitHub delivery. Older PNGs are eligible for Drive archive.
