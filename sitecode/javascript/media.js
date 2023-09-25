class MediaPlayer {
    constructor(options) {
        this.element = crel('div');
        this.options = options;
        this.active_index = 0;
        this.title = options.title;

        this.element_overlay = crel('div', {
            class: 'mp_overlay',
            data: {
                media_player: this
            }
        });

        this.element_video = crel('video', {
            controls: true,
            loop: true,
            style: "opacity: 0"
        });
        event_listen(this.element_video, 'loadeddata', function(event) {
            this.style.opacity = 1;
        });

        this.element_selector = null;
        if (this.options.srcs.length > 1) {
            this.element_selector = crel('div',
                { class: 'mp_selector' }
            );

            for (var vid in this.options.srcs) {
                var vidobj = crel('img', {
                    src: this.options.srcs[vid] + '.png',
                });

                var div = crel('div',
                    {
                        class: "thumb",
                        data: {
                            media_player: this,
                            index: vid
                        }
                    },
                    crel('div', {
                        'style': 'background-image: url("' + this.options.srcs[vid] + '.png");'
                    })
                );

                event_listen(vidobj, 'error', function(event) {
                    this.parentNode.removeChild(this);
                });

                event_listen(div, 'click', function(event) {
                    var data = this.data;
                    data.media_player.set_video(data.index);
                });
                this.element_selector.appendChild(div);
            }
        }

        var xbutton = crel('div',
            {
                class: "close_button",
                data: {
                    media_player: this
                }
            },
            crel('div', { class: 'vh_mid' }),
            crel('div', "X")
        );

        event_listen(xbutton, 'click', function(event) {
            var media_player = this.data.media_player;
            media_player.kill();
        });

        var title_element = null;
        if (this.title) {
            title_element = crel('div',
                { class: "mp_title" },
                crel('div',
                    crel('div', { class: "vh_mid" }),
                    crel('div', this.title)
                )
            );
        }

        this.element.appendChild(
            crel('div',
                crel('div', xbutton),
                crel('div',
                    crel('div',
                        { class: "mp_video_wrapper" },
                        crel('div', { class: "vh_mid" }),
                        this.element_video
                    ),
                    crel('div',
                     //   title_element,
                        this.element_selector
                    )
                )
            )
        );


        document.body.appendChild(this.element_overlay);
        this.element_overlay.appendChild(
            crel('div',
                crel('div', { class: 'vh_mid' }),
                this.element
            )
        );
        this.element.className = "media_player";

        this.set_video(0);

        event_listen(this.element, 'click', function(event) {
            event.stopPropagation();
        });

        event_listen(this.element_overlay, 'click', function(event) {
            this.data.media_player.kill();
        });

        this.overflow_backup = window.getComputedStyle(document.body).overflow;
        document.body.style.setProperty("overflow", "hidden");



        crel(document.body, {
            data: { MP: this }
        });

        event_listen(window, "mediacenter.resize",  function(event) {
            var media_player = document.body.data.MP;
            media_player.reposition();
        });

        event_listen(window, "mediacenter.keydown", function(event) {
            if (event.keyCode == 27) {
                var media_player = document.body.data.MP;
                media_player.kill();
            }
        });
        this.reposition();
    }

    reposition() {
        this.element_overlay.style.setProperty("top", window.scrollY + "px");
    }

    set_video(index) {
        var src = this.options.srcs[index % this.options.srcs.length];
        this.element_video.style.opacity = 0;
        this.element_video.setAttribute('src', src);

        if (this.element_selector) {
            var prev_thumb = this.element_selector.childNodes[this.active_index];
            var current_thumb = this.element_selector.childNodes[index];
            removeClass(prev_thumb, 'selected');
            addClass(current_thumb, 'selected');
            current_thumb.scrollIntoView();
        }

        this.active_index = index;
    }

    kill() {
        this.element_overlay.parentNode.removeChild(this.element_overlay);
        document.body.style.setProperty("overflow", this.overflow_backup);
        delete document.body.data.MP;

        event_ignore(window, "mediacenter.resize");
        event_ignore(window, "mediacenter.keydown");
    }
}

function polaroid_open_mediaplayer(elm) {
    var srcs = JSON.parse(elm.dataset['srcs']);
    new MediaPlayer({
        srcs: srcs,
        title: elm.textContent.trim()
    });
}

(function() {
    var media = document.body.getElementsByClassName("polaroid");
    for (var i = 0; i < media.length; i++) {
        var elm = media[i];
        event_listen(elm, "click", function(event) {
            polaroid_open_mediaplayer(this)
        });
    }

    var pieces = window.location.hash.split("?");
    while (pieces.length > 1) {
        pieces.pop();
    }
    //if (pieces.length > 0) {
    //    var hashid = pieces[0].substring(1);
    //    event_trigger(document.getElementById(hashid), 'click');
    //}

})()
