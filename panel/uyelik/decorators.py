from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from functools import wraps

def admin_only(view_func):
    """Sadece Admin veya Superuser erişebilir. Firma/Danışman → 403."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('uyelik:giris')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Admin':
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return _wrapped_view


def admin_veya_danisman_only(view_func):
    """Firmalar erişemez — sadece Admin ve Danışman rolü."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('uyelik:giris')
        if hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.role
            if role == 'Firma' and not request.user.is_superuser:
                return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
