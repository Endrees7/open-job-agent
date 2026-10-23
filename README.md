# Open Job Agent

**Privacy-first job discovery and explainable vacancy matching** · Python · GitHub Actions · Google Apps Script · Google Sheets

A **public portfolio project** that turns approved public job-board data into a deduplicated, human-reviewable vacancy dashboard. Runs fully offline against **fictional data** without accounts, tokens, or billing.

> **Current status:** Offline demo and unit tests implemented. Public Greenhouse/Lever/Ashby adapters are implemented and unit-tested with mock responses; live integrations and Google web-app deployment require the owner's independent setup. No automatic applications, Gmail sending, login, CAPTCHA bypass, scraping of restricted platforms or credential handling.

## Features

| Feature | Status |
|---|---|
| Reproducible synthetic demo (no network) | Implemented |
| Public employer board adapters (Greenhouse / Lever / Ashby) | Implemented; mock-tested |
| Explainable ranking (0–100) with unknowns and blockers | Implemented |
| Deduplication and structured JSON reports | Implemented |
| GitHub Actions CI and manual demo | Configured; verify on new GitHub repo |
| Signed optional Apps Script → private Sheets upsert | Implemented; integration not yet verified in new deployment |
| CV creation, Gmail follow-ups or automated applications | **Not implemented** |

> **A score is a ranking heuristic, not a probability of getting hired.** Unknown salary, contract or country restrictions are recorded as unknown; no action is taken automatically.

## 60-second local demo

Requires Python 3.10+.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m jobagent.cli demo
```

See `build/report.json` (local/ignored) for three **fictional** job postings. The CLI prints counts only, never private candidate data. All reports are ignored by Git.

## GitHub demo

Run **Actions → Open Job Agent (manual) → Run workflow → mode: demo**. The workflow does not need GitHub Secrets and doesn't contact outside job boards or Google. There is **no scheduled job** enabled.

## How it works

```text
Synthetic demo JSON        OR       Official public employer-board APIs
         \                                  /
          → Normalize + deduplicate + evaluate
                    → Human review status
                    → Local JSON report (Git-ignored)
                    → Optional signed webhook → Private Google Sheets
```

Configuration and secrets are intentionally separated from committed code. Real candidate profiles should live only in a Git-ignored local directory or owner-managed GitHub Actions Secrets. A fresh owner-only Google Sheet uses the Apps Script in `apps_script/`, with no Gmail/Drive scopes.

## Repository structure

```text
.github/workflows/   CI + manual demo/scan (no schedule)
apps_script/         Signed intake: receive reports and write Sheets
config/              Fictional examples only; config/private/ is Git-ignored
data/                Fictional vacancies only
jobagent/            CLI, private config, API adapters, scoring, pipeline, signed transport
tests/               Python tests with mock HTTP responses
tools/               Offline Node.js verifier smoke tests
docs/                Architecture, private setup, publishing checklist
```

## Documentation

- [Architecture & threat boundaries](docs/ARQUITETURA.md)
- [Private setup for optional live scan + Sheets](docs/CONFIGURACAO_PRIVADA.md)
- [Pre-publication security checklist](docs/SEGURANCA_E_PUBLICACAO.md)

## Responsible use

Use only sources that allow your intended read-only access, observe provider terms and rate limits, and avoid claiming confirmation of job availability or eligibility without evidence. This software **never submits a job application**. No real personal data is included in examples. Costs depend on your GitHub/Google usage plans; no payment or upgrade is required by the demo.

## License

No open-source license has been assigned. Publishing source for portfolio visibility does not itself grant redistribution or reuse rights. The owner may choose a license later.
