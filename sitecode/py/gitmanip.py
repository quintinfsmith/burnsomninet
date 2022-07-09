import os, sys
import re
from datetime import datetime, timedelta, timezone

class Author:
    def __init__(self, alias, email):
        self.alias = alias
        self.email = email

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHMAP = {}
for i, m in enumerate(_MONTHS):
    MONTHMAP[m] = i + 1


class Project:
    def __init__(self, path):
        self.path = path
        self.authors = {}

    def get_branch(self, branch_name=""):
        return ProjectBranch(self, branch_name)

    def get_branch_names(self):
        return os.listdir(f"{self.path}/refs/heads/")


class ProjectBranch:
    def __init__(self, project, branch=""):
        self.project = project
        self.commits = {}
        self.branch = branch

        cwd = os.getcwd()
        os.chdir(f"{self.project.path}")
        os.system(f"git whatchanged {branch} > /tmp/gitmanip")
        whatchanged_dump = ""

        with open("/tmp/gitmanip", "r") as fp:
            whatchanged_dump = fp.read()

        os.system("rm /tmp/gitmanip")
        os.chdir(cwd)
        if whatchanged_dump:
            whatchanged_dump = whatchanged_dump[7:]
            chunks = whatchanged_dump.split("\ncommit ")

            for chunk in chunks:
                commit = Commit.from_dump(chunk, self.project)
                if commit is not None:
                    self.commits[commit.id] = commit

    def get_latest_commit_id(self):
        return self.get_commits()[0].date

    def get_commit(self, commit_id):
        output = None
        if commit_id in self.commits:
            output = self.commits[commit_id]
        else:
            for check_id, commit in self.commits.items():
                if check_id[0:len(commit_id)] == commit_id:
                    output = commit
                    break
        return output

    def get_commits(self, latest_commit=None):
        commits = list(self.commits.values())
        commits = sorted(commits, key=lambda commit: commit.date, reverse=True)
        if not commits:
            return []

        i = 0
        if latest_commit is not None:
            commit_id = commits[i].id
            while latest_commit != commit_id[0:len(latest_commit)] and i < len(commits) - 1:
                commit_id = commits[i].id
                i += 1

            # id doesn't exist, show all
            if latest_commit != commit_id[0:len(latest_commit)]:
                i = 0

        return commits[i:]

    def get_filelist(self, directory="", latest_commit=None):
        commits = self.get_commits(latest_commit)
        if directory != "" and directory[-1] != "/":
            directory += "/"

        commit_map = {}
        files = set()
        for commit in commits[::-1]:
            for action, filepath in commit.files:
                if filepath[0:len(directory)] != directory:
                    continue

                if action == "A" or action == "M":
                    files.add(filepath)
                    commit_map[filepath] = commit.id
                elif action == "D":
                    try:
                        files.remove(filepath)
                    except KeyError:
                        pass
                    try:
                        del commit_map[filepath]
                    except KeyError:
                        pass

        files = list(files)
        files.sort()
        adj_files = []
        for file in files:
            adj_files.append((file, commit_map[file]))
        return adj_files

    def get_blame(self, filepath, commit_id=None):
        if not commit_id:
            commit_chunk = ""
        else:
            commit_chunk = f"--ignore-revision {commit_id}"

        cwd = os.getcwd()
        os.chdir(f"{self.project.path}")
        os.system(f"git blame {self.branch} {commit_chunk} \"{filepath}\" > /tmp/gitmanip")
        content = ""
        with open("/tmp/gitmanip", "r") as fp:
            content = fp.read()

        os.system("rm /tmp/gitmanip")
        os.chdir(cwd)

        lines = content.split("\n")
        output = []
        for i, line in enumerate(lines):
            last_commit_id = line[0:line.find(" ")]
            needle = f"{i+1}) "
            code = line[line.find(needle) + len(needle):]
            output.append((last_commit_id, code))

        return output


class Commit:
    @staticmethod
    def from_dump(text_dump, project):
        text_dump = text_dump.strip()
        lines = text_dump.split("\n")
        while lines and "" == lines[-1]:
            lines.pop()
        if not lines: return None
        id = lines[0]
        date_line = lines[2]
        date_line = date_line[5:].strip()
        date_line = date_line[date_line.find(" "):].strip()
        date_chunks = date_line.split(" ")
        time_chunks = date_chunks[2].split(":")

        utc_offset = date_chunks[-1]
        modifier = 1
        if utc_offset[0] == '-':
            modifier = -1
            utc_offset = utc_offset[1:]

        time_offset = timedelta(
            hours=int(utc_offset[0:2]) * modifier,
            minutes=int(utc_offset[2:-1]) * modifier
        )

        date = datetime(
            year=int(date_chunks[3]),
            month=MONTHMAP[date_chunks[0]],
            day=int(date_chunks[1]),
            hour=int(time_chunks[0]),
            minute=int(time_chunks[1]),
            second=int(time_chunks[2]),
            tzinfo=timezone(time_offset)
        )

        author_line = lines[1][7:].strip()
        author_email = author_line[author_line.rfind("<") + 1:author_line.rfind(">")]

        if author_email not in project.authors:
            author_alias = author_line[0:author_line.rfind("<")].strip()
            project.authors[author_email] = Author(author_alias, author_email)

        files = []
        while lines[-1] != "":
            file_line = lines.pop()
            for i in range(4):
                file_line = file_line[file_line.find(" ") + 1:]
            action = file_line[0:file_line.find("\t")]
            file_path = file_line[file_line.find("\t"):].strip()

            if action[0] == "R":
                file_path_a = file_path[0:file_path.find("\t")]
                file_path_b = file_path[file_path.find("\t") + 1:]
                files.append(("D", file_path_a))
                files.append(("A", file_path_b))
            else:
                files.append((action, file_path))
        lines.pop()

        description = ""
        while len(lines) > 3:
            description = lines.pop() + "\n" + description
        description = description.strip()

        return Commit(
            id=id,
            date=date,
            description=description,
            files=files,
            author=author_email
        )

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.date = kwargs.get('date', datetime.now())
        self.description = kwargs.get('description', '')
        self.files = kwargs.get('files', [])
        self.author = kwargs.get('author', '')

    def get_description(self):
        return self.description


if __name__ == "__main__":
    test_project = Project(sys.argv[1])
    test_branch = test_project.get_branch(sys.argv[2])

    #commit_id = "079de5655440e92429637ba8d834b047552fa758"
    #commits = test_branch.get_commits()

    #for commit in commits:
    #    print(commit.author)
    #    print(commit.description)
    #    print(commit.date)
    #    print("----------------")

    filelist = test_branch.get_filelist("scales")
    for file, commit_id in filelist:
        print(file, f"({commit_id})")
