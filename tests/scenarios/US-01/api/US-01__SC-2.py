# scenario-id: US-01/SC-2
"""AC-2, AC-3: python app.py starts ThreadingHTTPServer on 0.0.0.0:8099; GET /health returns 200."""

import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099"))

url = base_url.rstrip("/") + "/health"

req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    status = resp.status
    body = resp.read().decode()

print(json.dumps({
    "status": status,
    "body": body,
}))
