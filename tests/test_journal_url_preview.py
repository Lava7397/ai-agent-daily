from __future__ import annotations

import importlib.util
import socket
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "api" / "journal_url_preview.py"


def _load_preview_module():
    spec = importlib.util.spec_from_file_location("journal_url_preview", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_allowed_url_blocks_literal_private_addresses() -> None:
    preview = _load_preview_module()

    for url in (
        "http://127.0.0.1/",
        "http://10.0.0.12/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
    ):
        ok, reason = preview._allowed_url(url)
        assert not ok
        assert reason in {"host blocked", "ip blocked"}


def test_guarded_connection_blocks_private_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    preview = _load_preview_module()

    def fake_getaddrinfo(*_args, **_kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("10.0.0.5", 80),
            )
        ]

    def fail_socket(*_args, **_kwargs):  # pragma: no cover - should not be reached
        raise AssertionError("socket should not be opened for blocked DNS results")

    monkeypatch.setattr(preview.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(preview.socket, "socket", fail_socket)

    with pytest.raises(OSError, match="resolved ip blocked"):
        preview._guarded_create_connection(("example.test", 80), timeout=1)


def test_guarded_connection_blocks_mixed_public_private_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preview = _load_preview_module()

    def fake_getaddrinfo(*_args, **_kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("93.184.216.34", 80),
            ),
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("127.0.0.1", 80),
            ),
        ]

    monkeypatch.setattr(preview.socket, "getaddrinfo", fake_getaddrinfo)

    with pytest.raises(OSError, match="resolved ip blocked"):
        preview._guarded_create_connection(("example.test", 80), timeout=1)
