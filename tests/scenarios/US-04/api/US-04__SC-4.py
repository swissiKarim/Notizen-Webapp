# scenario-id: US-04/SC-4
"""AC-4: note IDs are incremental integers starting at 1.

then={body[0].id equals 1; body[1].id equals 2}
Platform evaluates body[0] as string-key "0" on an object.
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

# Build object with string keys so body[0].id and body[1].id resolve via dot-notation
body = {str(i): note for i, note in enumerate(notes)}

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body,
}))
