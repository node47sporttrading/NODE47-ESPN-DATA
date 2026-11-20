import unittest
from pathlib import Path

import yaml


class SearXNGWorkflowContractTests(unittest.TestCase):
    def test_workflow_yaml_and_embedded_python_are_valid(self):
        workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / "searxng-search.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        self.assertIn("jobs", workflow)
        steps = workflow["jobs"]["search"]["steps"]
        runner = next(step for step in steps if step.get("name") == "Execute search and return results to Render")
        script = runner["run"]
        try:
            compile(script, "<embedded-searxng-workflow>", "exec")
        except SyntaxError as exc:
            bad_line = script.splitlines()[exc.lineno - 1] if exc.lineno and exc.lineno <= len(script.splitlines()) else "<unknown>"
            self.fail(f"Embedded Python syntax error at line {exc.lineno}: {exc.msg}; source={bad_line!r}")
        self.assertIn("from node47_espn.source_fetch import fetch_public_page", script)
        self.assertIn("fetch_public_page(source_url)", script)

    def test_page_fetch_is_enabled_by_default_and_passed_to_runner(self):
        workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / "searxng-search.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        trigger = workflow.get("on", workflow.get(True))
        inputs = trigger["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["fetch_pages"]["default"], "true")
        steps = workflow["jobs"]["search"]["steps"]
        runner = next(step for step in steps if step.get("name") == "Execute search and return results to Render")
        self.assertEqual(runner["env"]["FETCH_PAGES"], "${{ inputs.fetch_pages }}")


if __name__ == "__main__":
    unittest.main()
