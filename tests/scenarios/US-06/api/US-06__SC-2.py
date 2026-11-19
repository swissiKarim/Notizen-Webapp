# scenario-id: US-06/SC-2
"""AC-2: Newly created note appears in GET /api/notes.

then={body contains "Persistenz-Check"}
"""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099")).rstrip("/")

# Create a note with a recognisable text
payload = json.dumps({"text": "Persistenz-Check"}).encode()
req_post = urllib.request.Request(
    base_url + "/api/notes",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req_post) as resp:
    resp.read()

# Now fetch the list and return it as the body so the platform can check containment
req_get = urllib.request.Request(base_url + "/api/notes", method="GET")
with urllib.request.urlopen(req_get) as resp:
    status = resp.status
    notes = json.loads(resp.read().decode())

# Flatten to a single string so "body contains Persistenz-Check" resolves
body_text = json.dumps(notes)

print(json.dumps({"status": status, "headers": {}, "body": body_text}))
