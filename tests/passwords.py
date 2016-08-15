import random
import string
import unittest

from utils import *


class PasswordTests(unittest.TestCase):

    def test_create_salt(self):
        for x in range(1000):
            create_salt()

    def test_get_hash(self):
        for x in range(1000):
            password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 256)))
            get_hash(create_salt(), password)

    def test_constant_time_hash_compare(self):
        for x in range(1000):
            password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
            assert constant_time_hash_compare(password, password) is True

        for x in range(1000):
            password_a = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
            password_b = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))

            assert constant_time_hash_compare(password_a, password_b) == (password_a == password_b)