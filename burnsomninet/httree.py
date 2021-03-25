TABWIDTH = 4
RETURN = "\n"

class Node:
    def __init__(self, name, **attributes):
        self.name = name.lower().strip()
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
            else:
                self.children.append(child)

        super().__init__(tagname, **attributes)



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
                output += " %s=\"%s\"" % (key, value)

        if not self.name in self.self_closing:
            output += ">"

            for child in self.children:
                output += RETURN + (" " * ((depth + 1) * TABWIDTH)) + child.to_markup(depth + 1)

            output += RETURN + (" " * (depth * TABWIDTH)) + "</%s>" % self.name
        else:
            output += " />"

        return output

class Text(Node):
    def __init__(self, text):
        self.text = text

    def to_markup(self, depth=0):
        return self.text

