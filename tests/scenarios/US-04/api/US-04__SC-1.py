# scenario-id: US-04/SC-1
"""AC-1: NoteStore items have id and text fields.

then={body[0].id exists true; body[0].text exists true}
body is an array-like object with numeric string keys so body[0] resolves.
"""

import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099"))

url = base_url.rstrip("/") + "/api/notes"

req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    status = resp.status
    notes = json.loads(resp.read().decode())

# Build array-like body object with string-index keys for evaluator compatibility
body = {str(i): note for i, note in enumerate(notes)}
body["length"] = len(notes)

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body,
}))
