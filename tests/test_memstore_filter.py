import unittest

from memstore import MemStore


class TestMemStoreFilter(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name', 'city'])
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})  # ID: 0
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})  # ID: 1
        self.db.add({'name': 'Alice', 'age': 26, 'city': 'Boston'})  # ID: 2
        self.db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})  # ID: 3

    def test_filter_first_single_match(self):
        result = self.db.filter_first({'name': 'Bob'})
        expected = {'name': 'Bob', 'age': 30, 'city': 'Boston'}  # ID: 1
        self.assertEqual(result, expected)

    def test_filter_last_single_match(self):
        result = self.db.filter_last({'name': 'Bob'})
        expected = {'name': 'Bob', 'age': 30, 'city': 'Boston'}  # ID: 1
        self.assertEqual(result, expected)

    def test_filter_first_multiple_matches(self):
        result = self.db.filter_first({'name': 'Alice'})
        expected = {'name': 'Alice', 'age': 25, 'city': 'New York'}  # ID: 0 (earliest)
        self.assertEqual(result, expected)

    def test_filter_last_multiple_matches(self):
        result = self.db.filter_last({'name': 'Alice'})
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}  # ID: 2 (latest)
        self.assertEqual(result, expected)

    def test_filter_first_no_match(self):
        result = self.db.filter_first({'name': 'David'})
        self.assertIsNone(result)

    def test_filter_last_no_match(self):
        result = self.db.filter_last({'name': 'David'})
        self.assertIsNone(result)

    def test_filter_first_with_indexed_field(self):
        result = self.db.filter_first({'city': 'Boston'})
        expected = {'name': 'Bob', 'age': 30, 'city': 'Boston'}  # ID: 1
        self.assertEqual(result, expected)

    def test_filter_last_with_indexed_field(self):
        result = self.db.filter_last({'city': 'Boston'})
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}  # ID: 2
        self.assertEqual(result, expected)

    def test_filter_first_with_multiple_conditions(self):
        result = self.db.filter_first({'name': 'Alice', 'city': 'Boston'})
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}  # ID: 2
        self.assertEqual(result, expected)

    def test_filter_last_with_multiple_conditions(self):
        result = self.db.filter_last({'name': 'Alice', 'city': 'Boston'})
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}  # ID: 2
        self.assertEqual(result, expected)

    def test_filter_first_after_delete(self):
        self.db.delete(0)
        result = self.db.filter_first({'name': 'Alice'})
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}  # ID: 2
        self.assertEqual(result, expected)

    def test_filter_last_after_delete(self):
        self.db.delete(2)
        result = self.db.filter_last({'name': 'Alice'})
        expected = {'name': 'Alice', 'age': 25, 'city': 'New York'}  # ID: 0
        self.assertEqual(result, expected)

    def test_filter_first_empty_store(self):
        empty_db = MemStore()
        result = empty_db.filter_first({'name': 'Alice'})
        self.assertIsNone(result)

    def test_filter_last_empty_store(self):
        empty_db = MemStore()
        result = empty_db.filter_last({'name': 'Alice'})
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
