import os
import sys
from pathlib import Path
import json
from collections import defaultdict

from common import JIRA_DUMP_DIRNAME


def extract_authors(jira_dump_file: Path) -> set[tuple[str, str]]:
    assert jira_dump_file.exists()
    authors = set([])
    with open(jira_dump_file) as fp:
        o = json.load(fp)
        reporter = __extract_reporter(o)
        authors.add(reporter)
        assignee = __extract_assignee(o)
        authors.add(assignee)
        comment_authors = set(__extract_comment_authors(o))
        authors |= comment_authors
    return authors
        

def __extract_reporter(o: dict) -> tuple[str, str]:
    reporter = o.get("fields").get("reporter")
    name = reporter.get("name", "") if reporter else ""
    disp_name = reporter.get("displayName", "") if reporter else ""
    return (name, disp_name)


def __extract_assignee(o: dict) -> tuple[str, str]:
    assignee = o.get("fields").get("assignee")
    name = assignee.get("name", "") if assignee else ""
    disp_name = assignee.get("displayName", "") if assignee else ""
    return (name, disp_name)


def __extract_comment_authors(o: dict) -> list[tuple[str, str]]:
    comments = o.get("fields").get("comment", {}).get("comments", [])
    if not comments:
        return []
    res = []
    for c in comments:
        author = c.get("author")
        name = author.get("name", "") if author else ""
        disp_name = author.get("displayName", "") if author else ""
        res.append((name, disp_name))
    return res


if __name__ == "__main__":
    dump_dir = Path(__file__).resolve().parent.parent.joinpath(JIRA_DUMP_DIRNAME)
    counts = defaultdict(int)
    num_files = 0
    for child in dump_dir.iterdir():
        if child.is_file() and child.name.endswith(".json"):
            num_files += 1
            authors = extract_authors(child)
            for author in authors:
                counts[author] += 1
    counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for a, c in counts:
        print(f"{a[0]},{a[1]},{c}")
    