# scenario-id: US-07/SC-1
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099"))

req = urllib.request.Request(f"{base_url}/")
try:
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8", errors="replace")
except Exception as e:
    print(json.dumps({"error": str(e), "status": 0, "headers": {"content-type": ""}, "body": ""}))
    raise SystemExit(1)

print(json.dumps({
    "status": status,
    "headers": {"content-type": content_type},
    "body": body[:200],
}))
