#
# Update GitHub issue contents and comments
# Usage:
#   python src/update_github_issues.py --min <min issue number> --max <max issue number>
#

import os
import sys
import logging
import json
from pathlib import Path

from github_issues_util import *
from common import GITHUB_DATA_DIRNAME, MAPPINGS_DATA_DIRNAME, ISSUE_MAPPING_FILENAME, github_data_file

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


def update_issue_content(issue_number: int, data_file: Path, token: str, repo: str) -> bool:
    if not data_file.exists():
        logger.warning(f"GitHub data file not found: {data_file}")
        return False
    
    issue = None
    with open(data_file) as fp:
        o = json.load(fp)
        issue = GHIssue(title=o["title"], body=o["body"], state=o["state"], labels=o["labels"])
    return update_issue(token, repo, issue_number, issue)


def create_issue_comments(issue_number: int, data_file: Path, token: str, repo: str) -> bool:
    if not data_file.exists():
        logger.warning(f"GitHub data file not found: {data_file}")
        return False
    res = True
    with open(data_file) as fp:
        o = json.load(fp)
        if "comments" not in o:
            return False
        for (i, c) in enumerate(o["comments"]):
            if i >= 10:
                break
            comment = GHIssueComment(body=c["body"])
            success = create_comment(token, repo, issue_number, comment)
            if res:
                res = success
    return res


if __name__ == "__main__":
    github_token = os.getenv("GITHUB_PAT")
    if not github_token:
        print("Please set your GitHub token to GITHUB_PAT environment variable.")
        sys.exit(1)
    github_repo = os.getenv("GITHUB_REPO")
    if not github_repo:
        print("Please set GitHub repo location to GITHUB_REPO environment varialbe.")
        sys.exit(1)

    check_authentication(github_token)

    mappings_dir = Path(__file__).resolve().parent.parent.joinpath(MAPPINGS_DATA_DIRNAME)
    issue_mapping_file = mappings_dir.joinpath(ISSUE_MAPPING_FILENAME)
    if not issue_mapping_file.exists():
        logger.error(f"Issue mapping file not found {issue_mapping_file}.")
        sys.exit(1)
    
    data_dir = Path(__file__).resolve().parent.parent.joinpath(GITHUB_DATA_DIRNAME)
    if not data_dir.exists():
        logger.error(f"GitHub data dir not exists {data_dir}")
        sys.exit(1)
    
    with open(issue_mapping_file) as fp:
        fp.readline()  # skip header
        for line in fp:
            cols = line.strip().split(",")
            if len(cols) < 3:
                continue
            (jira_issue_number, gh_issue_number) = (cols[0][7:], cols[2])
            data_file = github_data_file(data_dir, int(jira_issue_number))
            update_issue_content(int(gh_issue_number), data_file, github_token, github_repo)
            #if update_issue_content(int(gh_issue_number), data_file, github_token, github_repo):
                #create_issue_comments(int(gh_issue_number), data_file, github_token, github_repo)

    logger.info("Done.")