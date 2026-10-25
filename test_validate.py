from validation import validate

log = "Run echo Installing dependencies\nERROR: No matching distribution for requests==99.0.0"

good = {"summary": "pip install failed on a bad version pin",
        "failing_step": "Run echo Installing dependencies"}
long_summary = {"summary": "word " * 40, "failing_step": None}
made_up_step = {"summary": "deploy failed", "failing_step": "Deploy to production"}

print("good:        ", validate(good, log))
print("long summary:", validate(long_summary, log))
print("made-up step:", validate(made_up_step, log))