# scenario-id: US-01/SC-1
"""AC-1: app.py exists and uses only stdlib imports. Prints {"selftest":"ok"} and exits 0."""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "app.py", "--selftest"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "stdout": result.stdout.strip(),
    "exit_code": result.returncode,
}))
