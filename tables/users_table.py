from codec.messages import ERROR_MESSAGES, OK_MESSAGES
from utils import *


class UsersTable:

    def __init__(self, connection):
        self.conn = connection
        self.cur = self.conn.cursor()

    def is_email_existing(self, email):
        assert type(email) is str

        query = "SELECT EXISTS(SELECT 1 FROM users WHERE email=%s)"
        self.cur.execute(query, (email,))

        exists = self.cur.fetchone()

        assert type(exists[0]) is bool
        return exists[0]

    def password_match(self, email, password):
        assert type(email) is str
        assert type(password) is str

        if not self.is_email_existing(email):
            return 404, ERROR_MESSAGES.EMAIL_NOT_FOUND

        query = "SELECT password, password_salt FROM users WHERE email=%s"

        self.cur.execute(query, (email, ))

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

        salt = create_salt()
        hashed_password = get_hash(salt, password)

        before_count = self.users_count

        self.cur.execute(
            'INSERT INTO users (email, username, password, password_salt) VALUES (%s, %s, %s, %s)',
            (email, username, hashed_password, salt))

        self.conn.commit()

        assert self.users_count == (before_count + 1)

        return 201, OK_MESSAGES.USER_ADDED

    def get_user_id(self, email):
        assert type(email) is str

        if not self.is_email_existing(email):
            return 404, ERROR_MESSAGES.EMAIL_NOT_FOUND

        query = "SELECT id FROM users WHERE email=%s"
        self.cur.execute(query, (email,))

        ids = self.cur.fetchall()

        assert len(ids) == 1
        return ids[0][0]

    @property
    def users_count(self):
        self.cur.execute('SELECT COUNT(*) FROM users')
        return self.cur.fetchone()[0]
