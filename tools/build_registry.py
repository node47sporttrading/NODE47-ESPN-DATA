#!/usr/bin/env python3
"""V0.0.4 registry builder - candidates + probe evidence -> config/registry.json.

The multisport registry is the census of every ESPN competition in the NODE.47
scope (football, basketball, tennis). Statuses come only from probe evidence:

  verified    - endpoint identified, tested, data schema validated (constraint:
                a competition is only "integrated" once proven).
  unavailable - listed by ESPN's enumeration but the scoreboard endpoint does
                not answer (recorded, never fabricated).
  candidate   - present in the census but not yet probed.

category / gender / zone are a DERIVED editorial layer computed from ESPN's own
names and slug tokens; when no explicit signal exists the value is
"unspecified" - nothing is guessed. This classification is refineable in
V0.0.7 and never feeds the decision engine (constraint 7).

Usage:
    python3 tools/build_registry.py [--candidates ...] [--evidence ...]
        [--competitions config/competitions.json] [--out config/registry.json]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ZONE_BY_PREFIX = {
    # confederations / international
    "uefa": "Europe (UEFA)",
    "fifa": "International (FIFA)",
    "caf": "Africa (CAF)",
    "afc": "Asia (AFC)",
    "aff": "Southeast Asia (AFF)",
    "concacaf": "North & Central America Caribbean (CONCACAF)",
    "conmebol": "South America (CONMEBOL)",
    "ofc": "Oceania (OFC)",
    # countries present in ESPN's soccer enumeration
    "arg": "Argentina", "aus": "Australia", "aut": "Austria", "bel": "Belgium",
    "bol": "Bolivia", "bra": "Brazil", "can": "Canada", "chi": "Chile",
    "chn": "China", "col": "Colombia", "crc": "Costa Rica", "den": "Denmark",
    "ecu": "Ecuador", "eng": "England", "esp": "Spain", "fra": "France",
    "ger": "Germany", "gre": "Greece", "gua": "Guatemala", "hon": "Honduras", "ind": "India",
    "ita": "Italy", "jpn": "Japan", "ksa": "Saudi Arabia", "mex": "Mexico",
    "ned": "Netherlands", "nor": "Norway", "par": "Paraguay", "per": "Peru",
    "por": "Portugal", "rsa": "South Africa", "rus": "Russia", "sco": "Scotland",
    "slv": "El Salvador", "swe": "Sweden", "tur": "Turkey", "uru": "Uruguay",
    "usa": "United States", "ven": "Venezuela",
    # club-global friendly buckets used by ESPN
    "campeones": "International (clubs)",
    "club": "International (clubs)",
    "friendly": "International (clubs)",
    "global": "International",
}

# Editorial mappings for well-known leagues whose slugs carry no zone prefix.
ZONE_BY_KNOWN_LEAGUE = {
    "nonfifa": "International (non-FIFA)",
    "nba": "United States & Canada", "wnba": "United States",
    "nba-development": "United States", "nbl": "Australia",
    "mens-college-basketball": "United States (NCAA)",
    "womens-college-basketball": "United States (NCAA)",
    "fiba": "International (FIBA)",
    "mens-olympics-basketball": "International (IOC)",
    "womens-olympics-basketball": "International (IOC)",
    "atp": "International", "wta": "International",
}
for slug in ["nba-summer-california", "nba-summer-golden-state", "nba-summer-las-vegas",
             "nba-summer-orlando", "nba-summer-sacramento", "nba-summer-utah"]:
    ZONE_BY_KNOWN_LEAGUE[slug] = "United States"

FEMALE_SEGMENTS = {"w", "wwc", "wworld", "wworldq", "wwcq", "wchampions", "weuro",
                   "wnba", "wta", "wsl", "femenina", "femenino", "feminino"}
FEMALE_NAME_TOKENS = ["women", "women's", "womens", "female", "femenina", "femenino",
                      "feminino", "reina", "shebelieves", "arnold clark"]
MALE_SEGMENTS = {"mens"}
MALE_NAME_TOKENS = ["men's", "mens", " men "]
_MALE_KNOWN = ["nba", "nba-development", "nbl", "atp",
               "nba-summer-california", "nba-summer-golden-state", "nba-summer-las-vegas",
               "nba-summer-orlando", "nba-summer-sacramento", "nba-summer-utah"]
SPECIAL_GENDER = {slug: "male" for slug in _MALE_KNOWN}
SPECIAL_GENDER.update({"wta": "female", "wnba": "female"})

# Editorial category/zone for well-known leagues whose ESPN name carries no token.
KNOWN_CATEGORY = {
    "nba": "league", "wnba": "league", "nbl": "league", "nba-development": "league",
    "mens-college-basketball": "league", "womens-college-basketball": "league",
    "fiba": "tournament",
    "mens-olympics-basketball": "tournament", "womens-olympics-basketball": "tournament",
    "nba-summer-california": "tournament", "nba-summer-golden-state": "tournament",
    "nba-summer-las-vegas": "tournament", "nba-summer-orlando": "tournament",
    "nba-summer-sacramento": "tournament", "nba-summer-utah": "tournament",
    "conmebol.libertadores": "cup", "conmebol.sudamericana": "cup",
    "usa.1": "league", "usa.nwsl": "league", "usa.nwsl.cup": "cup",
    "usa.open": "cup", "usa.usl.1": "league", "usa.usl.l1": "league",
    "usa.usl.l1.cup": "cup", "usa.w.usl.1": "league", "can.w.nsl": "league",
    "usa.ncaa.m.1": "league", "usa.ncaa.w.1": "league",
    "uefa.champions": "cup", "uefa.champions_qual": "qualifiers",
    "uefa.europa": "cup", "uefa.europa.conf": "cup",
    "afc.champions": "cup", "afc.cup": "cup", "afc.asian.cup": "cup",
    "caf.champions": "cup", "caf.confed": "cup", "concacaf.champions": "cup",
    "concacaf.champions_cup": "cup", "concacaf.w.champions_cup": "cup",
    "uefa.wchampions": "cup", "uefa.wchampions_qual": "qualifiers",
    "nonfifa": "friendly",
    "esp.joan_gamper": "friendly", "global.club_challenge": "super_cup",
}

QUALIFIER_SEGMENTS = {"qual", "worldq", "wworldq", "euroq", "cupq", "olympicsq", "wcq", "wwcq", "ply"}
QUALIFIER_NAME_TOKENS = ["qualifying", "qualification", "qualifiers"]
PLAYOFF_SEGMENTS = {"promotion", "relegation", "playoff"}
FRIENDLY_SEGMENTS = {"friendly"}
FRIENDLY_NAME_TOKENS = ["friendly"]
SUPERCUP_SEGMENTS = {"super_cup", "supercopa", "supercoupe", "supercup", "campeon", "recopa", "trofeo", "charity", "supercopa_internacional"}
SUPERCUP_NAME_TOKENS = ["super cup", "supercup", "supercopa", "supercoupe", "campeon de campeones",
                        "campeones", "recopa", "trofeo de campeones", "community shield", "charity shield"]
CUP_SEGMENTS = {"cup", "cups", "pokal", "coppa", "copa", "taca", "trophy", "trofeo", "fa", "open", "kings_cup", "coupe"}
CUP_NAME_TOKENS = ["cup", "pokal", "coppa", "copa ", "taça", "taca", "trophy", "beker", "coupe"]
TOURNAMENT_SEGMENTS = {"olympics", "nations", "u17", "u20", "u21", "u23", "world_challenge"}
TOURNAMENT_NAME_TOKENS = ["tournament", "olympics", "nations league"]
LEAGUE_SEGMENTS = {"league", "nwsl", "usl", "nsl", "liga", "serie", "division", "premier", "premiership", "camp"}
LEAGUE_NAME_TOKENS = ["league", "liga", "serie", "division", "premiership", "primera", "bundesliga",
                      "premier league", "superliga", "eredivisie", "mls"]
CONFEDERATION_PREFIXES = {"uefa", "fifa", "caf", "afc", "concacaf", "conmebol", "aff", "ofc"}


def slug_segments(slug: str) -> list[str]:
    return [s for s in re.split(r"[._\-]", slug.lower()) if s]


def derive_zone(sport: str, competition_id: str, name: str | None) -> str:
    prefix = competition_id.split(".")[0].lower()
    if prefix in ZONE_BY_PREFIX:
        return ZONE_BY_PREFIX[prefix]
    if competition_id in ZONE_BY_KNOWN_LEAGUE:
        return ZONE_BY_KNOWN_LEAGUE[competition_id]
    return "unspecified"


def derive_gender(sport: str, competition_id: str, name: str | None) -> str:
    if competition_id in SPECIAL_GENDER:
        return SPECIAL_GENDER[competition_id]
    segments = set(slug_segments(competition_id))
    if segments & FEMALE_SEGMENTS:
        return "female"
    if name:
        lowered = name.lower()
        if any(token in lowered for token in FEMALE_NAME_TOKENS):
            return "female"
    if segments & MALE_SEGMENTS:
        return "male"
    if name:
        lowered = f" {name.lower()} "
        if any(token in lowered for token in MALE_NAME_TOKENS):
            return "male"
    return "unspecified"


def _hits(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def derive_category(sport: str, competition_id: str, name: str | None) -> str:
    if sport == "tennis":
        return "circuit"
    if competition_id in KNOWN_CATEGORY:
        return KNOWN_CATEGORY[competition_id]
    slug = competition_id.lower()
    segments = set(slug_segments(competition_id))
    lowered_name = (name or "").lower()

    if _hits(lowered_name, QUALIFIER_NAME_TOKENS) or segments & QUALIFIER_SEGMENTS or slug.endswith("_qual"):
        return "qualifiers"
    if segments & PLAYOFF_SEGMENTS:
        return "play_offs"
    if _hits(lowered_name, FRIENDLY_NAME_TOKENS) or segments & FRIENDLY_SEGMENTS:
        return "friendly"
    if _hits(lowered_name, SUPERCUP_NAME_TOKENS) or segments & SUPERCUP_SEGMENTS:
        return "super_cup"
    if _hits(lowered_name, CUP_NAME_TOKENS) or segments & CUP_SEGMENTS:
        return "cup"
    if (_hits(lowered_name, TOURNAMENT_NAME_TOKENS)
            or segments & TOURNAMENT_SEGMENTS
            or ("championship" in lowered_name and (
                (slug.split(".")[0] in CONFEDERATION_PREFIXES) or "nations" in lowered_name))):
        return "tournament"
    if _hits(lowered_name, LEAGUE_NAME_TOKENS) or segments & LEAGUE_SEGMENTS or any(s.isdigit() for s in segments):
        return "league"
    return "unspecified"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the multisport competition registry.")
    parser.add_argument("--candidates", default="data/registry/candidates.json")
    parser.add_argument("--evidence", default="data/registry/evidence.json")
    parser.add_argument("--competitions", default="config/competitions.json")
    parser.add_argument("--out", default="config/registry.json")
    args = parser.parse_args()

    candidates_doc = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    evidence_doc = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    competitions_doc = json.loads(Path(args.competitions).read_text(encoding="utf-8"))

    evidence_by_key = {
        (r["sport"], r["competition_id"]): r for r in evidence_doc.get("results", [])
    }
    collected_keys = {
        (c["sport"], c["league"])
        for c in competitions_doc.get("competitions", [])
        if c.get("enabled", False)
    }

    entries = []
    missing_evidence = []
    for sport, block in candidates_doc["sports"].items():
        for competition_id in block["competition_ids"]:
            key = (sport, competition_id)
            evidence = evidence_by_key.get(key)
            if evidence is None:
                missing_evidence.append(key)
                status = "candidate"
                last_verified = None
                espn_name = None
                windows = evidence_doc.get("windows", [])
                http_ok = 0
                events_max = 0
                sample_date = None
                last_error = None
            else:
                status = evidence["verdict"]
                last_verified = evidence["last_verified"]
                espn_name = evidence["espn_name"]
                windows = [w["date"] for w in evidence["windows"]]
                http_ok = evidence["http_ok_windows"]
                events_max = evidence["events_seen_max"]
                sample_date = evidence["sample_event_date"]
                last_error = evidence["last_error"]

            entries.append({
                "sport": sport,
                "competition_id": competition_id,
                "name": espn_name,
                "category": derive_category(sport, competition_id, espn_name),
                "gender": derive_gender(sport, competition_id, espn_name),
                "zone": derive_zone(sport, competition_id, espn_name),
                "status": status,
                "collected": key in collected_keys,
                "collection_enabled": key in collected_keys,
                "last_verified": last_verified,
                "classification": {
                    "method": "derived-from-espn-name-and-slug",
                    "registry_builder": "tools/build_registry.py v0.0.5",
                },
                "evidence": {
                    "windows": windows,
                    "http_ok_windows": http_ok,
                    "events_seen_max": events_max,
                    "sample_event_date": sample_date,
                    "last_error": last_error,
                    "source": "site.api.espn.com scoreboard probes via tools/probe_registry.py",
                },
            })

    if missing_evidence:
        print(f"WARNING: {len(missing_evidence)} candidates were never probed and stay 'candidate': "
              f"{missing_evidence[:10]}{'...' if len(missing_evidence) > 10 else ''}")

    # Invariant: every enabled collection route must exist and be verified.
    by_key = {(e["sport"], e["competition_id"]): e for e in entries}
    broken = []
    for key in sorted(collected_keys):
        entry = by_key.get(key)
        if entry is None:
            broken.append(f"{key}: absent from registry")
        elif entry["status"] != "verified":
            broken.append(f"{key}: status={entry['status']}")
    if broken:
        sys_exit = "FAIL: enabled competitions.json routes not verified in registry:\n" + "\n".join(broken)
        raise SystemExit(sys_exit)

    counts = {}
    for entry in entries:
        bucket = counts.setdefault(entry["sport"], {"verified": 0, "candidate": 0, "unavailable": 0, "total": 0})
        bucket[entry["status"]] += 1
        bucket["total"] += 1

    registry = {
        "schema_version": "1.0",
        "version": "0.0.5",
        "dataset": "node47_multisport_competition_registry",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": ["football (soccer)", "basketball", "tennis"],
        "status_values": ["verified", "candidate", "unavailable"],
        "status_semantics": {
            "verified": "endpoint identified, tested, data schema validated by live probes",
            "candidate": "listed by ESPN's enumeration, not yet probed",
            "unavailable": "probed and not exploitable through the scoreboard endpoint",
        },
        "classification_note": (
            "category/gender/zone are a derived editorial layer computed from ESPN names and "
            "slug tokens (see tools/build_registry.py). 'unspecified' means no explicit signal; "
            "nothing is guessed. This layer never feeds the decision engine."
        ),
        "counts": counts,
        "collection_activation": {
            "mode": "enabled_routes_from_competitions_config",
            "enabled_count": len(collected_keys),
            "semantics": "collected and collection_enabled indicate inclusion in the configured collector; observed request outcomes are recorded separately in the coverage manifest.",
        },
        "total": len(entries),
        "entries": entries,
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Registry written to {out_path}: {len(entries)} entries")
    for sport, bucket in counts.items():
        print(f"  {sport}: {bucket}")


if __name__ == "__main__":
    main()
