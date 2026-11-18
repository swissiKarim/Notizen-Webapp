# scenario-id: US-03/SC-3
"""SC-3: GET /health stable under concurrent requests."""
import json
import os
import threading
import urllib.request

base_url = os.environ["ASB_SVC_WEB_URL"].rstrip("/")

results = []
lock = threading.Lock()


def fetch():
    req = urllib.request.Request(f"{base_url}/health", method="GET")
    with urllib.request.urlopen(req) as resp:
        code = resp.status
    with lock:
        results.append(code)


threads = [threading.Thread(target=fetch) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

all_ok = all(s == 200 for s in results)
# Report the last status seen (all must be 200)
status = results[-1] if results else 0

print(json.dumps({"status": status, "all_ok": all_ok, "count": len(results)}))
