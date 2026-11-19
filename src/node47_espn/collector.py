"""Competition-level collection with bounded concurrency and isolated failures."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from .normalizer import normalize_scoreboard
from .validator import validate_event

def _collect_one(competition: dict, client, date: str | None) -> tuple[dict, list]:
    sport=competition["sport"]; league=competition["league"]; name=competition.get("name",league)
    record={"sport":sport,"league":league,"competition":name,"status":"unknown","event_count":0,"error":None}
    try:
        payload=client.scoreboard(sport,league,date=date)
        events=normalize_scoreboard(payload,sport,league,name)
        for event in events: validate_event(event)
        record["event_count"]=len(events); record["status"]="empty" if not events else "ok"
        return record,events
    except Exception as exc:
        record["status"]="unavailable"; record["error"]=str(exc)[:300]
        return record,[]

def collect(config: dict, client, date: str | None = None) -> dict:
    fetched_at=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    enabled=[c for c in config.get("competitions",[]) if c.get("enabled",False)]
    workers=max(1,min(int(config.get("max_workers",1)),12))
    records: list[tuple[dict,list] | None]=[None]*len(enabled)
    if workers==1:
        for index,competition in enumerate(enabled):
            records[index]=_collect_one(competition,client,date)
    else:
        with ThreadPoolExecutor(max_workers=workers,thread_name_prefix="node47-espn") as pool:
            futures={pool.submit(_collect_one,competition,client,date):index for index,competition in enumerate(enabled)}
            for future in as_completed(futures):
                records[futures[future]]=future.result()
    coverage=[]; all_events=[]
    for result in records:
        if result is None: continue
        record,events=result; coverage.append(record); all_events.extend(events)
    return {"schema_version":"1.0","dataset":"node47_espn_scoreboard","provider":"ESPN",
        "fetched_at_utc":fetched_at,"requested_date":date,"configured_route_count":len(enabled),
        "worker_count":workers,"event_count":len(all_events),"events":all_events,"coverage":coverage}
