# [WIP] Migration tools (Jira issue -> GitHub issue)

## Setup

You need Python 3.9+. The scripts were tested on Linux; maybe works also on Mac and Windows (not tested).

```
python -V
Python 3.9.13

# install dependencies
python -m venv .venv
source .venv/bin/activate
(.venv) pip install -r requirements.txt
```

You need a GitHub repository and personal access token for testing. Set `GITHUB_PAT` and `GITHUB_REPO` environment variables.

```
export GITHUB_PAT=<your token>
export GITHUB_REPO=<your repository location> # e.g. "mocobeta/sandbox-lucene-10557"
```

## Usage

### 1. Download Jira issues and attachments

`src/download_jira.py` downloads Jira issues and dumps them as JSON files in `migration/jira-dump`.

```
# Download issues (specify minimum and maximum issue numbers)
(.venv) migration $ python src/download_jira.py --min 10550 --max 10555
[2022-06-21 22:23:21,872] INFO:download_jira: Downloading Jira issues 10550 to 10555 in /mnt/hdd/repo/sandbox-lucene-10557/migration/jira-dump
[2022-06-21 22:23:24,956] INFO:download_jira: Downloading attachment LUCENE-10551-test.patch
[2022-06-21 22:23:32,061] INFO:download_jira: Done.

(.venv) migration $ ls jira-dump/
LUCENE-10550.json  LUCENE-10551.json  LUCENE-10552.json  LUCENE-10553.json  LUCENE-10554.json  LUCENE-10555.json
```

### 2. Create (initialize) GitHub issues

First pass: `src/create_github_issues.py` initializes GitHub issues and writes Jira issue ID and GitHub issue number mapping to a file in `migration/mappings-data`.

```
# Create issues (specify minimum and maximum issue numbers)
(.venv) migration $ python src/create_github_issues.py --min 1000 --max 1010
[2022-06-19 22:36:03,662] INFO:create_github_issues: Initializing GitHub issues for Jira issues 1000 to 1010
[2022-06-19 22:36:04,166] INFO:github_issues_util: Issue https://github.com/mocobeta/migration-test-1/issues/12 was successfully created.
[2022-06-19 22:36:04,631] INFO:github_issues_util: Issue https://github.com/mocobeta/migration-test-1/issues/13 was successfully created.
[2022-06-19 22:36:05,228] INFO:github_issues_util: Issue https://github.com/mocobeta/migration-test-1/issues/14 was successfully created.
...

(.venv) migration $ cat mappings-data/issue-map.csv
JiraKey,GitHubUrl,GitHubNumber
LUCENE-1000,https://github.com/mocobeta/migration-test-1/issues/12,12
LUCENE-1001,https://github.com/mocobeta/migration-test-1/issues/13,13
LUCENE-1002,https://github.com/mocobeta/migration-test-1/issues/14,14
LUCENE-1003,https://github.com/mocobeta/migration-test-1/issues/15,15
...
```

### 3. Convert Jira issues to GitHub issues

`src/jira2github.py` converts Jira issues to GitHub issues and dumps them to JSON files in `migration/github-data`. 
Also this resolves all neccesarry mappings using mapping files (cross-issue links, account ids, etc.)

```
# Convert issues (specify minimum and maximum issue numbers)
(.venv) migration $ python src/jira2github.py --min 1000 --max 1010
[2022-06-19 23:59:12,349] INFO:jira2github: Converting Jira issues 1000 to 1010 in /mnt/hdd/repo/sandbox-lucene-10557/migration/github-data

(.venv) migration $ ls github-data/
GH-LUCENE-1000.json  GH-LUCENE-1002.json  GH-LUCENE-1004.json  GH-LUCENE-1006.json  GH-LUCENE-1008.json  GH-LUCENE-1010.json
GH-LUCENE-1001.json  GH-LUCENE-1003.json  GH-LUCENE-1005.json  GH-LUCENE-1007.json  GH-LUCENE-1009.json  
```

### 4. Update GitHub issues and comments

Second pass: `src/update_github_issues.py` updates GitHub issues with previously created issue mapping and data files.

```
# Update issues and comments

(.venv) migration $ python src/update_github_issues.py 
[2022-06-20 00:44:31,638] INFO:github_issues_util: Issue #12 was successfully updated.
[2022-06-20 00:44:32,356] INFO:github_issues_util: Issue #13 was successfully updated.
[2022-06-20 00:44:33,415] INFO:github_issues_util: Issue #14 was successfully updated.
[2022-06-20 00:44:34,039] INFO:github_issues_util: Issue #15 was successfully updated.
[2022-06-20 00:44:34,734] INFO:github_issues_util: Issue #16 was successfully updated.
...
```

## Already implemented things

You can:

* migrate all issue description and comment texts to GitHub; browsing/searching old issues should work fine.
  * this would take many hours (days?) due to the severe API call rate limit.
* map Jira cross-issue link "LUCENE-xxx" to GitHub issue mention "#yyy".
* extract every issue metadata from Jira and port it to labels or issue description (as plain text).
* convert Jira markups to Markdown with parser library.
  * not perfect - there can be many conversion errors


## Limitations

You cannot:

* simulate original issue reporters and comment authors; they have to be preserved in free-text forms.
* simulate original created / updated timestamps; they have to be preserved in free-text forms.
* migrate attached files (pathces, images, etc.) to GitHub; thoese have to ramain in Jira.
  * it's not allowed to programatically upload files and attach them to issues.
* create hyperlinks from issues to GitHub accounts (reporters, comment authors, etc.) by mentions; otherwise everyone will receive huge volume of notifications.
  * still accounts can be noted with a markup `@xxxx` (without mentioing)