"""PostgreSQL persistence layer for Supabase and other PostgreSQL services."""
from __future__ import annotations

import json
from typing import Any

import psycopg
from psycopg.rows import dict_row


class PostgresDataStore:
    """Drop-in PostgreSQL implementation of the SQLite DataStore interface.

    Connections are short-lived so this works with Supabase's transaction
    pooler. Prepared statements are disabled for PgBouncer transaction mode.
    """

    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("DATABASE_URL is required")
        self.dsn = dsn
        self._init_db()

    def _connect(self):
        return psycopg.connect(
            self.dsn,
            row_factory=dict_row,
            connect_timeout=10,
            sslmode="require",
            prepare_threshold=None,
        )

    def _init_db(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    sport TEXT NOT NULL,
                    league TEXT NOT NULL,
                    start_time_utc TEXT,
                    status_state TEXT,
                    payload_json TEXT NOT NULL,
                    fetched_at_utc TEXT NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_events_sport_time ON events(sport, start_time_utc)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_events_league_time ON events(league, start_time_utc)")
            db.execute("""
                CREATE TABLE IF NOT EXISTS coverage (
                    sport TEXT NOT NULL,
                    league TEXT NOT NULL,
                    competition TEXT NOT NULL,
                    status TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    error TEXT,
                    fetched_at_utc TEXT NOT NULL,
                    PRIMARY KEY (sport, league)
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS service_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def save_dataset(self, dataset: dict[str, Any]) -> dict[str, int]:
        fetched = dataset["fetched_at_utc"]
        upserted = 0
        deleted = 0
        with self._connect() as db:
            for event in dataset.get("events", []):
                eid = event.get("event_id")
                if not eid:
                    continue
                db.execute(
                    """
                    INSERT INTO events
                        (event_id, sport, league, start_time_utc, status_state, payload_json, fetched_at_utc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO UPDATE SET
                        sport=EXCLUDED.sport,
                        league=EXCLUDED.league,
                        start_time_utc=EXCLUDED.start_time_utc,
                        status_state=EXCLUDED.status_state,
                        payload_json=EXCLUDED.payload_json,
                        fetched_at_utc=EXCLUDED.fetched_at_utc
                    """,
                    (
                        str(eid), event.get("sport", "unknown"), event.get("league", "unknown"),
                        event.get("start_time_utc"), (event.get("status") or {}).get("state"),
                        json.dumps(event, ensure_ascii=False), fetched,
                    ),
                )
                upserted += 1

            if dataset.get("requested_date") is None:
                events_by_route: dict[tuple[str, str], set[str]] = {}
                for event in dataset.get("events", []):
                    if event.get("event_id"):
                        key = (event.get("sport", "unknown"), event.get("league", "unknown"))
                        events_by_route.setdefault(key, set()).add(str(event["event_id"]))
                for row in dataset.get("coverage", []):
                    if row.get("status") not in {"ok", "empty"}:
                        continue
                    key = (row["sport"], row["league"])
                    current_ids = events_by_route.get(key, set())
                    if current_ids:
                        placeholders = ", ".join(["%s"] * len(current_ids))
                        cursor = db.execute(
                            f"DELETE FROM events WHERE sport=%s AND league=%s AND event_id NOT IN ({placeholders})",
                            [key[0], key[1], *sorted(current_ids)],
                        )
                    else:
                        cursor = db.execute(
                            "DELETE FROM events WHERE sport=%s AND league=%s", key
                        )
                    deleted += max(cursor.rowcount, 0)

            for row in dataset.get("coverage", []):
                db.execute(
                    """
                    INSERT INTO coverage
                        (sport, league, competition, status, event_count, error, fetched_at_utc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sport, league) DO UPDATE SET
                        competition=EXCLUDED.competition,
                        status=EXCLUDED.status,
                        event_count=EXCLUDED.event_count,
                        error=EXCLUDED.error,
                        fetched_at_utc=EXCLUDED.fetched_at_utc
                    """,
                    (
                        row["sport"], row["league"], row["competition"], row["status"],
                        int(row.get("event_count", 0)), row.get("error"), fetched,
                    ),
                )

            total = db.execute("SELECT COUNT(*) AS count FROM events").fetchone()["count"]
            for key, value in (
                ("last_refresh_utc", fetched),
                ("last_event_count", str(total)),
                ("last_upserted_count", str(upserted)),
                ("last_pruned_count", str(deleted)),
            ):
                db.execute(
                    """
                    INSERT INTO service_meta (key, value) VALUES (%s, %s)
                    ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
                    """,
                    (key, value),
                )
        return {"upserted_count": upserted, "deleted_stale_count": deleted}

    def get_meta(self):
        with self._connect() as db:
            return {r["key"]: r["value"] for r in db.execute("SELECT key, value FROM service_meta").fetchall()}

    def get_coverage(self):
        with self._connect() as db:
            return [
                dict(r) for r in db.execute(
                    "SELECT sport, league, competition, status, event_count, error, fetched_at_utc "
                    "FROM coverage ORDER BY sport, competition"
                ).fetchall()
            ]

    def list_events(self, *, sport=None, league=None, status=None, date_from=None, date_to=None, limit=100, offset=0):
        clauses = []
        values = []
        for value, expr in (
            (sport, "sport = %s"),
            (league, "league = %s"),
            (status, "status_state = %s"),
            (date_from, "start_time_utc >= %s"),
            (date_to, "start_time_utc <= %s"),
        ):
            if value:
                clauses.append(expr)
                values.append(value)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._connect() as db:
            rows = db.execute(
                "SELECT payload_json FROM events" + where +
                " ORDER BY start_time_utc LIMIT %s OFFSET %s",
                [*values, limit, offset],
            ).fetchall()
        return [json.loads(r["payload_json"]) for r in rows]

    def get_event(self, event_id):
        with self._connect() as db:
            row = db.execute(
                "SELECT payload_json FROM events WHERE event_id=%s", (event_id,)
            ).fetchone()
        return json.loads(row["payload_json"]) if row else None

    def count_events(self):
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) AS count FROM events").fetchone()["count"])
