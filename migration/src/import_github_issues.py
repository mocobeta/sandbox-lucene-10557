import argparse
from pathlib import Path
import json
import logging
import sys
import os

from common import GITHUB_IMPORT_DATA_DIRNAME, github_data_file
from github_issues_util import *

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


def import_issue_with_comments(num: int, data_dir: Path, token: str, repo: str):
    data_file = github_data_file(data_dir, num)
    assert data_file.exists()
    with open(data_file) as fp:
        issue_data = json.load(fp)
        import_issue(token, repo, issue_data)


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

    parser = argparse.ArgumentParser()
    parser.add_argument('--min', type=int, dest='min', required=False, default=1, help='Minimum Jira issue number to be converted')
    parser.add_argument('--max', type=int, dest='max', required=False, help='Maximum Jira issue number to be converted')
    args = parser.parse_args()

    github_data_dir = Path(__file__).resolve().parent.parent.joinpath(GITHUB_IMPORT_DATA_DIRNAME)
    if not github_data_dir.exists():
        logger.error(f"GitHub data dir not exists. {github_data_dir}")
        sys.exit(1)
    
    min = args.min
    max = args.max if args.max else args.min

    logger.info(f"Importing GitHub issues {args.min} to {args.max} in {github_data_dir}")
    for num in range(min, max + 1):
        import_issue_with_comments(num, github_data_dir, github_token, github_repo)
