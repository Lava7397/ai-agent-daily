"""
GET /api/journal_url_preview?url=<encoded>
返回 JSON: { ok, title?, summary?, error? } — 仅从目标页 HTML 提取 meta / <title>。
标准库；仅 http/https；简易防 SSRF。
"""
from __future__ import annotations

import html as html_mod
import ipaddress
import json
import re
import socket
from http.server import BaseHTTPRequestHandler
from typing import Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse, urlunparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_FETCH_BYTES = 900_000
MAX_REDIRECTS = 7
TIMEOUT = 14
USER_AGENT = (
    "Mozilla/5.0 (compatible; AiDailyJournalSubmit/1.0; +https://lava7397.com)"
)

_BAD_HOST = frozenset({"localhost", "127.0.0.1", "::1"})


def _address_blocked(addr: str) -> bool:
    return not ipaddress.ip_address(addr.split("%")[0]).is_global


def _host_resolves_to_blocked_ip(host: str, port: int) -> bool:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return any(_address_blocked(info[4][0]) for info in infos)


def _squash(s: str) -> str:
    return " ".join(s.replace("\xa0", " ").split())


def _allowed_url(raw: str) -> Tuple[bool, str]:
    s = (raw or "").strip()
    if not s or len(s) > 8000:
        return False, "bad url"
    p = urlparse(s)
    if p.scheme not in ("http", "https"):
        return False, "only http/https"
    host = (p.hostname or "").lower()
    if not host or host in _BAD_HOST:
        return False, "host blocked"
    if host.endswith(".local"):
        return False, "host blocked"
    try:
        if _address_blocked(host):
            return False, "ip blocked"
    except ValueError:
        pass
    try:
        port = p.port or (443 if p.scheme == "https" else 80)
    except ValueError:
        return False, "bad url"
    try:
        if _host_resolves_to_blocked_ip(host, port):
            return False, "ip blocked"
    except OSError:
        return False, "host blocked"
    rebuilt = urlunparse(
        (p.scheme, p.netloc.lower(), p.path or "", "", p.query or "", "")
    )
    return True, rebuilt


class _GuardRedirect(HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        if self._count >= MAX_REDIRECTS:
            raise URLError("too many redirects")
        ok, normalized = _allowed_url(newurl)
        if not ok:
            raise URLError(normalized)
        self._count += 1
        return Request(
            normalized,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            },
            method="GET",
        )


def _fetch(url: str) -> bytes:
    opener = build_opener(_GuardRedirect())
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    with opener.open(req, timeout=TIMEOUT) as resp:
        out: list[bytes] = []
        total = 0
        while total < MAX_FETCH_BYTES:
            chunk = resp.read(min(65536, MAX_FETCH_BYTES - total))
            if not chunk:
                break
            out.append(chunk)
            total += len(chunk)
        return b"".join(out)


def _decode(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def _rex_first(pattern: str, text: str) -> Optional[str]:
    m = re.search(pattern, text, flags=re.I | re.DOTALL)
    if not m:
        return None
    li = m.lastindex or 0
    for i in range(1, li + 1):
        g = m.group(i)
        if g:
            return g
    return None


def _extract(html_txt: str) -> Tuple[str, str]:
    head = html_txt[: min(len(html_txt), 700_000)]

    og_title = _rex_first(
        r'<meta\b[^>]*\bproperty\s*=\s*["\']og:title["\'][^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,2000})["\']',
        head,
    ) or _rex_first(
        r'<meta\b[^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,2000})["\'][^>]*\bproperty\s*=\s*["\']og:title["\']',
        head,
    )
    og_desc = _rex_first(
        r'<meta\b[^>]*\bproperty\s*=\s*["\']og:description["\'][^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,6000})["\']',
        head,
    ) or _rex_first(
        r'<meta\b[^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,6000})["\'][^>]*\bproperty\s*=\s*["\']og:description["\']',
        head,
    )

    tw_title = _rex_first(
        r'<meta\b[^>]*\bname\s*=\s*["\']twitter:title["\'][^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,2000})["\']',
        head,
    )
    tw_desc = _rex_first(
        r'<meta\b[^>]*\bname\s*=\s*["\']twitter:description["\'][^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,6000})["\']',
        head,
    )

    meta_desc = _rex_first(
        r'<meta\b[^>]*\bname\s*=\s*["\']description["\'][^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,6000})["\']',
        head,
    ) or _rex_first(
        r'<meta\b[^>]*\bcontent\s*=\s*["\']([^"\'<>]{1,6000})["\'][^>]*\bname\s*=\s*["\']description["\']',
        head,
    )

    ttl_raw = _rex_first(r"<title[^>]*>\s*(.*?)\s*</title>", head)
    ttl = html_mod.unescape(_squash(ttl_raw)) if ttl_raw else ""

    cand_title = og_title or tw_title
    title = _squash(html_mod.unescape(cand_title)) if cand_title else ttl
    title = title[:520]

    summary_src = og_desc or tw_desc or meta_desc
    summary = ""
    if summary_src:
        summary = _squash(html_mod.unescape(summary_src))[:8000]
    elif ttl:
        summary = ttl[:800]

    return title.strip(), summary.strip()


def _json(handler: BaseHTTPRequestHandler, code: int, obj: Dict) -> None:
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "private, max-age=120")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):  # noqa: N801
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        pu = urlparse(self.path)
        if pu.path.rstrip("/") != "/api/journal_url_preview":
            _json(self, 404, {"ok": False, "error": "not found"})
            return

        q = parse_qs(pu.query or "")
        urls = q.get("url") or []
        if not urls:
            _json(self, 400, {"ok": False, "error": "missing url"})
            return

        ok, normalized = _allowed_url(urls[0])
        if not ok:
            _json(self, 400, {"ok": False, "error": normalized})
            return

        try:
            raw_bytes = _fetch(normalized)
        except HTTPError as err:
            _json(self, 502, {"ok": False, "error": f"remote HTTP {err.code}"})
            return
        except URLError as err:
            _json(self, 502, {"ok": False, "error": f"fetch failed: {err.reason}"})
            return
        except TimeoutError:
            _json(self, 504, {"ok": False, "error": "timeout"})
            return
        except OSError as err:
            _json(self, 502, {"ok": False, "error": str(err)})
            return
        except Exception as exc:  # noqa: BLE001
            _json(self, 500, {"ok": False, "error": str(exc)})
            return

        text = _decode(raw_bytes)
        title, summary = _extract(text)
        if not title and not summary:
            _json(
                self,
                422,
                {"ok": False, "error": "could not extract title or description"},
            )
            return

        _json(self, 200, {"ok": True, "title": title, "summary": summary})
