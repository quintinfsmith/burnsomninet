import json, os
from sitecode.py.httree import Tag, Text, RawHTML
from django.conf import settings
from sitecode.py.gitmanip import Project as GitProject
from typing import Optional, Tuple, List, Dict
from urllib.parse import urlencode
from datetime import datetime, timedelta
from sitecode.py.cachemanager import check_cache, get_cached, update_cache

SITECODE = settings.SITECODE
STATIC_PATH = settings.STATIC_PATH
BASE_DIR = settings.BASE_DIR
COMMIT_ID = settings.COMMIT_ID
GIT_PATH = "/srv/git"

VH_TOP = Tag('div', { "class": "vh_top" })
VH_BOT = Tag('div', { "class": "vh_bot" })
VH_MID = Tag('div', { "class": "vh_mid" })

def relative_vague_date(date):
    now = datetime.now()
    delta = now - date
    output = ""
    if delta < timedelta(seconds=120):
        output = "Just now"
    elif delta < timedelta(minutes=120):
        output = f"{round(delta.seconds / 60)} minutes ago"
    elif delta < timedelta(hours=48):
        output = f"{round(delta.seconds / (60 * 60))} hours ago"
    elif delta < timedelta(days=7):
        output = f"{delta.days} days ago"
    elif delta < timedelta(days=11):
        output = f"A week ago"
    elif delta < timedelta(weeks=4, days=6):
        output = f"{round(delta.days / 7)} weeks ago"
    elif delta < timedelta(weeks=6):
        output = f"A month ago"
    elif delta < timedelta(weeks=52 + 27):
        output = f"{round(delta.days / 30)} months ago"
    else:
        year_count = round(delta.days / 365.25)
        output = f"{year_count} years ago"
    return output

def build_head(**kwargs):
    title = ""
    if "title" in kwargs:
        title = kwargs["title"]

    return Tag("head",
        Tag("title", title),
        Tag("link", {
            "rel": "stylesheet",
            "type": "text/css",
            "href": f"/style.css?commit={COMMIT_ID}"
        }),
        Tag("link", {
            "rel": "stylesheet",
            "type": "text/css",
            "href": "/content/style/prism.css"
        }),
        Tag("script", {
            "src": "/content/javascript/crel.js",
            "type": "text/javascript"
        }),
        Tag("script", {
            "src": f"/javascript/main.js?commit={COMMIT_ID}",
            "type": "text/javascript"
        }),
        Tag("meta", {
            "name": "viewport",
            "content": "initial-scale=1.0"
        }),
        Tag("script", {
            "src": "/content/javascript/prism.js",
            "type": "text/javascript"
        })
    )

def build_sitemap(*active_path):
    classname = "sitemap"
    if active_path:
        classname += " " + active_path[0]

    sitemap = Tag("div", { "class": classname })
    sitemap_sub = Tag("div")
    sitemap.append(sitemap_sub)
    svg_content = ""
    with open(f"{STATIC_PATH}/logo.svg", "r") as fp:
        svg_content = fp.read()
    sitemap_sub.append(
        Tag("div",
            { "class": "logo" },
            Tag("div"),
            Tag("a",
                { "href": "/" },
                RawHTML(svg_content)
            ),
            Tag("div")
        )
    )
    sitemap_sub.append(
        Tag("div",
            { "class": "hamburger-wrapper" },
            Tag("div",
                { "class": "hamburger" },
                Tag("div",
                    Tag("div"),
                    Tag("div"),
                    Tag("div"),
                    Tag("div"),
                    Tag("div")
                )
            ),
            Tag("script", {
                "src": f"/javascript/hamburger.js?commit={COMMIT_ID}",
                "type": "text/javascript"
            })
        )
    )

    subsitemap = Tag("div", { "class": "treemap" })
    #------------------------------------------#
    repositories = os.listdir(GIT_PATH)
    repositories.sort()
    working_repositories = []
    for path in repositories:
        if os.path.isfile(f"{GIT_PATH}/{path}/git-daemon-export-ok"):
            working_repositories.append(path)
    repositories = working_repositories


    entry = Tag("div", { "class": "entry" })
    for i, repo in enumerate(repositories):
        classname = "item"
        if ('project', repo) == active_path:
            classname += " active"

        entry.append(
            Tag('a',
                {
                    'class': classname,
                    'href': f"/project/{repo}"
                },
                VH_MID,
                Tag('div', repo)
            )
        )

    subsitemap.append(
        Tag("div",
            Tag('div',
                { 'class': 'header' },
                VH_MID,
                Tag('div', 'Repositories')
            ),
            entry
        )
    )

    #------------------------------------------#
    sectionsdir = f"{SITECODE}/sections/"

    headings = os.listdir(sectionsdir)
    headings.sort()

    for i, heading in enumerate(headings):
        entry = Tag("div", { "class": "entry" })
        files = os.listdir(sectionsdir + heading)
        files.sort()
        for f in files:
            title = f[0:f.rfind(".")]
            alias = title
            if f[f.rfind('.') + 1:] == "json":
                with open(f"{sectionsdir}{heading}/{f}", "r") as fp:
                    prefs = json.loads(fp.read())
                    alias = prefs.get('alias', title)

            classname = "item"
            if (heading, title) == active_path:
                classname += " active"

            entry.append(
                Tag('a',
                    {
                        'class': classname,
                        'href': f"/{heading}/{title}"
                    },
                    VH_MID,
                    Tag('div', alias.title())
                )
            )

        subsitemap.append(
            Tag("div",
                Tag('div',
                    { 'class': 'header' },
                    VH_MID,
                    Tag('div', heading.title())
                ),
                entry
            )
        )

    sitemap_sub.append(subsitemap)
    return sitemap

def media_content(mediamap):
    output = Tag("div",
        { "class": "media" }
    )
    src = mediamap["src"]
    media_path = f"{STATIC_PATH}/{src}/"
    for directory in os.listdir(media_path):
        section_path = f"{media_path}/{directory}/"
        sources = []
        for filename in os.listdir(section_path):
            ext = filename[filename.rfind(".") + 1:]
            if ext == "jpg":
                continue
            if not os.path.isfile(f"{section_path}{filename}.jpg"):
                os.system(f"ffmpeg -i \"{section_path}{filename}\" -ss 00:00:00 -vframes 1 \"{section_path}{filename}.jpg\"")
            sources.append(f"/content/{src}/{directory}/{filename}")
        # Create screenshots
        title = directory.capitalize()

        output.append(
            Tag("div",
                {},
                VH_MID,
                Tag("div",
                    {
                        "id": title.replace(" ", "_").lower(),
                        "class": "polaroid",
                        "data-srcs": json.dumps(sources)
                    },
                    Tag("div",
                        Tag("img", {
                            "src": sources[0] + ".jpg",
                        })
                    ),
                    Tag("div",
                        { 'class': 'label-wrapper' },
                        Tag("div",
                            { 'class': 'label' },
                            VH_MID,
                            Tag("div", title)
                        )
                    )
                )
            )
        )

    output.append(
        Tag("script", {
            "src": "/javascript/media.js",
            "type": "text/javascript"
        })
    )

    return output

def build_git_branch_select(project_name, active_branch_name: Optional[str]=None) -> Tag:
    if active_branch_name is None:
        active_branch_name = 'master'

    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch_names = git_project.get_branch_names()
    branch_names = sorted(branch_names, key=lambda x: int(x != "master"))

    if len(branch_names) > 1:
        output = slug_tag(
            '/javascript/git.js',
            'GitBranchSelect',
            branches=branch_names,
            active=active_branch_name,
            project=project_name
        )
    else:
        output = None

    return output

def build_git_commit_select(project_name, branch_name: str, active_commit: Optional[str]=None, active_path="") -> Tag:
    from sitecode.py.api.git.commits import process_request
    commits = process_request(
        project=project_name,
        branch=branch_name
    )

    output = None
    if len(commits) > 1:
        output = slug_tag(
            '/javascript/git.js',
            'GitCommitSelect',
            path=active_path,
            project=project_name,
            branch=branch_name,
            commits=commits,
            active=active_commit
        )

    return output

def build_git_path_navigator(branch_name: str, active_commit: Optional[str], path: str =""):
    query_attrs = {
        "branch": branch_name
    }
    if active_commit is not None:
        query_attrs['commit'] = active_commit

    tag_nav_path = Tag("div",
        { "class": "breadcrumb-nav" },
        Tag("a",
            { "href": "?" + urlencode(query_attrs) },
            "root"
        )
    )

    path_chunks = path.split("/")
    while "" in path_chunks:
        path_chunks.remove("")

    for i, chunk in enumerate(path_chunks):
        href_path = "/".join(path_chunks[0:i + 1]) + "/"
        query_attrs['path'] = href_path
        tag_nav_path.append(
            Tag("span", "/")
        )
        tag_nav_path.append(
            Tag("a",
                { "href": "?" + urlencode(query_attrs) },
                f"{chunk}"
            )
        )

    return tag_nav_path

def is_leap_year(year):
    try:
        datetime(year=year, month=2, day=29)
        return True
    except ValueError:
        return False

def build_git_overview(request, project_name: str, branch_name: str, active_commit: Optional[str], path: str = ""):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)

    query_attrs = {
        "branch": branch_name
    }
    if active_commit is not None:
        query_attrs['commit'] = active_commit

    file_table = Tag("table",
        { "class": "files-table" },
        Tag("tr",
            Tag("th",
                {"colspan": 2},
                build_git_path_navigator(branch_name, active_commit, path)
            ),
            Tag("th",
                "Last Updated"
            )
        )
    )

    filelist = branch.get_filelist(path, active_commit)
    sorter_list = []
    max_commit_ids = {}

    offset = len(path)
    for file_path, commit_id in filelist:
        file_path = file_path[offset:]
        parts = file_path.split("/")
        commit = branch.get_commit(commit_id)
        endpoint = parts[0].strip()
        if endpoint not in max_commit_ids or commit.date > max_commit_ids[endpoint][1]:
            max_commit_ids[endpoint] = (commit_id, commit.date, len(parts) == 1)

    for endpoint, (commit_id, commit_date, is_file) in max_commit_ids.items():
        commit = branch.get_commit(commit_id)
        sorter_list.append((is_file, endpoint, commit_id, commit.get_description(), commit_date))

    sorter_list.sort()
    for is_file, pathname, commit_id, description, commit_date in sorter_list:
        full_path = path + pathname

        icon = ""
        if not is_file:
            full_path += "/"
            icon_path = f"{STATIC_PATH}/dir-icon.svg"
            with open(icon_path, 'r') as fp:
                icon = RawHTML(fp.read())

        commit_query_attrs = {
            "commit": commit_id,
            "branch": branch_name
        }

        query_attrs['path'] = full_path
        file_table.append(
            Tag("tr",
                Tag("td",
                    Tag("a",
                        {
                            "class": "pathlink",
                            "href": f"/project/{project_name}?" + urlencode(query_attrs)
                        },
                        VH_MID,
                        Tag("span",
                            { "class": "icon-svg" },
                            icon
                        ),
                        Tag("span", pathname)
                    )
                ),
                Tag("td",
                    { 'title': commit_id, "class": "description" },
                    description
                ),
                Tag("td",
                    Tag("a",
                        { "href": f"?" + urlencode(commit_query_attrs) },
                        relative_vague_date(commit_date)
                    )
                )
            )
        )

    host = request.get_host()
    if ":" in host:
        host = host[0:host.rfind(":")]


    body_content = Tag("div",
        { "class": "git-overview" },
        Tag("div",
            Tag("div",
                { "class": "option-row" },
                Tag("div",
                    VH_MID,
                    slug_tag('/javascript/git.js', 'CloneButtonWidget', project = project_name)
                ),
                Tag("div",
                    Tag("div",
                        VH_MID,
                        build_git_branch_select(project_name, branch_name)
                    ),
                    Tag("div",
                        VH_MID,
                        build_git_commit_select(project_name, branch_name, active_commit, path)
                    )
                )
            ),
            Tag("div",
                { "class": "files-wrapper" },
                file_table
            )
        )
    )

    if (active_commit is None or active_commit == branch.get_latest_commit_id()) and path == "":
        body_content.append(
            Tag("div",
                slug_tag('/javascript/git.js', 'GitActivityWidget', project = project_name)
            )
        )


    return body_content

def get_raw_file_content(project_name, branch_name, commit_id, path):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)
    body_content = branch.get_file_content(path, commit_id)
    return body_content


def build_git_file_view(project_name, branch_name, commit_id, path):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)
    body_content = branch.get_file_content(path, commit_id)

    ext = path[path.rfind(".") + 1:].lower()
    if ext == "py":
        language = "python"
    elif ext == "rs":
        language = "rust"
    elif ext == "sh":
        language = "bash"
    elif ext == "yml":
        language = "yaml"
    elif ext == "toml":
        language = "toml"
    else:
        language = "none"

    query_attrs = {
        "branch": branch_name,
        'path': path,
        "raw": 1
    }
    if commit_id is not None:
        query_attrs['commit'] = commit_id
    else:
        commit_id = branch.get_latest_commit_id()

    return Tag("div",
        { "class": "git-fileoverview" },
        Tag("div",
            { "class": "title-row" },
            Tag("h1", path),
            Tag("hr"),
            Tag("div",
                Tag("div", branch_name),
                Tag("div", "|"),
                Tag("div", commit_id)
            )
        ),
        Tag("div",
            { "class": "navigation-row" },
            Tag("div",
                build_git_path_navigator(branch_name, commit_id, path)
            ),
            Tag("div",
                VH_MID,
                Tag("a",
                    {
                        "href": "?" + urlencode(query_attrs),
                        "download": path[path.rfind("/") + 1:],
                        "class": "button"
                    },
                    "Download File"
                )
            )
        ),
        Tag("div",
            Tag("pre",
                { "class": f"language-{language} line-numbers" },
                Tag("code",
                    { "class": f"language-{language}" },
                    body_content
                )
            )
        )
    )

def build_git_commit_view(project_name, branch_name, commit_id=None):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)
    if commit_id is None:
        commit_id = branch.get_latest_commit_id()

    branch.get_commit(commit_id)
    return Tag("div", f"commit/diff oviewview of {commit_id}")

def slug_tag(remote, classname, **kwargs):
    opts = {
        "class": f"widget-slug slug-{classname}",
        "data-remote": remote,
        "data-class": classname,
        "data-json": json.dumps(kwargs)
    }

    return Tag("div", opts)
