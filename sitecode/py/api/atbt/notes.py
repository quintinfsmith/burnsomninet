from sitecode.py.atbt import MariaObj, Tracker

import json
from datetime import datetime
import time

def process_request(**kwargs):
    # -------------------------------------------- #
    project_name = kwargs.get("project", "notaproject")
    # -------------------------------------------- #
    output = []
    tracker = Tracker(project_name, "tracker@burnsomni.net")
    issues = {}
    for issue_note in tracker.get_latest_notes(kwargs.get("limit", 0)):
        output.append(issue_note)
    # -------------------------------------------- #
    return output

