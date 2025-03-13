from sitecode.py import automanual
from burnsomninet.views import STATIC_PATH, SITECODE
import json
import marko
from datetime import datetime, timedelta
import time, os

def process_request(**kwargs):
    manual = kwargs.get("m", None)
    if manual is None:
        raise Exception("") # TODO: 404 in api?
    

    manualsdir = f"{SITECODE}/manuals/"
    directory_path = f"{manualsdir}/{manual}/"

    if not os.path.isdir(directory_path):
        raise Exception("") # TODO: 404

    raw_content = automanual.populate_page(directory_path, f"/manual/{manual}")
    raw_content = automanual.do_slugs(raw_content)
    description = raw_content[raw_content.find("## About") + 8:].strip()
    description = description[0:description.find("\n")]

    raw_content = automanual.replace_svg(raw_content, STATIC_PATH)
    raw_content = automanual.extra_markdown(raw_content)
    return {
        "html": marko.convert(raw_content)
    }
