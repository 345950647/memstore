import unittest

from mem_store import MemStore  # Assuming the class is in a file named memstore.py


class TestMemStore(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name', 'age'])

    def test_add(self):
        ident = self.db.add({'name': 'Alice', 'age': 25})
        self.assertEqual(ident, 0)
        self.assertEqual(self.db.get(0), {'name': 'Alice', 'age': 25})

    def test_get_nonexistent(self):
        self.assertIsNone(self.db.get(999))

    def test_get_by_index(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.add({'name': 'Bob', 'age': 25})
        results = self.db.get_by_index('name', 'Alice')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (0, {'name': 'Alice', 'age': 25}))

    def test_get_by_index_empty(self):
        results = self.db.get_by_index('name', 'Charlie')
        self.assertEqual(results, [])

    def test_all(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.add({'name': 'Bob', 'age': 30})
        all_records = self.db.all()
        self.assertEqual(len(all_records), 2)
        self.assertEqual(all_records[0], (0, {'name': 'Alice', 'age': 25}))
        self.assertEqual(all_records[1], (1, {'name': 'Bob', 'age': 30}))

    def test_delete(self):
        ident = self.db.add({'name': 'Alice', 'age': 25})
        self.assertTrue(self.db.delete(ident))
        self.assertIsNone(self.db.get(ident))
        self.assertFalse(self.db.delete(999))  # Non-existent ID

    def test_add_index(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.add_index('city')
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
        results = self.db.get_by_index('city', 'Boston')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}))

    def test_drop_index(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.drop_index('name')
        self.assertNotIn('name', self.db._indexes)


if __name__ == '__main__':
    unittest.main()
