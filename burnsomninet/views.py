import os
import json
import time
import marko
import importlib
from django.http import HttpResponse, Http404
from django.conf import settings
from sitecode.py.httree import Tag, Text, RawHTML
from sitecode.py.cachemanager import check_cache, get_cached, update_cache
from burnsomninet import wrappers

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

def style(request):
    main_path = f"{SCSS_PATH}/main.scss"
    mobile_path = f"{SCSS_PATH}/mobile.scss"
    desktop_path = f"{SCSS_PATH}/desktop.scss"

    cache_needs_update = check_cache(
        "sass_main",
        main_path,
        mobile_path,
        desktop_path
    )

    if not cache_needs_update:
        content, mimetype = get_cached("sass_main")
    else:
        midsize = 800
        content = ""
        with open(main_path, "r") as file_pipe:
            content = file_pipe.read()

        with open(mobile_path, "r") as file_pipe:
            content += f"\n@media only screen and (max-width: {midsize}px) {{\n"
            content += file_pipe.read()
            content += "\n}\n"

        with open(desktop_path, "r") as file_pipe:
            content += f"\n@media only screen and (min-width: {midsize}px) {{\n"
            content += file_pipe.read()
            content += "\n}\n"

        content = sass_compile(content)
        mimetype = "text/css"
        update_cache("sass_main", content, mimetype)

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


def section_controller(request, section, subsection):
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

    top = Tag("html",
        wrappers.build_head(title="Quintin Smith - Developer, Unicyclist"),
        Tag("body",
            wrappers.build_sitemap(*active_path),
            Tag("div",
                { "class": "content index" },
                Tag("div", { "class": "vh_mid" }),
                Tag("div",
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
                            Tag("a",
                                { "href": "https://github.com/quintinfsmith/" },
                                "Find me on GitHub"
                            )
                        )
                    )
                )
            )
        )
    )

    return HttpResponse(repr(top))

def git_controller(request, project):
    if project not in os.listdir(f"{GIT_PATH}"):
        raise Http404()

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
                wrappers.build_sitemap('project', project),
                Tag("div",
                    { "class": "content" },
                    body
                )
            )
        )

    return HttpResponse(content, mimetype)

def api_controller(request, section_path):
    section_split = section_path.split("/")
    while "" in section_split:
        section_split.remove("")
    module_name = f"sitecode.py.api.{'.'.join(section_split)}"

    try:
        controller = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise Http404()

    kwargs = {}
    for key in request.GET:
        kwargs[key] = request.GET.get(key, None)

    content = controller.process_request(**kwargs)
    content = json.dumps(content)

    return HttpResponse(content, content_type="application/json")


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

