import json, random, os, time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from schema import Postmortem
from pydantic import ValidationError

load_dotenv()
gemini_client = genai.Client()

SEVERITIES = ["SEV1", "SEV2", "SEV3", "SEV4"]
ROOT_CAUSES = ["bad deploy", "database exhaustion", "network partition",
               "third-party outage", "misconfiguration", "credential expiry",
               "scheduler/job failure", "data pipeline backlog"]
TONES = ["calm and organized", "frantic with cross-talk and false leads"]
INCIDENT_STYLES = [
    "a human engineer noticing an acute service outage and firefighting live in chat, with "
    "back-and-forth investigation before a fix is found",
    "an automated monitoring bot posting a tabular metric-threshold breach (e.g. queue lag or "
    "backlog counts per data type), followed by engineers re-triggering jobs and posting periodic "
    "status updates as the backlog clears over the next few hours",
]

GEN_PROMPT = """Generate synthetic training data for an incident-response model.

Produce TWO things as a single JSON object with keys "transcript" and "postmortem":
1. "transcript": a realistic Slack-style chat transcript (15-25 messages, 3-5 engineers,
   timestamps, some dead-end investigation), for an incident with:
   - Severity: {severity}
   - Root cause category: {root_cause}
   - Tone: {tone}
   - Style: {incident_style}
   If the style involves an automated bot, include one message from a bot-like sender (e.g.
   "monitoring-bot") containing a small plain-text table of 3-6 metric rows, then have the
   engineers respond to it.
2. "postmortem": the gold-standard post-mortem JSON with keys: incident_title, severity,
   summary, root_cause, contributing_factors (list), timeline (list of timestamp/actor/event),
   action_items (list of title/owner/priority[P0-P3]/category), services_affected (list),
   detection_method, resolution_time_minutes.

Return ONLY the JSON object, no prose, no markdown fences.
"""

def generate_one(severity, root_cause, tone, incident_style):
    resp = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=GEN_PROMPT.format(
            severity=severity, root_cause=root_cause, tone=tone, incident_style=incident_style
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=8192,
        ),
    )
    return json.loads(resp.text)

def generate_one_with_retry(severity, root_cause, tone, incident_style, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return generate_one(severity, root_cause, tone, incident_style)
        except genai_errors.ServerError as e:
            wait = 5 * (attempt + 1)
            print(f"  server busy, waiting {wait}s and retrying...")
            time.sleep(wait)
    raise RuntimeError("Gemini still unavailable after retries")

def main(n=7, out_path="data/incident_train.jsonl"):
    os.makedirs("data", exist_ok=True)
    kept, attempts = 0, 0
    max_total_attempts = n * 6  # stop instead of looping forever if something's fundamentally wrong
    with open(out_path, "a") as f:
        while kept < n and attempts < max_total_attempts:
            attempts += 1
            severity = random.choice(SEVERITIES)
            root_cause = random.choice(ROOT_CAUSES)
            tone = random.choice(TONES)
            incident_style = random.choice(INCIDENT_STYLES)
            try:
                example = generate_one_with_retry(severity, root_cause, tone, incident_style)
                Postmortem(**example["postmortem"])
                f.write(json.dumps({
                    "transcript": example["transcript"],
                    "postmortem_json": json.dumps(example["postmortem"]),
                }) + "\n")
                kept += 1
                print(f"saved {kept}/{n}")
            except (json.JSONDecodeError, ValidationError, KeyError) as e:
                print(f"skipped invalid example: {e}")
            except RuntimeError as e:
                print(f"stopping early: {e}")
                break
    if kept < n:
        print(f"finished with {kept}/{n} \u2014 rerun to top up the rest")

if __name__ == "__main__":
    main()