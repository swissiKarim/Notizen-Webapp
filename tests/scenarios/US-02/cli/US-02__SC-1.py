# scenario-id: US-02/SC-1
"""--selftest exits with code 0 without starting a server."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "app.py", "--selftest"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
}))
