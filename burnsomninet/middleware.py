from django.conf import settings
from django import http
from burnsomninet import wrappers
from sitecode.py.accesslogmanager import get_client_ip, log_access

class BlockedIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uagent = request.META.get('HTTP_USER_AGENT', '')

        ip = get_client_ip(request)
        # Checking for malicious queries is done in 404 handler, don't need to check acceptable queries
        if wrappers.is_ip_banned(ip):
            response = http.HttpResponseForbidden('<h1>Forbidden</h1>')
        elif "thinkbot" in uagent.lower():
            response = http.HttpResponse("<h1>Oi! You thieving, uncreative cunt. AI can't attribute. Kindly eat shit and remove yourself from society.</h1>")
        else:
            response = self.get_response(request)

        log_access(request, response)

        return response
