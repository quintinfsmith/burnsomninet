from django.http import HttpResponse, Http404
from django.shortcuts import render
import os, json
from httree import Tag, Text, RawHTML
import wrappers
import sass
import marko

from django.conf import settings
SITE_PATH = settings.SITE_PATH

def handle404(request, exception):
    top = Tag("html",
        Tag("head",
            Tag("style", { }),
        ),
        Tag("body",
            Tag("div",
                "Looks like you've gone and picked yourself an oopsie daisy there, friend.")
        )
    )

    return HttpResponse(top.__repr__(), status=404)

#def handle500(request):
#    top = Tag("html",
#        Tag("head",
#            Tag("style", { }),
#        ),
#        Tag("body",
#            Tag("div",
#                "Looks like I've gone and picked myself an oopsie daisy.")
#        )
#    )
#
#    return HttpResponse(top.__repr__(), status=500)


#def testt(request):
#    return HttpResponse(str(dir(request)) + "\n" + request.get_full_path())

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

def style(request):
    midsize = 1000
    content = ""
    with open("%s/styles/main.scss" % SITE_PATH, "r") as fp:
        content = fp.read()

    with open("%s/styles/mobile.scss" % SITE_PATH, "r") as fp:
        content += "\n@media only screen and (max-width: %dpx) {\n" % midsize
        content += fp.read()
        content += "\n}\n"

    with open("%s/styles/desktop.scss" % SITE_PATH, "r") as fp:
        content += "\n@media only screen and (min-width: %spx) {\n" % midsize
        content += fp.read()
        content += "\n}\n"

    content = sass.compile(string=content)

    return HttpResponse(content, content_type="text/css")

def section_json(request):
    active_path = request.get_full_path().split("/")
    while "" in active_path:
        active_path.remove("")

    sectionsdir = "%s/sections/" % SITE_PATH
    json_path = sectionsdir + "/".join(active_path)
    content = "{}"
    with open(json_path, "r") as fp:
        content = fp.read()

    return HttpResponse(content, content_type="application/json")


def section_controller(request):
    active_path = request.get_full_path().split("/")
    while "" in active_path:
        active_path.remove("")

    sectionsdir = "%s/sections/" % SITE_PATH
    kwargs = {}
    directory_path = "%s/%s/%s" % (sectionsdir, *active_path)
    files = os.listdir(directory_path)
    for f in files:
        ext = f[f.rfind(".") + 1:].lower()
        file_path = "%s/%s" % (directory_path, f)
        content = None
        if ext == "json":
            content = {}
            with open(file_path, "r") as fp:
                content = json.loads(fp.read())
        elif ext == "md":
            content = ""
            with open(file_path, "r") as fp:
                content = marko.convert(fp.read())

        if content != None:
            kwargs[ext] = content

    top = Tag("html",
        wrappers.build_head(),
        Tag("body",
            wrappers.build_sitemap(*active_path),
            Tag("div",
                { "class": "content" },
                VIEWMAP[active_path[0]][active_path[1]](request, **kwargs)
            )
        )
    )

    return HttpResponse(top.__repr__())

def index(request):
    active_path = request.get_full_path().split("/")

    while "" in active_path:
        active_path.remove("")

    top = Tag("html",
        wrappers.build_head(),
        Tag("body",
            wrappers.build_sitemap(*active_path),
            Tag("div",
                { "class": "content index" },
                Tag("div", { "class": "vh_mid" }),
                Tag("div",
                    Tag("div",
                        { "class": "img_wrapper" },
                        Tag("img", {
                            "src": "https://secure.gravatar.com/avatar/a5c06e62c415e83649434e3e668b1ff6?size=400"
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

    return HttpResponse(top.__repr__())

