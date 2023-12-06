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
    console.log("Loading widget slugs")
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

class NumberedDiagram extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        let item_table = crel("table")
        let label_layer = crel("div", {
            "class": "label-layer"
        })
        for (let i = 0; i < options["entries"].length; i++) {
            let padded_i = (i + 1).toString()
            while (padded_i.length < 2) {
                padded_i = "0" + padded_i
            }
            item_table.appendChild(
                crel("tr",
                    crel("td", padded_i),
                    crel("td", options["entries"][i][2])
                )
            )

            let x = (options["entries"][i][0] * 100).toString() + "%"
            let y = (options["entries"][i][1] * 100).toString() + "%"
            let label = crel("span", {
                    "class": "label",
                    "style": "position: absolute; left: " + x + "; top: " + y
                },
                padded_i
            )

            event_listen(label, "mouseout", function() {
                removeClass(item_table.children[i], "selected")
                removeClass(label, "selected")
            })
            event_listen(label, "mouseover", function() {
                addClass(item_table.children[i], "selected")
                addClass(label, "selected")
            })
            event_listen(label, "click", function() {
                addClass(item_table.children[i], "selected")
                addClass(label, "selected")
            })
            event_listen(item_table.children[i], "mouseout", function() {
                removeClass(item_table.children[i], "selected")
                removeClass(label, "selected")
            })
            event_listen(item_table.children[i], "mouseover", function() {
                addClass(item_table.children[i], "selected")
                addClass(label, "selected")
            })
            event_listen(item_table.children[i], "click", function() {
                addClass(item_table.children[i], "selected")
                addClass(label, "selected")
            })

            label_layer.appendChild(label)
        }

        this.element.appendChild(
            crel("div",
                crel("div", { "class": "padding" }),
                crel("div",
                    crel("img", {
                        "src": options["img"]
                    }),
                    label_layer
                ),
                crel("div", { "class": "padding" })
            )
        )
        this.element.appendChild(crel("div", item_table))
    }
}
