#
# Create GitHub issues
# Usage:
#   python src/create_github_issues.py --min <min issue number> --max <max issue number>
#

import os
import sys
import logging
import argparse
import json
from pathlib import Path

from github_issues_util import *
from common import JIRA_DUMP_DIRNAME, MAPPINGS_DATA_DIRNAME, ISSUE_MAPPING_FILENAME, jira_dump_file, jira_issue_id, make_github_title

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


def init_github_issue(num: int, dump_dir: Path, token: str, repo: str) -> Optional[tuple[str, int]]:
    jira_id = jira_issue_id(num)
    dump_file = jira_dump_file(dump_dir, num)
    if not dump_file.exists():
        logger.warning(f"Jira dump file not found: {dump_file}")
        return None

    response = None
    with open(dump_file) as fp:
        o = json.load(fp)
        # initialize issue
        summary = o.get("fields").get("summary", "")
        title = make_github_title(summary, jira_id)
        issue = GHIssue(title=title)
        response = create_issue(token, repo, issue)

        # initialize comments
        #(_, issue_number) = response
        #total_comments = o.get("fields").get("comment", {}).get("total", 0)
        #for _ in range(total_comments):
        #    create_comment(token, repo, issue_number, GHIssueComment(body="dummy"))

    return response


if __name__ == '__main__':
    github_token = os.getenv("GITHUB_PAT")
    if not github_token:
        print("Please set your GitHub token to GITHUB_PAT environment variable.")
        sys.exit(1)
    github_repo = os.getenv("GITHUB_REPO")
    if not github_repo:
        print("Please set GitHub repo location to GITHUB_REPO environment varialbe.")
        sys.exit(1)

    check_authentication(github_token)

    parser = argparse.ArgumentParser()
    parser.add_argument('--min', type=int, dest='min', required=False, default=1, help='Minimum Jira issue number to be created')
    parser.add_argument('--max', type=int, dest='max', required=False, help='Maximum Jira issue number to be created')
    args = parser.parse_args()

    dump_dir = Path(__file__).resolve().parent.parent.joinpath(JIRA_DUMP_DIRNAME)
    if not dump_dir.exists():
        logger.error(f"Jira dump dir not exists: {dump_dir}")
        sys.exit(1)

    mappings_dir = Path(__file__).resolve().parent.parent.joinpath(MAPPINGS_DATA_DIRNAME)
    if not mappings_dir.exists():
        mappings_dir.mkdir()
    assert mappings_dir.exists()

    issue_mapping_file = mappings_dir.joinpath(ISSUE_MAPPING_FILENAME)
    if not issue_mapping_file.exists():
        with open(issue_mapping_file, "w") as fp:
            fp.write("JiraKey,GitHubUrl,GitHubNumber\n")
    assert issue_mapping_file.exists()

    issue_mapping = []

    if not args.max:
        logger.info(f"Initializing GitHub issue for Jira issue {args.min}")
        response = init_github_issue(args.min, dump_dir, github_token, github_repo)
        if response:
            (issue_url, issue_number) = response
            issue_mapping.append((jira_issue_id(args.min), issue_url, issue_number))
    else:
        logger.info(f"Initializing GitHub issues for Jira issues {args.min} to {args.max}")
        with open(issue_mapping_file, "a") as fp:
            for num in range(args.min, args.max + 1):
                response = init_github_issue(num, dump_dir, github_token, github_repo)
                if response:
                    (issue_url, issue_number) = response
                    issue_mapping.append((jira_issue_id(num), issue_url, issue_number))

    with open(issue_mapping_file, "a") as fp:
        for (jira_issue_id, issue_url, issue_number) in issue_mapping:
            fp.write(f"{jira_issue_id},{issue_url},{issue_number}\n")
    
    logger.info("Done.")