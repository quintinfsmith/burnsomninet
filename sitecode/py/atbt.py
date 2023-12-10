import os
import mariadb
import time
from datetime import datetime, timezone

class MariaObj:
    connection_count = 0
    connection = None

    @staticmethod
    def _connect():
        MariaObj.connection_count += 1
        if MariaObj.connection is None:
            MariaObj.connection = mariadb.connect(
                user="http",
                password="terpankerpanhorseradishblot",
                host="localhost",
         #       port=3306,
                database="burnsomninet"
            )

        return MariaObj.connection.cursor()

    @staticmethod
    def _disconnect():
        MariaObj.connection_count -= 1
        if not (MariaObj.connection is None) and MariaObj.connection_count == 0:
            MariaObj.connection.commit()
            MariaObj.connection.close()

            MariaObj.connection = None

    def connect(self):
        return MariaObj._connect()

    def disconnect(self):
        MariaObj._disconnect()

class Issue(MariaObj):
    LOW = 0 # Will fix eventually
    PRESSING = 1 # Will be fixed next release
    URGENT = 2 # Will release fix ASAP
    FEATURE = 3

    @staticmethod
    def new(project, title, author, rating=0):
        cursor = MariaObj._connect()

        query = "INSERT INTO issue (`rating`, `title`, `project`, `author`) VALUES (?, ?, ?, ?); "
        cursor.execute(query, (rating, title, project, author))
        issue_id = cursor.lastrowid

        MariaObj._disconnect()
        return Issue(issue_id)

    def __init__(self, issue_id):
        self.id = issue_id
        self.notes = []
        self.dependents = []
        self.independents = []

        cursor = self.connect()

        query = "SELECT rating, ts, author, title, project FROM issue WHERE issue.id = ?;"
        cursor.execute(query, (issue_id,))
        vals = cursor.fetchall()[0]
        self.rating = vals[0]
        self.timestamp = vals[1]
        self.author = vals[2]
        self.title = vals[3]
        self.project = vals[4]

        query = "SELECT `id` FROM issue_note WHERE issue_id = ?;"
        cursor.execute(query, (issue_id,))
        for vals in cursor.fetchall():
            note = IssueNote(vals[0])
            self.notes.append(note)

        query = "SELECT dependent FROM issue_link WHERE independent = ?;"
        cursor.execute(query, (issue_id,))
        for vals in cursor.fetchall():
            self.dependents.append(vals[0])

        query = "SELECT independent FROM issue_link WHERE dependent = ?;"
        cursor.execute(query, (issue_id,))
        for vals in cursor.fetchall():
            self.independents.append(vals[0])

        self.disconnect()

    def get_state(self):
        output = None
        for note in self.notes:
            if note.state != 0:
                output = note.state
        return output

    def require(self, issue_id):
        cursor = self.connect()
        query = "REPLACE INTO issue_link (independent, dependent) VALUES (?, ?);"
        cursor.execute(query, (issue_id, issue.id))
        self.disconnect()

    def add_note(self, author, note, new_state):
        issue_note = IssueNote.new(self.id, author, new_state)
        issue_note.add_revision(note)

class IssueNote(MariaObj):
    OPEN = 1
    IN_PROGRESS = 2
    CANCELLED = 3
    RESOLVED = 4

    @staticmethod
    def new(issue_id, author, state = 0):
        cursor = MariaObj._connect()

        query = "INSERT INTO issue_note (issue_id, author, state) VALUES (?, ?, ?);"
        cursor.execute(query, (issue_id, author, state))
        MariaObj.connection.commit()

        note_id = cursor.lastrowid

        output = IssueNote(note_id)

        MariaObj._disconnect()

        return output

    def __init__(self, note_id):
        self.id = note_id

        cursor = self.connect()

        query = "SELECT ts, author, state FROM issue_note WHERE `id` = ?;"
        cursor.execute(query, (note_id,))
        vals = cursor.fetchall()[0]
        self.timestamp = vals[0]
        self.author = vals[1]
        self.state = vals[2]

        self.revisions = []
        query = "SELECT ts, note  FROM issue_note_revision WHERE `note_id` = ? ORDER BY issue_note_revision.ts;"
        cursor.execute(query, (note_id,))
        for vals in cursor.fetchall():
            self.revisions.append((vals[0], vals[1]))

        self.disconnect()

    def add_revision(self, note):
        cursor = self.connect()
        query = "INSERT INTO issue_note_revision (`note`, `note_id`) VALUES (?, ?);"
        cursor.execute(query, (note, self.id))

        row_id = cursor.lastrowid

        self.revisions.append((time.time(), note))

        self.disconnect()

    def get_text(self):
        if not self.revisions:
            return None

        return self.revisions[len(self.revisions) - 1][1]

class Tracker(MariaObj):
    def __init__(self, project, email):
        super().__init__()
        self.project = project
        self.email = email

    def get_all(self):
        cursor = self.connect()
        query = "SELECT issue.id FROM issue WHERE issue.project = ?;"
        cursor.execute(query, (self.project, ))

        output = []
        for vals in cursor.fetchall():
            issue_id = vals[0]
            output.append(Issue(issue_id))

        self.disconnect()
        return output

    def get_resolved(self):
        return self.get_by_state(self.RESOLVED)

    def get_open(self):
        return self.get_by_state(IssueNote.OPEN, IssueNote.IN_PROGRESS)

    def get_by_state(self, *target_states):
        cursor = self.connect()
        query = "SELECT issue_note.issue_id, issue_note.state FROM issue_note LEFT JOIN issue ON issue_note.issue_id = issue.id WHERE issue.project = ? GROUP BY issue.id ORDER BY issue_note.id;"
        cursor.execute(query, (self.project, ))

        issue_ids = {}
        for vals in cursor.fetchall():
            issue_id = vals[0]
            state = vals[1]
            if issue_id not in issue_ids:
                issue_ids[issue_id] = 0

            if state > 0:
                issue_ids[issue_id] = state

        self.disconnect()

        output = []
        for (issue_id, state) in issue_ids.items():
            if state not in target_states:
                continue
            output.append(Issue(issue_id))

        return output

    def new_issue(self, title, rating=0, state=0, description=""):
        issue = Issue.new(self.project, title, self.email, rating)
        note = IssueNote.new(issue.id, self.email, state)
        note.add_revision(description)
        return issue

    def add_issue_note(self, issue_id, note, state=0):
        issue = Issue(issue_id)
        issue_note = issue.add_note(self.email, note, state)


if __name__ == "__main__":
    import sys
    #issue = Issue.new("test", "Test Issue", "smith.quintin@protonmail.com", 0)
    #issue_note = IssueNote.new(issue.id, "smith.quintin@protonmail.com", 0)
    #issue_note.add_revision("Description")

    if len(sys.argv) < 2:
        print("project name needed")
        sys.exit()

    kwargs = {}
    args = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            key = arg[2:arg.find("=")].lower()
            value = arg[arg.find("=") + 1:]
            kwargs[key] = value
        else:
            args.append(arg)

    tracker = Tracker(args[0], "smith.quintin@protonmail.com")
    args = args[1:]
    if not args or args[0].lower() == "list":
        for issue in tracker.get_open():
            if issue.get_state() == IssueNote.OPEN:
                print(f"{issue.id}: {issue.title}")
            elif issue.state == Issue.IN_PROGRESS:
                print(f"\033[03;32m{issue.id}: {issue.title}\033[0m")

            for note in issue.notes:
                print(f"\033[03;35m   : {note.get_text()}\033[0m")

            for dependent_id in issue.independents:
                dependent = tracker.get_issue(dependent_id)
                if dependent.get_state() in (IssueNote.IN_PROGRESS, IssueNote.OPEN):
                    print(f" -> {dependent.id}: {dependent.title}")

    elif args[0].lower() == "new":
        issue = tracker.new_issue(
            title = args[1],
            rating = ["LOW", "PRESSING","URGENT", "FEATURE"].index(args[2].upper()),
            state = 1,
            description = args[3]
        )

        if "requires" in kwargs:
            issue.require(int(kwargs["requires"]))

    elif args[0].lower() == "rm":
        tracker.delete_issue(int(args[1]))

    elif args[0].lower() == "note":
        state = 0
        if len(args) >= 4:
            state =  ["", "OPEN", "IN_PROGRESS", "CANCELLED", "RESOLVED"].index(args[3].upper())
        tracker.add_issue_note(int(args[1]), args[2], state)

    elif args[0].lower() == "resolve":
        if len(args) < 3:
            tracker.add_issue_note(int(args[1]), "resolved", IssueNote.RESOLVED)
        else:
            tracker.add_issue_note(int(args[1]), args[2], IssueNote.RESOLVED)

    elif args[0].lower() == "start":
        if len(args) < 3:
            tracker.add_issue_note(int(args[1]), "", IssueNote.IN_PROGRESS)
        else:
            tracker.add_issue_note(int(args[1]), args[2], IssueNote.IN_PROGRESS)

