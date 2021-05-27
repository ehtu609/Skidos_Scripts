import os
import io
import time
from config import path_to_key, key_id, issuer_id
from authlib.jose import jwt

def get_token(path_to_key, key_id, issuer_id):
    KEY_ID = key_id
    ISSUER_ID = issuer_id
    EXPIRATION_TIME = int(round(time.time()))
    with open(path_to_key, 'r') as f:
        PRIVATE_KEY = f.read()
        header = {
        "alg": "ES256",
        "kid": KEY_ID,
        "typ": "JWT"
        }

        payload = {
        "iss": ISSUER_ID,
        "exp": EXPIRATION_TIME,
        "aud": "appstoreconnect-v1"
        }
        return jwt.encode(header, payload, PRIVATE_KEY)
