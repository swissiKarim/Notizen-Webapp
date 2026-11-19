# scenario-id: US-06/SC-5
"""AC-5: POST /api/notes with missing text field returns HTTP 400.

then={status equals 400}
"""
import json
import os
import urllib.request
import urllib.error

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099")).rstrip("/")

payload = json.dumps({"note": "no text field here"}).encode()
req = urllib.request.Request(
    base_url + "/api/notes",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        body = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    status = e.code
    body = json.loads(e.read().decode())

print(json.dumps({"status": status, "headers": {}, "body": body}))
