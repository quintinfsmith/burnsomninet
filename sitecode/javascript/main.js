function addClass(elm, new_class) {
    elm.classList.add(new_class);
}

function removeClass(elm, old_class) {
    elm.classList.remove(old_class);
}

function hasClass(elm, classname) {
    return elm.classList.contains(classname);
}

function toggleClass(elm, classname) {
    if (hasClass(elm, classname)) {
        removeClass(elm, classname);
    } else {
        addClass(elm, classname);
    }
}

class SlugWidget {
    constructor(element, options) {
        this.element = element;
        this.options = options;
        this.element.innerHTML = "";
    }
}

var EVENTMAP = {};
function touch_to_click_cancel(elm, e) {
    elm.__click_cancelled = true;
}
function touch_to_click_end(elm, e) {
    if (! elm.__click_cancelled) {
        event_trigger(elm, "click");
    }
    elm.__click_cancelled = false;
}

function event_trigger(elm, eventname) {
    var event; // The custom event that will be created
    if (document.createEvent){
        event = document.createEvent("HTMLEvents");
        event.initEvent(eventname, true, true);
        event.eventName = eventname;
        elm.dispatchEvent(event);
    } else {
        event = document.createEventObject();
        event.eventName = eventname;
        event.eventType = eventname;
        elm.fireEvent("on" + event.eventType, event);
    }
}

function event_listen(elm, eventname, function_hook) {
    var eventpath = eventname.split(".");
    var current_branch = EVENTMAP;
    for (var i in eventpath) {
        if (i == eventpath.length - 1) {
            break;
        } else if (!current_branch[eventpath[i]]) {
            current_branch[eventpath[i]] = {};
        }

        current_branch = current_branch[eventpath[i]];
    }

    var eventtype = eventpath[eventpath.length - 1];
    current_branch[eventtype] = function_hook;

    if (eventtype == "click") {
        event_listen(elm, "__.touchmove", touch_to_click_cancel);
        event_listen(elm, "__.touchend", touch_to_click_end);
    }

    elm.addEventListener(eventtype, function_hook);
}

function event_ignore(elm, eventname) {
    var eventpath = eventname.split(".");
    var current_branch = EVENTMAP;
    for (var i in eventpath) {
        if (i == eventpath.length - 1) {
            break;
        } else if (!current_branch[eventpath[i]]) {
            current_branch[eventpath[i]] = {};
        }

        current_branch = current_branch[eventpath[i]];
    }

    var eventtype = eventpath[eventpath.length - 1];
    var hook = current_branch[eventtype];

    elm.removeEventListener(eventtype, hook);
    delete current_branch[eventtype];

    if (eventtype == "click") {
        event_listen(elm, "__.touchmove", touch_to_click_cancel);
        event_listen(elm, "__.touchend", touch_to_click_end);
    }

}

function api_call(url, on_success, on_fail) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);

    xhr.onloadend = function () {
        if (xhr.status == 200) {
            on_success.apply(this, [JSON.parse(this.response)]);
        } else {
            on_fail.apply(this, [this.response]);
        }
    }

    xhr.send();
}

function ajax_call(url, on_success, on_fail) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);

    xhr.onloadend = function () {
        if (xhr.status == 200) {
            on_success.apply(this, [this.response]);
        } else {
            on_fail.apply(this, [this.response]);
        }
    }

    xhr.send();
}

function load_script(url, callback) {
    let script = document.createElement('script');
    script.src = url;
    script.type = 'text/javascript';

    if (callback) {
        script.onload = callback;
    }

    document.getElementsByTagName('head')[0].appendChild(script);
}

function widget_slug_callback() {
    let slug_data = this;
    for (let i = 0; i < slug_data.length; i++) {
        let slug = slug_data[i];
        // FIXME: I don't like this, i just don't have a better idea ATM.
        let classref = eval(slug.classname);
        let new_obj = new classref(slug.element, slug.kwargs);
    }
}

function load_widget_slugs() {
    let slugs = document.getElementsByClassName("widget-slug");

    let payloads = {};
    for (let i = 0; i < slugs.length; i++) {
        let url = slugs[i].getAttribute('data-remote');
        if (! payloads[url]) {
            payloads[url] = [];
        }
        let kwargs = JSON.parse(slugs[i].getAttribute('data-json'));
        let classname = slugs[i].getAttribute('data-class');

        payloads[url].push({
            element: slugs[i],
            classname: classname,
            kwargs: kwargs
        });
    }

    for (let url in payloads) {
        if (url == "main") {
            widget_slug_callback.apply(payloads[url])
        } else {
            load_script(url, widget_slug_callback.bind(payloads[url]))
        }
    }
}

class CustomSelect {
    constructor(option_nodes, onchange) {
        this.value = null;
        this.display = null;
        this.onchange = onchange;
        this.element_select = crel('select');
        this.element_display = crel('div');
        this.element_facade = crel('div',
            {
                "class": "facade",
                "tabindex": 0,
            },
            this.element_display,
            crel('div',
                { 'class': 'arrow' },
                crel('div', { "class": "vh_mid" }),
                crel('div', "\u25BC")
            )
        );

        for (let i = 0; i < option_nodes.length; i++) {
            this.element_select.appendChild(option_nodes[i]);
        }

        this.element = crel('div',
            { "class": "custom-select" },
            crel('div',
                { 'class': 'wrapper' },
                this.element_facade,
                this.element_select
            )
        );

        this.element_select.addEventListener('change', function(e) {
            this.set(this.element_select.value);
            this.onchange(this.element_select.value);
        }.bind(this));

    }

    set(new_value) {
        this.value = new_value;
        this.display = '';
        let option_tags = this.element_select.childNodes;
        for (let i = 0; i < option_tags.length; i++) {
            let option = option_tags[i];
            if (option.value == new_value) {
                option.setAttribute('selected', true);
                this.display = option.text;
            } else {
                option.removeAttribute('selected');
            }
        }

        this.element_display.innerText = this.display;
    }

    get() {
        return this.value;
    }
}

class RelativeVagueDate extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.element.innerText = this.convert_timestamp(options.date);
        let date = new Date(options.date);

        let values = [
            date.getMonth() + 1,
            date.getDate(),
            date.getHours(),
            date.getMinutes()
        ];

        let val_strings = [];
        for (let i = 0; i < values.length; i++) {
            let vstr = values[i].toString();

            if (values[i] < 10) {
                vstr = "0" + vstr;
            }

            val_strings.push(vstr);
        }


        let time_string = date.getFullYear() +
            "-" + val_strings[0] +
            "-" + val_strings[1] +
            " " + val_strings[2] +
            ":" + val_strings[3];
        this.element.title = time_string
    }
    convert_timestamp(timestamp) {
        let then = new Date(timestamp);
        let now = new Date();
        let delta = (now - then);
        let output;
        if (delta <                   2 * 60 * 1000) {
            output = "Just now";
        } else if (delta <       2 * 60 * 60 * 1000) {
            output = Math.round(delta / 60000) + " minutes ago";
        } else if (delta <  2 * 24 * 60 * 60 * 1000) {
            output = Math.round(delta / (60 * 60000)) + " hours ago";
        } else if (delta <  7 * 24 * 60 * 60 * 1000) {
            output = Math.round(delta / (24 * 60 * 60 * 1000)) + " days ago";
        } else if (delta < 11 * 24 * 60 * 60 * 1000) {
            output = "A week ago";
        } else if (delta < 30 * 24 * 60 * 60 * 1000) {
            output = Math.round(delta / (7 * 24 * 60 * 60 * 1000)) + " weeks ago";
        } else if (delta < 42 * 24 * 60 * 60 * 1000) {
            output = "A month ago";
        } else if (delta < 7 * 79 * 24 * 60 * 60 * 1000) {
            output = Math.round(delta / (30 * 24 * 60 * 60 * 1000)) + " months ago";
        } else {
            let year_count = Math.round(delta / (365.25 * 24 * 60 * 60 * 1000));
            output = year_count + " years ago";
        }
        return output;
    }
}

window.onload = function() {
    load_widget_slugs();
    let elements = document.body.getElementsByClassName("numbered-diagram");
    for (let i = 0; i < elements.length; i++) {
        activate_numbered_diagram(elements[i]);
    }
}

class HamburgerMenu extends SlugWidget {
    constructor(element, options) {
        super(element, options);

        let opt_groups = [];
        let is_option_selected = false;
        for (let i = 0; i < options.sitemap.length; i++) {
            let section = options.sitemap[i];
            let opt_group = crel('optgroup', { label: section.name });
            for (let j = 0; j < section.sections.length; j++) {
                let subsection = section.sections[j];
                let opt_args = {
                    value: subsection[1]
                };

                if (subsection[0]){
                    opt_args['selected'] = true;
                    is_option_selected = true;
                }

                opt_group.appendChild(
                    crel('option',
                        opt_args,
                        subsection[2]
                    )
                );
            }
            opt_groups.push(opt_group);
        }

        opt_groups.unshift(
            crel('option',
                { label: 'Home' },
                '/'
            )
        );

        this.select = new CustomSelect(opt_groups, function(href) {
            location.href = href;
        });

        this.element.appendChild(this.select.element);
        this.select.element_facade.replaceWith(crel('div',
            { "class": "hamburger-wrapper" },
            crel('div',
                { "class": "hamburger" },
                crel("div",
                    crel("div"),
                    crel("div"),
                    crel("div"),
                    crel("div"),
                    crel("div")
                )
            )
        ));
    }
}

function activate_numbered_diagram(element) {
    if (element.hasClass("activated") || !element.hasClass("numbered-diagram")) {
        return;
    }
    element.addClass("activated");
    let cells = element.getElementsByClassName("label-layer")[0].getElementsByTagName("span")
    let table = element.getElementsByTagName("table")[0];
    for (let i = 0; i < cells.length; i++) {
        let label = cells[i];
        let row = table.getElementsByTagName("tr")[i];

        event_listen(label, "mouseout", function() {
            removeClass(row, "selected");
            removeClass(label, "selected");
        })
        event_listen(label, "mouseover", function() {
            addClass(row, "selected");
            addClass(label, "selected");
        })
        event_listen(label, "click", function() {
            addClass(row, "selected");
            addClass(label, "selected");
        })
        event_listen(row, "mouseout", function() {
            removeClass(row, "selected");
            removeClass(label, "selected");
        })
        event_listen(row, "mouseover", function() {
            addClass(row, "selected");
            addClass(label, "selected");
        })
        event_listen(row, "click", function() {
            addClass(row, "selected");
            addClass(label, "selected");
        })
    }
}


class IssuesTable extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        /*
            I didn't think enough about the integer of states in the mysql table. So instead of changing the code/data,
            We'll just specify a new order here since I don't think it matters anywhere else.
        */
        this.state_reorder = {
            0: 3, // Cancelled
            1: 1, // Open
            2: 0, // In Progress
            3: 2  // Resolved
        }
        this.current_order = [
            "state",
            "rating",
            "id",
            "title"
        ];

        this.direction_map = {
            "rating": -1,
            "id": 1,
            "state": 1,
            "title": 1
        };

        this.issues = options["issues"];
        this.resort();
        this.populate();
    }

    prioritize_key(key) {
        let index = this.current_order.indexOf(key)
        if (index == -1) {
            return;
        }
        if (index == 0) {
            if (this.direction_map[key] == 1) {
                this.direction_map[key] = -1;
            } else {
                this.direction_map[key] = 1;
            }
        } else {
            this.current_order.splice(index, 1)
            this.current_order.unshift(key)
        }
    }

    resort() {
        let that = this;
        this.issues.sort(function(a, b) {
            for (let i = 0; i < that.current_order.length; i++) {
                let key = that.current_order[i];
                if (key != "state") {
                    if (a[key] > b[key]) {
                        return that.direction_map[key];
                    } else if (a[key] < b[key]) {
                        return that.direction_map[key] * -1;
                    }
                } else {
                    let compare_a = that.state_reorder[a[key]];
                    let compare_b = that.state_reorder[b[key]];
                    if (compare_a > compare_b) {
                        return that.direction_map[key];
                    } else if (compare_a < compare_b) {
                        return that.direction_map[key] * -1;
                    }
                }
            }
            return 0;
        });
    }

    clear() {
        let child_nodes_count = this.element.childNodes.length;
        for (let i = 0; i < child_nodes_count; i++) {
            this.element.childNodes[0].remove();
        }
    }

    populate() {
        let table_header_row = crel("tr",
            crel("th", { "data-key": "id" }, "#"),
            crel("th", { "data-key": "title" }, "Issue"),
            crel("th", { "data-key": "rating" }, "Urgency"),
            crel("th", { "data-key": "state" }, "Status")
        );

        let that = this;
        for (let i = 0; i < table_header_row.childNodes.length; i++) {
            let header = table_header_row.childNodes[i];
            event_listen(header, "click", function() {
                that.prioritize_key(header.dataset["key"]);
                that.resort();
                that.clear();
                that.populate();
            });
        }

        let table = crel("table",
            { "class": "std-table" },
            crel("thead", table_header_row),
            crel("tbody")
        );

        for (let i = 0; i < this.issues.length; i++) {
            let issue = this.issues[i];
            let state = ""
            if (issue["state"] != null) {
                state = ["cancelled", "open", "in progress", "resolved"][issue["state"]]
            }
            let rating = ["feature", "low", "pressing", "urgent"][issue["rating"]]
            let row = crel("tr",
                crel("td", issue["id"]),
                crel("td", crel("span", issue["title"])),
                crel("td",
                    crel("div",
                        { "class": "rating r" + issue["rating"] },
                        rating
                    )
                ),
                crel("td",
                    crel("div",
                        { "class": "status s" + issue["state"] },
                        state
                    )
                )
            );
            event_listen(row, "click", function() {
                window.location.href = "/issue/" + issue["id"]
            });
            table.lastChild.appendChild(row);
        }
        this.element.appendChild(table)
    }
}

class ViewableImg extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.element_overlay = crel("div",
            {
                "class": "img_overlay",
                "data": { "img": this }
            },
            crel("div", { "class": "vh_mid" }),
            crel("img", { "src": this.options.src })
        );


        this.img = crel("img", { "src": this.options.src })
        this.element.appendChild(this.img)


        let that = this;
        event_listen(this.img, "click", function() {
            document.body.appendChild(that.element_overlay);
        });

        event_listen(this.element_overlay, "click", function() {
            that.element_overlay.remove();
        });
    }
}

class StepDiagram extends SlugWidget {
    constructor(element, options) {
        super(element, options);

        for (let i = 0; i < options["entries"].length; i++) {
            let entry = options["entries"][i]
            if (i != 0) {
                this.element.appendChild(
                    crel("div", String.fromCodePoint(0x27F6))
                )
            }

            let label_text = ""
            if (entry["label"]) {
                label_text = (i + 1).toString() + ". " + entry["label"]
            }

            this.element.appendChild(
                crel("div",
                    crel("div",
                        { "class": "img-wrapper" },
                        crel("img", { "src": entry["src"] })
                    ),
                    crel("div", 
                        { "class": "label" },
                        label_text
                    )
                )
            )
        }
    }
}


function toggledm() {
    console.log("boop");
}
