# scenario-id: US-04/SC-4
"""AC-4: note IDs are incremental integers starting at 1.

then={body[0].id equals 1; body[1].id equals 2}
body is an array-like object with numeric string keys so body[0]/body[1] resolve.
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

# Build array-like body object with string-index keys for evaluator compatibility
body = {str(i): note for i, note in enumerate(notes)}
body["length"] = len(notes)

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body,
}))
