import os
from github import Github
from schema import Postmortem
from dotenv import load_dotenv

load_dotenv()

def escape_mentions(text: str) -> str:
    """Prevent accidental @mentions of real GitHub users from names in generated content."""
    return text.replace("@", "@\u200b")  # zero-width space breaks the mention, keeps it readable

def create_issue_from_postmortem(pm: Postmortem) -> str:
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPO"])
    timeline_md = "\n".join(
        f"- `{e.timestamp}` **{escape_mentions(e.actor)}**: {escape_mentions(e.event)}"
        for e in pm.timeline
    )
    actions_md = "\n".join(
        f"- [ ] {a.title} (Owner: {escape_mentions(a.owner) if a.owner else 'unassigned'}, {a.priority})"
        for a in pm.action_items
    )
    body = f"## Summary\n{pm.summary}\n\n## Root Cause\n{pm.root_cause}\n\n## Timeline\n{timeline_md}\n\n## Action Items\n{actions_md}"
    issue = repo.create_issue(
        title=f"[{pm.severity.value}] {pm.incident_title}",
        body=body,
        labels=[pm.severity.value, "postmortem", "auto-generated"],
    )
    return issue.html_url