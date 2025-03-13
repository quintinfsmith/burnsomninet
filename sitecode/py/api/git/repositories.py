from burnsomninet.views import GIT_PATH
import time, os

def process_request(**kwargs):
    output = []
    for directory in os.listdir(GIT_PATH):
        working_path = f"{GIT_PATH}/{directory}"
        if not os.path.isfile(f"{working_path}/git-daemon-export-ok"):
            continue
        output.append(directory)
    return output
