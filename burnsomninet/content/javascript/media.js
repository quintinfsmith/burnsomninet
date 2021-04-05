define_class("MediaPlayer", {
    init: function(options) {
        this.super('init', crel('div'), options);
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
            loop: true
        });
        this.element_selector = crel('div',
            { class: 'mp_selector' }
        );

        for (var vid in this.options.srcs) {
            var vidobj = crel('img', {
                src: this.options.srcs[vid] + '.jpg',
            });

            var div = crel('div',
                {
                    class: "thumb",
                    data: {
                        media_player: this,
                        index: vid
                    }
                },
                crel('div',
                    vidobj
                )
            );

            event_listen.call(vidobj, 'error', function(event) {
                this.parentNode.removeChild(this);
            });

            event_listen.call(div, 'click', function(event) {
                var data = this.data;
                data.media_player.set_video(data.index);
            });
            this.element_selector.appendChild(div);
        }

        var video_wrapper = crel('div');
        video_wrapper.appendChild(
            crel('div',
                { class: "mp_video_wrapper" },
                crel('div', { class: "vh_mid" }),
                this.element_video
            )
        );
        if (this.title) {
            video_wrapper.appendChild(
                crel('div',
                    { class: "mp_title" },
                    crel('div', { class: "vh_mid" }),
                    crel('div', this.title)
                )
            );
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

        event_listen.call(xbutton, 'click', function(event) {
            var media_player = this.data.media_player;
            media_player.kill();
        });

        this.element.appendChild(crel('div', xbutton));
        this.element.appendChild(video_wrapper);
        this.element.appendChild(this.element_selector);

        document.body.appendChild(this.element_overlay);
        this.element_overlay.appendChild(
            crel('div',
                crel('div', { class: 'vh_mid' }),
                this.element
            )
        );
        this.element.className = "media_player";

        this.set_video(0);

        event_listen.call(this.element, 'click', function(event) {
            event.stopPropagation();
        });

        event_listen.call(this.element_overlay, 'click', function(event) {
            this.data.media_player.kill();
        });

        this.overflow_backup = window.getComputedStyle(document.body).overflow;
        document.body.style.setProperty("overflow", "hidden");



        crel(document.body, {
            data: { MP: this }
        });

        event_listen.call(window, "mediacenter.resize",  function(event) {
            var media_player = document.body.data.MP;
            media_player.reposition();
        });
        this.reposition();
    },

    reposition: function() {
        this.element_overlay.style.setProperty("top", window.scrollY + "px");
    },

    set_video: function(index) {
        var src = this.options.srcs[index % this.options.srcs.length];

        this.element_video.setAttribute('src', src);

        var prev_thumb = this.element_selector.childNodes[this.active_index];
        var current_thumb = this.element_selector.childNodes[index];
        removeClass.call(prev_thumb, 'selected');
        addClass.call(current_thumb, 'selected');

        this.active_index = index;
    },

    kill: function() {
        this.element_overlay.parentNode.removeChild(this.element_overlay);
        document.body.style.setProperty("overflow", this.overflow_backup);
        delete document.body.data.MP;
        event_ignore.call(document.body, "mediacenter.resize");
    }

}, "Compound");

function polaroid_open_mediaplayer() {
    var srcs = JSON.parse(this.dataset['srcs']);
    new MediaPlayer({
        srcs: srcs,
        title: this.textContent.trim()
    });
}

(function() {
    var media = document.body.getElementsByClassName("polaroid");
    for (var i = 0; i < media.length; i++) {
        var elm = media[i];
        event_listen.call(elm, "click", function(event) {
            polaroid_open_mediaplayer.call(this)
        });
    }
})()
