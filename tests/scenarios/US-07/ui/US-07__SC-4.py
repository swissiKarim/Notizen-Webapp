# scenario-id: US-07/SC-4
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url + "/")
    page.wait_for_load_state("networkidle")

    # Type a note and submit without page reload
    page.fill('[data-testid="note-input"]', "Testnotiz E2E")
    page.click("#add-btn")

    # Wait for the note to appear in the list (fetch-based, no reload)
    page.wait_for_function(
        "document.getElementById('note-list').innerText.includes('Testnotiz E2E')"
    )

    text = page.inner_text("body")
    screenshot(page, "US-07/SC-4")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": text,
        "visible": {},
    }))
