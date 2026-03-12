from scholarly import scholarly
import json
from datetime import datetime
import os
import re


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "_config.yml")


def get_scholar_id() -> str:
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID")
    if scholar_id:
        return scholar_id

    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config_text = config_file.read()

    match = re.search(r"googlescholar\s*:\s*\"https?://scholar\.google\.com/citations\?user=([^\"]+)\"", config_text)
    if match:
        return match.group(1)

    raise RuntimeError("Google Scholar ID not found. Set GOOGLE_SCHOLAR_ID or configure author.googlescholar in _config.yml.")


author: dict = scholarly.search_author_id(get_scholar_id())
scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
author["updated"] = str(datetime.now())
author["publications"] = {publication["author_pub_id"]: publication for publication in author["publications"]}

print(json.dumps(author, indent=2, ensure_ascii=False))

os.makedirs("results", exist_ok=True)
with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
    json.dump(author, outfile, ensure_ascii=False)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author['citedby']}",
}
with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)
