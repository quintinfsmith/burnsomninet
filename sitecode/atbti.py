import os
import mariadb
import time
from datetime import datetime, timezone

class MariaObj:
    connection_count = 0
    connection = None

    @classmethod
    def connect_to_mariadb(cls):
        cls.connection_count += 1
        if cls.connection is None:
            cls.connection = mariadb.connect(
                user="http",
                password="terpankerpanhorseradishblot",
                host="localhost",
         #       port=3306,
                database="burnsomninet"
            )

        return cls.connection.cursor()

    @classmethod
    def close_connection(cls):
        cls.connection_count -= 1
        if not (cls.connection is None) and cls.connection_count == 0:
            cls.connection.commit()
            cls.connection.close()
        cls.connection = None

    def connect(self):
        return MariaObj.connect_to_mariadb()

    def disconnect(self):
        MariaObj.close_connection()

class Issue(MariaObj):
    @classmethod
    def new(cls, project, title, author, rating=0):
        cursor = cls.connect_to_mariadb()

        query = "INSERT INTO issue (`rating`, `title`, `project`, `author`) VALUES (?, ?, ?, ?); "
        cursor.execute(query, (rating, title, project, author))
        issue_id = cursor.lastrowid

        cls.close_connection()
        return Issue(issue_id)

    def __init__(self, issue_id):
        self.id = issue_id
        self.notes = []
        self.dependents = []
        self.independents = []

        cursor = self.connect_to_mariadb()

        query = "SELECT rating, ts, author FROM issue WHERE issue.id = ?;"
        cursor.execute(query, (issue_id,))
        vals = cursor.fetchall()[0]
        self.rating = vals[0]
        self.timestamp = vals[1]
        self.author = vals[2]

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

        self.close_connection()

    def get_state(self):
        output = None
        for note in self.notes:
            if note.state != 0:
                output = note.state
        return output

class IssueNote(MariaObj):
    @classmethod
    def new(cls, issue_id, author, state = None):
        cursor = cls.connect_to_mariadb()

        if state is None:
            query = "INSERT INTO issue_note (`issue_id`, `author`) VALUES (?, ?);"
            cursor.execute(query, (issue_id, author ))
        else:
            query = "INSERT INTO issue_note (`issue_id`, `author`, `state`) VALUES (?, ?, ?);"
            cursor.execute(query, (issue_id, author, state))

        note_id = cursor.lastrowid

        cls.close_connection()

        return IssueNote(note_id)

    def __init__(self, note_id):
        self.id = note_id

        cursor = self.connect_to_mariadb()

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

        self.close_connection()

    def add_revision(self, note):
        cursor = self.connect_to_mariadb()
        query = "INSERT INTO issue_note_revision (`note`, `note_id`) VALUES (?, ?);"
        cursor.execute(query, (note, self.id))
        self.close_connection()

if __name__ == "__main__":
    issue = Issue.new("test", "Test Issue", "smith.quintin@protonmail.com", 0)
    issue_note = IssueNote.new(issue.id, "smith.quintin@protonmail.com", 0)
    issue_note.add_revision("Description")



