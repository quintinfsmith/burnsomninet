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

function ajax_call(url, on_success, on_fail) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);

    xhr.onreadystatechange = function () {
        if (this.readyState == 4) {
            if (this.status == 200) {
                on_success.apply(this);
            } else {
                on_fail.apply(this);
            }
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
        load_script(url, widget_slug_callback.bind(payloads[url]))
    }
}

window.onload = function() {
    load_widget_slugs();
}
