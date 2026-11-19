# Architecture — NODE.47 ESPN DATA V0.0.7

ESPN public JSON scoreboards (unofficial / undocumented)
-> ESPNClient -> Collector -> Normalizer -> Validator
-> SQLite store on persistent /data volume
-> FastAPI /v1/* (health, competitions, coverage, events, refresh)
-> NODE.47 SPORT ANALYT (native MCP connector integration: next phase)
-> GitHub Pages snapshots / coverage manifest

## Runtime model
The API is an always-on HTTP service. At startup it attempts an initial collection, then refreshes every NODE47_REFRESH_SECONDS (default 900). The API remains available if a refresh fails; health reports degraded when the last successful collection is stale. SQLite persists events and the latest per-route coverage manifest. Production deployments must mount a persistent volume at /data.

## API contract
- GET /v1/health: service version, freshness, event count.
- GET /v1/competitions: registry catalogue with explicit collection_enabled flag.
- GET /v1/coverage: latest observed route status (ok, empty, unavailable).
- GET /v1/events: filtered and paginated normalized events.
- GET /v1/events/{event_id}: event lookup.
- POST /v1/refresh: API-key-protected manual refresh.
- /docs and /openapi.json: generated API schema.

## Security
Read endpoints expose public scoreboard data only. Manual refresh requires X-API-Key; configure NODE47_API_KEY as a Railway secret. Never store secrets in GitHub or Pages artifacts. Use HTTPS at the host edge.

## Coverage and quality
Registry membership, endpoint verification, active collection, and latest collection outcome are distinct states. A route marked empty is not an error. A failed route is isolated and marked unavailable; other routes continue. The API returns only source-observed values and preserves quality_flags.

## Known limitations
ESPN scoreboard endpoints are unofficial and undocumented. V0.0.7 does not provide odds, injuries, full rosters, advanced statistics, or a guaranteed real-time SLA. The active collector remains limited to routes enabled in config/competitions.json (12 in the baseline archive). Tennis match-level coverage is not implied by ATP/WTA tournament-level registry verification. Publishing this REST API alone does not establish the plugin's native MCP connection.
