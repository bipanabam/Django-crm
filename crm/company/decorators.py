from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def access_level_required(group_names=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_groups = request.user.access_level.all() if hasattr(request.user, 'access_level') else []
                user_group_names = [group.name for group in user_groups]

                if any(name in user_group_names for name in group_names):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "You do not have permission to access this page.")
                    return redirect(request.META.get('HTTP_REFERER', request.path))
            else:
                return redirect('login')
        return _wrapped_view
    return decorator