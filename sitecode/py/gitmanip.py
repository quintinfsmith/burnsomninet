import os, sys
import re, time
from datetime import datetime, timedelta, timezone
from sitecode.py.cachemanager import check_cache, get_cached, update_cache

class InvalidBranch(Exception):
    """Invalid Branch"""
class FileNotFound(Exception):
    """File Not Found"""
class InvalidCommit(Exception):
    def __init__(self, commit_id):
        super.__init__("Invalid Commit: " + commit_id)

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
        os.chdir(f"{self.path}")
        string = get_cmd_output("git branch | grep \" .*\" -o")
        output = string.split("\n")
        for (i, item) in enumerate(output):
            output[i] = item.strip()
        while "" in output:
            output.remove("")

        return output

    def get_path(self):
        return self.path

    def get_refs(self):
        cwd = os.getcwd()
        os.chdir(f"{self.path}")

        branches = self.get_branch_names()
        heads = {}
        remotes = {}
        for branch in branches:
            ref_path = f"{self.path}/refs/heads/{branch}"
            if not os.path.isfile(ref_path):
                continue
            with open(ref_path, "r") as fp:
                heads[branch] = fp.read().strip()

        for branch in branches:
            ref_path = f"{self.path}/refs/remotes/{branch}"
            if not os.path.isfile(ref_path):
                if branch in heads:
                    remotes[branch] = heads[branch]
            else:
                with open(ref_path, "r") as fp:
                    remotes[branch] = fp.read().strip()


        refsmap = {}
        for branch, hashstr in heads.items():
            refsmap[f"refs/heads/{branch}"] = hashstr
        for branch, hashstr in remotes.items():
            refsmap[f"refs/remotes/origin/{branch}"] = hashstr


        return refsmap

    def get_objects(self):
        cwd = os.getcwd()
        os.chdir(f"{self.path}")
        t = time.time()

        lines = get_cmd_output("git cat-file --batch-all-objects --batch-check").split("\n")

        output = {}
        for line in lines:
            key = line[0:line.find(" ")]
            obtype = line[line.find(" ") + 1:line.rfind(" ")]
            obnumber = line[line.rfind(" ") + 1:]
            output[key] = {
                'type': obtype,
                'number': obnumber
            }
        return output

    def get_blob(self, commit_id, obj_type='blob'):
        if not self.is_valid_commit_id(commit_id):
            return InvalidCommit(commit_id)
        cwd = os.getcwd()
        os.chdir(f"{self.path}")

        output = get_cmd_output(f"git cat-file {obj_type} {commit_id}", "rb")

        os.chdir(cwd)

        return output

    @staticmethod
    def is_valid_commit(commit_id):
        for c in commit_id:
            if c.lower() not in "1234567890abcdefghijklmnopqrstuvwxyz":
                return False
        return True

    def get_tags(self):
        cwd = os.getcwd()

        os.chdir(f"{self.path}")

        output = get_cmd_output("git tag").split("\n")
        os.chdir(cwd)
        while "" in output:
            output.remove("")

        return output

    def get_tag_commit(self, tag):
        cwd = os.getcwd()
        os.chdir(f"{self.path}")
        output = get_cmd_output(f"git show-ref -s \"{tag}\"")
        os.chdir(cwd)

        return output


class ProjectBranch:
    def __init__(self, project, branch="master"):
        if branch not in project.get_branch_names():
            raise InvalidBranch()

        self.project = project
        self.commits = {}
        self.branch = branch

        cwd = os.getcwd()

        cache_key = f"git_project_branch_{self.project.get_path()}_{branch}"

        is_cached = check_cache(
            cache_key,
            f"{self.project.get_path()}/refs/heads/{branch}"
        )

        if not is_cached:
            os.chdir(f"{self.project.get_path()}")
            whatchanged_dump = get_cmd_output(f"git whatchanged {branch}")
            os.chdir(cwd)
            update_cache(cache_key, whatchanged_dump)

        whatchanged_dump, _ = get_cached(cache_key)


        if whatchanged_dump:
            whatchanged_dump = whatchanged_dump.decode()[7:]
            chunks = whatchanged_dump.split("\ncommit ")

            for chunk in chunks:
                commit = Commit.from_dump(chunk, self.project)
                if commit is not None:
                    self.commits[commit.id] = commit

    def get_latest_commit_id(self):
        return self.get_commits()[1].id

    def get_first_commit_date(self):
        return self.get_commits()[-1].date

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

    def get_file_content(self, filepath, commit_id=None):
        filelist = self.get_filelist("", commit_id)
        file_exists = False
        for (name, _) in filelist:
            if name == filepath:
                file_exists = True
                break

        if not file_exists:
            raise FileNotFound()

        if not commit_id:
            cmd = f"git show \"{self.branch}:{filepath}\""
        else:
            cmd = f"git show \"{commit_id}:{filepath}\""

        cwd = os.getcwd()
        os.chdir(f"{self.project.path}")
        content = get_cmd_output(cmd)
        os.chdir(cwd)

        return content

    def get_blame(self, filepath, commit_id=None):
        filelist = self.get_filelist("", commit_id)
        file_exists = False
        for (name, _) in filelist:
            if name == filepath:
                file_exists = True
                break

        if not file_exists:
            raise FileNotFound()
        if not commit_id:
            commit_chunk = ""
        else:
            commit_chunk = f"--ignore-revision {commit_id}"

        cwd = os.getcwd()
        os.chdir(f"{self.project.path}")
        lines = get_cmd_output(f"git blame {self.branch} \"{filepath}\" {commit_chunk}").split("\n")
        os.chdir(cwd)

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
            minutes=int(utc_offset[2:]) * modifier
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

        timestamp = date.timestamp()
        date = datetime.fromtimestamp(timestamp)

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

    def get_id(self):
        return self.id

    def get_timestamp(self):
        return self.date.timestamp()

    def get_author_email(self):
        return self.author


def get_cmd_output(cmd, mode="r"):
    if mode not in ["rb", "r"]:
        raise Exception(f"Bad Mode: {mode}")

    timestamp = time.time()
    file_path = f"/tmp/.cmd_output{timestamp}"
    os.system(f"{cmd} > {file_path}")

    output = ""
    with open(file_path, mode) as fp:
        output = fp.read()
    os.system(f"rm {file_path}")

    return output

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
