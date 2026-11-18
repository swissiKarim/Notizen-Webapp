# scenario-id: US-03/SC-1
"""SC-1: GET /health returns HTTP 200."""
import json
import os
import urllib.request

base_url = os.environ["ASB_SVC_WEB_URL"].rstrip("/")

req = urllib.request.Request(f"{base_url}/health", method="GET")
with urllib.request.urlopen(req) as resp:
    status = resp.status
    body = resp.read().decode()

print(json.dumps({"status": status, "body": body}))
