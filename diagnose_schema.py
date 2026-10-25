import json
from validation import validate

DIAGNOSIS_TOOL = {
    "name": "record_diagnosis",
    "description": "Record the diagnosis of a failed CI/CD job or Kubernetes workload.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary":    {"type": "string", "description": "One sentence, max 20 words"},
            "root_cause": {"type": "string", "description": "Max 2 sentences"},
            "fix":        {"type": "string", "description": "Max 3 short steps"},
            "prevention": {"type": "string", "description": "Max 2 sentences"},
            "severity":   {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "category":   {"type": "string",
                           "enum": ["iam", "resources", "config", "network", "code", "dependency", "other"]},
            "failing_step": {"type": ["string", "null"],
                             "description": "Failing step name if visible in the log, else null. Do not guess."},
        },
        "required": ["summary", "root_cause", "fix", "prevention",
                     "severity", "category", "failing_step"],
    },
}

#print(json.dumps(DIAGNOSIS_TOOL, indent=2))
import os
import sys
import anthropic

client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]}
)
log = open(sys.argv[1]).read()

def ask_claude(user_text):
    """Send one request. Return the filled-in form, or None if Claude didn't use the tool."""
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=2000,
        system="You are a senior DevOps and Kubernetes engineer. "
               "You MUST respond by calling the record_diagnosis tool. Do not reply in plain text.",
        tools=[DIAGNOSIS_TOOL],
        messages=[{"role": "user", "content": user_text}],
    )
    blocks = [b for b in response.content if b.type == "tool_use"]
    return blocks[0].input if blocks else None


request = f"Diagnose this failure:\n\n{log}"
MAX_ATTEMPTS = 3

for attempt in range(1, MAX_ATTEMPTS + 1):
    result = ask_claude(request)

    if result is None:
        errors = ["You replied in text. You must call the record_diagnosis tool."]
    else:
        errors = validate(result, log)

    print(f"[attempt {attempt}] problems: {errors}")
    if not errors:
        break                                   # ✅ all good, stop retrying

    # ❌ Build the feedback for the next try: log + previous answer + exact problems
    request = (f"Diagnose this failure:\n\n{log}\n\n"
               f"Your previous answer was:\n{json.dumps(result, indent=2)}\n\n"
               "It has these problems:\n- " + "\n- ".join(errors) +
               "\n\nFix them and call record_diagnosis again.")

if errors:
    sys.exit(f"Still invalid after {MAX_ATTEMPTS} attempts: {errors}")

print(json.dumps(result, indent=2))
json.dump(result, open("diagnosis.json", "w"), indent=2)