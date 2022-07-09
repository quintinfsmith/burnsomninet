import html
TABWIDTH = 0
RETURN = ""

class Node:
    def __init__(self, tname, **attributes):
        self.name = tname.lower().strip()
        self.attributes = attributes

    def to_markup(self, depth=0):
        return ""

class Tag(Node):
    self_closing = [ "link", "img" ]
    def __init__(self, tagname, *children):
        self.children = []
        attributes = {}
        for child in children:
            if isinstance(child, dict):
                attributes = child
            elif isinstance(child, str):
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
        output = "<%s" % self.name
        for key, value in self.attributes.items():
            if isinstance(value, dict):
                tojoin = []
                for k, v in value.items():
                    tojoin.append("%s: %s" % (k, v))
                output += " %s=\"%s\"" % (key, "; ".join(tojoin))
            else:
                output += " %s=\"%s\"" % (key, html.escape(str(value)))

        if not self.name in self.self_closing:
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

