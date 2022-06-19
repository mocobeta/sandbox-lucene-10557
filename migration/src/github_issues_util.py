from dataclasses import dataclass, asdict, field
from typing import Optional
import logging
import requests

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


GITHUB_API_BASE = "https://api.github.com"


@dataclass
class GHIssue:
    title: str = ""
    body: str = ""
    state: str = "open"
    labels: list[str] = field(default_factory=list)
    milestone: Optional[str] = None


@dataclass
class GHIssueComment:
    body: str = ""


def check_authentication(token: str):
    check_url = GITHUB_API_BASE + "/user"
    headers = {"Authorization": f"token {token}"}
    res = requests.get(check_url, headers=headers)
    assert res.status_code == 200, f"Authentication failed. Please check your GitHub token. status_code={res.status_code}, message={res.text}"


def create_issue(token: str, repo: str, issue: GHIssue) -> Optional[tuple[str, int]]:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    res = requests.post(url, headers=headers, json=asdict(issue))
    if res.status_code != 201:
        logger.error(f"Failed to create issue {issue.title}; status_code={res.status_code}, message={res.text}")
        return None
    issue_url = res.json().get("html_url")
    issue_number = res.json().get("number")

    logger.info(f"Issue #{issue_number} was successfully created.")
    return (issue_url, issue_number)


def update_issue(token: str, repo: str, issue_number: int, issue: GHIssue) -> bool:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues/{issue_number}"
    headers = {"Authorization": f"token {token}"}
    res = requests.patch(url, headers=headers, json=asdict(issue))
    if res.status_code != 200:
        logger.error(f"Failed to update issue {issue.title}; status_code={res.status_code}, message={res.text}")
        return False
    logger.info(f"Issue #{issue_number} was successfully updated.")
    return True


def create_issue_comment(token: str, repo: str, issue_number: int, comment: GHIssueComment) -> bool:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {token}"}
    res = requests.post(url, headers=headers, json=asdict(comment))
    if res.status_code != 201:
        logger.error(f"Failed to create issue comment to {issue.title}; status_code={res.status_code}, message={res.text}")
        return False
    return True
