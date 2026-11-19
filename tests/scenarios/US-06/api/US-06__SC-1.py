# scenario-id: US-06/SC-1
"""AC-1: POST /api/notes with valid text returns HTTP 201.

then={status equals 201}
"""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099")).rstrip("/")

payload = json.dumps({"text": "Neue Testnotiz SC-1"}).encode()
req = urllib.request.Request(
    base_url + "/api/notes",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    status = resp.status
    body = json.loads(resp.read().decode())

print(json.dumps({"status": status, "headers": {}, "body": body}))
