"""One-time, idempotent import from the existing SQLite database to PostgreSQL."""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

from .postgres_store import PostgresDataStore


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=os.getenv("NODE47_DATA_PATH", "data/node47.sqlite3"))
    args = parser.parse_args()
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        parser.error("DATABASE_URL must be set in the environment")
    if not os.path.isfile(args.source):
        parser.error(f"SQLite source file does not exist: {args.source}")

    # Creating the store also creates the destination schema.
    target = PostgresDataStore(dsn)
    source = sqlite3.connect(args.source)
    source.row_factory = sqlite3.Row
    try:
        events = source.execute(
            "SELECT event_id, sport, league, start_time_utc, status_state, payload_json, fetched_at_utc FROM events"
        ).fetchall()
        coverage = source.execute(
            "SELECT sport, league, competition, status, event_count, error, fetched_at_utc FROM coverage"
        ).fetchall()
        meta = source.execute("SELECT key, value FROM service_meta").fetchall()
    finally:
        source.close()

    with target._connect() as db:
        for row in events:
            db.execute(
                """
                INSERT INTO events
                    (event_id, sport, league, start_time_utc, status_state, payload_json, fetched_at_utc)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO UPDATE SET
                    sport=EXCLUDED.sport, league=EXCLUDED.league,
                    start_time_utc=EXCLUDED.start_time_utc,
                    status_state=EXCLUDED.status_state,
                    payload_json=EXCLUDED.payload_json,
                    fetched_at_utc=EXCLUDED.fetched_at_utc
                """,
                tuple(row),
            )
        for row in coverage:
            db.execute(
                """
                INSERT INTO coverage
                    (sport, league, competition, status, event_count, error, fetched_at_utc)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sport, league) DO UPDATE SET
                    competition=EXCLUDED.competition, status=EXCLUDED.status,
                    event_count=EXCLUDED.event_count, error=EXCLUDED.error,
                    fetched_at_utc=EXCLUDED.fetched_at_utc
                """,
                tuple(row),
            )
        for row in meta:
            db.execute(
                """
                INSERT INTO service_meta (key, value) VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
                """,
                tuple(row),
            )

    with target._connect() as db:
        counts = {
            "events": db.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"],
            "coverage": db.execute("SELECT COUNT(*) AS n FROM coverage").fetchone()["n"],
            "metadata": db.execute("SELECT COUNT(*) AS n FROM service_meta").fetchone()["n"],
        }
    print(f"SQLite import completed: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
