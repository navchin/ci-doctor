# ci-doctor 🩺

LLM-powered diagnosis for CI/CD pipeline and Kubernetes failures.
Feed it a failed job or pod log → get **root cause, fix, and prevention** in seconds.

## Why

When a pipeline or pod fails, engineers spend the first 10–30 minutes just reading logs to figure out *what* broke.
ci-doctor hands that first pass to an LLM, so the engineer starts from a diagnosis instead of a wall of logs.

## Examples

| Script | Input | What it catches |
|---|---|---|
| `diagnose.py` | `failed_job.log` — Terraform apply failure | S3 `AccessDenied` → missing IAM `s3:CreateBucket` permission |
| `diagnose_k8s.py` | `pod_crash.log` — `kubectl describe` + `kubectl logs --previous` | `OOMKilled` / `CrashLoopBackOff` → memory limit too low for startup cache load |

Sample output (Kubernetes):

```
## 1) Root cause
- Container is OOMKilled (exit code 137), exceeding its 256Mi memory limit
- Crash happens during startup cache loading (48,000 items)
## 2) Fix
- Raise memory request/limit; confirm real usage with kubectl top / Prometheus
## 3) Prevention
- Alert on memory > 80% of limit; load-test with production-sized data
[stop reason]: end_turn
```

## Run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"     # never commit this
python3 diagnose_k8s.py
```

## How it works

1. **Gather context** — read the failed log
2. **Send to the model** — `system` prompt sets the role (senior DevOps/K8s engineer) and output format; the log goes in `messages`
3. **Use the answer** — keep only `text` blocks, and check `stop_reason` before trusting the output

## What I learned

- **system vs messages**: `system` is the role/JD (same every run); `messages` is the specific task and input for this run.
- **Context is everything**: the model can't see my files or cluster — it only knows what I put in the message.
- **stop_reason**: tells why the response ended — `end_turn` (finished) vs `max_tokens` (cut off). Always check it before trusting output.
- **Content blocks**: a response is a list of blocks (`text`, `thinking`, `tool_use`). The mix can change every run, so filter by type — never rely on `content[0]`.

## Roadmap

- [x] Diagnose Terraform/CI failure logs
- [x] Diagnose Kubernetes pod crashes
- [x] Fetch failed job logs directly from the GitLab API
- [x] Return a structured JSON diagnosis (`root_cause`, `fix`, `severity`)
- [x] Post results to Slack
- [ ] Agent mode: model decides what to inspect next (tool use)
- [x] Run automatically in GitLab CI on job failure
## How it runs
build fails → GitHub Actions (`workflow_run`) → fetch log → Claude diagnosis (JSON) → Slack alert
See [ci-doctor-lab](https://github.com/navchin/ci-doctor-lab) for the live setup.

## Slack message screenshot
<img width="1022" height="229" alt="image" src="https://github.com/user-attachments/assets/183d8233-6175-44b5-ba3e-0c35b4d0f9d5" />

## Security

- API keys are read from environment variables only — never hard-coded or committed
- `.gitignore` excludes `venv/`, `.env`, and caches
- Sample logs are synthetic; no real company data
