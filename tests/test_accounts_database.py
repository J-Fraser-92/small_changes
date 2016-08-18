import unittest
import psycopg2
from tables.accounts_table import AccountsTable
from tables.users_table import UsersTable


class TestAccountsDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(dbname='test_small_changes', user='postgres', host='localhost',
                                     password='LegendaryLevine')
        self.cur = self.conn.cursor()

        self.cur.execute("DELETE FROM users")
        self.cur.execute("DELETE FROM accounts")
        self.cur.execute("DELETE FROM access")
        self.cur.execute("DELETE FROM friends")
        self.conn.commit()

        user_db = UsersTable(self.conn)
        user_db.add_user("test_email@email.com", "username", "password")
        self.user_id = user_db.get_user_id("test_email@email.com")

        self.account_db = AccountsTable(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_new_user_has_no_accounts(self):
        self.assertEqual(self.account_db.get_accounts_for_user(self.user_id), [])

    def test_create_money_account_returns_id(self):
        self.assertIsInstance(self.account_db.create_money_account("Everyday", "Current Account", 2010.80), int)

    def test_grant_user_access(self):
        account_id = self.account_db.create_money_account("Everyday", "Current Account", 2010.80)
        self.account_db.grant_user_access("test_email@email.com", account_id)

    def test_add_account_single(self):
        self.account_db.add_account("test_email@email.com", "Shared account", "Current Account", 60.78)
        self.assertEqual(self.account_db.get_accounts_for_user("test_email@email.com"),
                         [("Shared account", "Current Account", "£60.78")])

    def test_add_account_multiple(self):
        self.account_db.add_account("test_email@email.com", "Shared account", "Current Account", 60.78)
        self.account_db.add_account("test_email@email.com", "Honeymoon fund", "Savings Account", 4780.00)
        self.account_db.add_account("test_email@email.com", "Retirement", "Savings Account", 1000.00)

        self.assertListEqual(self.account_db.get_accounts_for_user("test_email@email.com"),
                             [
                                 ("Shared account", "Current Account", "£60.78"),
                                 ("Honeymoon fund", "Savings Account", "£4,780.00"),
                                 ("Retirement", "Savings Account", "£1,000.00")
                             ]
                             )
