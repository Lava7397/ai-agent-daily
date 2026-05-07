from __future__ import annotations

import socket

from api import journal_url_preview


def _fake_addrinfo(*addresses: str):
    return [
        (
            socket.AF_INET6 if ":" in addr else socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            (addr, 443 if ":" in addr else 80),
        )
        for addr in addresses
    ]


def test_allowed_url_blocks_literal_private_ip():
    ok, reason = journal_url_preview._allowed_url("http://10.0.0.1/admin")

    assert ok is False
    assert reason == "ip blocked"


def test_allowed_url_blocks_dns_name_resolving_to_private_ip(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):  # noqa: A002, ANN001
        assert host == "preview.example"
        assert port == 80
        assert type == socket.SOCK_STREAM
        return _fake_addrinfo("10.0.0.5")

    monkeypatch.setattr(journal_url_preview.socket, "getaddrinfo", fake_getaddrinfo)

    ok, reason = journal_url_preview._allowed_url("http://preview.example/metadata")

    assert ok is False
    assert reason == "ip blocked"


def test_allowed_url_blocks_if_any_dns_answer_is_private(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):  # noqa: A002, ANN001
        return _fake_addrinfo("93.184.216.34", "169.254.169.254")

    monkeypatch.setattr(journal_url_preview.socket, "getaddrinfo", fake_getaddrinfo)

    ok, reason = journal_url_preview._allowed_url("https://mixed.example/")

    assert ok is False
    assert reason == "ip blocked"


def test_allowed_url_allows_dns_name_resolving_to_public_ip(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):  # noqa: A002, ANN001
        assert host == "example.com"
        assert port == 443
        return _fake_addrinfo("93.184.216.34")

    monkeypatch.setattr(journal_url_preview.socket, "getaddrinfo", fake_getaddrinfo)

    ok, normalized = journal_url_preview._allowed_url(
        "https://EXAMPLE.com:443/path?q=1#frag"
    )

    assert ok is True
    assert normalized == "https://example.com:443/path?q=1"
