# scenario-id: US-07/SC-2
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url + "/")
    page.wait_for_load_state("networkidle")
    text = page.inner_text("body")
    screenshot(page, "US-07/SC-2")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": text,
        "visible": {},
    }))
