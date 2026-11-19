# scenario-id: US-05/SC-3
"""SC-3: each note in list contains id and text.

then={body[0].id exists true; body[0].text exists true; body[1].id exists true; body[1].text exists true}
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

body = {str(i): note for i, note in enumerate(notes)}
body["length"] = len(notes)

print(json.dumps({"status": status, "headers": {}, "body": body}))
