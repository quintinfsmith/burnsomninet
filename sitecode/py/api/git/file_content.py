from sitecode.py.gitmanip import Project as GitProject
import json
from datetime import datetime
import time
import marko

def process_request(**kwargs):
    project_name = kwargs.get("project", None)
    if project_name is None:
        raise FileNotFoundError()

    content_type = kwargs.get("fmt", "md")
    project = GitProject(f"/srv/git/{project_name}")

    branch_names = project.get_branch_names()

    branch_name = kwargs.get("branch", "master")
    if branch_name not in branch_names:
        raise FileNotFoundError()

    path = kwargs.get("path", None)
    if path is None:
        raise FileNotFoundError()


    branch = project.get_branch(branch_name)

    active_commit = kwargs.get("commit", None)

    success = False
    try:
        readme_content = branch.get_file_content(path, active_commit)
        success = True
        if content_type == "md":
            readme_content = marko.convert(readme_content)
    except UnicodeDecodeError:
        readme_content = ""

    return {
        "success": success,
        "c": readme_content
    }
