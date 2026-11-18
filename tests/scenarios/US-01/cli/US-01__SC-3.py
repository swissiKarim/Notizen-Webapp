# scenario-id: US-01/SC-3
"""AC-3: ThreadingHTTPServer class is referenced in app.py."""

import json
import pathlib

source = pathlib.Path("app.py").read_text()
found = "ThreadingHTTPServer" in source

print(json.dumps({
    "found": found,
    "exit_code": 0 if found else 1,
}))

if not found:
    raise SystemExit(1)
