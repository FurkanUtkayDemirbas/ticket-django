import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from uyelik.models import UserProfile

def migrate_data():
    profiles = UserProfile.objects.all()
    count = 0
    for profile in profiles:
        updated = False
        if profile.muhatap_firma:
            profile.muhatap_firmalar.add(profile.muhatap_firma)
            updated = True
        if profile.danisman_profil:
            profile.danisman_profiller.add(profile.danisman_profil)
            updated = True
        
        if updated:
            print(f"Migrated user: {profile.user.username}")
            count += 1
            
    print(f"Total migrated profiles: {count}")

if __name__ == '__main__':
    migrate_data()
