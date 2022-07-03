import json, os
from httree import Tag, Text, RawHTML
from django.conf import settings
SITE_PATH = settings.SITE_PATH


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
            "href": "/style.css"
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
        #Tag("script", {
        #    "src": "/content/javascript/inheritance.js",
        #    "type": "text/javascript"
        #}),
        Tag("script", {
            "src": "/content/javascript/main.js",
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
    with open("%s/content/logo.svg" % SITE_PATH, "r") as fp:
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
                "src": "/content/javascript/hamburger.js",
                "type": "text/javascript"
            })
        )
    )
    sectionsdir = "%s/sections/" % SITE_PATH

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
                        'href': "/%s/%s"  % (heading, title)
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
            abs_src = SITE_PATH + "/" + src
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
            "src": "/content/javascript/media.js",
            "type": "text/javascript"
        })
    )

    return output

