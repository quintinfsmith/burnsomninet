import os
from datetime import datetime
import time
import re
from sitecode.py.gitmanip import Project, FileNotFound

def process_not_found(_, **kwargs):
    return []


def process_android(project_name, **kwargs):
    project = Project(f"/srv/git/{project_name}")
    project_branch = project.get_branch("master")
    tags = project.get_tags()
    output = []
    version_code_patt = re.compile(r"versionCode\s(?P<versionCode>\d*)", re.S)
    for tag in tags:
        commit_id = project.get_tag_commit(tag).strip()
        gradle_content = project_branch.get_file_content(
            "app/build.gradle",
            commit_id
        )
        version_code = None
        for hit in version_code_patt.finditer(gradle_content):
            version_code = hit.group("versionCode")
            break

        if not version_code:
            continue

        commit = project_branch.get_commit(commit_id)

        if commit is None:
            continue
        try:
            changelog = project_branch.get_file_content(f"fastlane/metadata/android/en-US/changelogs/{version_code}.txt")
        except FileNotFound as e:
            changelog = ""
        entry = {
            "version_name": tag,
            "version_code": version_code,
            "timestamp": commit.date,
            "commit": commit_id,
            "changelog": changelog
        }

        if os.path.exists(f"/srv/http/content/release/{project_name}/{project_name}-{tag}.apk"):
            entry["apk"] = f"/content/release/{project_name}/{project_name}-{tag}.apk"

        output.append(entry)

    output = sorted(output, key=lambda entry: entry["timestamp"], reverse=True) 
    # -------------------------------------------- #

    return output

PROJECTS = {
    "pagan": process_android
}

def process_request(**kwargs):
    project_name = kwargs.get('project', None)
    return PROJECTS.get(project_name, process_not_found)(project_name, **kwargs)

