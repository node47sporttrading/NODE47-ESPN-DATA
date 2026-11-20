# NODE.47 SearXNG

Standalone public SearXNG service for NODE.47 research.

## Render deployment

Create a Render Blueprint using `searxng/render.yaml`. The service is intentionally reachable from the public internet and has no HTTP authentication. The generated `SEARXNG_SECRET` is an internal SearXNG application secret; it does not restrict public access.

SearXNG's `public_instance` mode is disabled because that mode forces the built-in limiter, which requires Valkey. Disabling that mode does not add authentication or make the URL private; the search endpoint remains publicly accessible. The built-in limiter is also disabled, so there is no application-level request throttling in this deployment.

Set `SEARXNG_URL` on the NODE.47 MCP service to the deployed service URL. The MCP client uses the public JSON endpoint `/search?format=json`.

## Operational warning

This instance is open to all internet users. Public traffic can consume Render resources and trigger upstream search-engine throttling. Add Valkey-backed rate limiting or an edge rate-limit layer before scaling production traffic.

The Render free plan may spin down after inactivity and is intended for initial validation, not guaranteed always-on production use.
