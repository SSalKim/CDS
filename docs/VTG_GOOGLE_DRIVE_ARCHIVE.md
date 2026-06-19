# VTG Google Drive archive

This project keeps live VTG images fast by loading active storm images from
`raw.githubusercontent.com`. Ended storms can remain in `VTG_IMG`, or can be
moved to Google Drive and exposed through a small archive manifest.

## Frontend contract

`typhoon-guidance.js` optionally loads:

```text
VTG_IMG/drive_archive_manifest.json
```

If the file is missing, the page falls back to the existing `VTG_IMG` image
paths. If the file exists, ended storm image paths listed in the manifest are
loaded from the provided Drive URLs.

Supported object form:

```json
{
  "updated_at_utc": "202606190415",
  "images": {
    "VTG_IMG/2025/TYP_2501_SAMPLE/2025010100_120h.png": {
      "file_id": "google-drive-file-id",
      "url": "https://drive.google.com/uc?export=view&id=google-drive-file-id"
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
      "image_path": "VTG_IMG/2025/TYP_2501_SAMPLE/2025010100_120h.png",
      "file_id": "google-drive-file-id",
      "url": "https://drive.google.com/uc?export=view&id=google-drive-file-id"
    }
  ]
}
```

## GitHub Actions connection

1. Create a Google Cloud project.
2. Enable the Google Drive API.
3. Create a service account and JSON key.
4. Create a Google Drive folder for the VTG archive.
5. Share that folder with the service account email as Editor.
6. Make the archive folder or uploaded files readable by anyone with the link.
7. Add these GitHub repository secrets:

```text
GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON
VTG_ARCHIVE_DRIVE_FOLDER_ID
```

`GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON` should contain the full service account
JSON. `VTG_ARCHIVE_DRIVE_FOLDER_ID` is the folder ID from the Drive URL.

## Recommended flow

Keep the latest active storm images in the repository for raw GitHub delivery.
When a storm ends, upload that storm folder to Google Drive, remove or stop
publishing those older image files from the deploy artifact, and update
`VTG_IMG/drive_archive_manifest.json` with the Drive URLs.

Google Drive is best treated as an archive store, not a high-performance CDN.
For old storms this is usually acceptable because they are viewed less often
than active storms.

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

`max_files` limits only new Drive uploads. Files already present in
`drive_archive_manifest.json` can still be removed from the repository when
`delete_local_after_upload` is true. Use `max_files: 0` only when a one-shot
large migration is acceptable.

The script follows the same live-image rule as `typhoon-guidance.js`: active
window images and images from roughly the last 30 hours stay in the repository
for raw GitHub delivery. Older PNGs are eligible for Drive archive.
