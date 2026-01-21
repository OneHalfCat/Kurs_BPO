"""
Custom middleware for security enhancements
"""


class SecurityHeadersMiddleware:
    """
    Middleware to remove/modify security-sensitive HTTP headers
    
    Fixes OWASP ZAP finding: Server Leaks Version Information (CWE-ID: 497)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Remove Server header to prevent version information leakage
        # Try multiple methods as different servers handle this differently
        try:
            # Method 1: Delete from response object
            if 'Server' in response:
                del response['Server']
        except (KeyError, AttributeError):
            pass
        
        try:
            # Method 2: Set to empty string (some servers respect this)
            response['Server'] = ''
        except Exception as e:
            # Log the exception for debugging purposes
            # In production, this should use proper logging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Could not modify Server header: {e}")
        
        # Add additional security headers
        # X-Content-Type-Options: prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options: prevent clickjacking (already set by Django, but ensure it's there)
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection: enable XSS filter in older browsers
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy: control referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
