from sitecode.py.gitmanip import Project
from sitecode.py.cachemanager import get_cached, check_cache, update_cache
from sitecode.py import api
from burnsomninet.views import STATIC_PATH

import json
from datetime import datetime, timedelta
import time, os

def process_request(**kwargs):
    svg_github = ""
    with open(f"{STATIC_PATH}/icons/github.svg", "r") as fp:
        svg_github = fp.read()

    svg_email = ""
    with open(f"{STATIC_PATH}/icons/email.svg", "r") as fp:
        svg_email = fp.read()

    svg_bsky = ""
    with open(f"{STATIC_PATH}/icons/bsky.svg", "r") as fp:
        svg_bsky = fp.read()


    svg_keybase = ""
    with open(f"{STATIC_PATH}/icons/keybase.svg", "r") as fp:
        svg_keybase = fp.read()

    svg_kofi = ""
    with open(f"{STATIC_PATH}/icons/kofi.svg", "r") as fp:
        svg_kofi = fp.read()

    return [
        {
            "href": "mailto:smith.quintin@protonmail.com",
            "alt": "Email",
            "svg": svg_email
        },
        {
            "href": "https://github.com/quintinfsmith",
            "alt": "Github",
            "svg": svg_github
        },
        {
            "href": "https://bsky.app/profile/quintinfsmith.bsky.social",
            "alt": "Bluesky",
            "svg": svg_bsky
        },
        {
            "href": "https://keybase.io/quintinfsmith",
            "alt": "Keybase",
            "svg": svg_keybase
        },
        {
            "href": "https://ko-fi.com/quintinfsmith",
            "alt": "Ko-Fi",
            "svg": svg_kofi
        }
    ]
