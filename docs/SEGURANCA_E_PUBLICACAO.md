# Publishing checklist

## What has been sanitized

The public package was written as a clean new project, without any `.git` history, real candidate profile, CV, Gmail access, salary preference or existing Google deployment URL. The example data is fictional.

## Mandatory checks before pushing your own edits

- [ ] Do not copy `.git` folders or historical commits from any private repository.
- [ ] Confirm new GitHub repository is empty; **do not use a template/importer linked to the private repository**.
- [ ] Do not copy credentials or real `config/private` files into Git.
- [ ] Verify `git status` and the staged files (no build/report.json, PDFs, resumes, tokens).
- [ ] Check the GitHub Actions logs after first run; avoid revealing private jobs in logs.
- [ ] Keep new Google Sheet and Script Properties private and independent from the old project.
- [ ] Decide separately whether to add an open-source license. Public visibility alone does not set reuse permissions.

Automated tests validate key safety properties but cannot certify that future edits or all third-party services are secure. Review every contribution before merging.
