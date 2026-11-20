"""Safe retrieval and text extraction for public web evidence pages."""
from __future__ import annotations

import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class _TextParser(HTMLParser):
    """Extract readable page text while ignoring executable and navigational markup."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "aside"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.title_parts = []
        self.meta = {}
        self.in_title = False
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = (attrs.get("property") or attrs.get("name") or "").lower()
            value = attrs.get("content")
            allowed = {"og:title", "og:description", "description", "article:published_time", "date", "dc.date"}
            if key in allowed and value:
                self.meta[key] = value[:500]

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        value = " ".join(data.split())
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        if not self.skip_depth:
            self.parts.append(value)

    def text(self):
        return re.sub(r"\\s+", " ", " ".join(self.parts)).strip()


def validate_public_url(url: str) -> str:
    """Reject non-web URLs, credentials, unusual ports and non-public DNS targets."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("unsupported_url")
    if parsed.port not in (None, 80, 443):
        raise ValueError("unsupported_port")
    host = parsed.hostname.rstrip(".")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    addresses = {item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    if not addresses:
        raise ValueError("dns_no_address")
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise ValueError("non_public_address")
    return url


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl)
        validate_public_url(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


def fetch_public_page(
    url: str,
    *,
    opener=None,
    timeout: int = 12,
    max_bytes: int = 700_000,
    max_chars: int = 9_000,
) -> dict:
    """Fetch and extract a public HTML/plain-text page, returning explicit status fields."""
    try:
        validate_public_url(url)
        active_opener = opener or build_opener(_SafeRedirectHandler())
        request = Request(
            url,
            headers={
                "User-Agent": "NODE47-EvidenceReader/1.0 (+source verification)",
                "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8",
            },
        )
        with active_opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            validate_public_url(final_url)
            content_type = response.headers.get("Content-Type", "").lower()
            if not (
                "text/html" in content_type
                or "application/xhtml+xml" in content_type
                or "text/plain" in content_type
            ):
                return {"fetch_status": "unsupported_content_type", "page_url": final_url, "page_content": ""}
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                return {"fetch_status": "page_too_large", "page_url": final_url, "page_content": ""}
        decoded = body.decode("utf-8", "replace")
        if "text/plain" in content_type:
            text = re.sub(r"\\s+", " ", decoded).strip()
            title = ""
            metadata = {}
        else:
            parser = _TextParser()
            parser.feed(decoded[:max_bytes])
            text = parser.text()
            title = " ".join(parser.title_parts)[:300]
            metadata = parser.meta
        return {
            "fetch_status": "ok" if len(text) >= 300 else "limited_text",
            "page_url": final_url,
            "page_title": title or metadata.get("og:title", ""),
            "page_description": metadata.get("og:description") or metadata.get("description", ""),
            "page_published_date": metadata.get("article:published_time") or metadata.get("date") or metadata.get("dc.date"),
            "page_content": text[:max_chars],
            "page_content_chars": len(text),
        }
    except HTTPError as exc:
        return {"fetch_status": f"http_{exc.code}", "page_content": ""}
    except Exception as exc:
        return {
            "fetch_status": "blocked_or_unavailable",
            "fetch_detail": str(exc)[:180],
            "page_content": "",
        }
