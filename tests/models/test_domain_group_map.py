import unittest

from vegadns.api.models.domain import Domain
from vegadns.api.models.group import Group
from vegadns.api.models.domain_group_map import DomainGroupMap


class TestDomainGroupMap(unittest.TestCase):
    def test_permissions_success(self):
        map = DomainGroupMap()

        self.assertTrue(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        self.assertEquals(map.validate(), None)

        my_dict = map.to_dict()
        self.assertTrue(my_dict["can_read"])
        self.assertTrue(my_dict["can_write"])
        self.assertFalse(my_dict["can_delete"])

        self.assertEquals(map.validate(), None)

        map.set_perm(map.READ_PERM, True)
        self.assertTrue(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        self.assertEquals(map.validate(), None)

        map.set_perm(map.READ_PERM, False)
        map.set_perm(map.WRITE_PERM, True)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        self.assertEquals(map.validate(), None)

        map.set_perm(map.WRITE_PERM, False)
        map.set_perm(map.DELETE_PERM, True)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertFalse(map.has_perm(map.WRITE_PERM))
        self.assertTrue(map.has_perm(map.DELETE_PERM))

        self.assertEquals(map.validate(), None)

        map.set_perm(map.DELETE_PERM, False)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertFalse(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        self.assertEquals(map.validate(), None)

        my_dict = map.to_dict()
        self.assertFalse(my_dict["can_read"])
        self.assertFalse(my_dict["can_write"])
        self.assertFalse(my_dict["can_delete"])

    def test_permissions_failure(self):
        map = DomainGroupMap()

        with self.assertRaises(ValueError) as cm1:
            map.has_perm('foobar')

        with self.assertRaises(ValueError) as cm2:
            map.set_perm('boofar', True)

    def test_validate_failure(self):
        map = DomainGroupMap()

        map.permissions = -1
        with self.assertRaises(ValueError) as cm1:
            map.validate()

        map.permissions = 8
        with self.assertRaises(ValueError) as cm2:
            map.validate()

    def test_format_map(self):
        domain = Domain()
        domain.domain_id = 252
        domain.domain = "example.com"

        group = Group()
        group.group_id = 252
        group.name = "Test Group 1"

        map = DomainGroupMap()
        map.map_id = 1
        map.group_id = group
        map.domain_id = domain
        map.permissions = 7

        formatted = map.format_map(map)
        self.assertTrue(formatted["can_read"])
        self.assertTrue(formatted["can_write"])
        self.assertTrue(formatted["can_delete"])
        self.assertEquals(formatted["map_id"], map.map_id)
        self.assertEquals(formatted["group"], map.group_id.to_clean_dict())
        self.assertEquals(formatted["domain"], map.domain_id.to_clean_dict())
