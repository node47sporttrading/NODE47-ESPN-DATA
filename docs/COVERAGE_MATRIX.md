# Coverage matrix — V0.0.5

Since V0.0.4/V0.0.5, the full census lives in **`config/registry.json`** (237 competitions: 220 soccer, 15 basketball, 2 tennis, all verified by live scoreboard probes on **2026-11-19** across 4 matchday-aligned windows: Nov 19, 22, 25, 28). The registry is the source of truth for verification status; this matrix keeps the collection-route detail and the sport-specific notes.

Probe evidence: `data/registry/evidence.json` (948 requests, 237/237 verified, 0 unavailable; 82 competitions had real events captured in the windows, 155 are verified but out-of-calendar — seasonal tournaments, summer leagues, one-off cups).

## Collection routes (12, all verified)

Verification state at last update: **2026-11-19**, live probe sessions (V0.0.3 session with windows day/D-5/D+3 + season probes, then V0.0.5 registry probes). A route stays **verified** only while repeatable live probes keep succeeding; the states below must not be treated as permanent coverage guarantees.

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
The ESPN tennis scoreboard does not follow the team-sport shape. `events[]` items are **tournaments** (e.g. `Nitto ATP Finals`, id `339-2026`), each exposing `groupings[].competitions[].competitors[].athlete` instead of `competitions[].competitors[].team`. The V0.0.5 normalizer therefore records one event per tournament, with `participants` empty and a `participants_unavailable` quality flag. No data is invented. Match-level tennis mapping remains an open sport-specific work item (from V0.0.6 on), not something to fake into the current schema.

## Interpretation of collection status
- `ok`: HTTP request succeeded and one or more events were normalized.
- `empty`: HTTP request succeeded and ESPN returned an empty event list. This can be a legitimate off-day/off-season result (measured for `uefa.champions` and `wnba` on non-match days).
- `unavailable`: request, HTTP, or payload parsing failed. See the error field in the manifest.

## Not included yet
Injuries, player availability, rosters, advanced statistics, bookmaker odds, lineups, historical backfill and real-time push updates. Registry-driven collection (beyond the 12 routes) starts with V0.0.6.
