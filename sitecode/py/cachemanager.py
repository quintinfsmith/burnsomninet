import os
import sqlite3
import time

BASE_DIR = "/srv/http/burnsomninet/"
def check_cache(cache_key, *file_list):
    max_date = 0
    for path in file_list:
        max_date = max(max_date, os.stat(path).st_mtime)

    timestamp = sql_get_simple("cache", "timestamp", "key", cache_key)
    output = False
    if timestamp is not None:
        output = max_date < float(timestamp)

    return output

def get_cached(cache_key):
    content = sql_get_simple("cache", "content", "key", cache_key)
    mimetype = sql_get_simple("cache", "mimetype", "key", cache_key)
    return (content, mimetype)

def update_cache(cache_key, value, mime="text/plain"):
    timestamp = time.time()
    con = sqlite3.connect(f"{BASE_DIR}/main.db")
    query = f"REPLACE INTO cache (key, content, timestamp, mimetype) VALUES ((?), (?), (?), (?));"
    con.execute(query, (cache_key, value, time.time(), mime))
    con.close()

def sql_get_simple(table, column, match_column, match_value):
    output = None
    con = sqlite3.connect(f"{BASE_DIR}/main.db")
    query = f"select `{column}` from `{table}` where `{match_column}` = (?)"
    row = con.execute(query, [match_value]).fetchone()
    if row is not None:
        output = row[0]
    con.close()
    return output
