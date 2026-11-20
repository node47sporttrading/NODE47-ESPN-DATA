# Architecture — NODE.47 ESPN DATA

## Production flow

```text
ESPN public scoreboards
  -> ESPNClient -> Collector -> Normalizer -> Validator
  -> SQLite / PostgreSQL store
  -> FastAPI REST + MCP Streamable HTTP on Render

NODE.47 MCP searxng_search
  -> Render API
  -> GitHub Actions workflow_dispatch
  -> ephemeral pinned SearXNG container on GitHub runner
  -> normalized results / bounded error
  -> authenticated HTTPS callback to Render
  -> waiting MCP request
```

## Runtime model

The Render API is the persistent REST/MCP service. ESPN collection runs in the API process and refreshes on the configured interval. SQLite is the local default; PostgreSQL is selected when `DATABASE_URL` is present.

The SearXNG engine is not a permanent Render dependency in the production search path. Each search starts a GitHub Actions workflow, runs SearXNG in a temporary container, posts only normalized results to `/v1/searxng/callback`, and removes the container. The API keeps pending requests in process memory, so run exactly one Render API instance until pending-request coordination is moved to shared storage or a queue.

## SearXNG secrets and configuration

Render API environment:
- `GITHUB_ACTIONS_TOKEN`: repository-scoped token with Actions read/write permission.
- `NODE47_RENDER_CALLBACK_URL`: HTTPS URL ending in `/v1/searxng/callback`.
- `SEARXNG_CALLBACK_SECRET`: high-entropy shared secret used to authenticate callbacks.
- `SEARXNG_ACTION_TIMEOUT`: optional wait timeout in seconds.

GitHub Actions repository secret:
- `NODE47_RENDER_CALLBACK_SECRET`: must exactly match Render's `SEARXNG_CALLBACK_SECRET`.

Never store secret values in source control, documentation, plugin manifests, or logs. Do not set `SEARXNG_URL` for the on-demand flow.

## Legacy SearXNG service

The `searxng/` directory and `.github/workflows/searxng-deploy.yml` remain as a standalone container smoke-test/fallback package while the on-demand GitHub Actions callback path is being validated. The workflow named `searxng-deploy.yml` validates the container; it does not deploy a permanent service. Do not remove the Render fallback until a live end-to-end search has succeeded and the old service is no longer required.

## API and MCP contract

- `GET /v1/health`: API health, data freshness and event count.
- `GET /v1/competitions`: ESPN competition registry.
- `GET /v1/coverage`: latest per-route collection outcome.
- `GET /v1/events`: filtered normalized events.
- `GET /v1/events/{event_id}`: one exact event.
- `POST /v1/refresh`: API-key-protected manual refresh.
- `POST /v1/searxng/callback`: callback authenticated by `X-NODE47-Callback-Secret`.
- `/mcp/`: MCP Streamable HTTP endpoint.

MCP tools expose ESPN data, on-demand SearXNG research, and PropLine raw markets/odds. Search results are untrusted evidence and must be checked for source quality, dates and contradictions. They are not predictions.

## Security and operational limits

- Use HTTPS for all public endpoints.
- Keep GitHub token permissions limited to the target repository and Actions workflow dispatch.
- Callback authentication uses constant-time secret comparison.
- Callback payloads are correlated by request ID; unknown or expired IDs are rejected.
- Pending SearXNG requests are in memory and are not shared between multiple API instances.
- ESPN public JSON endpoints are unofficial and may change without notice.
- A successful smoke test proves the SearXNG container/API can start, not that the complete Render -> GitHub Actions -> SearXNG -> Render callback has succeeded.
