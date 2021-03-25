import json, os
from httree import Tag, Text

VHACK = Tag('div', { "class": "vhack" })

def build_sitemap():
    sitemap = Tag("div", { "class": "sitemap" })
    sectionsdir = "/srv/http/burnsomninet/burnsomninet/sections/"

    headings = os.listdir(sectionsdir)
    headings.sort()
    for heading in headings:
        entry = Tag("div", { "class": "entry" })
        entry.append(
            Tag('div',
                { 'class': 'header' },
                VHACK,
                Tag('div', heading.title())
            )
        )
        files = os.listdir(sectionsdir + heading)
        files.sort()
        for f in files:
            title = f[0:f.rfind(".")]
            entry.append(
                Tag('a',
                    {
                        'class': 'item',
                        'href': "/%s/%s"  % (heading.lower(), title)
                    },
                    VHACK,
                    Tag('div', title.title())
                )
            )
        sitemap.append(entry)

    return sitemap

