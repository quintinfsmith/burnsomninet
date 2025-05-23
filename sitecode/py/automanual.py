'''
    Merge together a directory tree of  .md files to make a single .md
    I've built this for 2 reasons:
    1) To allow lazy loading when manuals get a bit bloated
    2) To allow loading individual sections as navicable pages.
'''

import os
import json
import re
import html

SVG_PATT = re.compile(r"!\[(?P<desc>.*?)\]\((?P<path>.*?svg)\)", re.M)
CONTENT_PATT = re.compile("^@\\$(?P<cname>.*?)$", re.M)
TITLE_PATT = re.compile("^# (?P<title>.*?)$", re.M)
SUBTITLE_PATT = re.compile("^### (?P<title>.*?)$", re.M)
def get_all_paths(directory):
    output = []
    for sublevel in os.listdir(directory):
        if os.path.isdir(f"{directory}/{sublevel}"):
            if os.path.isfile(f"{directory}/{sublevel}/mod.md"):
                output.append([sublevel])

            for subpath in get_all_paths(f"{directory}/{sublevel}"):
                subpath.insert(0, sublevel)
                output.append(subpath)

        elif os.path.isfile(f"{directory}/{sublevel}") and sublevel != 'mod.md':
            output.append([sublevel[0:sublevel.rfind(".")]])

    return output


def do_slugs(content):
    matches = []
    pivot = 0
    while True:
        i = content.find("~SLUG", pivot)
        if i == -1:
            break

        pivot = i + 5

        bracket_count = 0
        escape_flag = False
        for x, c in enumerate(content[i + 5:]):
            if c == "\\":
                escape_flag = True
                continue

            if c == "{":
                bracket_count += 1
            elif c == "}":
                if not escape_flag:
                    bracket_count -= 1

            escape_flag = False

            if bracket_count == 0:
                matches.append((x + 6 + i, i, json.loads(content[i + 5: x + i + 6])))
                break

    matches.sort()

    for (end, start, json_obj) in matches[::-1]:
        classname = json_obj["class"]
        slug_name = json_obj["slug"]
        data_json = html.escape(json.dumps(json_obj["data-json"]))
        new_string = f"""<div class="widget-slug {classname}" data-class="{slug_name}" data-json="{data_json}" data-remote="main"></div>"""
        content = content[0:start] + new_string + content[end:]

    return content

def populate_page(directory, url_path=""):
    content = ''

    if "sbyte" in directory:
        with open(f"{directory}/main.html", "r") as fp:
            content = fp.read()
        return content


    section_paths = get_all_paths(directory)

    with open(directory + '/mod.md', 'r') as fp:
        content = fp.read()

    path_info = []
    for path in section_paths:
        subpath = "/".join(path)
        wpath = f"{directory}/{subpath}"
        node = path[-1]
        reptag = f"@${node}"
        if reptag in content:
            subcontent = None
            if os.path.isfile(wpath + '/mod.md'):
                with open(wpath + '/mod.md', 'r') as fp:
                    subcontent = fp.read()
            elif os.path.isfile(wpath + '.md'):
                with open(wpath + '.md', 'r') as fp:
                    subcontent = fp.read()

            if subcontent is None:
                continue

            subcontent_title = ""
            for hit in TITLE_PATT.finditer(subcontent):
                subcontent_title = hit.group("title")
                break



            # Adjust octothorp tags to reflect depth of content
            subtitle_tagger = "#" * (len(path) + 1)
            subcontent = ("\n" + subcontent).replace("\n#", f"\n{subtitle_tagger}").strip()

            # Find and replace the @$ tag
            pivot = content.find(reptag)
            sb_len = len(subcontent)
            # Adjust the already recorded insertion points of other subcontent
            for i, (index, key, title) in enumerate(path_info):
                if index > pivot:
                    path_info[i] = (index + sb_len - len(reptag), key, title)

            path_info.append((pivot, subpath, subcontent_title))


            for hit in SUBTITLE_PATT.finditer(subcontent):
                subsection_title = hit.group("title")
                subpivot = pivot + hit.span()[0]
                subsubpath = path.copy()
                subsubpath.append(subsection_title.replace(" ", "-").lower())
                path_info.append((subpivot, "/".join(subsubpath), subsection_title))


            content = content[0:pivot] + subcontent + content[pivot + len(reptag):]

    if "@@TOC" in content:

        #toc_lines = ["## Table of Contents"]

        #path_info.sort()
        #for insert_point, subpath, title in path_info:
        #    depth = subpath.count('/')
        #    key = subpath.replace("/", "_")
        #    depth_buffer = " " * (depth * 4)
        #    toc_lines.append(f"{depth_buffer}- [{title}](#{key})")

        #for insert_point, subpath, _title in path_info[::-1]:
        #    key = subpath.replace("/", "_")
        #    content = content[0:insert_point] + f"<a name=\"{key}\"></a>\n" + content[insert_point:]

        (toc, link_pairs) = build_toc(content, url_path)

        lines = content.split("\n")
        link_pairs.sort()
        for (index, key) in link_pairs[::-1]:
            lines.insert(index, f"<a name=\"{key}\"></a>")

        toc.insert(0, "## Table of Contents")

        content = "\n".join(lines).replace("@@TOC", "<span class=\"md-table-of-contents\">\n\n" + "\n".join(toc) + "\n\n</span>")

    return content

def build_toc(content, url_path=""):
    lines = content.split("\n")
    top_node = { "node": None,  "children": [] }
    working_position = []
    last_count = 0
    y = 0
    for line in lines:
        if line.startswith("#"):
            hashtag_count = 0

            while hashtag_count < len(line) and line[hashtag_count] == "#":
                hashtag_count += 1

            if hashtag_count > 1:
                hashtag_count -= 1
                if hashtag_count > last_count:
                    working_position += [0] * (hashtag_count - last_count)
                elif hashtag_count == last_count:
                    working_position[-1] += 1
                else:
                    working_position = working_position[0:hashtag_count] 
                    working_position[-1] += 1

                check = top_node
                for p in working_position:
                    while len(check["children"]) <=p:
                        check["children"].append({ "node": None, "children": [] })
                    check = check["children"][p]

                last_count = hashtag_count

                check["node"] = (line[hashtag_count + 1:].strip(), y)
        y += 1
    return _build_toc_from_tree(top_node, 0, [], url_path)


def _build_toc_from_tree(node, depth=0, key_split=None, url_path=""):
    if key_split is None:
        key_split = []

    node_content = node["node"]
    logg(node_content, depth)

    key_indices = []
    output_lines = []

    if node_content is None:
        new_key_split = key_split.copy()
        level_tag = "top"
    else:
        level_tag = node_content[0].replace("#", "").replace(" ", "-").strip().replace("?", "").lower()
        new_key_split = key_split.copy() + [level_tag]
        working_key = "_".join(new_key_split)

        output_lines.append(f"{'    ' * (depth - 1)}- [{node_content[0]}]({url_path}#{working_key})")

        key_indices.append((node_content[1], working_key))

    for child_node in node["children"]:
        (working_lines, working_key_indices) = _build_toc_from_tree(child_node, depth + 1, new_key_split, url_path)

        output_lines += working_lines
        key_indices += working_key_indices

    return (output_lines, key_indices)



def logg(*msgs):
    return
#    with open("/var/log/httpd/burnsomninet/log", "a") as fp:
#        v = []
#        for msg in msgs:
#            v.append(str(msg))
#
#        fp.write(", ".join(v) + "\n")
            

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
        if d == "[":
            continue
        if c == ">":
            continue
        for codechunk in codespans:
            if (a >= codechunk[0] and a < codechunk[1]) or (b >= codechunk[0] and b < codechunk[1]):
                incode = True
                break
        if incode:
            continue

        content = f"{content[0:a]}{c}<br/>\n{d}{content[b:]}"

    return content

def replace_svg(content, root_path):
    ordered_matches = []
    for hit in SVG_PATT.finditer(content):
        ordered_matches.append((hit.span(), hit.group('desc'), hit.group('path')))
    ordered_matches.sort()

    for (a, b), desc, path in ordered_matches[::-1]:
        svg_path = f"{root_path}{path}"
        if not os.path.isfile(svg_path):
            continue

        svg_content = ""
        with open(svg_path) as fp:
            svg_content = fp.read().replace("\n", "")

        content = f"{content[0:a]}<span class=\"inline-svg\">{svg_content}</span>{content[b:]}"
    return content

if __name__ == "__main__":
    import sys
    print(populate_page(sys.argv[1]))

