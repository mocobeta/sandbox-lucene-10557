from pathlib import Path

JIRA_DUMP_DIRNAME = "jira-dump"
GITHUB_DATA_DIRNAME = "github-data"
MAPPINGS_DATA_DIRNAME = "mappings-data"

ISSUE_MAPPING_FILENAME = "issue-map.csv"

ASF_JIRA_BASE_URL = "https://issues.apache.org/jira/browse"


def jira_issue_url(issue_number: int) -> str:
    return ASF_JIRA_BASE_URL + f"/{jira_issue_id(issue_number)}"


def jira_issue_id(issue_number: int) -> str:
    return f"LUCENE-{issue_number}"


def jira_dump_file(dump_dir: Path, issue_number: int) -> Path:
    issue_id = jira_issue_id(issue_number)
    return dump_dir.joinpath(f"{issue_id}.json")


def github_data_file(data_dir: Path, issue_number: int) -> Path:
    issue_id = jira_issue_id(issue_number)
    return data_dir.joinpath(f"GH-{issue_id}.json")


def make_github_title(summary: str, jira_id: str) -> str:
    return f"{summary} (Jira: {jira_id})"


ISSUE_TYPE_TO_LABEL_MAP = {
    "Bug": "type:bug",
    "New Feature": "type:new_feature",
    "Improvement": "type:enhancement",
    "Test": "type:test",
    "Wish": "type:enhancement",
    "Task": "type:task"
}