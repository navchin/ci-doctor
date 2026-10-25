def validate(result, log):
    MAX_SUMMARY_WORDS = 25
    """Return a list of problems with the diagnosis. Empty list = all good."""
    errors = []

    words = len(result["summary"].split())
    if words > MAX_SUMMARY_WORDS:
         errors.append(f"summary has {words} words; keep it to {MAX_SUMMARY_WORDS} words max.")

    step = result.get("failing_step")
    if step and step not in log:
        errors.append(f"failing_step '{step}' does not appear in the log. "
                      "Use the exact step text from the log, or null.")

    return errors