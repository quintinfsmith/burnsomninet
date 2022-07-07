import json, os
from sitecode.py.httree import Tag, Text, RawHTML
from django.conf import settings
from sitecode.py.gitmanip import Project as GitProject

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
        #Tag("script", {
        #    "src": "/content/javascript/inheritance.js",
        #    "type": "text/javascript"
        #}),
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

def build_git_overview(project, branch, path=""):
    git_project = GitProject(f"{GIT_PATH}/{project}")
    branch = git_project.get_branch()

    body_content = Tag("table")

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

    for endpoint, (commit_id, _, is_file) in max_commit_ids.items():
        commit = branch.get_commit(commit_id)
        sorter_list.append((is_file, endpoint, commit_id, commit.get_description()))

    sorter_list.sort()
    for is_file, pathname, commit_id, description in sorter_list:

        full_path = path + pathname

        if not is_file:
            full_path += "/"

        body_content.append(
            Tag("tr",
                Tag("td",
                    Tag("a",
                        { "href": f"/git/{project}?path={full_path}" },
                        pathname
                    )
                ),
                Tag("td",
                    { 'title': commit_id },
                    description
                )
            )
        )

    return body_content


def build_git_file_view(project, branch, path):

    return Tag("div", f"File Overview for {path}")
