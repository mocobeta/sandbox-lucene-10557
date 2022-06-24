from dataclasses import dataclass, asdict, field
from typing import Optional
import logging
import time
import requests

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


GITHUB_API_BASE = "https://api.github.com"
INTERVAL = 2


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


@dataclass
class GHContent:
    message: str
    content: str
    sha: str


def check_authentication(token: str):
    check_url = GITHUB_API_BASE + "/user"
    headers = {"Authorization": f"token {token}"}
    res = requests.get(check_url, headers=headers)
    assert res.status_code == 200, f"Authentication failed. Please check your GitHub token. status_code={res.status_code}, message={res.text}"


def create_issue(token: str, repo: str, issue: GHIssue) -> Optional[tuple[str, int]]:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Retry-After": "30"}
    res = requests.post(url, headers=headers, json=asdict(issue))
    if res.status_code != 201:
        logger.error(f"Failed to create issue {issue.title}; status_code={res.status_code}, message={res.text}")
        return None
    issue_url = res.json().get("html_url")
    issue_number = res.json().get("number")

    logger.info(f"Issue #{issue_number} was successfully created.")
    time.sleep(INTERVAL)
    return (issue_url, issue_number)


def update_issue(token: str, repo: str, issue_number: int, issue: GHIssue) -> bool:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues/{issue_number}"
    headers = {"Authorization": f"token {token}", "Retry-After": "30"}
    res = requests.patch(url, headers=headers, json=asdict(issue))
    if res.status_code != 200:
        logger.error(f"Failed to update issue {issue.title}; status_code={res.status_code}, message={res.text}")
        return False
    logger.info(f"Issue #{issue_number} was successfully updated.")
    time.sleep(INTERVAL)
    return True


def create_comment(token: str, repo: str, issue_number: int, comment: GHIssueComment) -> bool:
    url = GITHUB_API_BASE + f"/repos/{repo}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {token}", "Retry-After": "30"}
    res = requests.post(url, headers=headers, json=asdict(comment))
    if res.status_code != 201:
        logger.error(f"Failed to create issue comment to {issue_number}; status_code={res.status_code}, message={res.text}")
        return False
    time.sleep(INTERVAL)
    return True


def create_file(token: str, repo: str, path: str, content: GHContent) -> Optional[tuple[str, str]]:
    url = GITHUB_API_BASE + f"/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}", "Retry-After": "30"}
    res = requests.put(url, headers=headers, json=asdict(content))
    if res.status_code not in [200, 201]:
        logger.error(f"Failed to create file on {path}; status_code={res.status_code}, message={res.text}")
        return None
    download_url = res.json().get("content").get("download_url")
    path = res.json().get("content").get("path")
    sha = res.json().get("content").get("sha")

    logger.info(f"File content {path} was successfully created.")
    time.sleep(INTERVAL)
    return (download_url, sha)

