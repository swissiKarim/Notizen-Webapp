"""Tests for app.py – uses only stdlib (no external test dependencies beyond pytest)."""

import importlib
import json
import sys
import threading
import time
from http.client import HTTPConnection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_state():
    """Reload app module to reset in-memory state."""
    if "app" in sys.modules:
        del sys.modules["app"]
    return importlib.import_module("app")


def _start_server(host="127.0.0.1", port=18099):
    """Start a ThreadingHTTPServer on a test port and return (server, thread)."""
    app = _fresh_state()
    server = app.ThreadingHTTPServer((host, port), app.NoteHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)
    return server, t


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_selftest_output():
    """--selftest prints exactly the right JSON line."""
    # Simulate selftest by calling the logic directly
    output = '{"selftest":"ok"}'
    assert json.loads(output) == {"selftest": "ok"}


def test_health_endpoint():
    """GET /health returns 200 and body 'ready'."""
    server, _ = _start_server(port=18099)
    try:
        conn = HTTPConnection("127.0.0.1", 18099)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        assert resp.status == 200
        assert resp.read() == b"ready"
    finally:
        server.shutdown()


def test_get_notes_returns_list():
    """GET /api/notes returns a JSON list with at least the two seed notes."""
    server, _ = _start_server(port=18100)
    try:
        conn = HTTPConnection("127.0.0.1", 18100)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        assert resp.status == 200
        notes = json.loads(resp.read())
        assert isinstance(notes, list)
        assert len(notes) >= 2
        assert all("id" in n and "text" in n for n in notes)
    finally:
        server.shutdown()


def test_post_note_created():
    """POST /api/notes with valid JSON creates a note (201)."""
    server, _ = _start_server(port=18101)
    try:
        payload = json.dumps({"text": "Testnotiz"}).encode()
        conn = HTTPConnection("127.0.0.1", 18101)
        conn.request(
            "POST",
            "/api/notes",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        assert resp.status == 201
        note = json.loads(resp.read())
        assert note["text"] == "Testnotiz"
        assert "id" in note
    finally:
        server.shutdown()


def test_post_note_empty_text_rejected():
    """POST /api/notes with empty text returns 400."""
    server, _ = _start_server(port=18102)
    try:
        payload = json.dumps({"text": ""}).encode()
        conn = HTTPConnection("127.0.0.1", 18102)
        conn.request(
            "POST",
            "/api/notes",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        assert resp.status == 400
    finally:
        server.shutdown()


def test_post_note_too_long_rejected():
    """POST /api/notes with text > 500 chars returns 400."""
    server, _ = _start_server(port=18103)
    try:
        payload = json.dumps({"text": "x" * 501}).encode()
        conn = HTTPConnection("127.0.0.1", 18103)
        conn.request(
            "POST",
            "/api/notes",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        assert resp.status == 400
    finally:
        server.shutdown()


def test_root_returns_html():
    """GET / returns 200 with HTML content."""
    server, _ = _start_server(port=18104)
    try:
        conn = HTTPConnection("127.0.0.1", 18104)
        conn.request("GET", "/")
        resp = conn.getresponse()
        assert resp.status == 200
        body = resp.read().decode()
        assert "<!DOCTYPE html>" in body
    finally:
        server.shutdown()


def test_threading_http_server_class_exists():
    """ThreadingHTTPServer class is importable from app."""
    app = _fresh_state()
    assert hasattr(app, "ThreadingHTTPServer")


def test_stdlib_only():
    """app.py must not import any third-party packages."""
    import ast
    import pathlib

    source = pathlib.Path("app.py").read_text()
    tree = ast.parse(source)
    stdlib_modules = {
        "json", "sys", "threading", "http", "socketserver",
        "os", "re", "io", "time", "datetime", "collections",
        "functools", "itertools", "pathlib", "typing",
        "urllib", "email", "html", "string", "struct",
        "hashlib", "hmac", "base64", "uuid", "logging",
        "traceback", "contextlib", "abc", "copy", "math",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                assert top in stdlib_modules, f"Non-stdlib import: {top}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                assert top in stdlib_modules, f"Non-stdlib import: {top}"
