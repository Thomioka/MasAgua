from functools import wraps
from django.shortcuts import redirect

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_profile = getattr(request.user, 'userprofile', None)
                if user_profile and user_profile.role in roles:
                    return view_func(request, *args, **kwargs)
            return redirect('index')  # O la URL que quieras redirigir si no tiene permisos
        return wrapper
    return decorator