class HamburgerMenu extends WidgetSlug {
    constructor(element, options) {
        super(element, options);

        this.element.classList.add('hamburger-wrapper');
        this.element.appendChild(
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
        );
    }
}
