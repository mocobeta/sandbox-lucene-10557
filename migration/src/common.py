from pathlib import Path

JIRA_DUMP_DIRNAME = "jira-dump"
GITHUB_DATA_DIRNAME = "github-data"
GITHUB_IMPORT_DATA_DIRNAME = "github-import-data"
MAPPINGS_DATA_DIRNAME = "mappings-data"

ISSUE_MAPPING_FILENAME = "issue-map.csv"
ACCOUNT_MAPPING_FILENAME = "account-map.csv"

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


def read_issue_id_map(issue_mapping_file: Path) -> dict[str, str]:
    id_map = {}
    with open(issue_mapping_file) as fp:
        fp.readline()  # skip header
        for line in fp:
            cols = line.strip().split(",")
            if len(cols) < 3:
                continue
            id_map[cols[0]] = cols[2]  # jira issue key -> github issue number
    return id_map


def read_account_map(account_mapping_file: Path) -> dict[str, str]:
    id_map = {}
    with open(account_mapping_file) as fp:
        fp.readline()  # skip header
        for line in fp:
            cols = line.strip().split(",")
            if len(cols) < 2:
                continue
            id_map[cols[0]] = cols[1]  # jira name -> github account
    return id_map


ISSUE_TYPE_TO_LABEL_MAP = {
    "Bug": "type:bug",
    "New Feature": "type:new_feature",
    "Improvement": "type:enhancement",
    "Test": "type:test",
    "Wish": "type:enhancement",
    "Task": "type:task"
}


COMPONENT_TO_LABEL_MAP = {
    "core": "component:module/core",
    "modules/analysis": "component:module/analysis",
    "modules/benchmark": "component:module/benchmark",
    "modules/classification": "component:module/classification",
    "modules/expressions": "component:module/expressions",
    "modules/facet": "component:module/facet",
    "modules/grouping": "component:module/grouping",
    "modules/highlithter": "component:module/highlithter",
    "modules/join": "component:module/join",
    "modules/luke": "component:module/luke",
    "modules/monitor": "component:module/monitor",
    "modules/queryparser": "component:module/queryparser",
    "modules/replicator": "component:module/replicator",
    "modules/sandbox": "component:module/sandbox",
    "modules/spatial": "component:module/spatial",
    "modules/spatial-extras": "component:module/spatial-extras",
    "modules/spatial3d": "component:module/spatial3d",
    "modules/suggest": "component:module/suggest",
    "modules/spellchecker": "component:module/suggest",
    "modules/test-framework": "component:module/test-framework",
    "luke": "component:module/luke",
    "general/build": "component:general/build",
    "general/javadocs": "component:general/javadocs",
    "general/test": "component:general/test",
    "general/website": "component:general/website",
    "release wizard": "component:general/release wizard",
}