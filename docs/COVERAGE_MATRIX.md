# Coverage matrix — V0.0.3

Verification state at last update: **2026-11-19**, one live probe session (3 date windows per route: current day, D-5, D+3, plus season-date probes for WNBA and UEFA Champions League). A route becomes **verified** only after repeatable successful live probes across several sessions; the states below are intermediate and must not be treated as permanent coverage guarantees.

| Sport | League | Configured | Verification state (2026-11-19 live probe) | Notes |
|---|---|---:|---|---|
| Football (soccer) | eng.1 | Yes | HTTP 200, events found (D+3) | Uses ESPN `soccer` slug |
| Football (soccer) | esp.1 | Yes | HTTP 200, events found (D+3) | |
| Football (soccer) | ger.1 | Yes | HTTP 200, events found (D+3) | |
| Football (soccer) | ita.1 | Yes | HTTP 200, events found (D+3) | |
| Football (soccer) | fra.1 | Yes | HTTP 200, events found (D+3) | |
| Football (soccer) | uefa.champions | Yes | HTTP 200, events found (9 per league-phase matchday: Oct 20-21, Nov 24-25, Dec 9, Jan 20) | `empty` on non-matchdays is normal; the ESPN default scoreboard (no `dates` param) returns the next league-phase matchday |
| Football (soccer) | usa.1 | Yes | HTTP 200, events found (today, D+3) | |
| Basketball | nba | Yes | HTTP 200, events found (today, D-5, D+3) | Scoreboard only |
| Basketball | wnba | Yes | HTTP 200, events found on season dates (Jul 15-16, Aug 20 2026); `empty` off-season is normal | Scoreboard only |
| Basketball | mens-college-basketball | Yes | HTTP 200, events found (today, D-5, D+3) | Payload also carries `day` and `eventsDate` top-level fields |
| Tennis | atp | Yes | HTTP 200, but payload shape is tournament-level | See tennis note below |
| Tennis | wta | Yes | HTTP 200, but payload shape is tournament-level | See tennis note below |

## Tennis note (important, measured on 2026-11-19)
The ESPN tennis scoreboard does not follow the team-sport shape. `events[]` items are **tournaments** (e.g. `Nitto ATP Finals`, id `339-2026`), each exposing `groupings[].competitions[].competitors[].athlete` instead of `competitions[].competitors[].team`. The V0.0.3 normalizer therefore records one event per tournament, with `participants` empty and a `participants_unavailable` quality flag. No data is invented. Match-level tennis mapping is a V0.0.4 concern (sport-specific normalizer), not something to fake into the current schema.

## Interpretation of collection status
- `ok`: HTTP request succeeded and one or more events were normalized.
- `empty`: HTTP request succeeded and ESPN returned an empty event list. This can be a legitimate off-day/off-season result (measured for `uefa.champions` and `wnba` on non-match days).
- `unavailable`: request, HTTP, or payload parsing failed. See the error field in the manifest.

## Not included in V0.0.3
Injuries, player availability, rosters, advanced statistics, bookmaker odds, lineups, historical backfill and real-time push updates.
