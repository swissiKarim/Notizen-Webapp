# scenario-id: US-02/SC-3
"""--selftest does not bind port 8099."""
import json
import socket
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "app.py", "--selftest"],
    capture_output=True,
    text=True,
)

# After selftest exits, try to bind port 8099 ourselves.
# If the app had bound it and not released it, this would fail.
port_bindable = False
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 8099))
    s.close()
    port_bindable = True
except OSError:
    port_bindable = False

output = result.stdout.strip()
# Ensure no ERROR in stdout and port was never bound
stdout_clean = "ERROR" not in output

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": output,
    "port_bindable": port_bindable,
    "stdout_clean": stdout_clean,
}))
