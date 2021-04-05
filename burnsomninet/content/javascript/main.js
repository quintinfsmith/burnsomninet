function addClass(new_class) {
    var classes = this.className.toLowerCase().split(" ");
    if (classes.indexOf(new_class.toLowerCase()) == -1) {
        classes.push(new_class.toLowerCase());
    }
    this.className = classes.join(" ");
}

function removeClass(old_class) {
    var classes = this.className.toLowerCase().split(" ");
    while (classes.indexOf(old_class.toLowerCase()) != -1) {
        classes.splice(classes.indexOf(old_class.toLowerCase()), 1);
    }
    this.className = classes.join(" ");
}

