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




# Get Cursor
def check_cache(cache_key, *file_list):
    """ Is cache out of date? """
    max_date = 0
    for path in file_list:
        max_date = max(max_date, os.stat(path).st_mtime)

    latest_file_change = datetime.fromtimestamp(max_date)
    lastupdate = sql_get_simple("cache", "lastupdate", "key", cache_key)

    out_of_date = True
    if lastupdate is not None:
        out_of_date = latest_file_change > lastupdate

    return out_of_date

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

def sql_get_simple(table, column, match_column, match_value):
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    output = None
    query = f"SELECT `{column}` FROM {table} WHERE `{match_column}` = ?;"
    cursor.execute(query, [match_value])
    rows = cursor.fetchall()

    if rows:
        output = rows[0][0]

    connection.close()

    return output
