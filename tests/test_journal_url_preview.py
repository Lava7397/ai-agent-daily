"""Regression tests for the public journal URL preview API."""

from __future__ import annotations

import socket

from api import journal_url_preview as preview


def test_allowed_url_rejects_hostname_resolving_to_private_ip(monkeypatch) -> None:
    def fake_getaddrinfo(host, port, *args, **kwargs):  # noqa: ANN001
        assert host == "example.com"
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("127.0.0.1", 443),
            )
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    ok, reason = preview._allowed_url("https://example.com/article")

    assert ok is False
    assert reason == "ip blocked"
