# scenario-id: US-04/SC-2
"""AC-2: exactly two sample notes present on startup.

then={body.length equals 2}
The platform evaluator resolves body.length via key lookup on the body object.
We expose body as an array-like dict with a "length" key alongside numeric indices.
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

# Build body as object with explicit "length" key so body.length path resolves
body = {"length": len(notes)}
for i, note in enumerate(notes):
    body[str(i)] = note

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body,
}))
