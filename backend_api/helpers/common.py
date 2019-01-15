import string
import random

def create_unique_hash(no_of_characters):
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits,
         k=no_of_characters))
