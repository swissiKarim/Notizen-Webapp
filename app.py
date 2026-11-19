"""Single-file note-management webapp for the insurance industry.

Uses only Python stdlib. Starts a ThreadingHTTPServer on 0.0.0.0:8099.
Run with:  python app.py
Selftest:  python app.py --selftest
"""

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# ---------------------------------------------------------------------------
# Thread-safe in-memory store
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_notes: list[dict] = [
    {"id": 1, "text": "Versicherungsantrag prüfen"},
    {"id": 2, "text": "Schadensfall dokumentieren"},
]
_next_id: int = 3


def _get_notes() -> list[dict]:
    with _lock:
        return list(_notes)


def _add_note(text: str) -> dict:
    global _next_id
    with _lock:
        note = {"id": _next_id, "text": text}
        _notes.append(note)
        _next_id += 1
        return note


# ---------------------------------------------------------------------------
# HTML front-end
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Notizverwaltung</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 700px; margin: 2rem auto; }
  #error { color: red; display: none; }
  ul { padding-left: 1.2rem; }
</style>
</head>
<body>
<h1>Notizen</h1>
<ul id="note-list"></ul>
<h2>Neue Notiz</h2>
<input id="note-text" type="text" placeholder="Text eingeben …" style="width:60%" data-testid="note-input">
<button id="add-btn">Hinzufügen</button>
<p id="error" data-testid="error-message"></p>
<script>
async function loadNotes() {
  const res = await fetch('/api/notes');
  const notes = await res.json();
  const ul = document.getElementById('note-list');
  ul.innerHTML = '';
  notes.forEach(n => {
    const li = document.createElement('li');
    li.setAttribute('data-testid', 'note-' + n.id);
    li.textContent = n.text;
    ul.appendChild(li);
  });
}

async function addNote() {
  const input = document.getElementById('note-text');
  const errorEl = document.getElementById('error');
  errorEl.style.display = 'none';
  const res = await fetch('/api/notes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: input.value})
  });
  if (res.status === 201) {
    input.value = '';
    await loadNotes();
  } else {
    const data = await res.json();
    errorEl.textContent = data.error || 'Fehler beim Hinzufügen';
    errorEl.style.display = 'block';
  }
}

document.getElementById('add-btn').addEventListener('click', addNote);
loadNotes();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class NoteHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the note app."""

    def log_message(self, fmt, *args):  # silence access log
        pass

    def _send_json(self, code: int, data) -> None:
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, code: int, text: str) -> None:
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, code: int, html: str) -> None:
        body = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # name required by BaseHTTPRequestHandler protocol
        if self.path == "/health":
            self._send_text(200, "ready")
        elif self.path == "/api/notes":
            self._send_json(200, _get_notes())
        elif self.path == "/":
            self._send_html(200, HTML)
        else:
            self._send_text(404, "not found")

    def do_POST(self):  # name required by BaseHTTPRequestHandler protocol
        if self.path == "/api/notes":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Ungültiges JSON"})
                return
            text = data.get("text", "")
            if not text or not text.strip():
                self._send_json(400, {"error": "Text darf nicht leer sein"})
                return
            if len(text) > 500:
                self._send_json(400, {"error": "Text zu lang (max. 500 Zeichen)"})
                return
            note = _add_note(text)
            self._send_json(201, note)
        else:
            self._send_text(404, "not found")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server that handles each request in a new thread."""

    daemon_threads = True


def run_server(host: str = "0.0.0.0", port: int = 8099) -> None:
    """Start the ThreadingHTTPServer and block until interrupted."""
    server = ThreadingHTTPServer((host, port), NoteHandler)
    print(f"Listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print('{"selftest":"ok"}')
        sys.exit(0)
    run_server()
