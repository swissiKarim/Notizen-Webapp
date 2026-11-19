# scenario-id: US-07/SC-6
import json
import subprocess

# Count standalone HTML files in the workspace (excluding .git and node_modules)
result = subprocess.run(
    ["find", ".", "-name", "*.html", "-not", "-path", "./.git/*", "-not", "-path", "./node_modules/*"],
    capture_output=True,
    text=True,
)
html_files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
count = len(html_files)

print(json.dumps({"stdout": str(count), "files": html_files}))
