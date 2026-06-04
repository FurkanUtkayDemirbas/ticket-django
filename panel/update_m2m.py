import os
import re

def update_files():
    base_dir = r"c:\Users\asus\Desktop\VollProjeler\MYKEEPfurkanyeni\panel"
    for root, dirs, files in os.walk(base_dir):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if not file.endswith('.py') and not file.endswith('.html'):
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            # Form related
            new_content = re.sub(r"profile\.muhatap_firma\.unvan", r"profile.muhatap_firmalar.first().unvan if profile.muhatap_firmalar.exists() else None", new_content)

            # Queryset filters
            new_content = re.sub(r"unvan=profile\.muhatap_firma", r"unvan__in=profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"ticketno__unvan=profile\.muhatap_firma", r"ticketno__unvan__in=profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"sozlesme_baglantisi__muhatap=profile\.muhatap_firma", r"sozlesme_baglantisi__muhatap__in=profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"muhatap=profile\.muhatap_firma", r"muhatap__in=profile.muhatap_firmalar.all()", new_content)
            
            # Danisman filters
            new_content = re.sub(r"danisman=profile\.danisman_profil", r"danisman__in=profile.danisman_profiller.all()", new_content)

            # Check existence
            new_content = re.sub(r"if profile\.role == 'Firma' and profile\.muhatap_firma:", r"if profile.role == 'Firma' and profile.muhatap_firmalar.exists():", new_content)
            new_content = re.sub(r"elif profile\.role == 'Danisman' and profile\.danisman_profil:", r"elif profile.role == 'Danisman' and profile.danisman_profiller.exists():", new_content)
            new_content = re.sub(r"if hasattr\(request\.user, 'userprofile'\) and request\.user\.userprofile\.role == 'Firma' else sozlesmeler\._meta\.get_field\(\"muhatap\"\)\.remote_field\.model\.objects\.order_by\(\"unvan\"\)", r"if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Firma' else sozlesmeler._meta.get_field('muhatap').remote_field.model.objects.order_by('unvan')", new_content)

            # Direct equality checks (kayit.unvan not in profile.muhatap_firmalar.all())
            new_content = re.sub(r"kayit\.unvan != profile\.muhatap_firma", r"kayit.unvan not in profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"kayit\.ticketno\.unvan != profile\.muhatap_firma", r"kayit.ticketno.unvan not in profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"kayit\.sozlesme_baglantisi\.muhatap != profile\.muhatap_firma", r"kayit.sozlesme_baglantisi.muhatap not in profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"kayit\.muhatap != profile\.muhatap_firma", r"kayit.muhatap not in profile.muhatap_firmalar.all()", new_content)
            new_content = re.sub(r"kayit\.danisman != profile\.danisman_profil", r"kayit.danisman not in profile.danisman_profiller.all()", new_content)
            
            # Admin.py
            new_content = re.sub(r"'get_muhatap_firmalar'", r"'get_muhatap_firmalar'", new_content)
            new_content = re.sub(r"'get_danisman_profiller'", r"'get_danisman_profiller'", new_content)

            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {path}")

if __name__ == '__main__':
    update_files()
