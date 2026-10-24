import json

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

response = client.messages.create(
    model="claude-sonnet-5-5",          # same model as your other scripts
    max_tokens=2000,
    #system="You are a senior DevOps and Kubernetes engineer. "
    #       "Diagnose the failure and record it using the record_diagnosis tool.",
    system="You are a senior DevOps and Kubernetes engineer. "
           "You MUST respond by calling the record_diagnosis tool. Do not reply in plain text.",
    tools=[DIAGNOSIS_TOOL],
    #tool_choice={"type": "tool", "name": "record_diagnosis"},
    messages=[{"role": "user", "content": f"Diagnose this failure:\n\n{log}"}],
)


print("[stop reason]:", response.stop_reason)
for block in response.content:
    print("[block type]:", block.type)

tool_blocks = [b for b in response.content if b.type == "tool_use"]
if not tool_blocks:
    sys.exit("Model did not fill in the diagnosis form")

result = tool_blocks[0].input           # already a Python dict — no json.loads needed
print(json.dumps(result, indent=2))
json.dump(result, open("diagnosis.json", "w"), indent=2)

tool_blocks = [b for b in response.content if b.type == "tool_use"]
if not tool_blocks:
    sys.exit("Model did not fill in the diagnosis form")

result = tool_blocks[0].input
print(json.dumps(result, indent=2))
json.dump(result, open("diagnosis.json", "w"), indent=2)