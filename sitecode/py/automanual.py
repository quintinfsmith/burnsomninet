'''
    Merge together a directory tree of  .md files to make a single .md
    I've built this for 2 reasons:
    1) To allow lazy loading when manuals get a bit bloated
    2) To allow loading individual sections as navicable pages.
'''

import os
import re

CONTENT_PATT = re.compile("^@\\$(?P<cname>.*?)$", re.M)
TITLE_PATT = re.compile("^# (?P<title>.*?)$", re.M)
SUBTITLE_PATT = re.compile("^## (?P<title>.*?)$", re.M)

def build_toc(content_order, subdir_dict):
    output_lines = ["## Table of Contents"]
    stack = [("", content_order, subdir_dict, 0)]
    while stack:
        title, cord, cmap, depth = stack.pop(0)
        if depth > 0:
            gap = " " * (4 * (depth - 1))
            output_lines.append(f"{gap}- [{title}]")

        for key in cord:
            subtitle, subcontent, submap, suborder = cmap[key]
            stack.append((subtitle, suborder, submap, depth + 1))
            if not suborder: # If a suborder isn't given, check the subcontent for subsections
                suborder = []
                for hit in SUBTITLE_PATT.finditer(subcontent):
                    suborder.append((hit.span()[0], hit.group('title')))
                suborder.sort()
                for i, (_, key) in enumerate(suborder):
                    stack.append((key, [], {}, depth + 2))

    return "\n".join(output_lines)


def populate_page(directory, depth=0):
    subdir_dict = {}
    for sublevel in os.listdir(directory):
        if os.path.isdir(f"{directory}/{sublevel}"):
            subdir_dict[sublevel] = populate_page(f"{directory}/{sublevel}", depth+1)
        elif os.path.isfile(f"{directory}/{sublevel}") and sublevel != 'mod.md':
            with open(f"{directory}/{sublevel}", 'r') as fp:
                subcontent = fp.read()

            title = ''
            for hit in TITLE_PATT.finditer(subcontent):
                title = hit.group('title')
                break

            subdir_dict[sublevel[0:sublevel.rfind(".")]] = (title, subcontent, {}, [])

    content = ''
    with open(f"{directory}/mod.md", "r") as fp:
        content = fp.read()

    subcontent_order = []

    for hit in CONTENT_PATT.finditer(content):
        cname = hit.group('cname')
        subcontent_order.append((hit.span()[0], cname))
        subcontent = subdir_dict[cname][1].replace("\n#", "\n##")
        if subcontent[0] == "#":
            subcontent = f"#{subcontent}"

        content = content.replace(f"@${cname}", subcontent.strip())

    subcontent_order.sort()
    for i, (_, key) in enumerate(subcontent_order):
        subcontent_order[i] = key

    if "\n@@TOC\n" in content:
        toc = build_toc(subcontent_order, subdir_dict)
        content = content.replace("@@TOC", toc)


    title = ''
    for hit in TITLE_PATT.finditer(content):
        title = hit.group('title')
        break

    return (title, content, subdir_dict, subcontent_order)

BR_PATT = re.compile("(?P<c>[^\n])\n(?P<c2>[^\n])", re.M)
def extra_markdown(content):
    spans = []
    for hit in BR_PATT.finditer(content):
        spans.append((hit.span(), hit.group('c'), hit.group('c2')))
    spans.sort()

    codespans = []
    code_start = None
    for i, c in enumerate(content):
        if c == "`":
            if code_start is None:
                code_start = i
            else:
                codespans.append((code_start, i))
                code_start = None

    for (a, b), c, d in spans[::-1]:
        incode = False
        for codechunk in codespans:
            if (a >= codechunk[0] and a < codechunk[1]) or (b >= codechunk[0] and b < codechunk[1]):
                incode = True
                break
        if incode:
            continue

        content = f"{content[0:a]}{c}<br/>\n{d}{content[b:]}"
    return content
