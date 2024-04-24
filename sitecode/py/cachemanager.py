import os
from datetime import datetime
from sitecode.py.quicksql import connect_to_mariadb, sql_get_simple

# Get Cursor
def check_cache(cache_key, *file_list):
    """ Is cache out of date? """
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
    lastupdate = sql_get_simple("cache", "lastupdate", "key", cache_key)

    out_of_date = True
    if lastupdate is not None:
        out_of_date = latest_file_change > lastupdate

    return out_of_date

def key_exists(cache_key):
    last_update = sql_get_simple("cache", "lastupdate", "key", cache_key)
    return last_update is not None

def get_cached(cache_key):
    content = sql_get_simple("cache", "content", "key", cache_key)
    mimetype = sql_get_simple("cache", "mimetype", "key", cache_key)
    return (content, mimetype)

def update_cache(cache_key, value, mime="text/html"):
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    query = f"REPLACE INTO cache (`key`, `content`, `mimetype`) VALUES (?, ?, ?);"
    cursor.execute(query, (cache_key, value, mime))
    connection.commit()
    connection.close()

