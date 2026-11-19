import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "activate_verified_competitions.py"

class ActivationTests(unittest.TestCase):
    def test_activates_only_verified_routes_and_marks_verified_routes_as_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path, config_path = root / "registry.json", root / "competitions.json"
            registry = {"entries": [
                {"sport":"soccer","competition_id":"eng.1","name":"Premier League","status":"verified","collected":False},
                {"sport":"basketball","competition_id":"nba","name":"NBA","status":"verified","collected":False},
                {"sport":"tennis","competition_id":"candidate","name":"Candidate","status":"candidate","collected":False}
            ]}
            config = {"base_url":"https://example.invalid","max_workers":4,"competitions":[]}
            registry_path.write_text(json.dumps(registry),encoding="utf-8")
            config_path.write_text(json.dumps(config),encoding="utf-8")
            result = subprocess.run([sys.executable,str(SCRIPT),"--registry",str(registry_path),
                "--config",str(config_path),"--expected-total","2"],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            activated=json.loads(config_path.read_text(encoding="utf-8"))
            updated=json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(len(activated["competitions"]),2)
            self.assertTrue(all(x["enabled"] for x in activated["competitions"]))
            self.assertEqual(activated["max_workers"],4)
            self.assertTrue(updated["entries"][0]["collection_enabled"])
            self.assertFalse(updated["entries"][2]["collection_enabled"])
            self.assertTrue(updated["entries"][0]["collected"])

    def test_guard_rejects_incomplete_verified_census(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); reg=root/"r.json"; cfg=root/"c.json"
            reg.write_text(json.dumps({"entries":[{"sport":"soccer","competition_id":"eng.1","status":"verified"}]}))
            cfg.write_text(json.dumps({"competitions":[]}))
            result=subprocess.run([sys.executable,str(SCRIPT),"--registry",str(reg),"--config",str(cfg),
                "--expected-total","237"],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)

    def test_new_routes_require_verification_and_existing_routes_survive_outage(self):
        registry = {"entries": [
            {"sport": "soccer", "competition_id": "old.league", "name": "Old", "status": "unavailable"},
            {"sport": "soccer", "competition_id": "new.league", "name": "New", "status": "verified"},
            {"sport": "basketball", "competition_id": "candidate.league", "name": "Candidate", "status": "candidate"},
        ]}
        config = {"max_workers": 4, "competitions": [
            {"sport": "soccer", "league": "old.league", "enabled": True},
        ]}
        from tools.activate_verified_competitions import build_activation
        active, enriched = build_activation(registry, config)
        keys = {(item["sport"], item["league"]) for item in active["competitions"]}
        self.assertEqual(keys, {("soccer", "old.league"), ("soccer", "new.league")})
        statuses = {(item["sport"], item["competition_id"]): item["status"] for item in enriched["entries"]}
        self.assertEqual(statuses[("soccer", "old.league")], "unavailable")
        self.assertFalse(enriched["entries"][2]["collection_enabled"])


if __name__ == "__main__":
    unittest.main()
