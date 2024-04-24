from django.conf import settings
from django import http

class BlockedIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if False: # && request.META['REMOTE_ADDR']:
            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        return self.get_response(request)
