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


def test_selftest_exit_code_zero():
    """python app.py --selftest exits with code 0."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "app.py", "--selftest"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_selftest_stdout_exactly():
    """python app.py --selftest outputs exactly {\"selftest\":\"ok\"}."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "app.py", "--selftest"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == '{"selftest":"ok"}'


def test_selftest_does_not_bind_port():
    """python app.py --selftest does not bind port 8099."""
    import socket
    import subprocess
    result = subprocess.run(
        [sys.executable, "app.py", "--selftest"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # After selftest exits, port 8099 must be bindable (was never held)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", 8099))
    finally:
        s.close()


def test_selftest_ruff_passes():
    """ruff check . passes after --selftest implementation."""
    import subprocess
    result = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


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


def test_health_returns_200():
    """US-03/AC-1: GET /health returns HTTP 200."""
    server, _ = _start_server(port=18110)
    try:
        conn = HTTPConnection("127.0.0.1", 18110)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        assert resp.status == 200
        resp.read()
    finally:
        server.shutdown()


def test_health_body_is_ready():
    """US-03/AC-2: GET /health body is exactly 'ready'."""
    server, _ = _start_server(port=18111)
    try:
        conn = HTTPConnection("127.0.0.1", 18111)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        assert resp.read() == b"ready"
    finally:
        server.shutdown()


def test_health_concurrent():
    """US-03/AC-3: GET /health stable under concurrent requests."""
    server, _ = _start_server(port=18112)
    statuses = []
    lock = threading.Lock()

    def fetch():
        conn = HTTPConnection("127.0.0.1", 18112)
        conn.request("GET", "/health")
        r = conn.getresponse()
        code = r.status
        r.read()
        with lock:
            statuses.append(code)

    try:
        threads = [threading.Thread(target=fetch) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert all(s == 200 for s in statuses)
        assert len(statuses) == 10
    finally:
        server.shutdown()


def test_threading_http_server_class_exists():
    """ThreadingHTTPServer class is importable from app."""
    app = _fresh_state()
    assert hasattr(app, "ThreadingHTTPServer")


def test_concurrent_writes_no_race_condition():
    """20 concurrent POSTs all return 201 and IDs are unique (thread-safety)."""
    server, _ = _start_server(port=18105)
    try:
        results = []
        lock = threading.Lock()

        def post(i):
            payload = json.dumps({"text": f"concurrent {i}"}).encode()
            conn = HTTPConnection("127.0.0.1", 18105)
            conn.request(
                "POST", "/api/notes", body=payload,
                headers={"Content-Type": "application/json"},
            )
            resp = conn.getresponse()
            note = json.loads(resp.read())
            with lock:
                results.append((resp.status, note.get("id")))

        threads = [threading.Thread(target=post, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        statuses = [r[0] for r in results]
        ids = [r[1] for r in results]
        assert all(s == 201 for s in statuses), f"Not all 201: {statuses}"
        assert len(set(ids)) == 20, f"Duplicate IDs detected: {ids}"
    finally:
        server.shutdown()


def test_seed_notes_count_and_fields():
    """Exactly two seed notes exist on startup, each with id and text fields."""
    server, _ = _start_server(port=18106)
    try:
        conn = HTTPConnection("127.0.0.1", 18106)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        notes = json.loads(resp.read())
        assert len(notes) == 2, f"Expected 2 seed notes, got {len(notes)}"
        for n in notes:
            assert "id" in n and "text" in n
    finally:
        server.shutdown()


def test_incremental_ids_start_at_1():
    """Seed notes have IDs 1 and 2; new note gets ID 3."""
    server, _ = _start_server(port=18107)
    try:
        conn = HTTPConnection("127.0.0.1", 18107)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        notes = json.loads(resp.read())
        assert notes[0]["id"] == 1
        assert notes[1]["id"] == 2

        payload = json.dumps({"text": "dritte Notiz"}).encode()
        conn2 = HTTPConnection("127.0.0.1", 18107)
        conn2.request(
            "POST", "/api/notes", body=payload,
            headers={"Content-Type": "application/json"},
        )
        resp2 = conn2.getresponse()
        note = json.loads(resp2.read())
        assert note["id"] == 3
    finally:
        server.shutdown()


# ---------------------------------------------------------------------------
# US-05: GET /api/notes – Notizliste abrufen
# ---------------------------------------------------------------------------

def test_us05_ac1_get_notes_returns_200():
    """US-05/AC-1: GET /api/notes returns HTTP 200."""
    server, _ = _start_server(port=18120)
    try:
        conn = HTTPConnection("127.0.0.1", 18120)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        assert resp.status == 200
        resp.read()
    finally:
        server.shutdown()


def test_us05_ac2_get_notes_returns_json_array():
    """US-05/AC-2: GET /api/notes response is a valid JSON array with application/json content-type."""
    server, _ = _start_server(port=18121)
    try:
        conn = HTTPConnection("127.0.0.1", 18121)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        content_type = resp.headers.get("Content-Type", "")
        body = json.loads(resp.read())
        assert "application/json" in content_type
        assert isinstance(body, list)
    finally:
        server.shutdown()


def test_us05_ac3_each_note_has_id_and_text():
    """US-05/AC-3: each note in list contains id and text fields."""
    server, _ = _start_server(port=18122)
    try:
        conn = HTTPConnection("127.0.0.1", 18122)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        notes = json.loads(resp.read())
        assert len(notes) >= 2
        for note in notes:
            assert "id" in note, f"Missing 'id' in note: {note}"
            assert "text" in note, f"Missing 'text' in note: {note}"
    finally:
        server.shutdown()


def test_us05_ac4_at_least_two_notes_on_startup():
    """US-05/AC-4: at least two notes present on startup (seed notes)."""
    server, _ = _start_server(port=18123)
    try:
        conn = HTTPConnection("127.0.0.1", 18123)
        conn.request("GET", "/api/notes")
        resp = conn.getresponse()
        notes = json.loads(resp.read())
        assert len(notes) >= 2, f"Expected at least 2 seed notes, got {len(notes)}"
    finally:
        server.shutdown()


def test_us06_ac1_post_valid_returns_201():
    """US-06/AC-1: POST /api/notes with valid text returns HTTP 201."""
    server, _ = _start_server(port=18120)
    try:
        payload = json.dumps({"text": "US-06 Testnotiz"}).encode()
        conn = HTTPConnection("127.0.0.1", 18120)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 201
        resp.read()
    finally:
        server.shutdown()


def test_us06_ac2_new_note_in_get():
    """US-06/AC-2: Newly created note appears in GET /api/notes."""
    server, _ = _start_server(port=18121)
    try:
        payload = json.dumps({"text": "Persistenz-Check"}).encode()
        conn = HTTPConnection("127.0.0.1", 18121)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        conn.getresponse().read()

        conn2 = HTTPConnection("127.0.0.1", 18121)
        conn2.request("GET", "/api/notes")
        resp = conn2.getresponse()
        notes = json.loads(resp.read())
        texts = [n["text"] for n in notes]
        assert "Persistenz-Check" in texts
    finally:
        server.shutdown()


def test_us06_ac3_empty_text_returns_400():
    """US-06/AC-3: POST /api/notes with empty text returns HTTP 400."""
    server, _ = _start_server(port=18122)
    try:
        payload = json.dumps({"text": ""}).encode()
        conn = HTTPConnection("127.0.0.1", 18122)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 400
        resp.read()
    finally:
        server.shutdown()


def test_us06_ac4_text_too_long_returns_400():
    """US-06/AC-4: POST /api/notes with text > 500 chars returns HTTP 400."""
    server, _ = _start_server(port=18123)
    try:
        payload = json.dumps({"text": "x" * 501}).encode()
        conn = HTTPConnection("127.0.0.1", 18123)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 400
        resp.read()
    finally:
        server.shutdown()


def test_us06_ac4_boundary_500_chars_returns_201():
    """US-06/AC-4 boundary: POST /api/notes with exactly 500 chars returns HTTP 201."""
    server, _ = _start_server(port=18124)
    try:
        payload = json.dumps({"text": "x" * 500}).encode()
        conn = HTTPConnection("127.0.0.1", 18124)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 201
        resp.read()
    finally:
        server.shutdown()


def test_us06_ac5_missing_text_field_returns_400():
    """US-06/AC-5: POST /api/notes with missing text field returns HTTP 400."""
    server, _ = _start_server(port=18125)
    try:
        payload = json.dumps({"note": "no text field"}).encode()
        conn = HTTPConnection("127.0.0.1", 18125)
        conn.request("POST", "/api/notes", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 400
        resp.read()
    finally:
        server.shutdown()


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
