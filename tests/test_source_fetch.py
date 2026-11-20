import unittest
from unittest.mock import MagicMock, patch

from node47_espn.source_fetch import fetch_public_page, validate_public_url


PUBLIC_DNS = [(None, None, None, None, ("93.184.216.34", 0))]


class SourceFetchTests(unittest.TestCase):
    def test_rejects_private_ip_targets(self):
        with patch("node47_espn.source_fetch.socket.getaddrinfo", return_value=[
            (None, None, None, None, ("127.0.0.1", 0))
        ]):
            with self.assertRaisesRegex(ValueError, "non_public_address"):
                validate_public_url("https://example.org/article")

    def test_rejects_non_http_schemes_and_credentials(self):
        with self.assertRaisesRegex(ValueError, "unsupported_url"):
            validate_public_url("file:///etc/passwd")
        with self.assertRaisesRegex(ValueError, "unsupported_url"):
            validate_public_url("https://user:pass@example.org")

    def test_extracts_readable_html_and_metadata(self):
        html = (
            "<html><head><title>Match analysis</title>"
            '<meta name="description" content="Tactical report">'
            '<meta property="article:published_time" content="2026-11-20">'
            "<script>secret javascript text</script></head><body>"
            "<nav>navigation should disappear</nav><main>"
            + ("The team pressed high and attacked the wide channel. " * 12)
            + "</main></body></html>"
        ).encode()
        response = MagicMock()
        response.geturl.return_value = "https://example.org/match"
        response.headers = {"Content-Type": "text/html; charset=utf-8"}
        response.read.return_value = html
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch("node47_espn.source_fetch.validate_public_url", return_value="https://example.org/match"):
            result = fetch_public_page("https://example.org/match", opener=opener)
        self.assertIn(result["fetch_status"], ("ok", "limited_text"))
        self.assertEqual(result["page_title"], "Match analysis")
        self.assertEqual(result["page_description"], "Tactical report")
        self.assertEqual(result["page_published_date"], "2026-11-20")
        self.assertNotIn("javascript", result["page_content"])
        self.assertNotIn("navigation should disappear", result["page_content"])
        self.assertIn("pressed high", result["page_content"])

    def test_marks_unsupported_content_type(self):
        response = MagicMock()
        response.geturl.return_value = "https://example.org/data.pdf"
        response.headers = {"Content-Type": "application/pdf"}
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch("node47_espn.source_fetch.validate_public_url", return_value="https://example.org/data.pdf"):
            result = fetch_public_page("https://example.org/data.pdf", opener=opener)
        self.assertEqual(result["fetch_status"], "unsupported_content_type")


if __name__ == "__main__":
    unittest.main()
