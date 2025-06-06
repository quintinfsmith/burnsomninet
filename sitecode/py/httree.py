import html
import json
TABWIDTH = 0
RETURN = ""

class Node:
    def __init__(self, tname, **attributes):
        self.name = tname.lower().strip()
        self.attributes = attributes

    def to_markup(self, depth=0):
        return ""

class Tag(Node):
    self_closing = [ "img", "link" ]
    def __init__(self, tagname, *children):
        self.children = []
        self.contains_text = False
        attributes = {}
        for child in children:
            if isinstance(child, dict):
                attributes = child
            elif isinstance(child, str):
                self.contains_text = True
                self.children.append(Text(child))
            elif child:
                self.children.append(child)

        super().__init__(tagname, **attributes)

    def get_attribute(self, key):
        return self.attributes[key]

    def set_attribute(self, key, new_value):
        self.attributes[key] = new_value

    def append(self, child):
        self.children.append(child)

    def pop(self, n=-1):
        return self.children.pop(n)

    def __repr__(self):
        return self.to_markup()

    def to_markup(self, depth=0):
        if self.name.lower() == "html" and depth == 0:
            output = "<!DOCTYPE html>"
        else:
            output = ""

        output += "<%s" % self.name
        for key, value in self.attributes.items():
            if isinstance(value, dict):
                tojoin = []
                for k, v in value.items():
                    tojoin.append("%s: %s" % (k, v))
                output += " %s=\"%s\"" % (key, "; ".join(tojoin))
            else:
                output += " %s=\"%s\"" % (key, html.escape(str(value)))

        if not self.name in self.self_closing or self.contains_text:
            output += ">"

            for child in self.children:
                output += RETURN + (" " * ((depth + 1) * TABWIDTH)) + child.to_markup(depth + 1)

            output += RETURN + (" " * (depth * TABWIDTH)) + "</%s>" % self.name
        else:
            output += " />"

        return output

class RawHTML(Node):
    def __init__(self, text):
        super().__init__("_html")
        self.text = text

    def to_markup(self, depth=0):
        return self.text

class Text(Node):
    def __init__(self, text):
        super().__init__("_text")
        self.text = text

    def to_markup(self, depth=0):
        return html.escape(self.text)


def slug_tag(remote, classname, **kwargs):
    opts = {
        "class": f"widget-slug slug-{classname}",
        "data-remote": remote,
        "data-class": classname,
        "data-json": json.dumps(kwargs)
    }

    return Tag("div", opts)
