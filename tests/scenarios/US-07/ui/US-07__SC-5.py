# scenario-id: US-07/SC-5
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url + "/")
    page.wait_for_load_state("networkidle")

    # Submit with empty input to trigger validation error
    page.fill('[data-testid="note-input"]', "")
    page.click("#add-btn")

    # Wait for the error element to become visible
    page.wait_for_selector('[data-testid="error-message"]', state="visible", timeout=5000)

    text = page.inner_text("body")
    error_visible = page.is_visible('[data-testid="error-message"]')
    screenshot(page, "US-07/SC-5")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": text,
        "visible": {"error-message": error_visible},
    }))
