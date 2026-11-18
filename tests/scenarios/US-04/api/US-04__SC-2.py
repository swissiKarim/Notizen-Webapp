# scenario-id: US-04/SC-2
"""AC-2: exactly two sample notes present on startup.

then={body.length equals 2}
body is an object with "length" key so body.length resolves via key lookup.
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

body = {str(i): note for i, note in enumerate(notes)}
body["length"] = len(notes)

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body,
}))
