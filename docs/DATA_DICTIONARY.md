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
- `participants.competitors`: full participant list; supports tennis/player-style events.
- `venue`: venue label or null.
- `source`: provider and source event URL.
- `quality_flags`: missing/invalid-field indicators.

Missing data is represented as null or an empty list where appropriate. It is never replaced by zero, an inferred participant, or a fabricated timestamp.
