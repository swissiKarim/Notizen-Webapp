# scenario-id: US-01/SC-4
"""AC-4: ruff check passes with exit code 0."""

import json
import subprocess

result = subprocess.run(
    ["ruff", "check", "."],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
    "exit_code": result.returncode,
}))
