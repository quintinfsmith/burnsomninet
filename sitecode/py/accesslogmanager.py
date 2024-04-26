import os
import mariadb
import time
from datetime import datetime, timezone
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_access(request):
    access_log_dir = f"{settings.BASE_DIR}/access_logs"
    if not os.path.isdir(access_log_dir):
        os.mkdir(access_log_dir)
    now = datetime.now()
    current_log = f"{access_log_dir}/{now.strftime('%Y-%m-%d')}"
    if not os.path.isfile(current_log):
        mode = "w"
    else:
        mode = "a"

    ip = get_client_ip(request)
    uagent = request.META.get('HTTP_USER_AGENT', '')
    entry_string = f"{now.strftime('%Y-%m-%d %H:%M:%S')}\t|{ip}\t|{uagent}\t|{request.get_full_path()}\n"
    with open(current_log, mode) as fp:
        fp.write(entry_string)

