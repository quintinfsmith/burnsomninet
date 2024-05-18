import json, os
import marko
from django.conf import settings
from typing import Optional, Tuple, List, Dict
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PIL import Image
from sitecode.py.quicksql import connect_to_mariadb, sql_get_simple, sql_get_inverse_regex
from sitecode.py.cachemanager import check_cache, get_cached, update_cache
from sitecode.py.gitmanip import Project as GitProject, FileNotFound
from sitecode.py.httree import Tag, Text, RawHTML, slug_tag
from sitecode.py import api

SITECODE = settings.SITECODE
STATIC_PATH = settings.STATIC_PATH
BASE_DIR = settings.BASE_DIR
COMMIT_ID = settings.COMMIT_ID
GIT_PATH = "/srv/git"

VH_TOP = Tag('div', { "class": "vh_top" })
VH_BOT = Tag('div', { "class": "vh_bot" })
VH_MID = Tag('div', { "class": "vh_mid" })

def build_favicon_links(**kwargs):
    sizes = [16, 32, 48, 167, 180, 192]
    output = []

    favicon = kwargs.get("favicon", "main")
    if not os.path.isdir(f"{STATIC_PATH}/favicons/{favicon}"):
        favicon = "main"

    for size in sizes:
        output.append(
            Tag("link", {
                "rel": "icon",
                "type": "image/png",
                "sizes": f"{size}x{size}",
                "href": f"/content/favicons/{favicon}/favicon-{size}x{size}.png"
            })
        )

    return output

def build_head(**kwargs):
    title = kwargs.get("title", '')

    return Tag("head",
        Tag("title", title),
        Tag("link", {
            "rel": "stylesheet",
            "type": "text/css",
            "href": f"/style/main.css?commit={COMMIT_ID}"
        }),
        Tag("link", {
            "rel": "stylesheet",
            "type": "text/css",
            "href": f"/style/prismschema.css?commit={COMMIT_ID}"
        }),
        Tag("script", {
            "src": "/content/javascript/crel.js",
            "type": "text/javascript"
        }),
        *build_favicon_links(**kwargs),
        Tag("script", {
            "src": f"/javascript/main.js?commit={COMMIT_ID}",
            "type": "text/javascript"
        }),
        Tag("meta", {
            "name": "description",
            "content": kwargs.get('description', '')
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
    else:
        classname += " home"

    sitemap = Tag("div", { "class": classname })
    sitemap_sub = Tag("div")
    sitemap.append(sitemap_sub)
    svg_content = ""
    with open(f"{STATIC_PATH}/logo.svg", "r") as fp:
        svg_content = fp.read()

    sitemap_sub.append(
        Tag("div",
            { "class": "logo" },
            Tag("a",
                { "href": "/" },
                RawHTML(svg_content)
            )
        )
    )

    section_map = []
    #------------------------------------------#
    repositories = os.listdir(GIT_PATH)
    repositories.sort()
    working_repositories = []
    for path in repositories:
        if os.path.isfile(f"{GIT_PATH}/{path}/git-daemon-export-ok"):
            working_repositories.append(path)
    repositories = working_repositories

    section_map.append({
        'name': 'Repositories',
        'sections': []
    })
    for i, repo in enumerate(repositories):
        section_map[-1]['sections'].append((
            ('git', repo) == active_path,
            f"/git/{repo}",
            repo
        ))

    #------------------------------------------#
    manualsdir = f"{SITECODE}/manuals/"

    section_map.append({
        'name': 'manuals',
        'sections': []
    })

    for folder in os.listdir(manualsdir):
        if not os.path.isdir(f"{manualsdir}{folder}"):
            continue

        section_map[-1]['sections'].append((
            ('manual', folder) == active_path,
            f"/manual/{folder}",
            folder.title()
        ))

    #------------------------------------------#
    sectionsdir = f"{SITECODE}/sections/"

    headings = os.listdir(sectionsdir)
    headings.sort()

    heading_alias_map = {}

    for i, heading in enumerate(headings):
        section_map.append({
            'name': heading.title(),
            'sections': []
        })

        files = os.listdir(sectionsdir + heading)
        files.sort()
        for f in files:
            title = f[0:f.rfind(".")]
            alias = title
            if f[f.rfind('.') + 1:] == "json":
                with open(f"{sectionsdir}{heading}/{f}", "r") as fp:
                    prefs = json.loads(fp.read())
                    alias = prefs.get('alias', title)
            elif f == "alias":
                with open(f"{sectionsdir}{heading}/{f}", "r") as fp:
                    heading_alias_map[heading.lower().strip()] = fp.read().strip()
                continue

            section_map[-1]['sections'].append((
                (heading, title) == active_path,
                f"/{heading}/{title}",
                alias.title()
            ))


    subsitemap = Tag("div", { "class": "treemap" })
    for section in section_map:
        heading = section['name']
        entry = Tag("div", { "class": "entry" })
        for (is_active, href, title) in section['sections']:
            classname = "item"
            if is_active:
                classname += " active"

            entry.append(
                Tag('a',
                    {
                        'class': classname,
                        'href': href
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
                    Tag('div', heading_alias_map.get(heading.lower().strip(), heading.title()))
                ),
                entry
            )
        )

    sitemap_sub.append(
        slug_tag(
            "main",
            "HamburgerMenu",
            sitemap=section_map
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
            if ext in ("jpg", "png"):
                continue
            vidpath = f"{section_path}{filename}".replace("//", "/")
            if not os.path.isfile(f"{vidpath}.png"):
                os.system(f"ffmpeg -i \"{vidpath}\" -ss 00:00:00 -vframes 1 \"{vidpath}.png\"")
                image = Image.open(f"{vidpath}.png")
                if (image.size[0] / image.size[1]) < (16 / 9):
                    nh = image.size[1]
                    nw = int(nh * (16 / 9))
                    new_image = Image.new("RGBA", (nw, nh), (0,0,0,0))
                    x_offset = (nw - image.size[0]) // 2
                    for y in range(image.size[1]):
                        for x in range(image.size[0]):
                            new_image.putpixel((x_offset + x, y), image.getpixel((x, y)))
                    new_image.save(f"{vidpath}.png")
                elif image.size[0] / image.size[1] > (16 / 9):
                    nw = image.size[0]
                    nh = int(nw / (16 / 9))
                    new_image = Image.new("RGBA", (nw, nh), (0,0,0,0))
                    y_offset = (nh - image.size[1]) // 2
                    for y in range(image.size[1]):
                        for x in range(image.size[0]):
                            new_image.putpixel((x, y_offset + y), image.getpixel((x, y)))
                else:
                    new_image = image

                nw = 500
                nh = int(nw * (9 / 16))
                new_image = new_image.resize((nw, nh))
                new_image.save(f"{vidpath}.png")



            sources.append(f"/content/{src}/{directory}/{filename}")
        # Create screenshots
        title = directory.capitalize()

        output.append(
            Tag("div",
                Tag("div",
                    VH_MID,
                    Tag("div",
                        {
                            "id": title.replace(" ", "_").lower(),
                            "class": "polaroid",
                            "data-srcs": json.dumps(sources)
                        },
                        Tag("div",
                            Tag("img", {
                                "src": sources[0] + ".png",
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
        )

    output.append(
        Tag("script", {
            "src": "/javascript/media.js",
            "type": "text/javascript"
        })
    )

    return output

def build_git_branch_select(project_name, active_branch_name: Optional[str]=None) -> Tag:
    git_project = GitProject(f"{GIT_PATH}/{project_name}")

    branch_names = git_project.get_branch_names()
    branch_names = sorted(branch_names, key=lambda x: int(x != "master"))

    if active_branch_name not in branch_names:
        active_branch_name = "master"

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
    commits = api.handle(
        'git', 'commits',
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
            {
                "rel": "nofollow",
                "href": "?" + urlencode(query_attrs)
            },
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
                {
                    "rel": "nofollow",
                    "href": "?" + urlencode(query_attrs)
                },
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
        { "class": "std-table" },
        Tag("thead",
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
                            "rel": "nofollow",
                            "href": f"/git/{project_name}?" + urlencode(query_attrs)
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
                        {
                            "rel": "nofollow",
                            "href": f"?" + urlencode(commit_query_attrs)
                        },
                        slug_tag(
                            'main',
                            'RelativeVagueDate',
                            date=commit_date.timestamp() * 1000
                        )
                    )
                )
            )
        )

    host = request.get_host()
    if ":" in host:
        host = host[0:host.rfind(":")]

    show_extra = (active_commit is None or active_commit == branch.get_latest_commit_id()) and path == ""

    body_content = Tag("div",
        { "class": "git-overview" },
    )

    if show_extra:
        now = datetime.now()
        first_commit_date = branch.get_first_commit_date()
        from_date = datetime(now.year - 1, now.month, now.day)
        #from_date = max(first_commit_date, from_date)
        body_content.append(
            slug_tag(
                '/javascript/git.js',
                'GitActivityWidget',
                project=project_name,
                branch=branch_name,
                datefrom=from_date.timestamp() * 1000, # JS timestamp
                datefirst=first_commit_date.timestamp() * 1000,
                orientation="horizontal",
                commits=api.handle(
                    'git', 'commits',
                    project=project_name,
                    branch=branch_name,
                    datefrom=(from_date - timedelta(days=1)).timestamp(),
                    all_branches=(branch_name == "master")
                )
            )
        )

    body_content.append(
        Tag("div",
            Tag("div",
                { "class": "option-row" },
                Tag("div",
                    VH_MID,
                    slug_tag(
                        '/javascript/git.js',
                        'CloneButtonWidget',
                        project = project_name
                    )
                ),
                Tag("div",
                    # Can't support commit/branch browsing on a small server anymore
                    #Tag("div",
                    #    VH_MID,
                    #    build_git_branch_select(project_name, branch_name)
                    #),
                    #Tag("div",
                    #    VH_MID,
                    #    build_git_commit_select(project_name, branch_name, active_commit, path)
                    #)
                )
            ),
            Tag("div",
                { "class": "files-wrapper" },
                file_table
            )
        )
    )

    try:
        readme_content = branch.get_file_content(f"{path}README.md", active_commit)
        if readme_content:
            readme_markdown = marko.convert(readme_content)
            body_content.append(
                Tag('div',
                    { 'class': 'markdown-wrapper' },
                    Tag('div',
                        { "class": "markdown readme" },
                        RawHTML(readme_markdown)
                    )
                )
            )
    except FileNotFound as e:
        pass

    return body_content

def get_raw_file_content(project_name, branch_name, commit_id, path):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    if branch_name not in git_project.get_branch_names():
        branch = git_project.get_branch(branch_name)
    else:
        branch = git_project.get_branch("master")
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
    elif ext == "md":
        language = "markdown"
    elif ext == "kt":
        language = "kotlin"
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
        Tag("pre",
            { "class": f"language-{language} line-numbers" },
            Tag("code",
                { "class": f"language-{language}" },
                body_content
            )
        )
    )

def build_git_commit_view(project_name, branch_name, commit_id=None):
    git_project = GitProject(f"{GIT_PATH}/{project_name}")
    branch = git_project.get_branch(branch_name)
    if commit_id is None:
        commit_id = branch.get_latest_commit_id()

    branch.get_commit(commit_id)
    return Tag("div", f"commit/diff overview of {commit_id}")

def datetime_to_rfc822(datetime_obj):
    # KLUDGE: the serveris PDT, and rss needs the zone info
    return datetime_obj.strftime("%a, %d %b %Y, %I:%M:%S PDT")

def rss_issues(project):
    from_date = datetime(year=2023, month=1, day=1)
    results = api.handle(
        'atbt', 'notes',
        project=project,
        limit=15
    )
    items = []
    last_date = None
    states = ["Cancelled", "Open", "In Progress", "Resolved"]
    for result in results:
        issue_id = result["issue_id"]
        timestamp = result["timestamp"]
        title = str(result["issue_id"]) + ": " + result["issue_title"]
        note_id = result["id"]

        if result["state_update"] is not None: 
            title += " [" + states[result["state_update"]] + "]"

        items.append(
            Tag("item",
                Tag("title", title),
                Tag("link", f"https://burnsomni.net/issue/{issue_id}"),
                Tag("description", result["note"]),
                Tag("pubDate", datetime_to_rfc822(timestamp)),
                Tag("guid", f"{note_id:016}")
            )
        )

        if last_date is None or last_date < result["timestamp"]:
            last_date = result["timestamp"]

    rss_channel = Tag("channel",
        Tag("title", f"{project.title()} Issue Tracker"),
        Tag("link", f"https://burnsomni.net/issues/{project}"),
        Tag("description", f"{project.title()} Issue Tracker"),
        Tag("language", "en-us"),
        Tag("pubDate", datetime_to_rfc822(from_date)),
        Tag("lastBuildDate", datetime_to_rfc822(last_date)),
        Tag("generator", "burnsomni.net rss"),
        Tag("webMaster", "smith.quintin@protonmail (Quintin Smith)"),
        *items
    )


    return Tag("rss",
        { "version": "2.0" },
        rss_channel
    )


def atom_releases(project):
    from_date = datetime(year=2023, month=1, day=1)
    results = api.handle(
        'releases',
        project=project
    )

    items = []
    last_date = from_date
    for result in results:
        file_name = result.get("apk", None)
        if file_name is None:
            continue

        if file_name.startswith("/"):
            file_name = file_name[1:]

        version_code = result["version_code"]
        version_name = result["version_name"]
        timestamp = result["timestamp"]
        changes = result["changelog"]

        items.append(
            Tag("entry",
                Tag("author",
                    Tag("name", "Quintin Smith")
                ),
                Tag("id", f"tag:burnsomni.net,0000:Repository/{project}/{version_code}"),
                Tag("updated", timestamp.isoformat()),
                Tag("title", f"{version_name}"),
                Tag("link", {
                    "rel": "alternate",
                    "type": "text/html",
                    "href": f"https://burnsomni.net/{file_name}"
                }),
                Tag("content",
                    {"type": "html"},
                    marko.convert(changes),
                )
            )
        )

        if last_date is None or last_date < result["timestamp"]:
            last_date = result["timestamp"]

    return Tag("feed",
        {
            "xmlns": "http://www.w3.org/2005/Atom",
            "xml:lang": "en-US"
        },
        Tag("id", f"https://burnsomni.net/releases/{project}.atom"),
        Tag("author",
            Tag("name", "Quintin Smith")
        ),
        Tag("link", {
            "type": "text/html",
            "rel": "alternate",
            "href": f"https://burnsomni.net/git/{project}"
        }),
        Tag("link", {
            "type": "application/atom+xml",
            "rel": "self",
            "href": f"https://burnsomni.net/releases/{project}.atom"
        }),
        Tag("title", f"{project.title()} Releases"),
        Tag("updated", last_date.isoformat()),
        *items
    )

def is_malicious_query(path):
    path = path.lower()
    return path.startswith("/admin/") \
        or path.startswith("/administrator/") \
        or path.startswith("/app_dev.php") \
        or path.startswith("/wp/") \
        or path.startswith("/db/") \
        or path.startswith("/wp-includes/") \
        or path.startswith("/wp-json/") \
        or path.startswith("/wp-admin/") \
        or path.startswith("/wp-content/") \
        or path.startswith("/frontend/") \
        or path.startswith("/debug/") \
        or path.startswith("/sapi/") \
        or path.startswith("/plugins/") \
        or path.startswith("/config/") \
        or path.startswith("/_wpeprivate/") \
        or path.startswith("/graphql/") \
        or path.startswith("/modules/mod_simplefileuploadv1.3") \
        or path.startswith("/phpmy-admin/") \
        or path.startswith("/mysql/") \
        or path.startswith("/phpmyadmin") \
        or path.endswith(".env") \
        or path.endswith("/frontend_dev.php") \
        or path.endswith("/ofc_upload_imaged.php") \
        or path.endswith("/ofc_upload_image.php") \
        or path.endswith("/upload.php") \
        or path.endswith("/cloud.php") \
        or path.endswith("/dialog.php") \
        or path.endswith("/connector.php") \
        or path.endswith("/updates.php") \
        or path.endswith("/wallet.dat") \
        or path.endswith("/udd.php") \
        or path.endswith("?xdebug_session_start=phpstorm") \
        or "/jquery-file-upload/" in path


def register_banned_ip(ip_address):
    with open(f"{BASE_DIR}/banned_ips", "a") as fp:
        fp.write(f"{ip_address}\n")

def is_ip_banned(ip_address: str):
    with open(f"{BASE_DIR}/banned_ips", "r") as fp:
        return f"{ip_address}\n" in fp.read()

def log(msg, suffix=""):
    with open("/var/log/httpd/burnsomninet/log", "a") as fp:
        fp.write(msg + "\n")

