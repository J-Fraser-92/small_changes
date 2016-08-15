import unittest

import psycopg2

from codec.messages import *
from database_cursor import UserDatabase


class TestUsersDatabase(unittest.TestCase):

    def setUp(self):
        self.conn = psycopg2.connect(dbname='test_small_changes', user='postgres', host='localhost', password='LegendaryLevine')
        self.cur = self.conn.cursor()
        self.cur.execute("DELETE FROM users")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_add_user_for_new_user(self):
        db = UserDatabase(dbname='test_small_changes')

        self.assertEqual(db.add_user("test_email@email.com", "username", "password"), (201, OK_MESSAGES.USER_ADDED))

    def test_add_user_for_existing_email(self):
        db = UserDatabase(dbname='test_small_changes')
        db.add_user("existing_email@email.com", "username1", "password")

        self.assertEqual(db.add_user("existing_email@email.com", "username2", "password"), (409, ERROR_MESSAGES.EMAIL_IN_USE))

    def test_add_user_for_existing_username(self):
        db = UserDatabase(dbname='test_small_changes')
        db.add_user("test_email1@email.com", "username", "password")

        self.assertEqual(db.add_user("test_email2@email.com", "username", "password"), (409, ERROR_MESSAGES.USERNAME_IN_USE))

    def test_user_log_in_with_email(self):
        db = UserDatabase(dbname='test_small_changes')
        db.add_user("test_email@email.com", "username", "password")

        self.assertTrue(db.password_match("test_email@email.com", "password"))

    def test_user_log_in_with_username(self):
        db = UserDatabase(dbname='test_small_changes')
        db.add_user("test_email@email.com", "username", "password")

        self.assertTrue(db.password_match("username", "password"))