from hashids import Hashids
from django.conf import settings
from django.http import Http404

def get_ticket_hashids():
    # Use SECRET_KEY to make it unique per project, min_length=6
    return Hashids(salt=settings.SECRET_KEY + 'ticket', min_length=6)

def encode_ticket_id(ticket_id):
    hashids = get_ticket_hashids()
    return hashids.encode(ticket_id)

def decode_ticket_id(hash_id):
    hashids = get_ticket_hashids()
    decoded = hashids.decode(hash_id)
    if decoded:
        return decoded[0]
    return None
