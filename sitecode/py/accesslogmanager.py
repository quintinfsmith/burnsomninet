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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_access(request):
    connection = connect_to_mariadb()
    cursor = connection.cursor()
    query = f"INSERT INTO accesslog (`ip`, `path`, `uagent`) VALUE (?, ?, ?);"
    ip = get_client_ip(request)
    uagent = request.META.get('HTTP_USER_AGENT', '')
    cursor.execute(query, (ip, request.get_full_path(), uagent))
    connection.commit()
    connection.close()

