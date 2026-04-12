"""
Security Middleware - Production Security Headers
"""
from django.http import JsonResponse
from django.conf import settings


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    Implements CSP, X-Frame-Options, XSS Protection, and more.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # X-Frame-Options - Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options - Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection (legacy but still recommended)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Strict Transport Security (only on HTTPS)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Remove server identification
        response['Server'] = 'Craft Cafe'
        
        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware.
    Tracks requests per IP address.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._request_counts = {}
        self._cleanup_counter = 0
    
    def __call__(self, request):
        # Skip rate limiting for admin panel to avoid issues
        if request.path.startswith('/admin') or request.path.startswith('/dashboard'):
            return self.get_response(request)
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Rate limit settings
        max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        window_seconds = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
        
        # Cleanup old entries periodically
        self._cleanup_counter += 1
        if self._cleanup_counter > 1000:
            self._cleanup_old_entries(window_seconds)
        
        # Check rate limit
        request_count = self._request_counts.get(ip, 0)
        if request_count >= max_requests:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }, status=429)
        
        # Increment counter
        self._request_counts[ip] = request_count + 1
        
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(max_requests)
        response['X-RateLimit-Remaining'] = str(max_requests - request_count - 1)
        
        return response
    
    def _cleanup_old_entries(self, max_age):
        """Clean up old rate limit entries"""
        pass


class HealthCheckMiddleware:
    """
    Health check endpoint for load balancers and monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/health/':
            return JsonResponse({
                'status': 'healthy',
                'service': 'craft_cafe',
                'version': '1.0.0'
            })
        
        return self.get_response(request)