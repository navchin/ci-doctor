import anthropic
import os
client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]}
)
log = open("pod_crash.log").read()

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=2000,
    system="You are a senior kuberenets engineer. Given a failed pod crash failed job log, "
           "reply with: 1) Root cause, 2) Fix, 3) prevention."
           "Max 3 bullet points per section. No code blocks longer than 5 lines.",
    messages=[{"role": "user", "content": f"Diagnose this kubernets pod crash failed issue:\n\n{log}"}],
    
)

for block in response.content:
    print("[block type]:", block.type)

answer = "".join(b.text for b in response.content if b.type == "text")

print(answer)
print("\n[stop reason]:", response.stop_reason)