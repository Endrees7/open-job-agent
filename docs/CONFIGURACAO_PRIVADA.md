# Private setup: optional, not required for a public demo

This document is not a deployment guarantee; the public demo runs without any account.

## Local scan

On Windows (PowerShell), open the new project folder:

```powershell
py -m pip install -e ".[dev]"
New-Item -ItemType Directory -Path config/private -Force
Copy-Item config/profile.example.json config/private/profile.json
Copy-Item config/sources.example.json config/private/sources.json
```

Edit the copies **locally**, not the committed examples. Put approved public company board entries in `config/private/sources.json`:

```json
{"boards": [{"provider": "greenhouse", "slug": "example-company-board", "company": "Example Company"}]}
```

That slug is illustrative; replace it with a publicly documented real employer slug before scanning.

```powershell
py -m jobagent.cli scan
```

The output is written to ignored `build/report.json` locally. This public project never sends an application.

## Owner-only Google Sheets integration

1. Create a **new private spreadsheet**. In Extensions > Apps Script, paste `apps_script/Code.gs` and add the `apps_script/appsscript.json` manifest (requires enabling the manifest editor). Do **not** copy the private project's code, sheet or properties.
2. Execute `setupProject` once and authorize only spreadsheet access. New sheets `VAGAS`, `EXECUCOES`, `PAINEL` are created.
3. Under Apps Script Project Settings > Script Properties set `OJA_HMAC_SECRET` to a new random 32+ character value. Store it safely; never copy it into source code or screenshots.
4. Deploy a Web App running **as you**, with access appropriate for a GitHub Actions server-to-server call. Google Apps Script Web Apps do not directly accept GitHub as an authenticated Google user, so a publicly reachable deployment may be necessary; the **HMAC validates every POST**. Treat the URL as secret. Do not reuse the old project's endpoint or key.
5. In the NEW GitHub repository > Settings > Secrets and variables > Actions > New repository secret, create **four new secrets**: `OJA_PROFILE_JSON`, `OJA_SOURCES_JSON`, `OJA_APPS_SCRIPT_URL`, `OJA_HMAC_SECRET`. The first two values are complete JSON documents; never paste them into workflow files. Use a brand-new HMAC secret unrelated to your private repository.
6. Test authentication with `python -m jobagent.cli test-webhook --send` locally or configure the manual `scan` workflow. These steps require the private values in your environment. Validate results in the **new private** Sheet.

**Safety:** A public code repository is not the same as a public Google Sheet. Keep the Google Sheet private. Do not paste credentials, real resumes, spreadsheet identifiers, webhook links or execution reports into GitHub issues, Actions logs, commits or chats.

## Optional workflow behavior

`.github/workflows/run.yml` is a manual workflow only. It starts in synthetic demo mode. The `scan` option fails if the four Secrets are not provided. No GitHub billing is enabled by this code, but quotas and platform plan limits remain your responsibility.

## If anything goes wrong

Do not make the old private repo public, and do not migrate its `.git` history. Disable the web-app deployment if necessary; revoke/rotate any exposed HMAC key or URL. The new app has no send/auto-apply implementation, so no application should be triggered by this code.
