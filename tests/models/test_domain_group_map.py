import unittest

from vegadns.api.models.domain_group_map import DomainGroupMap


class TestDomainGroupMap(unittest.TestCase):
    def test_permissions_success(self):
        map = DomainGroupMap()

        self.assertTrue(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        my_dict = map.to_dict()
        self.assertTrue(my_dict["can_read"])
        self.assertTrue(my_dict["can_write"])
        self.assertFalse(my_dict["can_delete"])

        map.set_perm(map.READ_PERM, True)
        self.assertTrue(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        map.set_perm(map.READ_PERM, False)
        map.set_perm(map.WRITE_PERM, True)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertTrue(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

        map.set_perm(map.WRITE_PERM, False)
        map.set_perm(map.DELETE_PERM, True)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertFalse(map.has_perm(map.WRITE_PERM))
        self.assertTrue(map.has_perm(map.DELETE_PERM))

        map.set_perm(map.DELETE_PERM, False)
        self.assertFalse(map.has_perm(map.READ_PERM))
        self.assertFalse(map.has_perm(map.WRITE_PERM))
        self.assertFalse(map.has_perm(map.DELETE_PERM))

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
