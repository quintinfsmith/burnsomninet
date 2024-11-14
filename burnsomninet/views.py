import os
import json
import time
import marko
import zlib
import re
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import redirect
from sitecode.py.httree import Tag, Text, RawHTML, slug_tag
from sitecode.py.cachemanager import check_cache, get_cached, update_cache, get_latest_update
from sitecode.py.quicksql import connect_to_mariadb
from sitecode.py.gitmanip import Project as GitProject
from sitecode.py.gitmanip import FileNotFound, InvalidBranch
from burnsomninet import wrappers
from sitecode.py import api, accesslogmanager
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus
import mimetypes
from sitecode.py import automanual
from sitecode.py.atbt import Issue, IssueNote

SITECODE = settings.SITECODE
STATIC_PATH = settings.STATIC_PATH
GIT_PATH = "/srv/git"
COMMIT_ID = settings.COMMIT_ID
JS_PATH = settings.JS_PATH
SCSS_PATH = settings.SCSS_PATH

def sass_compile(input_scss):
    timestamp = time.time()
    scss_path = f"/tmp/.tmp_scss{timestamp}"
    css_path = f"/tmp/.tmp_css{timestamp}"
    with open(scss_path, "w") as file_pipe:
        file_pipe.write(input_scss)
    os.system(f"source /srv/bon_venv/bin/activate && pysassc {scss_path} {css_path} && deactivate")
    output = ""
    with open(css_path, "r") as file_pipe:
        output = file_pipe.read()
    if os.path.isfile(css_path):
        os.system(f"rm {css_path}")
    if os.path.isfile(scss_path):
        os.system(f"rm {scss_path}")

    return output

#NOTE: Do not change the argument names. that fucks django
def handler404(request, exception):
    if wrappers.is_malicious_query(request.path):
        wrappers.register_banned_ip(accesslogmanager.get_client_ip(request))

    wrappers.log(f"DEBUG: {request.path}")

    daisy = ""
    with open(f"{STATIC_PATH}/oopsie daisy.svg", "r") as file_pipe:
        daisy = file_pipe.read()

    top = Tag("html",
        wrappers.build_head(title="404"),
        Tag("body",
            wrappers.build_sitemap(),
            Tag("div",
                { "class": "content daisy" },
                Tag("div",
                    { "class": "img_wrapper" },
                    RawHTML(daisy)
                ),
                Tag("div",
                    { "class": "details"},
                    Tag("div",
                        "Looks like you've gone and picked yourself an oopsie daisy there, friend."
                    )
                )
            )
        )
    )

    return HttpResponse(repr(top), status=404)

#NOTE: Do not change the argument names. that fucks django
def handler500(request):
    #wrappers.log(str(exception))
    top = Tag("html",
        Tag("head",
            Tag("style", { }),
        ),
        Tag("body",
            Tag("div",
                "Looks like I've gone and picked myself an oopsie daisy.")
        )
    )

    return HttpResponse(repr(top), status=500)

def unicycling_street(request, **kwargs):
    content = wrappers.media_content(kwargs["json"])
    return content

def unicycling_mountain(request, **kwargs):
    try:
        content = wrappers.media_content(kwargs["json"])
    except KeyError:
        content = Text("Nothing Here yet")
    return content

def projects_hook(request, **kwargs):
    return Tag("div",
        { "class": "markdown-wrapper" },
        Tag("div",
            { "class": "markdown" },
            RawHTML(kwargs["md"])
        )
    )

def robots(request):
    content = ''
    with open(f"{SITECODE}/robots.txt", "r") as file_pipe:
        content = file_pipe.read()
    return HttpResponse(content, "text/plain")

def keybase(request):
    content = ''
    with open(f"{SITECODE}/keybasejson", "r") as file_pipe:
        content = file_pipe.read()
    return HttpResponse(content)

def favicon(request):
    content = b''
    with open(f"{STATIC_PATH}/favicon-32.ico", 'rb') as file_pipe:
        content = file_pipe.read()
    return HttpResponse(content)

def style(request, style_name):
    style_directory = f"{SCSS_PATH}/{style_name}"
    if not os.path.isdir(style_directory):
        return handler404(request, None)

    cache_key = f"sass_{style_name}"
    paths = []
    for filename in os.listdir(style_directory):
        if filename[filename.rfind(".") + 1:].lower() == "scss":
            paths.append(f"{style_directory}/{filename}")

    cache_needs_update = check_cache(
        cache_key,
        *paths
    )

    if not cache_needs_update:
        content, mimetype = get_cached(cache_key)
    else:
        content = ""
        paths.sort()

        for filepath in paths:
            with open(filepath, 'r', encoding='utf-8') as file_pipe:
                content += "\n" + file_pipe.read()

        content = sass_compile(content)
        mimetype = "text/css"
        update_cache(cache_key, content, mimetype)

    return HttpResponse(content, mimetype)

def javascript_controller(request, file_path):
    active_path = file_path.split("/")
    while "" in active_path:
        active_path.remove("")

    js_path = f"{JS_PATH}/" + "/".join(active_path)
    content = ""
    if os.path.isfile(js_path):
        with open(js_path, 'r') as file_pipe:
            content = file_pipe.read()
        return HttpResponse(content, content_type="text/javascript")
    else:
        return handler404(request, None)

def section_json(request):
    active_path = request.get_full_path().split("/")
    while "" in active_path:
        active_path.remove("")

    sectionsdir = f"{SITECODE}/sections/"
    json_path = sectionsdir + "/".join(active_path)
    content = "{}"
    with open(json_path, "r") as file_pipe:
        content = file_pipe.read()

    return HttpResponse(content, content_type="application/json")

def manual_controller(request, manual):
    manualsdir = f"{SITECODE}/manuals/"
    directory_path = f"{manualsdir}/{manual}/"

    if not os.path.isdir(directory_path):
        raise Http404()


    title = f"{manual.title()} User Manual"
    raw_content = automanual.populate_page(directory_path)
    raw_content = automanual.do_slugs(raw_content)
    description = raw_content[raw_content.find("## About") + 8:].strip()
    description = description[0:description.find("\n")]

    raw_content = automanual.replace_svg(raw_content, STATIC_PATH)
    raw_content = automanual.extra_markdown(raw_content)
    top = Tag("html",
        wrappers.build_head(**{
            "description": description,
            "title": title,
            "favicon": manual
        }),
        Tag("body",
            wrappers.build_sitemap('manual', manual),
            Tag("div",
                { "class": "content" },
                Tag("div",
                    { "class": "markdown-wrapper" },
                    Tag("div",
                        { "class": "markdown" },
                        RawHTML(marko.convert(raw_content))
                        #RawHTML(markdown.markdown(raw_content))
                    )
                )
            )
        )
    )

    return HttpResponse(repr(top))


def section_controller(request, section, subsection_path):
    subsections = subsection_path.split("/")

    # redirect apres_bindings/wrecked_bindings to merged projects
    if subsections[0] in ("apres_bindings", "wrecked_bindings"):
        subsections[0] = subsections[0][0:subsections[0].rfind("_")]
    elif subsections[0] == "radixulous":
        subsections[0] = "pagan"

    if section in ("git", "project") and subsections[0].lower().endswith(".git"):
        subsections[0] = subsections[0][0:subsections[0].rfind(".")]


    if section in ("git", "project") or (section == 'software' and subsections[0] in ('apres', 'wrecked')):
        return git_controller(request, subsections[0], *subsections[1:])
    elif section == "software" or section == "manuals":
        return manual_controller(request, subsections[0])


    subsection = subsections[0]

    sectionsdir = f"{SITECODE}/sections/"
    kwargs = {}
    directory_path = f"{sectionsdir}/{section}/"

    if not os.path.isdir(directory_path):
        raise Http404()


    files = os.listdir(directory_path)
    description = ""
    title = "test"
    for file_name in files:
        ext = file_name[file_name.rfind(".") + 1:].lower()
        name = file_name[0:file_name.rfind(".")]
        if name != subsection:
            continue

        file_path = f"{directory_path}/{file_name}"
        content = None
        if ext == "json":
            content = {}
            with open(file_path, "r") as file_pipe:
                content = json.loads(file_pipe.read())
            description = content.get('description', '')
            title = content.get('title', '')

        elif ext == "md":
            raw_content = ""
            with open(file_path, "r") as file_pipe:
                raw_content = file_pipe.read()

            description = raw_content[raw_content.find("## About") + 8:].strip()
            description = description[0:description.find("\n")]

            title = raw_content[0:raw_content.find("\n\n")].strip()
            while title[0] == "#":
                title = title[1:].strip()
            title = title.replace("\n", " - ")

            content = marko.convert(raw_content)

        if content is not None:
            kwargs[ext] = content

        break

    try:
        body_content = VIEWMAP[section][subsection](request, **kwargs)
    except KeyError:
        raise Http404()
    except FileNotFoundError:
        raise Http404()

    top = Tag("html",
        wrappers.build_head(**{
            "description": description,
            "title": title
        }),
        Tag("body",
            wrappers.build_sitemap(section, subsection),
            Tag("div",
                { "class": "content" },
                body_content
            )
        )
    )

    return HttpResponse(repr(top))

def index(request):
    active_path = request.get_full_path().split("/")

    while "" in active_path:
        active_path.remove("")

    # Do Git Commit Overview
    private_projects = set()
    repositories = os.listdir(GIT_PATH)
    repositories.sort()
    working_repositories = []
    for path in repositories:
        if not os.path.isfile(f"{GIT_PATH}/{path}/git-daemon-export-ok") and path != "burnsomninet":
            private_projects.add(path)
        working_repositories.append(path)
    repositories = working_repositories

    all_commits = []
    now = datetime.now()
    from_date = datetime(year=now.year - 1, month=now.month, day=now.day) - timedelta(days=1) 
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

    # bmac_content = ""
    # with open(f"{STATIC_PATH}/bmac.svg", "r") as fp:
    #     bmac_content = fp.read()

    top = Tag("html",
        wrappers.build_head(
            title="Quintin Smith - Developer, Unicyclist",
        ),
        Tag("body",
            wrappers.build_sitemap(*active_path),
            Tag("div",
                { "class": "content index" },
                Tag("div",
                    Tag("div",
                        Tag("div", { "class": "vh_mid" }),
                        Tag("div",
                            { "class": "details-img-wrapper" },
                            Tag("div",
                                { "class": "img_wrapper" },
                                Tag("img", {
                                    "src": "/content/profile.png?v=2"
                                })
                            ),
                            Tag("div",
                                { "class": "details"},
                                Tag("div",
                                    Tag("div",
                                        { "class": "nametag" },
                                        "Quintin Smith",
                                    ),
                                    Tag("div",
                                        "Software Developer"
                                    )
                                ),
                                Tag("div",
                                    { "class": "externals" },
                                    Tag("a",
                                        { "href": "mailto:smith.quintin@protonmail.com" },
                                        Tag("div", { "class": "vh_mid" }),
                                        "Email"
                                    ),
                                    Tag("a",
                                        { "href": "https://keybase.io/quintinfsmith" },
                                        Tag("div", { "class": "vh_mid" }),
                                        "Keybase"
                                    ),
                                    Tag("div",
                                        { "class": "nvm" },
                                        Tag("div", { "class": "vh_mid" }),
                                        "GitHub"
                                    ),
                                )
                                # Tag("div",
                                #     { "class": "externals" },
                                #     Tag("a",
                                #         {
                                #             "href": "https://buymeacoffee.com/qfsmith",
                                #             "class": "bmac"
                                #         },
                                #         Tag("div", { "class": "vh_mid" }),
                                #         Tag("span", RawHTML(bmac_content)),
                                #         "Buy Me A Coffee"
                                #     )
                                # )
                            )
                        )
                    ),
                    slug_tag(
                        '/javascript/git.js',
                        'GitActivityWidget',
                        commits=all_commits,
                    )
                )
            )
        )
    )

    return HttpResponse(repr(top))

def api_controller(request, section_path):
    section_split = section_path.split("/")
    while "" in section_split:
        section_split.remove("")

    kwargs = {}
    for key in request.GET:
        kwargs[key] = request.GET.get(key, None)

    try:
        content = api.handle(*section_split, **kwargs)
    except ModuleNotFoundError:
        raise Http404()

    content = json.dumps(content)
    return HttpResponse(content, content_type="application/json")

def get_botlist():
    bots = []
    with open(f"{SITECODE}/robot_useragents", "r") as fp:
        bots = fp.read().split("\n")
    return bots

def git_controller(request, project, *project_path):
    uagent = request.META.get("HTTP_USER_AGENT", "")
    #TEMPORARY: Block bot that is traversing git commits
    if uagent in get_botlist() and len(request.GET.keys()) > 0:
        raise Http404()

    if not os.path.isdir(f"{GIT_PATH}/{project}"):
        raise Http404()

    if not os.path.isfile(f"{GIT_PATH}/{project}/git-daemon-export-ok"):
        raise Http404()

    if request.headers['User-Agent'][0:3] == 'git':
        path = "/".join(project_path)
        getstring = urlencode(request.GET, quote_via=quote_plus)
        if getstring:
            getstring = "?" + getstring
        return redirect(f"/gitserve/{project}/{path}{getstring}")

    view = request.GET.get('view', 'files')
    branch = request.GET.get('branch', 'master')
    commit = request.GET.get('commit', None)

    # Disabled commit/branch browsing
    if branch != 'master' or commit is not None:
        Http404()

    path = request.GET.get('path', '')
    raw = request.GET.get("raw", 0)

    if project_path and project_path[0] == "blob":
        raw = 1
        commit = project_path[1]
        path = "/".join(project_path[2:])
        branch = "master"

    is_directory = (path == '' or path[-1] == '/')
    content = None

    try:
        if view == "files" and not is_directory and raw:
            mimetype = "text/plain"
            content = wrappers.get_raw_file_content(project, branch, commit, path)
        else:
            mimetype = "text/html"
            if view == 'files':
                if is_directory:
                    body = wrappers.build_git_overview(request, project, branch, commit, path)
                else:
                    body = wrappers.build_git_file_view(project, branch, commit, path)
            elif view == "commit":
                body = wrappers.build_git_commit_view(project, branch, commit)
            else:
                raise Http404()

            content = Tag("html",
                wrappers.build_head(
                    title=f"{project.capitalize()} overview",
                    favicon=project
                ),
                Tag("body",
                    wrappers.build_sitemap('git', project),
                    Tag("div",
                        { "class": "content" },
                        body
                    )
                )
            )
    except FileNotFound:
        raise Http404()
    except InvalidBranch:
        raise Http404()

    return HttpResponse(content, mimetype)


class GitDumbServer:
    @classmethod
    def main(cls, request, project_name, *path):
        project_path = f"{GIT_PATH}/{project_name}"
        if not os.path.isfile(f"{project_path}/git-daemon-export-ok"):
            raise Http404()

        service = request.GET.get('service', None)
        git_project = GitProject(project_path)
        path_str = "/".join(path)
        file_path = f"{GIT_PATH}/{project_name}/{path_str}"

        mimetype = 'application/octet-stream'
        status = 200

        output = ""
        if path_str == "info/refs" and service == "git-upload-pack":
            refs = git_project.get_refs()
            keys = list(refs.keys())
            keys.sort()
            for i, path in enumerate(keys):
                hashstr = refs[path]

                # We dont' want HEAD in the info/refs advertisement
                if "HEAD" in path:
                    continue

                line = f"{hashstr}\t{path.strip()}"
                line += "\n"
                if i == len(refs) - 1:
                    line += "^{}"

                output += line

            mimetype = f"text/plain; charset=utf-8"

        elif path_str == "HEAD":
            ref = ''
            with open(f"{GIT_PATH}/{project_name}/HEAD", "r") as fp:
                ref = fp.read()
                ref = ref[ref.find(" ") + 1:].strip()
            with open(f"{GIT_PATH}/{project_name}/{ref}", "r") as fp:
                output = fp.read().strip()

        elif re.search("^objects/[0-9a-zA-Z]{2}/[0-9a-zA-Z]{38}$", path_str):
            if os.path.isfile(file_path):
                with open(file_path, "rb") as fp:
                    filebytes = fp.read()
                output = filebytes
            else:
                object_key = "".join(path[1:])
                objects = git_project.get_objects()

                if object_key not in objects:
                    raise Http404()

                working_object = objects[object_key]
                obj_type = working_object['type']
                obj_number = working_object['number']

                blob_content = git_project.get_blob(object_key, obj_type)
                blob_content = f"{obj_type} {obj_number}".encode('utf8') + b'\x00' + blob_content
                output = zlib.compress(blob_content)

        else:
            raise Http404()

        return HttpResponse(output, mimetype, status=status)

def content_controller(request, content_path):
    status = 200


    abs_content_path = os.path.abspath(f"{STATIC_PATH}/{content_path}")

    # TODO: Change the 404 message to a 'cheekier' response
    # when the request is clearly trying to access files outside
    # of the content folder
    if len(abs_content_path) < len(STATIC_PATH):
        raise Http404()

    if abs_content_path[0:len(STATIC_PATH)] != STATIC_PATH:
        raise Http404()

    if not os.path.exists(abs_content_path):
        raise Http404()

    point = abs_content_path.rfind(".")
    if point != -1:
        ext = abs_content_path[point:]
        mimetypes.init()
        mimetype = mimetypes.types_map.get(ext, 'application/octet-stream')
    else:
        mimetype = 'text/plain'

    response_content = b''
    with open(abs_content_path, 'rb') as fp:
        response_content = fp.read()

    return HttpResponse(response_content, mimetype, status=status)

def releases_atom_controller(request, project):
    status = 200

    releases_dir = f"{STATIC_PATH}/release/{project}/"
    if project not in os.listdir(GIT_PATH) or not os.path.exists(f"{GIT_PATH}/{project}/git-daemon-export-ok") or not os.path.exists(releases_dir):
        raise Http404()

    cache_key = f"atom_releases_{project}"
    paths = []
    for filename in os.listdir(releases_dir):
        if filename.lower().endswith(".apk"):
            paths.append(f"{releases_dir}{filename}")

    cache_needs_update = check_cache(
        cache_key,
        *paths
    )

    if cache_needs_update:
        content = '<?xml version="1.0" encoding="UTF-8"?>' + repr(wrappers.atom_releases(project))
        mimetype = "application/atom+xml"
        update_cache(cache_key, content, mimetype)
    else:
        content, mimetype = get_cached(cache_key)

    return HttpResponse(content, mimetype, status=status)


def issues_rss_controller(request, project):
    status = 200

    if project not in os.listdir(GIT_PATH) or not os.path.exists(f"{GIT_PATH}/{project}/git-daemon-export-ok"):
        raise Http404()

    # Cache Control -------------------------
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    query = "SELECT MAX(issue_note.ts) FROM issue_note INNER JOIN issue ON issue.id = issue_note.issue_id AND issue.project = ? LIMIT 1;"
    cursor.execute(query, (project, ))
    max_ts = None
    for vals in cursor.fetchall():
        max_ts = vals[0]
    cursor.close()
    connection.close()

    cache_key = f"rss_issues_{project}"
    last_update = get_latest_update(cache_key)


    # End Cache Control---------------------

    if max_ts is not None and last_update is not None and max_ts <= last_update:
        output, mimetype = get_cached(cache_key)
    else:
        output = repr(wrappers.rss_issues(project))
        mimetype = "application/rss+xml"
        update_cache(cache_key, output, mimetype)

    return HttpResponse(output, mimetype, status=status)


def issues_controller(request, project):
    status = 200

    if project not in os.listdir(GIT_PATH) or not os.path.exists(f"{GIT_PATH}/{project}/git-daemon-export-ok"):
        raise Http404()

    # Cache Control -------------------------
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    query = "SELECT MAX(issue_note.ts) FROM issue_note INNER JOIN issue ON issue.id = issue_note.issue_id AND issue.project = ? LIMIT 1;"
    cursor.execute(query, (project, ))
    max_ts = None
    for vals in cursor.fetchall():
        max_ts = vals[0]
    cursor.close()
    connection.close()

    cache_key = f"issues_{project}"
    last_update = get_latest_update(cache_key)

    # End Cache Control---------------------

    if max_ts is not None and last_update is not None and max_ts <= last_update:
        output, mimetype = get_cached(cache_key)
        return HttpResponse(output, mimetype, status=status)


    from_date = datetime(year=2022, month=1, day=1)

    issues = api.handle(
        'atbt', 'issues',
        project=project,
        datefrom=from_date.timestamp(),
        **request.GET
    )

    title = f"{project.title()} Issues"

    body_content = Tag("div",
        Tag("h2", f"Known Issues in {project.title()}"),
        Tag("div", {
            "data-json": json.dumps({
                "project": project,
                "issues": issues
            }),
            "data-remote": "main",
            "data-class": "IssuesTable",
            "class": "widget-slug slug-IssuesTable"
        })
    )

    top = Tag("html",
        wrappers.build_head(**{
            "description": f"Issues logged in {project.title()}",
            "title": title,
            "favicon": project
        }),
        Tag("body",
            wrappers.build_sitemap("git", project),
            Tag("div",
                { "class": "content" },
                body_content
            )
        )
    )

    content = repr(top)
    mimetype="text/html"
    update_cache(cache_key, content, mimetype)

    return HttpResponse(content, mimetype, status=status)


def issue_controller(request, issue_id):
    status = 200

    state_labels = ["cancelled", "open", "in progress", "resolved"]
    urgency_labels = ["feature", "low", "pressing", "urgent"]

    try:
        issue = Issue(issue_id)
    except Issue.NoSuchIssueException:
        raise Http404()
    if issue.project not in os.listdir(GIT_PATH) \
            or not os.path.exists(f"{GIT_PATH}/{issue.project}/git-daemon-export-ok"):
        raise Http404()

    notes_table = Tag("div", { "class": "notes-table" })

    working_state = 1
    for note in issue.notes:
        note_top_line = Tag("div",
            { "class": "top-line" },
            Tag("div",
                #Tag("div", { "class": "vh_mid" }),
                #Tag("div",
                #    { "class": "author" },
                #    note.author
                #)
            )
        )

        if note.state != working_state and note.state is not None:
            note_state_str = state_labels[note.state]
            note_top_line.append(
                Tag("div",
                    Tag("div", { "class": "vh_mid" }),
                    Tag("div",
                        { "class": f"status-update status s{note.state}" },
                        f"{note_state_str}"
                    )
                )
            )

        note_top_line.append(
            Tag("div",
                Tag("div", { "class": "vh_mid" }),
                Tag("div", {
                    "data-class": "RelativeVagueDate",
                    "data-json": json.dumps({
                        "date": note.timestamp.timestamp() * 1000
                    }),
                    "data-remote": "main",
                    "class": "date widget-slug"
                })
            )
        )

        working_state = note.state

        note_entry = Tag("div",
            { "class": f"note-{note.id}" },
            note_top_line,
            Tag("div",
                { "class": "note-description" },
                note.get_text()
            )
        )

        note_img_path = f"{STATIC_PATH}/issues/{issue.project}/{note.id}"
        if os.path.isdir(note_img_path):
            imgs_line = Tag("div", {
                "class": "issue_note_imgs"
            })


            for f in os.listdir(note_img_path):
                imgs_line.append(
                    Tag("div", {
                        "class": "widget-slug slug-ViewableImg",
                        "data-class": "ViewableImg",
                        "data-remote": "main",
                        "data-json": json.dumps({
                            "src": f"/content/issues/{issue.project}/{note.id}/{f}"
                        })
                    })
                )

            note_entry.append(imgs_line)

        notes_table.append(note_entry)

    issue_state_label = ""
    issue_state = issue.get_state()
    if issue_state is not None:
        issue_state_label = state_labels[issue_state]
    else:
        issue_state = 1

    body_content = Tag("div",
        { "class": "issue-body" },

        Tag("h2",
            { "class": "title" },
            issue.title.title()
        ),

        Tag("div",
            { "class": "status-line" },
            Tag("div",
                { "class": f"rating r{issue.rating}" },
                urgency_labels[issue.rating]
            ),
            Tag("div",
                { "class": f"status s{issue_state}" },
                issue_state_label
            )
        ),
        notes_table
    )

    description = f"Issue for {issue.project.title()} - {issue.title}"
    title = description

    top = Tag("html",
        wrappers.build_head(**{
            "description": description,
            "title": title,
            "favicon": issue.project
        }),
        Tag("body",
            wrappers.build_sitemap("git", issue.project),
            Tag("div",
                { "class": "content" },
                body_content
            )
        )
    )

    return HttpResponse(repr(top), "text/html", status=status)

def ban_hammer(request, *args):
    wrappers.log(str(dir(request)))
    body = Tag("html", Tag("body", "BAN HAMMER!"))
    return HttpResponse(repr(body), "text/html", status=200)

VIEWMAP = {
    "unicycling": {
        "street": unicycling_street,
        "mountain": unicycling_mountain
    },
    "software": {
        "sbyte": projects_hook,
        "apres": projects_hook,
        "rory": projects_hook,
        "wrecked": projects_hook
    }
}

