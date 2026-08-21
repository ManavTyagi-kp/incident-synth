from pipeline_local import validate_with_retry
from action_engine import create_issue_from_postmortem

sample_transcript = """
14:02 @raj: anyone seeing 500s on checkout??
14:03 @mei: yeah, error rate just spiked hard
14:04 @sam: could be the deploy from 13:50
14:06 @raj: rolling back now, standby
14:11 @mei: rollback done, errors dropping
14:14 @sam: root cause: DB connection pool exhausted
"""

pm = validate_with_retry(sample_transcript)
print(create_issue_from_postmortem(pm))