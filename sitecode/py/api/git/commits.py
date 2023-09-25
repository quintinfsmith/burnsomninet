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
    # -------------------------------------------- #
    project = Project(f"/srv/git/{project_name}")
    if project_branch == "*":
        project_branches = project.get_branch_names()
    else:
        project_branches = [project_branch]

    output = []
    for branch_name in project_branches:
        branch  = project.get_branch(branch_name)
        commits = branch.get_commits()

        for commit in commits:
            timestamp = commit.get_timestamp()
            if timestamp < date_from or timestamp >= date_to:
                continue

            simple_commit = {}
            if "date" in fields:
                simple_commit['date'] = timestamp
            if "description" in fields:
                simple_commit['description'] = commit.get_description()
            if "id" in fields:
                simple_commit['id'] = commit.get_id()

            if "author" in fields:
                simple_commit['author'] = commit.get_author_email()

            output.append(simple_commit)
    # -------------------------------------------- #

    return output

