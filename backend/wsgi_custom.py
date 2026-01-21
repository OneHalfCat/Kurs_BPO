"""
Custom WSGI application that removes Server header

This is a workaround for Django's development server which adds
the Server header at WSGI level, making it difficult to remove via middleware.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Get the standard WSGI application
_application = get_wsgi_application()


class ServerHeaderRemovalWSGI:
    """
    WSGI middleware to remove Server header from responses
    """
    
    def __init__(self, application):
        self.application = application
    
    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Filter out Server header
            filtered_headers = [
                (name, value) for name, value in headers 
                if name.lower() != 'server'
            ]
            return start_response(status, filtered_headers, exc_info)
        
        return self.application(environ, custom_start_response)


# Wrap the application
application = ServerHeaderRemovalWSGI(_application)
