#!/bin/env python

import random
import string
import time
import unittest

from ixf import IXFClient

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])

class TestIXFClient(unittest.TestCase):

    def setUp(self):
        self.db = IXFClient(host='dev0.lo0.20c.com')

    def _get_obj(self, typ, id):
        """
        """
        time.sleep(1)
        return self.db.get(typ, id)

    def random_str(self, length=6):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

    def test_connect_options(self):
        db = IXFClient()
        self.db.ixp_all(limit=1)

    def test_get_all(self):
        ixps = self.db.list_all("IXP")["IXP"]
        self.assertTrue(len(ixps) > 400)

        last = self.db.ixp_all(limit=2)["IXP"]
        self.assertTrue(len(last) == 2)

        # iterate over all records 2 at a time
        for i in xrange(1, len(ixps) - 2):
            obj = self.db.ixp_all(skip=i, limit=2)["IXP"]
            self.assertEqual(2, len(obj))
#            print "diff %s %s <> %s %s" % (last.keys()[0], last.keys()[1], obj.keys()[0], obj.keys()[1])
            diff = DictDiffer(last, obj)
            self.assertTrue(len(diff.added()) == 1)
            self.assertTrue(len(diff.removed()) == 1)
            last = obj

        # same skip to check for idempotence
        for i in xrange(128):
            skip = len(ixps) - 3
            obj = self.db.ixp_all(skip=skip, limit=2)["IXP"]
            self.assertTrue(len(obj) == 2)
            diff = DictDiffer(last, obj)
            self.assertEqual(0, len(diff.added()))
            self.assertEqual(0, len(diff.removed()))

        obj = self.db.ixp_all(skip=41, limit=1)["IXP"]
        self.assertEqual(len(obj), 1)
        #self.db.ixp_all(skip=1)
        pass

    def test_get(self):
        self.assertRaises(KeyError, self.db.ixp, 420000)
        data = self.db.get('IXP', 42)

    def test_create(self):
        data = {
            "full_name": "Test IXP",
            "short_name": "TIX",
            }
        obj = self.db.save("IXP", data)
        self.assertIn("id", obj)
        id = obj["id"]

        time.sleep(1)
        obj = self.db.ixp(id)
        for k,v in data.iteritems():
            self.assertIn(k, obj)
            self.assertEqual(data[k], obj[k])

    def test_save(self):
        state = self.random_str()
        data = self.db.ixp(42)
        data['state'] = state
# test for updated_at
        self.db.ixp_save(data)

        data = self._get_obj('IXP', 42)
        self.assertEqual(state, data['state'])

    def test_update(self):
        state = self.random_str()
# test for updated_at
        self.db.update('IXP', 42, state=state)

        data = self._get_obj('IXP', 42)
        self.assertEqual(state, data['state'])

    def test_rm(self):
        test_id = 42
        self.assertTrue(test_id)
        data = self.db.ixp(test_id)
        self.assertIn('state', data)

        self.db.ixp_rm(test_id)

        time.sleep(1)
        data = self.db.ixp(test_id)
        self.assertEqual('deleted', data['state'])

        self.db.update('IXP', 42, state='active')

        time.sleep(1)
        data = self.db.ixp(test_id)
        self.assertEqual('active', data['state'])

    def test_ixp_get(self):
        #self.assertRaises(KeyError, self.db.ixp, 420000)
        self.db.ixp(42)

if __name__ == '__main__':
    unittest.main()

