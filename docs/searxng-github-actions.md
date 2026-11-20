# NODE.47 — SearXNG à la demande via GitHub Actions

## Architecture

1. The NODE.47 MCP tool receives a web-research query on the Render API.
2. Render dispatches `.github/workflows/searxng-search.yml` through the GitHub Actions REST API.
3. The workflow starts a short-lived SearXNG container on its GitHub-hosted runner, performs the search and normalizes the result records.
4. The workflow sends only the structured results (or a bounded error) to Render's authenticated callback.
5. Render returns the results to the MCP caller. The SearXNG container is removed when the workflow finishes.

The Render API does not connect to a persistent SearXNG service. The existing Render SearXNG service should remain available during rollout and be retired only after the end-to-end workflow has been verified.

## Required secrets and variables

### Render API service — secret environment variables

- `GITHUB_ACTIONS_TOKEN`: fine-grained GitHub token scoped only to `node47sporttrading/NODE47-ESPN-DATA`, with **Actions: Read and write** permission. Contents write is not needed.
- `SEARXNG_CALLBACK_SECRET`: high-entropy random secret shared with the GitHub Actions repository secret.
- `NODE47_RENDER_CALLBACK_URL`: `https://node47-espn-data.onrender.com/v1/searxng/callback`
- `SEARXNG_ACTION_TIMEOUT`: optional; defaults to 210 seconds.

### GitHub repository — Actions secret

- `NODE47_RENDER_CALLBACK_SECRET`: set to exactly the same random value as Render's `SEARXNG_CALLBACK_SECRET`.

The workflow passes the callback URL as a dispatch input. The callback secret is never passed as a workflow input; it is read from the GitHub Actions secret store and sent only as an HTTPS request header.

## Search execution and freshness

- Default language: French.
- Default categories: general and news.
- Default recency window: last week.
- Allowed recency windows: day, week, month, year, or omitted.
- Search result limit: 1–20.
- SearXNG runs only for the duration of a workflow; no Render SearXNG web service is required for new searches.

## Operational constraints

- GitHub-hosted runner startup, Docker image build and search add latency; this is not an instant local search endpoint.
- The Render API waits for the callback, with a bounded timeout. A timeout is reported as an error; it never silently falls back to the old Render SearXNG instance.
- The callback is authenticated with a shared secret and correlated to an unpredictable request UUID.
- Pending requests are held in process memory. Keep the Render API at one instance during initial rollout; a multi-instance deployment would require a shared result store/queue.
- GitHub Actions usage quotas and runner minutes apply. No paid Render plan is required for the SearXNG search execution itself.
- Do not remove the existing Render SearXNG service until a real MCP search has succeeded through GitHub Actions and the old path is no longer used.

## Verification

1. Configure the Render and GitHub secrets above.
2. Merge the workflow and API changes to `main`.
3. Deploy the API on Render.
4. Call `searxng_health`, then `searxng_search` with a recent query.
5. Verify the GitHub Actions run, authenticated callback, and returned source URLs.
6. Only after successful verification, remove the old Render SearXNG service and its obsolete `SEARXNG_URL` configuration.
