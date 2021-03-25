from django.http import HttpResponse, Http404
from django.shortcuts import render
import os, json
from httree import Tag, Text
import wrappers
import sass

def handle404(request, exception):
    top = Tag("html",
        Tag("head",
            Tag("style", { }),
        ),
        Tag("body",
            Tag("div",
                "Looks like you've gone and picked yourself an oopsie daisy there, friend."
            )
        )
    )

    return HttpResponse(top.__repr__(), status=404)

#def testt(request):
#    return HttpResponse(str(dir(request)) + "\n" + request.get_full_path())
#

def style(request):
    content = ""
    with open("/srv/http/burnsomninet/burnsomninet/style.css", "r") as fp:
        content = fp.read()
    content = sass.compile(string=content)

    return HttpResponse(content, content_type="text/css")


def index(request):
    top = Tag("html",
        Tag("head",
            Tag("link", {
                "rel": "stylesheet",
                "type": "text/css",
                "href": "/style.css"
            }),
        ),
        Tag("body",
            wrappers.build_sitemap()
        )
    )

    return HttpResponse(top.__repr__())

