import os
from datetime import datetime
from sitecode.py.quicksql import connect_to_mariadb, sql_get_simple
from django.conf import settings

# Get Cursor
def check_cache(cache_key, *file_list) -> bool:
    """ Is cache out of date? """

    if not key_exists(cache_key):
        return True

    max_date = 0
    for path in file_list:
        if os.path.isdir(path):
            for main, _, files in os.walk(path):
                for f in files:
                    s = os.stat(f"{main}/{f}")
                    max_date = max(max_date, s.st_mtime, s.st_ctime)
        else:
            s = os.stat(path)
            max_date = max(max_date, s.st_mtime, s.st_ctime)

    latest_file_change = datetime.fromtimestamp(max_date)
    
    file_path = f"{settings.BASE_DIR}/cached_files/{cache_key}"
    file_stat = os.stat(file_path)
    last_update = datetime.fromtimestamp(max(file_stat.st_mtime, file_stat.st_ctime))

    out_of_date = True
    if last_update is not None:
        out_of_date = latest_file_change > last_update

    return out_of_date

def get_latest_update(cache_key: str):
    file_path = f"{settings.BASE_DIR}/cached_files/{cache_key}"
    if not os.path.isfile(file_path):
        return None

    file_stat = os.stat(file_path)
    last_update = datetime.fromtimestamp(max(file_stat.st_mtime, file_stat.st_ctime))
    return last_update

def key_exists(cache_key: str) -> bool:
    file_path = f"{settings.BASE_DIR}/cached_files/{cache_key}"
    return os.path.isfile(file_path)

def get_cached(cache_key: str) -> tuple[str, str]:
    file_path = f"{settings.BASE_DIR}/cached_files/{cache_key}"

    content = ""
    with open(file_path, "r") as fp:
        content = fp.read()

    mimetype = content[0:content.find("||")]
    content = content[content.find("||") + 2:]
    return (content, mimetype)

def update_cache(cache_key: str, value: str, mime="text/html"):
    cached_dir = f"{settings.BASE_DIR}/cached_files/"
    if not os.path.isdir(cached_dir):
        os.mkdir(cached_dir)

    file_path = f"{cached_dir}/{cache_key}"
    with open(file_path, "w") as fp:
        fp.write(f"{mime}||{value}")

