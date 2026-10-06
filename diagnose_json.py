import json
import sys
import os
import anthropic

client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]}
)

log_file = sys.argv[1]           # file name comes from the command line
log = open(log_file).read()

SYSTEM = """You are a senior DevOps and Kubernetes engineer. Diagnose the failed log.
Respond with ONLY a JSON object, no other text, in exactly this shape:
{"summary": "one sentence, max 20 words",
 "root_cause": "max 2 sentences", "fix": "max 3 short steps",
 "prevention": "max 2 sentences",
 "severity": "low|medium|high|critical",
 "category": "iam|resources|config|network|code|other"}"""

response = client.messages.create(
    model="claude-sonnet-5-5",        # same model as your other scripts
    max_tokens=2000,
    system=SYSTEM,
    messages=[{"role": "user", "content": f"Diagnose this failure:\n\n{log}"}],
)

usage = response.usage
PRICE_IN = 3.00 / 1_000_000    # $ per input token — EXAMPLE, check your model's price
PRICE_OUT = 15.00 / 1_000_000  # $ per output token — EXAMPLE, check your model's price
cost = usage.input_tokens * PRICE_IN + usage.output_tokens * PRICE_OUT
print(f"Tokens: in={usage.input_tokens}  out={usage.output_tokens}  | cost ≈ ${cost:.4f}")
if response.stop_reason != "end_turn":
    print("Warning: response incomplete:", response.stop_reason)
    sys.exit(1)

text = "".join(b.text for b in response.content if b.type == "text")
text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

try:
    result = json.loads(text)
except json.JSONDecodeError:
    print("Model did not return valid JSON:\n", text)
    sys.exit(1)

print(json.dumps(result, indent=2))
print("\nSeverity:", result["severity"], "| Category:", result["category"])

json.dump(result, open("diagnosis.json", "w"), indent=2)