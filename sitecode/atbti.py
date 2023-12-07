import os
import mariadb
import time
from datetime import datetime, timezone

def connect_to_mariadb():
    return mariadb.connect(
        user="http",
        password="terpankerpanhorseradishblot",
        host="localhost",
 #       port=3306,
        database="burnsomninet"

    )


def new_issue(project, rating = 0):
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    query = "INSERT INTO issue (`rating`, `project`) VALUES (?, ?); "
    cursor.execute(query, (rating, project))
    issue_id = cursor.lastrowid

    query = "INSERT INTO issue_note (`note`, `author`,  `issue_id`, `state`) VALUES (?, ?, ?, ?);"
    cursor.execute(query, ("First Note", "smith.quintin@protonmail.com", issue_id, 0))

    connection.commit()
    connection.close()

    return issue_id


def add_note(issue_id, note, state=None):
    connection = connect_to_mariadb()
    cursor = connection.cursor()
    if state is None:
        query = "INSERT INTO issue_note (`note`, `author`,  `issue_id`) VALUES (?, ?, ?);"
        cursor.execute(query, (note, "smith.quintin@protonmail.com", issue_id, ))
    else:
        query = "INSERT INTO issue_note (`note`, `author`, `issue_id`, `state`) VALUES (?, ?, ?, ?);"
        cursor.execute(query, (note, "smith.quintin@protonmail.com", issue_id, state))

    connection.commit()
    connection.close()

def get_notes(issue_id):
    connection = connect_to_mariadb()
    cursor = Connection.cursor()
    query = "SELECT note, ts, author, state FROM issue_note WHERE issue_id = ? ORDER BY issue_note.ts;"
    cursor.execute(query, (issue_id,))

    notes = []
    for vals in cursor.fetchall():
        notes.append()

    connection.close()

class Issue:
    @staticmethod
    def new(project, rating=0):
        new_id = new_issue(project, rating)
        return Issue.from_id(new_id)

    @staticmethod
    def from_id(issue_id):
        connection = connect_to_mariadb()
        cursor = connection.cursor()

        query = "SELECT rating, ts FROM issue WHERE id = ?;"
        cursor.execute(query, (issue_id, ))
        rating = 0
        ts = 0
        for vals in cursor.fetchall():
            rating = vals[0]
            ts = vals[1]
            break

        query = "SELECT note, ts, author, state FROM issue_note WHERE issue_id = ? ORDER BY issue_note.ts;"
        cursor.execute(query, (issue_id,))

        notes = []
        for vals in cursor.fetchall():
            notes.append(
                IssueNote(
                    note = vals[0],
                    timestamp = vals[1],
                    author = vals[2],
                    state = vals[3]
                )
            )
        dependencies = []
        query = "SELECT independent FROM issue_dependency WHERE dependent = ?;"
        cursor.execute(query, (issue_id,))
        for vals in cursor.fetchall():
            dependencies.append(vals[0])

        independencies = []
        query = "SELECT dependent FROM issue_dependency WHERE independent = ?;"
        cursor.execute(query, (issue_id,))
        for vals in cursor.fetchall():
            dependencies.append(vals[0])

        return Issue(
            issue_id = issue_id,
            rating = rating,
            timestamp = ts,
            notes = notes,
            dependencies = dependencies,
            dependents = independencies
        )

    def __init__(self, issue_id, rating, notes, dependencies, dependents, timestamp):
        self.issue_id = issue_id
        self.notes = notes
        self.dependencies = dependencies
        self.dependents = dependents
        self.timestamp = timestamp
        self.rating = rating

    def get_state(self):
        output = None
        for note in self.notes:
            if note.state != 0:
                output = note.state
        return output

class IssueNote:
    def __init__(self, author, state, note, timestamp):
        self.author = author
        self.state = state
        self.note = note
        self.timestamp = timestamp


