from sitecode.py.gitmanip import Project
import json
from datetime import datetime
import time

def process_request(**kwargs):
    # -------------------------------------------- #
    date_from = float(kwargs.get("datefrom", 0))
    date_to = float(kwargs.get("dateto", time.time()))

    project_name = kwargs.get("project", "")
    project_branch = kwargs.get("branch", "master")

    fields = kwargs.get("fields", "date,description,id,author")
    fields = set(fields.split(","))
    get_all_branches = kwargs.get("all_branches", False)
    # -------------------------------------------- #

    project = Project(f"/srv/git/{project_name}")
    all_project_branches = project.get_branch_names()

    if project_branch not in all_project_branches:
        project_branch = "master"

    if get_all_branches:
        project_branches = all_project_branches
    else:
        project_branches = [project_branch]

    mapped_commits = {}
    for branch_name in project_branches:
        branch  = project.get_branch(branch_name)
        commits = branch.get_commits()

        for commit in commits:
            timestamp = commit.get_timestamp()
            if timestamp < date_from or timestamp >= date_to:
                continue

            commit_id = commit.get_id()

            if commit_id in mapped_commits.keys():
                mapped_commits[commit_id]["branches"].append(branch_name)
            else:
                simple_commit = {
                    "branches": [branch_name]
                }

                if "date" in fields:
                    simple_commit['date'] = timestamp
                if "description" in fields:
                    simple_commit['description'] = commit.get_description()
                if "id" in fields:
                    simple_commit['id'] = commit_id

                if "author" in fields:
                    simple_commit['author'] = commit.get_author_email()
                mapped_commits[commit_id] = simple_commit
    # -------------------------------------------- #
    output = []
    for _i, commit in mapped_commits.items():
        output.append(commit)

    return output

