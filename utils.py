import hashlib
import os
from base64 import b64encode


def create_salt():
    salt = b64encode(os.urandom(32)).decode()

    assert type(salt) is str
    assert len(salt) == 44

    return salt


def get_hash(salt, password):
    assert type(salt) is str
    assert len(salt) == 44
    assert type(password) is str

    hash_str = hashlib.sha256((salt + password).encode()).hexdigest()

    assert type(hash_str) is str
    assert len(hash_str) == 64

    return hash_str


def constant_time_hash_compare(hash_a, hash_b):
    assert len(hash_a) == 64
    assert len(hash_b) == 64

    match = True
    for i in range(64):
        try:
            match = match and (hash_a[i] == hash_b[i])
        except IndexError:
            match = False

    assert type(match) is bool

    return match