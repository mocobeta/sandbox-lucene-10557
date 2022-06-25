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


from common import JIRA_DUMP_DIRNAME, GITHUB_DATA_DIRNAME, MAPPINGS_DATA_DIRNAME, ISSUE_MAPPING_FILENAME, ACCOUNT_MAPPING_FILENAME, ISSUE_TYPE_TO_LABEL_MAP, COMPONENT_TO_LABEL_MAP, \
    jira_issue_url, jira_dump_file, jira_issue_id, github_data_file, make_github_title, read_issue_id_map, read_account_map
from jira_util import *

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)


def convert_issue(num: int, dump_dir: Path, output_dir: Path, issue_id_map: dict[str, str], account_map: dict[str, str]) -> bool:
    jira_id = jira_issue_id(num)
    dump_file = jira_dump_file(dump_dir, num)
    if not dump_file.exists():
        logger.warning(f"Jira dump file not found: {dump_file}")
        return False

    with open(dump_file) as fp:
        o = json.load(fp)
        summary = extract_summary(o).strip()
        description = extract_description(o).strip()
        status = extract_status(o)
        issue_type = extract_issue_type(o)
        (reporter_name, reporter_dispname) = extract_reporter(o)
        (assignee_name, assignee_dispname) = extract_assignee(o)
        created = extract_created(o)
        updated = extract_updated(o)
        resolutiondate = extract_resolutiondate(o)
        fix_versions = extract_fixversions(o)
        versions = extract_versions(o)
        components = extract_components(o)
        linked_issues = extract_issue_links(o)
        subtasks = extract_subtasks(o)
        pull_requests =extract_pull_requests(o)

        reporter_gh = account_map.get(reporter_name)
        reporter = f"{reporter_dispname} (`{reporter_gh}`)" if reporter_gh else f"{reporter_dispname}"
        assignee_gh = account_map.get(assignee_name)
        assignee = f"{assignee_dispname} (`{assignee_gh}`)" if assignee_gh else f"{assignee_dispname}"

        # embed github issue number next to linked issue keys
        linked_issues_with_gh_links = []
        for jira_key in linked_issues:
            num_gh = issue_id_map.get(jira_key)
            linked_issues_with_gh_links.append(f"- {jira_key}\n" if not num_gh else f"- {jira_key} (#{num_gh})\n")
        
        # embed github issue number next to sub task keys
        subtasks_with_gh_links = []
        for jira_key in subtasks:
            num_gh = issue_id_map.get(jira_key)
            subtasks_with_gh_links.append(f"- {jira_key}\n" if not num_gh else f"- {jira_key} (#{num_gh})\n")
        
        # make pull requests list
        pull_requests_list = [f"- {x}\n" for x in pull_requests]

        body = f"""{convert_text(description, issue_id_map)}

---
### Jira information

Original Jira: {jira_issue_url(num)}
Reporter: {reporter}
Assignee: {assignee}
Created: {created}
Updated: {updated}
Resolved: {resolutiondate}

Issue Links:
{"".join(linked_issues_with_gh_links)}
Sub-Tasks:
{"".join(subtasks_with_gh_links)}

Pull Requests:
{"".join(pull_requests_list)}
"""

        def comment_author(author_name, author_dispname):
            author_gh = account_map.get(author_name)
            return f"{author_dispname} (`{author_gh}`)" if author_gh else author_dispname
        
        comments = extract_comments(o)
        comments_data = [{"body":  f"""{convert_text(x[2], issue_id_map)}

Author: {comment_author(x[0], x[1])}
Created: {x[3]}
Updated: {x[4]}        
        """} for x in comments]

        labels = []
        if issue_type and ISSUE_TYPE_TO_LABEL_MAP.get(issue_type):
            labels.append(ISSUE_TYPE_TO_LABEL_MAP.get(issue_type))
        # milestone?
        for v in fix_versions:
            if v:
                labels.append(f"fixVersion:{v}")
        for v in versions:
            if v:
                labels.append(f"affectsVersion:{v}")
        for c in components:
            if c.startswith("core"):
                labels.append(f"component:module/{c}")
            elif c in COMPONENT_TO_LABEL_MAP:
                labels.append(COMPONENT_TO_LABEL_MAP.get(c))

        data = {
            "title": make_github_title(summary, jira_id),
            "body": body,
            "labels": labels,
            "state": "closed" if status in ["Closed", "Resolved"] else "open",
            "comments": comments_data
        }

        data_file = github_data_file(output_dir, num)
        with open(data_file, "w") as fp:
            json.dump(data, fp, indent=2)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min', type=int, dest='min', required=False, default=1, help='Minimum Jira issue number to be converted')
    parser.add_argument('--max', type=int, dest='max', required=False, help='Maximum Jira issue number to be converted')
    args = parser.parse_args()

    dump_dir = Path(__file__).resolve().parent.parent.joinpath(JIRA_DUMP_DIRNAME)
    if not dump_dir.exists():
        logger.error(f"Jira dump dir not exists: {dump_dir}")
        sys.exit(1)

    mappings_dir = Path(__file__).resolve().parent.parent.joinpath(MAPPINGS_DATA_DIRNAME)
    account_mapping_file = mappings_dir.joinpath(ACCOUNT_MAPPING_FILENAME)
    issue_mapping_file = mappings_dir.joinpath(ISSUE_MAPPING_FILENAME)
    if not issue_mapping_file.exists():
        logger.error(f"Issue mapping file not found {issue_mapping_file}.")
        sys.exit(1)

    output_dir = Path(__file__).resolve().parent.parent.joinpath(GITHUB_DATA_DIRNAME)
    if not output_dir.exists():
        output_dir.mkdir()
    assert output_dir.exists()

    account_map = read_account_map(account_mapping_file) if account_mapping_file else {}
    issue_id_map = read_issue_id_map(issue_mapping_file)
    if not args.max:
        logger.info(f"Converting Jira issue {args.min} to GitHub issue in {output_dir}")
        convert_issue(args.min, dump_dir, output_dir, issue_id_map, account_map)
    else:
        logger.info(f"Converting Jira issues {args.min} to {args.max} in {output_dir}")
        for num in range(args.min, args.max + 1):
            convert_issue(num, dump_dir, output_dir, issue_id_map, account_map)

