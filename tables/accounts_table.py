from codec.messages import ERROR_MESSAGES
from tables.users_table import UsersTable


class AccountsTable:

    def __init__(self, connection):
        self.conn = connection
        self.cur = self.conn.cursor()

    def add_account(self, user_email, account_name, account_type, account_balance):
        assert type(user_email) is str
        assert type(account_name) is str
        assert type(account_type) is str
        assert type(account_balance) is float

        existing_accounts = self.get_accounts_for_user(user_email)

        account_exists = False

        for account in existing_accounts:
            if account[1] == account_name:
                account_exists = True

        if account_exists:
            return 409, ERROR_MESSAGES.ACCOUNT_NAME_IN_USE

        account_id = self.create_money_account(account_name, account_type, account_balance)
        self.grant_user_access(user_email, account_id)

        assert len(self.get_accounts_for_user(user_email)) == len(existing_accounts) + 1

    def grant_user_access(self, user_email, account_id):
        assert type(user_email) is str
        assert type(account_id) is int

        before_count = self.access_count

        query = "INSERT INTO access (user_id, account_id) VALUES (%s, %s)"
        users_db = UsersTable(self.conn)
        user_id = users_db.get_user_id(user_email)

        self.cur.execute(query, (user_id, account_id))
        self.conn.commit()

        assert self.access_count == before_count + 1

    def create_money_account(self, account_name, account_type, account_balance):
        assert type(account_name) is str
        assert type(account_type) is str
        assert type(account_balance) is float

        before_count = self.accounts_count

        query = "INSERT INTO accounts (name, account_type, balance) VALUES (%s, %s, %s) RETURNING id"
        self.cur.execute(query, (account_name, account_type, account_balance))

        account_id = self.cur.fetchone()[0]
        self.conn.commit()

        assert self.accounts_count == before_count + 1
        assert type(account_id) is int
        return account_id

    def get_accounts_for_user(self, user_email):
        assert type(user_email) is str

        query = """
        WITH account_ids AS (
            SELECT account_id FROM access
            JOIN users ON users.id = access.user_id
            WHERE users.email = %s
        )

        SELECT name, account_type, balance FROM accounts
        WHERE accounts.id IN (SELECT account_id FROM account_ids);
        """

        self.cur.execute(query, (user_email,))

        results = self.cur.fetchall()

        assert type(results) is list
        return results

    def get_friends_for_user(self, user_id):
        assert type(user_id) is int

        query = "SELECT user_2 FROM friends WHERE user_1=%s"
        self.cur.execute(query, (user_id,))

        results = self.cur.fetchall()

        query = "SELECT user_1 FROM friends WHERE user_2=%s"
        self.cur.execute(query, (user_id,))

        results += self.cur.fetchall()

        assert type(results) is list
        return results

    @property
    def accounts_count(self):
        self.cur.execute('SELECT COUNT(*) FROM accounts')
        return self.cur.fetchone()[0]

    @property
    def access_count(self):
        self.cur.execute('SELECT COUNT(*) FROM access')
        return self.cur.fetchone()[0]
