import os
import sys
import requests

REPO = sys.argv[1] if len(sys.argv) > 1 else "navchin/ci-doctor-lab"
API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# 1. Latest failed run
r = requests.get(f"{API}/repos/{REPO}/actions/runs",
                 headers=HEADERS, params={"status": "failure", "per_page": 1})
r.raise_for_status()
runs = r.json()["workflow_runs"]
if not runs:
    print("No failed runs found.")
    sys.exit(1)
run = runs[0]
print(f"Failed run: {run['name']} #{run['run_number']} -> {run['html_url']}")

# 2. Which job failed in that run
r = requests.get(run["jobs_url"], headers=HEADERS)
r.raise_for_status()
failed_jobs = [j for j in r.json()["jobs"] if j["conclusion"] == "failure"]
job = failed_jobs[0]
print(f"Failed job: {job['name']}")

# 3. Download the job log (keep only the last 80 lines)
r = requests.get(f"{API}/repos/{REPO}/actions/jobs/{job['id']}/logs", headers=HEADERS)
r.raise_for_status()
lines = r.text.splitlines()[-80:]

with open("github_job.log", "w") as f:
    f.write("\n".join(lines))
print(f"Saved last {len(lines)} lines to github_job.log")