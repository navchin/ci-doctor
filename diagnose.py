import anthropic
import os
client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]}
)
log = open("failed_job.log").read()

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=500,
    system="You are a senior DevOps engineer. Given a failed CI job log, "
           "reply with: 1) Root cause, 2) Fix, 3) prevention."
           "Max 3 bullet points per section. No code blocks longer than 5 lines.",
    messages=[{"role": "user", "content": f"Diagnose this failed job:\n\n{log}"}],
    
)

print(response.content[0].text)
print("\n[stop reason]:", response.stop_reason)