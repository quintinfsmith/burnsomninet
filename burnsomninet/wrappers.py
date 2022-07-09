import json, os
from sitecode.py.httree import Tag, Text, RawHTML
from django.conf import settings
from sitecode.py.gitmanip import Project as GitProject
from typing import Optional, Tuple, List, Dict
from urllib.parse import urlencode
from datetime import datetime

SITECODE = settings.SITECODE
STATIC_PATH = settings.STATIC_PATH
BASE_DIR = settings.BASE_DIR
COMMIT_ID = settings.COMMIT_ID
GIT_PATH = "/srv/git"

VH_TOP = Tag('div', { "class": "vh_top" })
VH_BOT = Tag('div', { "class": "vh_bot" })
VH_MID = Tag('div', { "class": "vh_mid" })

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
    sectionsdir = f"{SITECODE}/sections/"

    headings = os.listdir(sectionsdir)
    headings.sort()
    subsitemap = Tag("div", { "class": "treemap" })

    for i, heading in enumerate(headings):
        entry = Tag("div", { "class": "entry" })
        files = os.listdir(sectionsdir + heading)
        files.sort()
        for f in files:
            if not os.path.isdir(sectionsdir + heading + '/' + f):
                continue

            title = f
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
                    Tag('div', title.title())
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
    for media in mediamap:
        # Create screenshots
        for src in media['srcs']:
            abs_src = f"{BASE_DIR}/{src}"
            if not os.path.isfile(abs_src + ".jpg"):
                os.system("ffmpeg -i \"%s\" -ss 00:00:00 -vframes 1 \"%s.jpg\"" % (abs_src, abs_src))

        output.append(
            Tag("div",
                {},
                VH_MID,
                Tag("div",
                    {
                        "id": media["title"].replace(" ", "_").lower(),
                        "class": "polaroid",
                        "data-srcs": json.dumps(media["srcs"])
                    },
                    Tag("div",
                        Tag("img", {
                            "src": media["srcs"][0] + ".jpg",
                        })
                    ),
                    Tag("div",
                        { 'class': 'label-wrapper' },
                        Tag("div",
                            { 'class': 'label' },
                            VH_MID,
                            Tag("div", media["title"])
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

def build_git_branch_select(git_project: GitProject, active_branch_name: Optional[str]=None) -> Tag:
    if active_branch_name is None:
        active_branch_name = 'master'

    output: Tag = Tag("select", {
        'class': 'branch-selector'
    })
    branch_names = git_project.get_branch_names()
    branch_names = sorted(branch_names, key=lambda x: int(x != "master"))
    for branch_name in branch_names:
        tag_attrs = {
            "value": branch_name
        }

        if branch_name == active_branch_name:
            tag_attrs["selected"] = True

        output.append(
            Tag("option",
                tag_attrs,
                branch_name
            )
        )
    return output

def build_git_commit_select(git_project: GitProject, branch_name: str, active_commit: Optional[str]=None) -> Tag:
    branch = git_project.get_branch(branch_name)
    output: Tag = Tag("select", { "class": "commit-selector" })
    for i, commit in enumerate(branch.get_commits()):
        tag_attrs = {
            "value": commit.id
        }

        if (i == 0 and active_commit is None) or commit.id == active_commit:
            tag_attrs['selected'] = True

        output.append(
            Tag("option",
                tag_attrs,
                str(commit.date)
            )
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

def build_git_activity_chart(git_branch) -> Tag:
    commits = git_branch.get_commits()
    years = set()
    commit_days: Dict[Tuple[int, int], int] = {}
    for commit in commits:
        years.add(commit.date.year)
        commit_key = (commit.date.year, commit.date.timetuple().tm_yday)
        if commit_key not in commit_days:
            commit_days[commit_key] = 0
        commit_days[commit_key] += 1

    years = list(years)
    years.sort()
    #for year in years:
    working_year = 2022 #For Dev, switch to loop when done
    offset = datetime(year=working_year, month=1, day=1).weekday()
    day_count = 365
    if is_leap_year(working_year):
        day_count += 1

    year_table = Tag("table", { "class": "year-table" })
    day_tds = []
    rows = []
    for i in range(7):
        rows.append(Tag("tr"))
        year_table.append(rows[i])

    for i in range(day_count + offset):
        if i < offset:
            classname = "oob"
        else:
            classname = ""

        td = Tag("td", { "class": classname })
        rows[i % 7].append(td)
        day_tds.append(td)

    for (year, day), count in commit_days.items():
        if year != working_year:
            continue
        td = day_tds[day + offset]
        td.set_attribute('class', 'active')


    return Tag("div", { "class": "activity-overview"}, year_table)

def build_git_overview(project_name: str, branch_name: str, active_commit: Optional[str], path: str = ""):
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

    filelist = branch.get_filelist(path)
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

        if not is_file:
            full_path += "/"
            icon_path = f"{STATIC_PATH}/dir-icon.svg"
        else:
            icon_path = f"{STATIC_PATH}/file-icon.svg"

        icon = ""
        with open(icon_path, 'r') as fp:
            icon = RawHTML(fp.read())

        commit_query_attrs = {
            "view": "commit",
            "commit": commit_id,
            "branch": branch_name
        }

        query_attrs['path'] = full_path
        file_table.append(
            Tag("tr",
                Tag("td",
                    Tag("a",
                        { "href": f"/git/{project_name}?" + urlencode(query_attrs) },
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
                        { "href": f"/git/{project_name}?" + urlencode(commit_query_attrs) },
                        str(commit_date)
                    )
                )
            )
        )

    body_content = Tag("div",
        { "class": "git-overview" },
        Tag("div",
            { "class": "option-row" },
            Tag("div",
                { "title": "Branch" },
                build_git_branch_select(git_project, branch_name),
            ),
            Tag("div",
                { "title": "Commit" },
                build_git_commit_select(git_project, branch_name, active_commit)
            )
        ),
        Tag("div",
            { "class": "files-wrapper" },
            file_table
        )
    )

    if active_commit is None and path == "":
        body_content.append(build_git_activity_chart(branch))


    return body_content


def build_git_file_view(project_name, branch_name, commit_id, path):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)
    blame = branch.get_blame(path, commit_id)
    body_content = ""
    for i, (last_commit_id, content) in enumerate(blame):
        body_content += content + "\n"

    ext = path[path.rfind(".") + 1:].lower()
    if ext == "py":
        language = "python"
    elif ext == "rs":
        language = "rust"
    elif ext == "sh":
        language = "bash"
    elif ext == "yml":
        language = "yaml"
    else:
        language = "none"

    return Tag("div",
        { "class": "git-fileoverview" },
        Tag("div",
            { "class": "navigation-row" },
            Tag("div",
                build_git_path_navigator(branch_name, commit_id, path)
            ),
            Tag("div",
                { "title": "Branch" },
                VH_MID,
                build_git_branch_select(git_project, branch_name)
            ),
            Tag("div",
                { "title": "Commit" },
                VH_MID,
                build_git_commit_select(git_project, branch_name, commit_id)
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
