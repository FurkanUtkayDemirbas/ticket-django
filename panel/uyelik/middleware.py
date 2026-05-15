from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Kullanıcı giriş yapmamışsa, tüm sayfaları (giriş ve kayıt hariç)
    giriş sayfasına yönlendiren ara katman (middleware).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Eğer kullanıcı giriş yapmamışsa...
        if not request.user.is_authenticated:
            # İzin verilen yollar: giriş, kayıt ve admin paneli
            exempt_urls = [
                reverse('uyelik:giris'),
                reverse('uyelik:kayit'),
                '/admin/',
            ]
            
            # Eğer girilmek istenen sayfa izin verilenlerden biri değilse girişe yönlendir
            if not any(request.path.startswith(url) for url in exempt_urls):
                return redirect('uyelik:giris')
        
        response = self.get_response(request)
        return response
