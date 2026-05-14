"""Regression tests for the public journal URL preview API."""

from __future__ import annotations

import socket
from urllib.error import URLError

import pytest

from api import journal_url_preview as preview


def test_allowed_url_rejects_multicast_literal_ip() -> None:
    ok, reason = preview._allowed_url("http://224.0.0.1/")

    assert ok is False
    assert reason == "ip blocked"


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


def test_fetch_blocks_private_ip_at_connection_time(monkeypatch) -> None:
    def fake_getaddrinfo(host, port, *args, **kwargs):  # noqa: ANN001
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("127.0.0.1", port),
            )
        ]

    def fail_if_socket_created(*args, **kwargs):  # noqa: ANN001
        raise AssertionError("unguarded private connection attempted")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(socket, "socket", fail_if_socket_created)

    with pytest.raises(URLError) as excinfo:
        preview._fetch("http://example.com/")

    assert "ip blocked" in str(excinfo.value.reason)
