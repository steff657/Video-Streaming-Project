from django.conf import settings


class FrameAncestorsCspMiddleware:
    """
    Protect against clickjacking while allowing a strict iframe allowlist.

    CSP `frame-ancestors` supports explicit origins (unlike modern X-Frame-Options).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        allowed_origins = [
            origin.strip()
            for origin in getattr(settings, 'EMBED_ALLOWED_ORIGINS', [])
            if origin.strip()
        ]
        frame_ancestors = ["'self'", *allowed_origins]

        # Replace any existing frame-ancestors directive to avoid conflicts.
        existing_csp = response.get('Content-Security-Policy', '')
        directives = [
            directive.strip()
            for directive in existing_csp.split(';')
            if directive.strip()
            and not directive.strip().lower().startswith('frame-ancestors')
        ]
        directives.append(f"frame-ancestors {' '.join(frame_ancestors)}")
        response['Content-Security-Policy'] = '; '.join(directives)

        # Remove X-Frame-Options if present so CSP is the single source of truth.
        response.headers.pop('X-Frame-Options', None)

        return response
