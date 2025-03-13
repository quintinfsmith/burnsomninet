from sitecode.py.gitmanip import Project as GitProject
import json
from datetime import datetime
import time

def process_request(**kwargs):
    project_name = kwargs.get("project", None)
    # TODO
    # if project_name is None:
    #     raise HTTP404()

    project = GitProject(project_name)
    branch_name = kwargs.get("branch", "master")
    branch = project.get_branch(branch_name)

    filelist = branch.get_filelist("")
    commits = {}
    output_tree = {
        "_i": {},
        "name": "",
        "folders": [],
        "files": []
    }

    # offset = len(path)
    for file_path, commit_id in filelist:
        parts = file_path.split("/")
        if commit_id not in commits:
            commit = branch.get_commit(commit_id)
            commits[commit_id] = {
                "id": commit_id, 
                "description": commit.get_description(),
                "date": commit.date.timestamp()
            }
        stack = [(output_tree, parts)]
        while stack:
            working_tree, working_parts = stack.pop(0)
            if len(working_parts) > 0:
                next_node = working_parts[0]
                if next_node in working_tree["_i"].keys():
                    index = working_tree["_i"][next_node]
                else:
                    if len(working_parts) == 1:
                        working_tree["files"].append({
                            "name": next_node, 
                            "commit": commit_id,
                        })
                        continue


                    index = len(working_tree["folders"])
                    working_tree["folders"].append({
                        "name": [working_parts[0]],
                        "_i": {},
                        "folders": [],
                        "files": []
                    })
                    working_tree["_i"][next_node] = index
                
                stack.append((working_tree["folders"][index], working_parts[1:]))

    stack = [output_tree]
    while stack:
        working_tree = stack.pop(0)
        for subtree in working_tree["folders"]:
            stack.append(subtree)
        del working_tree["_i"]


    return {
        "branch": branch_name,
        "tree": output_tree,
        "commits": commits
    }