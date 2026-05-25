from ticket.models import ticket, aktivite

def sync():
    tickets = ticket.objects.all()
    count = 0
    for t in tickets:
        aktiviteler = aktivite.objects.filter(ticketno=t)
        for a in aktiviteler:
            if a.danisman:
                t.danisman.add(a.danisman)
                count += 1
    print(f"Senkronize edilen aktivite danışman ataması sayısı: {count}")

sync()
