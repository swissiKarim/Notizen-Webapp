# scenario-id: US-05/SC-4
"""SC-4: at least two notes present on startup."""
import json
import os
import urllib.request

base_url = os.environ["ASB_SVC_WEB_URL"].rstrip("/")

req = urllib.request.Request(f"{base_url}/api/notes", method="GET")
with urllib.request.urlopen(req) as resp:
    status = resp.status
    headers = dict(resp.headers)
    body = json.loads(resp.read().decode())

print(json.dumps({"status": status, "headers": headers, "body": body}))
