from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0027_alter_ticket_taleptarih'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketYazisma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mesaj', models.TextField()),
                ('olusturma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('kullanici', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('ticketno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yazismalar', to='ticket.ticket', to_field='ticketno')),
            ],
            options={
                'ordering': ['-olusturma_tarihi'],
            },
        ),
    ]
