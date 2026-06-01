from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from functools import wraps

def admin_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role != 'Admin' and not request.user.is_superuser:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
