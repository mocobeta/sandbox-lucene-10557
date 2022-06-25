import sys, os
from github_issues_util import check_import_status, check_authentication


github_token = os.getenv("GITHUB_PAT")
if not github_token:
    print("Please set your GitHub token to GITHUB_PAT environment variable.")
    sys.exit(1)
github_repo = os.getenv("GITHUB_REPO")
if not github_repo:
    print("Please set GitHub repo location to GITHUB_REPO environment varialbe.")
    sys.exit(1)
check_authentication(github_token)

issue_num = sys.argv[1]
check_import_status(github_token, github_repo, issue_num)

