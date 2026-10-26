# Handoff — xAI Bot Marketplace archival mirror

Repository: https://github.com/imanbarati/ideal-waddle  
Source: https://x.ai/bot/marketplace  
Status: Bootstrap planning only; a full crawl has NOT yet been run or verified. Do not claim completeness until coverage checks are committed.

## Goal
Create a reproducible, respectful archive of publicly accessible xAI/Grok Bot Marketplace pages and linked public bot detail pages. Preserve source URLs, fetch timestamps, HTTP status, hashes, HTML/text snapshots when permitted, and a resumable URL inventory.

## Guardrails
- Public unauthenticated pages only. Do not log in, use private APIs, evade access controls, solve CAPTCHAs, or bypass rate limits.
- Read and honor https://x.ai/robots.txt and applicable site terms. If policy prohibits a path or crawl, stop and document it.
- Use low request rates and gentle retries; no parallel request storms.
- Preserve attribution and source URLs. Before publicly redistributing full HTML or descriptions at scale, review copyright/licensing and site terms. If redistribution is not permitted, keep metadata, links, hashes, and limited excerpts rather than full text.
- Never collect private user data, credentials, cookies, or account-only content. Never commit tokens.

## Expected deliverables
1. Resumable crawler in scripts/scrape_marketplace.py.
2. data/manifest.jsonl: each attempted URL, status, timestamp, final URL, content hash, artifact paths, and error.
3. data/pages/ and data/text/ snapshots only if policy allows retaining them.
4. data/catalog.json normalized index where extraction is reliable.
5. reports/coverage.md documenting crawl date, counts, failures, robots decisions, duplicates, and gaps.
6. Optional manually triggered/scheduled GitHub Actions refresh with conservative rate limiting and size controls.
7. Update this handoff with exact commit SHA, crawl outcome, counts, failures, and next steps.

## Known facts at handoff creation
- Repository was empty on main when checked 2026-10-26; connected GitHub integration has write permission.
- Marketplace category pages include paths such as /bot/marketplace/marketing, /personal, and /operations. The catalog changes, so derive URLs at crawl time instead of hard-coding counts.
- This repository does not yet contain a verified full archive.

## Next agent checklist
1. Inspect the repository and this handoff first.
2. Review current robots.txt, terms, and whether retaining/re-publishing full HTML/text is permitted.
3. Implement or inspect a conservative crawler; test on 5–10 URLs and inspect output.
4. Extract public bot fields (name, creator, description, categories, skills, routines, integrations) only when present in public page content.
5. Crawl all discovered category pages and publicly linked detail pages within approved scope, with resume support.
6. Verify duplicates, canonical URLs, failures, and output size. Commit inventory and coverage report; consider release/workflow artifacts for large snapshots if permitted.
7. Test manual refresh and ensure no credentials are needed.
8. Update this file with exact commands, commit SHA, run date, counts, failures, and remaining work.

## Definition of done
- robots/terms review and scope documented.
- Every discovered in-scope page is archived or explicitly listed as skipped/failed.
- Snapshots have source attribution, timestamps, hashes, and HTTP status.
- Coverage report states actual counts and known gaps.
- Crawl resumes after interruption without unnecessarily re-downloading successful URLs.
- No private/authenticated data or secrets are included.
