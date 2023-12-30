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
    FEATURE = 0
    LOW = 1 # Will fix eventually
    PRESSING = 2 # Will be fixed next release
    URGENT = 3 # Will release fix ASAP
    class NoSuchIssueException(Exception):
        """..."""

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
        fetched = cursor.fetchall()
        if not fetched:
            raise Issue.NoSuchIssueException()
        vals = fetched[0]
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
            if note.state is not None:
                output = note.state
        return output

    def require(self, issue_id):
        cursor = self.connect()
        query = "REPLACE INTO issue_link (independent, dependent) VALUES (?, ?);"
        cursor.execute(query, (issue_id, issue.id))
        self.disconnect()

    def add_note(self, author, note, new_state=None):
        issue_note = IssueNote.new(self.id, author, new_state)
        issue_note.add_revision(note)

class IssueNote(MariaObj):
    CANCELLED = 0
    OPEN = 1
    IN_PROGRESS = 2
    RESOLVED = 3

    @staticmethod
    def new(issue_id, author, state = None):
        cursor = MariaObj._connect()

        if state is None:
            query = "INSERT INTO issue_note (issue_id, author) VALUES (?, ?);"
            cursor.execute(query, (issue_id, author))
        else:
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

        query = "SELECT ts, author, state, issue_id FROM issue_note WHERE `id` = ?;"
        cursor.execute(query, (note_id,))
        vals = cursor.fetchall()[0]
        self.timestamp = vals[0]
        self.author = vals[1]
        self.state = vals[2]
        self.issue = vals[3]

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
        return self.get_by_state(IssueNote.RESOLVED)

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

            if state is not None:
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

    def add_issue_note(self, issue_id, note, state=None):
        issue = Issue(issue_id)
        issue_note = issue.add_note(self.email, note, state)

    def get_latest_notes(self, limit=0):
        cursor = MariaObj._connect()
        if limit:
            query = "SELECT DISTINCT issue_id, max(issue_note.ts), issue.title, issue_note_revision.note FROM issue_note INNER JOIN issue ON issue.id = issue_id AND issue.project = ? INNER JOIN issue_note_revision ON issue_note_revision.note_id = issue_note.id GROUP BY issue_id LIMIT ?"
            cursor.execute(query, (self.project, limit))
        else:
            query = "SELECT DISTINCT issue_id, max(issue_note.ts), issue.title, issue_note_revision.note FROM issue_note INNER JOIN issue ON issue.id = issue_id AND issue.project = ? INNER JOIN issue_note_revision ON issue_note_revision.note_id = issue_note.id GROUP BY issue_id"
            cursor.execute(query, (self.project,))

        output = []
        for vals in cursor.fetchall():
            output.append({
                "id": vals[0],
                "timestamp": vals[1],
                "issue_title": vals[3],
                "note": vals[3]
            })

        MariaObj._disconnect()
        return output


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
            elif issue.get_state() == IssueNote.IN_PROGRESS:
                print(f"\033[03;32m{issue.id}: {issue.title}\033[0m")
            else:
                continue

            for note in issue.notes:
                print(f"\033[03;35m   : {note.get_text()}\033[0m")

            for dependent_id in issue.independents:
                dependent = tracker.get_issue(dependent_id)
                if dependent.get_state() in (IssueNote.IN_PROGRESS, IssueNote.OPEN):
                    print(f" -> {dependent.id}: {dependent.title}")

    elif args[0].lower() == "new":
        issue = tracker.new_issue(
            title = args[1],
            rating = ["FEATURE", "LOW", "PRESSING","URGENT"].index(args[2].upper()),
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
            state =  ["CANCELLED", "OPEN", "IN_PROGRESS", "RESOLVED"].index(args[3].upper())
            tracker.add_issue_note(int(args[1]), args[2], state)
        else:
            tracker.add_issue_note(int(args[1]), args[2])

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

    elif args[0].lower() == "cancel":
        if len(args) < 3:
            tracker.add_issue_note(int(args[1]), "", IssueNote.CANCELLED)
        else:
            tracker.add_issue_note(int(args[1]), args[2], IssueNote.CANCELLED)

