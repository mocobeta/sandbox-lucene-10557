#
# Create local dump of Jira issues 
# Usage:
#   python src/download_jira.py --min <min issue number> --max <max issue number>
#

import argparse
from pathlib import Path
import json
import logging
import time

import requests

from .common import JIRA_DUMP_DIRNAME, jira_dump_file, jira_issue_id

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)

DOWNLOAD_INTERVAL_SEC = 0.5


def issue_uri(issue_id: str) -> str:
    return f"https://issues.apache.org/jira/rest/api/latest/issue/{issue_id}"


def dowload_issue(num: int, dump_dir: Path) -> bool:
    issue_id = jira_issue_id(num)
    uri = issue_uri(issue_id)
    res = requests.get(uri)
    if res.status_code != 200:
        logger.warning(f"Can't download {issue_id}. status code={res.status_code}, message={res.text}")
        return False
    dump_file = jira_dump_file(dump_dir, num)
    with open(dump_file, "w") as fp:
        json.dump(res.json(), fp, indent=2)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min', type=int, dest='min', required=False, default=1, help='Minimum Jira issue number to be donloaded')
    parser.add_argument('--max', type=int, dest='max', required=False, help='Maximum Jira issue number to be donloaded')
    args = parser.parse_args()

    dump_dir = Path(__file__).resolve().parent.parent.joinpath(JIRA_DUMP_DIRNAME)
    if not dump_dir.exists():
        dump_dir.mkdir()
    assert dump_dir.exists()

    if not args.max:
        logger.info(f"Downloading Jira issue {args.min} in {dump_dir}")
        dowload_issue(args.min, dump_dir)
    else:
        logger.info(f"Downloading Jira issues {args.min} to {args.max} in {dump_dir}")
        for num in range(args.min, args.max + 1):
            dowload_issue(num, dump_dir)
            time.sleep(DOWNLOAD_INTERVAL_SEC)
    
    logger.info("Done.")
    

    
