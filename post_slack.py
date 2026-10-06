import json
import os
import requests

result = json.load(open("diagnosis.json"))

EMOJI = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
sev = result["severity"]

def short(text, limit=400):
    return text if len(text) <= limit else text[:limit] + "…"

message = (
    f"{EMOJI.get(sev, '⚪')} *CI failure — {sev.upper()}* ({result['category']})\n"
    f"*{result['summary']}*\n\n"
    f"*Root cause:* {short(result['root_cause'])}\n"
    f"*Fix:* {short(result['fix'])}\n"
    f"*Prevention:* {short(result['prevention'])}"
)

r = requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": message}, timeout=10)
r.raise_for_status()
print("Posted to Slack ✅")
