from sitecode.py.atbt import Tracker

import json
from datetime import datetime
import time

def process_request(**kwargs):
    # -------------------------------------------- #
    date_from = float(kwargs.get("datefrom", 0))
    date_to = float(kwargs.get("dateto", time.time()))

    project_name = kwargs.get("project", "")

    str_states = kwargs.get("states", "0,1,2,3,4")
    states = set()
    for state in str_states.split(","):
        try:
            states.add(int(state.strip()))
        except ValueError as e:
            pass

    # -------------------------------------------- #
    output = []
    tracker = Tracker(project_name, "tracker@burnsomni.net")
    for issue in tracker.get_by_state(*states):
        #issue_ts = issue.timestamp.timestamp()
        #if issue_ts < date_to or issue_ts > date_from:
        #    continue

        output.append({
            "author":  issue.author,
            "id": issue.id,
            "title": issue.title,
            "rating": issue.rating,
            "state": issue.get_state()
        })
    # -------------------------------------------- #

    return output

