#
# Convert Jira issues to GitHub issues
# Usage:
#   python src/jira2github.py --min <min issue number> --max <max issue number>
#

import argparse
from pathlib import Path
import json
import logging
import sys

from common import JIRA_DUMP_DIRNAME, GITHUB_DATA_DIRNAME, ISSUE_TYPE_TO_LABEL_MAP, jira_issue_url, jira_dump_file, jira_issue_id, github_data_file, make_github_title

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


def convert_issue(num: int, dump_dir: Path, output_dir: Path) -> bool:
    jira_id = jira_issue_id(num)
    dump_file = jira_dump_file(dump_dir, num)
    if not dump_file.exists():
        logger.warning(f"Jira dump file not found: {dump_file}")
        return False

    with open(dump_file) as fp:
        o = json.load(fp)
        summary = __extract_summary(o).strip()
        description = __extract_description(o).strip()
        status = __extract_status(o)
        issue_type = __extract_issue_type(o)
        (reporter, reporter_dispname) = __extract_reporter(o)
        (assignee, assignee_dispname) = __extract_assignee(o)
        created = __extract_created(o)
        updated = __extract_updated(o)
        resolutiondate = __extract_resolutiondate(o)
        fix_versions = __extract_fixversions(o)

        body = f"""{description}

---
Original Jira: {jira_issue_url(num)}
Created: {created}
Updated: {updated}
Resolved: {resolutiondate}
Reporter: {reporter_dispname}
Assignee: {assignee_dispname}"""

        labels = []
        if issue_type and ISSUE_TYPE_TO_LABEL_MAP.get(issue_type):
            labels.append(ISSUE_TYPE_TO_LABEL_MAP.get(issue_type))
        # milestone?
        for v in fix_versions:
            if v:
                labels.append(f"version:{v}")

        data = {
            "title": make_github_title(summary, jira_id),
            "body": body,
            "labels": labels,
            "state": "closed" if status == "Closed" else "open"
        }

        data_file = github_data_file(output_dir, num)
        with open(data_file, "w") as fp:
            json.dump(data, fp, indent=2)

    return True


def __extract_summary(o: dict) -> str:
    return o.get("fields").get("summary", "")


def __extract_description(o: dict) -> str:
    return o.get("fields").get("description", "")


def __extract_status(o: dict) -> str:
    status = o.get("fields").get("status")
    return status.get("name", "") if status else ""


def __extract_issue_type(o: dict) -> str:
    issuetype = o.get("fields").get("issuetype")
    return issuetype.get("name", "") if issuetype else ""


def __extract_reporter(o: dict) -> tuple[str, str]:
    reporter = o.get("fields").get("reporter")
    key = reporter.get("key", "") if reporter else ""
    disp_name = reporter.get("displayName", "") if reporter else ""
    return (key, disp_name)


def __extract_assignee(o: dict) -> tuple[str, str]:
    assignee = o.get("fields").get("assignee")
    key = assignee.get("key", "") if assignee else ""
    disp_name = assignee.get("displayName", "") if assignee else ""
    return (key, disp_name)


def __extract_created(o: dict) -> str:
    return o.get("fields").get("created", "")


def __extract_updated(o: dict) -> str:
    return o.get("fields").get("updated", "")


def __extract_resolutiondate(o: dict) -> str:
    return o.get("fields").get("resolutiondate", "")


def __extract_fixversions(o: dict) -> list[str]:
    return [x.get("name", "") for x in o.get("fields").get("fixVersions", [])]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min', type=int, dest='min', required=False, default=1, help='Minimum Jira issue number to be converted')
    parser.add_argument('--max', type=int, dest='max', required=False, help='Maximum Jira issue number to be converted')
    args = parser.parse_args()

    dump_dir = Path(__file__).resolve().parent.parent.joinpath(JIRA_DUMP_DIRNAME)
    if not dump_dir.exists():
        logger.error(f"Jira dump dir not exists: {dump_dir}")
        sys.exit(1)
    

    output_dir = Path(__file__).resolve().parent.parent.joinpath(GITHUB_DATA_DIRNAME)
    if not output_dir.exists():
        output_dir.mkdir()
    assert output_dir.exists()

    if not args.max:
        logger.info(f"Converting Jira issue {args.min} to GitHub issue in {output_dir}")
        convert_issue(args.min, dump_dir, output_dir)
    else:
        logger.info(f"Converting Jira issues {args.min} to {args.max} in {output_dir}")
        for num in range(args.min, args.max + 1):
            convert_issue(num, dump_dir, output_dir)

