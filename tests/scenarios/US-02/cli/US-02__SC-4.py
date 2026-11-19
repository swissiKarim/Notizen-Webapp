# scenario-id: US-02/SC-4
"""ruff check still passes after --selftest implementation."""
import json
import subprocess

result = subprocess.run(
    ["ruff", "check", "."],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
}))
