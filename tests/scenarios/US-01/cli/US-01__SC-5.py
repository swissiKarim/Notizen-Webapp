# scenario-id: US-01/SC-5
"""AC-5: pytest runs successfully with at least one test."""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--tb=short", "-q"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "stdout": result.stdout,
    "stderr": result.stderr,
    "exit_code": result.returncode,
}))
