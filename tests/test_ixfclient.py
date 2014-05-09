#!/bin/env python

import random
import string
import time
import unittest

from ixf import IXFClient


class TestIXFClient(unittest.TestCase):

    def setUp(self):
        self.db = IXFClient(host='localhost', port=7003, user='dev', password='test')
        self.db = IXFClient()

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

    def test_all(self):
        ixps = self.db.all('IXP')
        self.assertGreater(len(ixps), 400)

    def test_all_iter_cycle(self):
        ixps = self.db.all('IXP')

        last = self.db.ixp_all(limit=2)
        self.assertEqual(len(last), 2)

        # iterate over all records 2 at a time
        #for i in xrange(1, len(ixps) - 2):
        for i in xrange(1, 100):
            obj = self.db.ixp_all(skip=i, limit=2)
            self.assertEqual(2, len(obj))
            self.assertGreater(obj[1]['id'], obj[0]['id'])
            self.assertEqual(last[1], obj[0])
#            print "diff %s %s <> %s %s" % (last.keys()[0], last.keys()[1], obj.keys()[0], obj.keys()[1])
            last = obj

    def test_all_iter(self):
        skip = 13
        last = self.db.ixp_all(skip=skip, limit=2)
        self.assertEqual(len(last), 2)

        # same skip to check for idempotence
        for i in xrange(128):
            obj = self.db.ixp_all(skip=skip, limit=2)
            self.assertEqual(last[0]['id'], obj[0]['id'])
            self.assertEqual(last[1]['id'], obj[1]['id'])

        obj = self.db.ixp_all(skip=41, limit=1)
        self.assertEqual(len(obj), 1)
        pass

    def test_get(self):
        self.assertRaises(KeyError, self.db.ixp, 420000)
        data = self.db.get('IXP', 42)

    def test_create(self):
        data = {
            "full_name": "Test IXP",
            "short_name": "TIX",
            }
        obj = self.db.save('IXP', data)
        self.assertEqual(1, len(obj))
        obj = obj[0]
        self.assertIn("id", obj)
        id = obj["id"]

        time.sleep(1)
        obj = self.db.ixp(id)
        self.assertEqual(1, len(obj))
        obj = obj[0]
        for k,v in data.iteritems():
            self.assertIn(k, obj)
            self.assertEqual(data[k], obj[k])

    def test_save(self):
        state = self.random_str()
        data = self.db.ixp(42)[0]
        data['state'] = state
# test for updated_at
        self.db.ixp_save(data)

        data = self._get_obj('IXP', 42)[0]
        self.assertEqual(state, data['state'])

    def test_update(self):
        state = self.random_str()
# test for updated_at
        self.db.update('IXP', 42, state=state)

        data = self._get_obj('IXP', 42)[0]
        self.assertEqual(state, data['state'])

    def test_rm(self):
        test_id = 42
        self.assertTrue(test_id)
        data = self.db.ixp(test_id)[0]
        self.assertIn('state', data)

        self.db.ixp_rm(test_id)

        time.sleep(1)
        data = self.db.ixp(test_id)[0]
        self.assertEqual('deleted', data['state'])

        self.db.update('IXP', 42, state='active')

        time.sleep(1)
        data = self.db.ixp(test_id)[0]
        self.assertEqual('active', data['state'])

    def test_ixp_get(self):
        #self.assertRaises(KeyError, self.db.ixp, 420000)
        self.db.ixp(42)

if __name__ == '__main__':
    unittest.main()

