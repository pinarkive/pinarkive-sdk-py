"""Minimal unit tests for pinarkive_client."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest

from pinarkive_client import PinarkiveClient, PinarkiveError


class _Handler(BaseHTTPRequestHandler):
    status = 200
    body = b'{"ok":true}'
    last_auth = ""
    last_path = ""

    def log_message(self, format, *args):  # noqa: A003
        return

    def do_GET(self):  # noqa: N802
        type(self).last_auth = self.headers.get("Authorization") or self.headers.get("X-API-Key") or ""
        type(self).last_path = self.path
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.body)


@pytest.fixture()
def http_api():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base = f"http://{host}:{port}"
    try:
        yield base, _Handler
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_client_init_and_bearer(http_api):
    base, handler = http_api
    handler.status = 200
    handler.body = b'{"id":"u1"}'
    client = PinarkiveClient(token="tok", base_url=base)
    data = client.get_me()
    assert handler.last_auth == "Bearer tok"
    assert handler.last_path == "/users/me"
    assert data["id"] == "u1"


def test_api_error(http_api):
    base, handler = http_api
    handler.status = 401
    handler.body = json.dumps(
        {"error": "Unauthorized", "message": "bad", "code": "unauthorized"}
    ).encode()
    client = PinarkiveClient(token="x", base_url=base)
    with pytest.raises(PinarkiveError) as exc:
        client.get_me()
    assert exc.value.status_code == 401
    assert exc.value.code == "unauthorized"
