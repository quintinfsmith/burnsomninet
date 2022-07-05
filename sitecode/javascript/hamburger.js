(function() {
    var hamburger = document.getElementsByClassName("hamburger")[0];
    event_listen(hamburger, "click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var tree = document.getElementsByClassName("treemap")[0];
        var content = document.getElementsByClassName("content")[0];
        if (!hasClass(tree, "visible")) {
            event_listen(content, "hamburger.click", function(e) {
                event_ignore(this, "hamburger.click");
                toggleClass(tree, "visible");
                toggleClass(content, "active");
            });
        } else {
            event_ignore(content, "hamburger.click");
        }
        toggleClass(tree, "visible");
        toggleClass(this, "active");
    });
})()
