# scenario-id: US-04/SC-1
"""AC-1: NoteStore items have id and text fields.

then={body[0].id exists true; body[0].text exists true}
body is a JSON array so body[0] resolves as array index 0.
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

print(json.dumps({
    "status": status,
    "headers": {},
    "body": notes,
}))
