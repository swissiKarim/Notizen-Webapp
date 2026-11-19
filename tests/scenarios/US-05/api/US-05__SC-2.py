# scenario-id: US-05/SC-2
"""SC-2: GET /api/notes response is a valid JSON array with application/json content-type.

then={body exists true; headers.content-type contains "application/json"}
"""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099"))
url = base_url.rstrip("/") + "/api/notes"

req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    status = resp.status
    headers = {k.lower(): v for k, v in resp.headers.items()}
    notes = json.loads(resp.read().decode())

body = {str(i): note for i, note in enumerate(notes)}
body["length"] = len(notes)

print(json.dumps({"status": status, "headers": headers, "body": body}))
