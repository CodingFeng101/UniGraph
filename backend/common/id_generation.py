# app/core_layer/id_generation.py

import secrets
import string


def generate_id(length=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))
