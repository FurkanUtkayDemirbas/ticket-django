from django.db import migrations


def copy_danisman_to_m2m(apps, schema_editor):
    """Mevcut ForeignKey danisman verilerini yeni ManyToMany alanına kopyala."""
    Ticket = apps.get_model("ticket", "ticket")
    Danisman = apps.get_model("modul", "danisman")
    for t in Ticket.objects.filter(danisman__isnull=False):
        try:
            d = Danisman.objects.get(username=t.danisman_id)
            t.danismanlar.add(d)
        except Danisman.DoesNotExist:
            pass


def reverse_copy(apps, schema_editor):
    """Geri dönüş: M2M'deki ilk danışmanı FK'ya yaz."""
    Ticket = apps.get_model("ticket", "ticket")
    for t in Ticket.objects.all():
        first = t.danismanlar.first()
        if first:
            t.danisman_id = first.username
            t.save(update_fields=["danisman_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0022_add_danismanlar_m2m"),
    ]

    operations = [
        migrations.RunPython(copy_danisman_to_m2m, reverse_copy),
    ]
