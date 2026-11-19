# scenario-id: US-07/SC-7
import json
import pathlib
import sys

source = pathlib.Path("app.py").read_text(encoding="utf-8")

# Check that app.py contains an inline HTML string literal (triple-quoted with DOCTYPE)
has_inline_html = '"""<!DOCTYPE html>' in source or "'''<!DOCTYPE html>" in source or '= """<!DOCTYPE' in source or "HTML = " in source

exit_code = 0 if has_inline_html else 1

print(json.dumps({
    "has_inline_html": has_inline_html,
    "exit_code": exit_code,
}))

sys.exit(exit_code)
