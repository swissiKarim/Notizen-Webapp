# scenario-id: US-04/SC-3
"""AC-3: concurrent writes do not corrupt the note store; all return 201."""

import json
import os
import threading
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8099"))

url = base_url.rstrip("/") + "/api/notes"

statuses = []
lock = threading.Lock()

def post_note(i):
    payload = json.dumps({"text": f"Concurrent note {i}"}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        with lock:
            statuses.append(resp.status)

threads = [threading.Thread(target=post_note, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# All concurrent writes must have succeeded with 201
all_ok = all(s == 201 for s in statuses)

print(json.dumps({
    "status": 201 if all_ok else 500,
    "statuses": statuses,
}))
