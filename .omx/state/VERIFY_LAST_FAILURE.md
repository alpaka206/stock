# Verify Last Failure

status: active
failing_command: scripts/verify_minimal.sh
symptom: text_quality_guard regex compile failed
likely_cause: UNICODE_ESCAPE_RE in scripts/text_quality_guard.py uses an unescaped backslash-u pattern and raises re.error before workspace checks start
remediation_owner: current iteration
next_fix: fix UNICODE_ESCAPE_RE in scripts/text_quality_guard.py and rerun scripts/verify_minimal.sh first
