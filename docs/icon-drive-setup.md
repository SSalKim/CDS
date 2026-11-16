# Second Chart Drive Setup

The second personal Google Drive account can store ICON and future chart models;
it is not ICON-exclusive. Do not replace existing PUBLIC_CHARTS_DRIVE_* or VTG
credentials. The new repository secrets have the prefix PUBLIC_CHARTS_DRIVE2_.

## Google Console

1. Sign into the new Drive account and create an owned My Drive folder, e.g.
   CDS_Chart2. Copy the folder ID after /folders/ in its URL. Keep it private.
   The folder name is arbitrary; authentication and storage use its folder ID.
2. Create/select a Google Cloud project and enable Google Drive API.
3. In Google Auth Platform, configure Branding with an app name, support email
   and developer contact email. Select External audience; add the new account
   as a test user while the app is in Testing.
4. Create an OAuth client of type Desktop app and download its JSON. Keep the
   JSON outside Git, for example in Downloads.
5. In Audience, use Publish app to switch to In production before authorizing
   a long-running connection. Testing authorizations for Drive expire after
   seven days. Publishing is not the same as submitting for brand verification.
   Personal-use verification exceptions do not guarantee that a particular
   Console configuration accepts empty homepage/privacy-policy fields. If the
   Console blocks publication, inspect its exact message rather than inventing
   domains or uploading an unnecessary logo.

A separate Cloud project is optional. An existing External/In-production OAuth
client may be reused, but the NEW Drive account must grant its own authorization.
That creates a separate account-specific refresh token. Do not revoke the old
account's authorization or replace its secrets.

Official documentation:
- https://developers.google.com/workspace/drive/api/quickstart/python
- https://support.google.com/cloud/answer/15549945
- https://developers.google.com/identity/protocols/oauth2#expiration

The currently published app disclosure pages can be used for CDS-CHART branding:

- Homepage: https://ssalkim.github.io/CDS/oauth.html
- Privacy policy: https://ssalkim.github.io/CDS/privacy.html
- Authorized domain: ssalkim.github.io (no scheme or path)

Do not claim domain verification is complete merely because these pages load.
If Google requests ownership verification, complete that separate check.

## Local Authorization

Run PowerShell in E:\\제작자료\\CDS3\\CDS_Git. The updated helper can locate an
installed GitHub CLI even when this terminal has an older PATH.

```powershell
& .\local_tools\weathermesh\.venv\Scripts\python.exe public_charts_authorize.py `
  --client-secrets "$env:USERPROFILE\Downloads\<OAuth JSON filename>" `
  --folder-id "<NEW Drive folder ID>" `
  --account-email "<NEW Drive account email>" `
  --register-repo "SSalKim/CDS-Public-Charts" `
  --secret-prefix "PUBLIC_CHARTS_DRIVE2_"
```

The helper validates the authenticated account and folder owner before setting
any secrets. It sends values to gh secret set over stdin; it does not print or
save refresh tokens. Never send the JSON contents or tokens in chat.

Five new secrets are registered:

```text
PUBLIC_CHARTS_DRIVE2_CLIENT_ID
PUBLIC_CHARTS_DRIVE2_CLIENT_SECRET
PUBLIC_CHARTS_DRIVE2_REFRESH_TOKEN
PUBLIC_CHARTS_DRIVE2_FOLDER_ID
PUBLIC_CHARTS_DRIVE2_ACCOUNT_EMAIL
```

After registration, use CDS-Public-Charts Actions > Verify chart Drive connection
with drive_account=secondary. This verifies ownership without uploading or deleting
files and does not fall back to the primary account if secondary settings are missing.
Authentication does not by itself enable automatic ICON production.
