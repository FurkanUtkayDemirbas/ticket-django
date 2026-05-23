from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modul', '0007_danisman_email_danisman_tur'),
        ('ticket', '0023_copy_danisman_to_m2m'),
    ]

    operations = [
        # 1. Eski FK alanını kaldır
        migrations.RemoveField(
            model_name='ticket',
            name='danisman',
        ),
        # 2. M2M alanını danismanlar -> danisman olarak yeniden adlandır
        migrations.RenameField(
            model_name='ticket',
            old_name='danismanlar',
            new_name='danisman',
        ),
        # 3. related_name'i güncelle (model tanımıyla uyumlu)
        migrations.AlterField(
            model_name='ticket',
            name='danisman',
            field=models.ManyToManyField(blank=True, related_name='ticket_danismanlar', to='modul.danisman'),
        ),
    ]
