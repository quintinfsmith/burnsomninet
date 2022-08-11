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
from sitecode.py.cachemanager import check_cache, get_cached, update_cache
from sitecode.py.gitmanip import Project as GitProject
from burnsomninet import wrappers
from sitecode.py import api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode, quote_plus

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
    os.system(f"pysassc {scss_path} {css_path}")
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


def section_controller(request, section, subsection_path):
    subsections = subsection_path.split("/")

    if section == "git" or section == "project":
        return git_controller(request, subsections[0], *subsections[1:])

    subsection = subsections[0]

    sectionsdir = f"{SITECODE}/sections/"
    kwargs = {}
    directory_path = f"{sectionsdir}/{section}/"
    files = os.listdir(directory_path)
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

        elif ext == "md":
            content = ""
            with open(file_path, "r") as file_pipe:
                content = marko.convert(file_pipe.read())

        if content is not None:
            kwargs[ext] = content

        break

    head_kwargs = {}
    #if os.path.isfile(f"{directory_path}/head.json"):
    #    with open(f"{directory_path}/head.json", 'r') as file_pipe:
    #        head_kwargs = json.loads(file_pipe.read())

    body_content = VIEWMAP[section][subsection](request, **kwargs)
    top = Tag("html",
        wrappers.build_head(**head_kwargs),
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
    from_date = datetime.now() - relativedelta(years=1)
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
                'git', 'commits',
                project=project,
                datefrom=from_date.timestamp()
            )
            if project in private_projects:
                project_alias = "a private project";
            else:
                project_alias = project
            for i, _commit in enumerate(working_commits):
                working_commits[i]['group'] = project_alias

            update_cache(cache_key, json.dumps(working_commits))

        all_commits.extend(working_commits)

    top = Tag("html",
        wrappers.build_head(title="Quintin Smith - Developer, Unicyclist"),
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
                                    "src": "https://avatars.githubusercontent.com/u/72575658?v=4"
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
                                    Tag("div",
                                        Tag("a",
                                            { "href": "mailto:smith.quintin@protonmail.com" },
                                            "Email"
                                        )
                                    ),
                                    Tag("div",
                                        Tag("a",
                                            { "href": "https://keybase.io/quintinfsmith" },
                                            "Keybase"
                                        )
                                    ),
                                    Tag("div",
                                        { "class": "nvm" },
                                        "GitHub"
                                    ),
                                )
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

    response = {}
    try:
        content = api.handle(*section_split, **kwargs)
    except ModuleNotFoundError:
        raise Http404()

    content = json.dumps(content)
    return HttpResponse(content, content_type="application/json")

def git_controller(request, project, *project_path):
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
    path = request.GET.get('path', '')
    raw = request.GET.get("raw", 0)

    is_directory = (path == '' or path[-1] == '/')
    content = None
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

        content = Tag("html",
            wrappers.build_head(title=f"{project.capitalize()} overview"),
            Tag("body",
                wrappers.build_sitemap('git', project),
                Tag("div",
                    { "class": "content" },
                    body
                )
            )
        )

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

