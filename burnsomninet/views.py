import os
import json
import time
import marko
from django.http import HttpResponse, Http404
from django.conf import settings
from sitecode.py.httree import Tag, Text, RawHTML
from burnsomninet import wrappers

SITECODE = settings.SITECODE
STATIC_PATH = settings.STATIC_PATH
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
    midsize = 800
    content = ""
    with open(f"{SCSS_PATH}/main.scss", "r") as file_pipe:
        content = file_pipe.read()

    with open(f"{SCSS_PATH}/mobile.scss", "r") as file_pipe:
        content += f"\n@media only screen and (max-width: {midsize}px) {{\n"
        content += file_pipe.read()
        content += "\n}\n"

    with open(f"{SCSS_PATH}/desktop.scss", "r") as file_pipe:
        content += f"\n@media only screen and (min-width: {midsize}px) {{\n"
        content += file_pipe.read()
        content += "\n}\n"

    content = sass_compile(content)

    return HttpResponse(content, content_type="text/css")

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


def section_controller(request):
    active_path = request.get_full_path().split("/")
    while "" in active_path:
        active_path.remove("")

    sectionsdir = f"{SITECODE}/sections/"
    kwargs = {}
    directory_path = f"{sectionsdir}/{active_path[0]}/{active_path[1]}"
    files = os.listdir(directory_path)
    for file_name in files:
        if file_name == 'head.json':
            continue

        ext = file_name[file_name.rfind(".") + 1:].lower()
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

    head_kwargs = {}
    if os.path.isfile(f"{directory_path}/head.json"):
        with open(f"{directory_path}/head.json", 'r') as file_pipe:
            head_kwargs = json.loads(file_pipe.read())

    body_content = VIEWMAP[active_path[0]][active_path[1]](request, **kwargs)
    top = Tag("html",
        wrappers.build_head(**head_kwargs),
        Tag("body",
            wrappers.build_sitemap(*active_path),
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

