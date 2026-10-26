# ideal-waddle — public marketplace archive

A resumable, conservative crawler bootstrap for the public xAI Grok Bot Marketplace.

## Status
This is not yet a completed scrape. Run the crawler, inspect the output, and commit a coverage report before claiming completeness. Read HANDOFF.md first.

## Run
Requires Python 3.11+ and the standard library.

Start with a small test:

    python3 scripts/scrape_marketplace.py --delay 3 --max-pages 10

Then increase --max-pages after checking site policy and output quality. To follow linked public bot detail URLs under the marketplace bot path, add --include-detail-pages.

## Output
- data/manifest.jsonl: attempted URL, status, timestamp, hashes, and artifact paths.
- data/catalog.json: index of successfully parsed pages.
- data/pages/: HTML snapshots.
- data/text/: extracted readable text.

The crawler skips successful URLs already in the manifest. It checks robots.txt and refuses to crawl if robots.txt cannot be fetched. It does not authenticate or bypass blocks.

## Reuse policy
Only public pages are in scope. Respect robots.txt, site terms, rate limits, attribution, and copyright. Before committing or redistributing full HTML/text at scale, verify that doing so is permitted. If not, keep URLs, hashes, metadata, and limited excerpts instead.
