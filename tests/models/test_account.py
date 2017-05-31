import unittest
from mock import Mock, MagicMock

from vegadns.api.models.account import Account
from vegadns.api.models.domain import Domain
import peewee


class TestAccount(unittest.TestCase):
    def test_status_validation(self):
        account = Account()

        account.first_name = "Test"
        account.last_name = "User"
        account.email = "user@example.com"
        account.account_type = "senior_admin"

        # good
        account.status = "active"
        self.assertIsNone(account.validate())

        # good
        account.status = "inactive"
        self.assertIsNone(account.validate())

        # bad
        account.status = "foobar"
        with self.assertRaises(Exception) as cm:
            account.validate()
        self.assertEquals('Invalid status: foobar', cm.exception.message)

    def test_get_domain_by_record_acl_fail_soa(self):
        account = Account()
        self.assertFalse(
            account.get_domain_by_record_acl(
                1, "example.com", "SOA"
            )
        )

    def test_get_domain_by_record_acl_email_fail(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=False)

        self.assertFalse(
            account.get_domain_by_record_acl(1, "example.com", "TXT")
        )

    def test_get_domain_by_record_acl_domain_success(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        domain = MagicMock()
        domain.get = MagicMock(return_value=dm)
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(return_value=["DOMAIN"])
        self.assertEquals(
            dm,
            account.get_domain_by_record_acl(1, "example.com", "TXT")
        )

    def test_get_domain_by_record_acl_single_label_success(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        domain = MagicMock()
        domain.get = MagicMock(return_value=dm)
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertEquals(
            dm,
            account.get_domain_by_record_acl(
                1, "_acme-challenge.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_failure(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        domain = MagicMock()
        domain.get = MagicMock(return_value=dm)
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertFalse(
            account.get_domain_by_record_acl(
                1, "foobar.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_failure_two(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        domain = MagicMock()
        domain.get = MagicMock(return_value=dm)
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertFalse(
            account.get_domain_by_record_acl(1, "foo.bar.example.com", "TXT")
        )

    def test_get_domain_by_record_acl_multiple_label_success(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        dget = Mock()
        dget.side_effect = [dm, peewee.DoesNotExist, dm]
        domain = MagicMock()
        domain.get = dget
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertEquals(
            dm,
            account.get_domain_by_record_acl(
                1, "_acme-challenge.bar.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_success_two(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        dget = Mock()
        dget.side_effect = [dm, dm]
        domain = MagicMock()
        domain.get = dget
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertEquals(
            dm,
            account.get_domain_by_record_acl(
                1, "_acme-challenge.bar.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_failure_collision(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        dm2 = MagicMock()
        dm2.domain = "bar.example.com"
        dm2.domain_id = 2

        dget = Mock()
        dget.side_effect = [dm, peewee.DoesNotExist, dm2]
        domain = Mock()
        domain.get = dget
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertFalse(
            account.get_domain_by_record_acl(
                1, "_acme-challenge.foo.bar.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_success_no_match(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        dget = Mock()
        dget.side_effect = [dm, peewee.DoesNotExist, peewee.DoesNotExist]
        domain = MagicMock()
        domain.get = dget
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertEquals(
            dm,
            account.get_domain_by_record_acl(
                1, "_acme-challenge.foo.bar.example.com", "TXT"
            )
        )

    def test_get_domain_by_record_acl_multiple_label_fail_no_match(self):
        account = Account()
        account.email = "user@example.com"
        account.in_global_acl_emails = MagicMock(return_value=True)

        dm = MagicMock()
        dm.domain = "example.com"
        dm.domain_id = 1
        dget = Mock()
        dget.side_effect = [
            dm, peewee.DoesNotExist, peewee.DoesNotExist,
            peewee.DoesNotExist, peewee.DoesNotExist
        ]
        domain = MagicMock()
        domain.get = dget
        account.get_domain_object = MagicMock(return_value=domain)

        account.get_global_acl_labels = MagicMock(
            return_value=["_acme-challenge", "DOMAIN"]
        )
        self.assertFalse(
            account.get_domain_by_record_acl(
                1, "_acme-challenge.foo.bar.example2.com", "TXT"
            )
        )

    def test_get_domain(self):
        account = Account()

        self.assertEquals(peewee.BaseModel, type(account.get_domain_object()))
