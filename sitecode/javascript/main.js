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
