from sitecode.py.atbt import MariaObj, Tracker

import json
from datetime import datetime
import time

def process_request(**kwargs):
    # -------------------------------------------- #
    project_name = kwargs.get("project", "notaproject")
    limit = kwargs.get("limit", 0)
    # -------------------------------------------- #
    tracker = Tracker(project_name, "tracker@burnsomni.net")
    all_notes = []
    issues = {}
    issue_states = {}
    for issue in tracker.get_all():
        issues[issue.id] = issue
        issue_states[issue.id] = issue.get_state()

        for note in issue.notes:
            all_notes.append(note)

    def by_timestamp(note):
        return note.timestamp

    output = []
    count = 0
    for note in sorted(all_notes, key=by_timestamp, reverse=True):
        output.append({
            "id": note.id,
            "note": note.get_text(),
            "state_update": note.state,
            "issue_state": issue_states[note.issue],
            "issue_title": issues[note.issue].title,
            "timestamp": note.timestamp,
            "issue_id": note.issue
        })
        count += 1
        if count == limit:
            break

    # -------------------------------------------- #
    return output

