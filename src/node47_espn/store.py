"""Small SQLite persistence layer for the NODE.47 data service."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import Any
class DataStore:
    def __init__(self, path: str | Path):
        self.path=str(path)
        if self.path != ":memory:": Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    def _connect(self):
        db=sqlite3.connect(self.path, timeout=20); db.row_factory=sqlite3.Row; return db
    def _init_db(self):
        with self._connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,sport TEXT NOT NULL,league TEXT NOT NULL,start_time_utc TEXT,status_state TEXT,payload_json TEXT NOT NULL,fetched_at_utc TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_events_sport_time ON events(sport,start_time_utc);
            CREATE INDEX IF NOT EXISTS idx_events_league_time ON events(league,start_time_utc);
            CREATE TABLE IF NOT EXISTS coverage(sport TEXT NOT NULL,league TEXT NOT NULL,competition TEXT NOT NULL,status TEXT NOT NULL,event_count INTEGER NOT NULL,error TEXT,fetched_at_utc TEXT NOT NULL,PRIMARY KEY(sport,league));
            CREATE TABLE IF NOT EXISTS service_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            """)
    def save_dataset(self,dataset:dict[str,Any]):
        fetched=dataset["fetched_at_utc"]
        with self._connect() as db:
            for event in dataset.get("events",[]):
                eid=event.get("event_id")
                if not eid: continue
                db.execute("""INSERT INTO events VALUES(?,?,?,?,?,?,?) ON CONFLICT(event_id) DO UPDATE SET sport=excluded.sport,league=excluded.league,start_time_utc=excluded.start_time_utc,status_state=excluded.status_state,payload_json=excluded.payload_json,fetched_at_utc=excluded.fetched_at_utc""",
                  (str(eid),event.get("sport","unknown"),event.get("league","unknown"),event.get("start_time_utc"),(event.get("status") or {}).get("state"),json.dumps(event,ensure_ascii=False),fetched))
            for row in dataset.get("coverage",[]):
                db.execute("""INSERT INTO coverage VALUES(?,?,?,?,?,?,?) ON CONFLICT(sport,league) DO UPDATE SET competition=excluded.competition,status=excluded.status,event_count=excluded.event_count,error=excluded.error,fetched_at_utc=excluded.fetched_at_utc""",
                  (row["sport"],row["league"],row["competition"],row["status"],int(row.get("event_count",0)),row.get("error"),fetched))
            for key,value in (("last_refresh_utc",fetched),("last_event_count",str(dataset.get("event_count",0)))):
                db.execute("INSERT INTO service_meta VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,value))
    def get_meta(self):
        with self._connect() as db: return {r["key"]:r["value"] for r in db.execute("SELECT key,value FROM service_meta")}
    def get_coverage(self):
        with self._connect() as db: return [dict(r) for r in db.execute("SELECT sport,league,competition,status,event_count,error,fetched_at_utc FROM coverage ORDER BY sport,competition")]
    def list_events(self,*,sport=None,league=None,status=None,date_from=None,date_to=None,limit=100,offset=0):
        clauses=[]; values=[]
        for value,expr in ((sport,"sport = ?"),(league,"league = ?"),(status,"status_state = ?"),(date_from,"start_time_utc >= ?"),(date_to,"start_time_utc <= ?")):
            if value: clauses.append(expr); values.append(value)
        where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
        with self._connect() as db:
            rows=db.execute("SELECT payload_json FROM events"+where+" ORDER BY start_time_utc LIMIT ? OFFSET ?",[*values,limit,offset]).fetchall()
        return [json.loads(r["payload_json"]) for r in rows]
    def get_event(self,event_id):
        with self._connect() as db: row=db.execute("SELECT payload_json FROM events WHERE event_id=?",(event_id,)).fetchone()
        return json.loads(row["payload_json"]) if row else None
    def count_events(self):
        with self._connect() as db: return int(db.execute("SELECT COUNT(*) FROM events").fetchone()[0])
