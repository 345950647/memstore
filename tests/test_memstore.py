import unittest

from memstore import MemStore  # Assuming the class is in a file named memstore.py


class TestMemStore(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name', 'age'])

    def test_add(self):
        ident = self.db.add({'name': 'Alice', 'age': 25})
        self.assertEqual(ident, 0)
        self.assertEqual(self.db.get(0), {'name': 'Alice', 'age': 25})

    def test_get_nonexistent(self):
        self.assertIsNone(self.db.get(999))

    def test_filter_with_index(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.add({'name': 'Bob', 'age': 25})
        self.db.add({'name': 'Alice', 'age': 30})
        results = self.db.filter({'name': 'Alice'})
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (0, {'name': 'Alice', 'age': 25}))
        self.assertEqual(results[1], (2, {'name': 'Alice', 'age': 30}))

    def test_filter_without_index(self):
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
        self.db.add({'name': 'Charlie', 'age': 35, 'city': 'New York'})
        results = self.db.filter({'city': 'New York'})
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}))
        self.assertEqual(results[1], (2, {'name': 'Charlie', 'age': 35, 'city': 'New York'}))

    def test_filter_multiple_conditions(self):
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'Boston'})
        self.db.add({'name': 'Alice', 'age': 30, 'city': 'New York'})
        results = self.db.filter({'name': 'Alice', 'age': 25})
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}))
        self.assertEqual(results[1], (1, {'name': 'Alice', 'age': 25, 'city': 'Boston'}))

    def test_filter_empty(self):
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        results = self.db.filter({'city': 'Chicago'})
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
        results = self.db.filter({'city': 'Boston'})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}))

    def test_drop_index(self):
        self.db.add({'name': 'Alice', 'age': 25})
        self.db.drop_index('name')
        self.assertNotIn('name', self.db._indexes)


if __name__ == '__main__':
    unittest.main()
