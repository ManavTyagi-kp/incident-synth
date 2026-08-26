from fastapi import FastAPI
from pipeline import validate_with_retry
from action_engine import create_issue_from_postmortem

app = FastAPI()

@app.post("/synthesize")
def synthesize(payload: dict):
    pm = validate_with_retry(payload["transcript"])
    issue_url = create_issue_from_postmortem(pm)
    return {"postmortem": pm.model_dump(), "issue_url": issue_url}