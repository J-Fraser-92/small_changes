import psycopg2

from codec.messages import ERROR_MESSAGES, OK_MESSAGES
from utils import *


class UserDatabase:

    def __init__(self, dbname='test_small_changes'):
        self.conn = psycopg2.connect("dbname=%s user='postgres' host='localhost' password='LegendaryLevine'" % dbname)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def is_email_existing(self, email):
        assert type(email) is str

        query = "SELECT EXISTS(SELECT 1 FROM users WHERE email=%s)"
        self.cur.execute(query, (email,))

        exists = self.cur.fetchone()

        assert type(exists[0]) is bool
        return exists[0]

    def is_username_existing(self, username):
        assert type(username) is str

        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username=%s)"
        self.cur.execute(query, (username,))

        exists = self.cur.fetchone()

        assert type(exists[0]) is bool
        return exists[0]

    def password_match(self, username, password):
        assert type(username) is str
        assert 0 < len(username) <= 256
        assert type(password) is str

        if '@' in username:
            if not self.is_email_existing(username):
                return 404, ERROR_MESSAGES.EMAIL_NOT_FOUND

            query = "SELECT password, password_salt FROM users WHERE email=%s"
        else:
            if not self.is_username_existing(username):
                return 404, 'The username provided was not found'

            query = "SELECT password, password_salt FROM users WHERE username=%s"

        self.cur.execute(query, (username, ))

        actual_hash, salt = self.cur.fetchone()
        generated_hash = get_hash(salt, password)

        return constant_time_hash_compare(actual_hash, generated_hash)

    def add_user(self, email, username, password):
        assert type(email) is str
        assert 0 < len(email) <= 256
        assert type(username) is str
        assert 0 < len(username) <= 256
        assert type(password) is str

        if self.is_email_existing(email):
            return 409, ERROR_MESSAGES.EMAIL_IN_USE

        if self.is_username_existing(username):
            return 409, ERROR_MESSAGES.USERNAME_IN_USE

        salt = create_salt()
        hashed_password = get_hash(salt, password)

        before_count = self.users_count

        self.cur.execute(
            'INSERT INTO users (email, username, password, password_salt) VALUES (%s, %s, %s, %s)',
            (email, username, hashed_password, salt))

        self.conn.commit()

        assert self.users_count == (before_count + 1)

        return 201, OK_MESSAGES.USER_ADDED

    @property
    def users_count(self):
        self.cur.execute('SELECT COUNT(*) FROM users')
        return self.cur.fetchone()[0]
