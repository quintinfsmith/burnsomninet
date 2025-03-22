from sitecode.py.gitmanip import Project
from sitecode.py.cachemanager import get_cached, check_cache, update_cache
from sitecode.py import api
from burnsomninet.views import GIT_PATH
import json
from datetime import datetime, timedelta
import time, os

def process_request(**kwargs):
    private_projects = set()
    repositories = os.listdir(GIT_PATH)
    repositories.sort()

    working_repositories = []
    for path in repositories:
        if not os.path.isfile(f"{GIT_PATH}/{path}/git-daemon-export-ok") and path not in ("burnsomninet", "bon_angular"):
            private_projects.add(path)
        working_repositories.append(path)
    repositories = working_repositories

    all_commits = []
    now = datetime.now()
    from_date = kwargs.get("datefrom", None)
    if from_date is None:
        from_date = datetime(year=now.year - 1, month=now.month, day=now.day) - timedelta(days=1)
    else:
        from_date = datetime.fromtimestamp(int(from_date))

    for project in repositories:
        cache_key = f"INDEX_GIT_{project}"
        needs_update = check_cache(
            cache_key,
            f"{GIT_PATH}/{project}"
        )

        if not needs_update:
            working_commits = json.loads(get_cached(cache_key)[0])
        else:
            working_commits = api.handle(
                'git',
                'commits',
                project=project,
                datefrom=from_date.timestamp(),
                branch="master",
                all_branches=True
            )

            if project in private_projects:
                project_alias = "a private project"
            else:
                project_alias = project

            for i, _commit in enumerate(working_commits):
                working_commits[i]['group'] = project_alias

            update_cache(cache_key, json.dumps(working_commits))

        all_commits.extend(working_commits)

    return all_commits
