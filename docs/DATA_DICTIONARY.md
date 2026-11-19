# Data dictionary — snapshot schema 1.0

## Root object
- `schema_version`: schema revision.
- `dataset`: dataset identifier.
- `provider`: source provider name.
- `fetched_at_utc`: UTC time the collection completed.
- `requested_date`: optional ESPN date filter.
- `event_count`: number of normalized events.
- `events`: normalized event array.
- `coverage`: per-competition request status and event count.

## Event
- `event_id`: ESPN event identifier, string or null.
- `sport`, `league`, `competition`: configured route metadata.
- `name`, `short_name`: source labels.
- `start_time_utc`: ISO-8601 UTC timestamp or null.
- `status`: ESPN state/name/description/completed fields, nullable.
- `participants.home`, `participants.away`: optional home/away entities.
- `participants.competitors`: full participant list; teams for team sports, athletes for player-style routes.
- `venue`: venue label or null.
- `source`: provider and source event URL.
- `quality_flags`: missing/invalid-field indicators.

Missing data is represented as null or an empty list where appropriate. It is never replaced by zero, an inferred participant, or a fabricated timestamp.

## Sport-specific reality check (2026-11-19 live probe)
- Team sports (soccer, basketball): one event = one match, `participants.home/away` and `competitors` are populated, `score` is a string when present.
- Tennis: one event = one **tournament** (ESPN tennis scoreboard shape: `events[].groupings[].competitions[]`). The current schema stores the tournament as an event with `participants` empty and the `participants_unavailable` flag. Individual tennis matches are not represented in schema 1.0.

## Competition registry (config/registry.json, V0.0.5)
The registry is a census, not a snapshot of matches. Fields per entry:
- `sport`: soccer, basketball or tennis.
- `competition_id`: ESPN code (slug), e.g. `eng.1`.
- `name`: ESPN name captured by the probes (`null` when ESPN returns none).
- `category`: derived layer — league, cup, super_cup, tournament, qualifiers, friendly, play_offs, circuit, unspecified.
- `gender`: derived layer — male, female, unspecified (set only on explicit ESPN signal).
- `zone`: derived layer — country, confederation or International, from slug prefix/name; unspecified when no signal.
- `status`: verified (endpoint tested, schema validated) / candidate (not yet probed) / unavailable (probed, not exploitable).
- `collected`: true when the competition is part of the active collection routes (`config/competitions.json`).
- `last_verified`: ISO date of the last live probe.
- `evidence`: windows probed, HTTP-ok window count, max events seen, sample event date, last error, probe tool.

Classification fields are a derived editorial layer (see `tools/build_registry.py`); `unspecified` means "no explicit signal" — nothing is guessed, and the layer never feeds the decision engine.
