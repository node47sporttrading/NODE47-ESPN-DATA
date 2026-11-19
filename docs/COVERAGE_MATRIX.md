# Coverage matrix — V0.3.0

| Sport | League | Configured | Verification state | Notes |
|---|---|---:|---|---|
| Football (soccer) | EPL, LaLiga, Bundesliga, Serie A, Ligue 1, UCL, MLS | Yes | Pending live probes | Uses ESPN `soccer` slug |
| Basketball | NBA, WNBA, NCAA Men's | Yes | Pending live probes | Scoreboard only |
| Tennis | ATP, WTA | Yes | Exploratory | Route shape and season coverage must be confirmed |

## Interpretation of collection status
- `ok`: HTTP request succeeded and one or more events were normalized.
- `empty`: HTTP request succeeded and ESPN returned an empty event list. This can be a legitimate off-day/off-season result.
- `unavailable`: request, HTTP, or payload parsing failed. See the error field in the manifest.

A route becomes **verified** only after repeatable successful live probes for representative dates, including an event day and a no-event day. A single HTTP 200 is not sufficient to certify full competition coverage.

## Not included in V0.3.0
Injuries, player availability, rosters, advanced statistics, bookmaker odds, lineups, historical backfill and real-time push updates.
