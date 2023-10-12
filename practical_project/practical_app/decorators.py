import time
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status

def rate_limit_request(identifier, timeout, limit):
    """
    Decorator to rate limit requests based on identifier.
    """
    def decorator(view_func):
        def wrapped_view(self, request, *args, **kwargs):
            cache_key = f"rate_limit:{identifier}:{request.META['REMOTE_ADDR']}"

            # Check if the cache key exists and exceeds the limit
            request_count = cache.get(cache_key, 0)
            if request_count >= limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Increment the request count and update cache
            cache.set(cache_key, request_count + 1, timeout)

            return view_func(self, request, *args, **kwargs)

        return wrapped_view

    return decorator