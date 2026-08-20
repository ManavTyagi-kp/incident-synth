# TODO: Using Gemini for setting up pipelines, etc, will swap out for local SLM in later stages.
import json
from google import genai
from google.genai import types
from pydantic import ValidationError
from schema import Postmortem
from dotenv import load_dotenv

load_dotenv()
gemini_client = genai.Client()  # reads GEMINI_API_KEY from the environment automatically

SYSTEM_PROMPT = (
    "You are an SRE assistant. Read the incident chat transcript and output "
    "ONLY a JSON object matching this schema: incident_title (str), "
    "severity (SEV1|SEV2|SEV3|SEV4), summary (str), root_cause (str), "
    "contributing_factors (list[str]), timeline (list of {timestamp, actor, event}), "
    "action_items (list of {title, owner, priority: P0|P1|P2|P3, category}), "
    "services_affected (list[str]), detection_method (str), resolution_time_minutes (int). "
    "No prose, no markdown fences — just the JSON object."
)

def call_model(user_content: str, model: str = "gemini-2.5-flash") -> str:
    resp = gemini_client.models.generate_content(
        model=model,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )
    return resp.text

def validate_with_retry(transcript: str, model: str = "gemini-2.5-flash", max_retries: int = 2) -> Postmortem:
    prompt = transcript
    last_error = None
    for attempt in range(max_retries + 1):
        raw = call_model(prompt, model)
        try:
            return Postmortem(**json.loads(raw))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            prompt = f"Your previous output was invalid: {last_error}\nFix it and return ONLY the corrected JSON.\n\nOriginal transcript:\n{transcript}"
    raise ValueError(f"Failed after {max_retries} retries: {last_error}")

if __name__ == "__main__":
    sample_transcript = """
14:02 @raj: anyone seeing 500s on checkout??
14:03 @mei: yeah, error rate just spiked hard
14:04 @sam: could be the deploy from 13:50
14:06 @raj: rolling back now, standby
14:11 @mei: rollback done, errors dropping
14:14 @sam: root cause: DB connection pool exhausted
"""
    pm = validate_with_retry(sample_transcript)
    print(pm.model_dump_json(indent=2))