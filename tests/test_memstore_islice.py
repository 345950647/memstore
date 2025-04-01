import unittest

from memstore import MemStore


class TestMemStoreIslice(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name'])
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
        self.db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        self.db.add({'name': 'David', 'age': 40, 'city': 'Seattle'})

    def test_islice_single_stop_positive(self):
        result = list(self.db.islice(stop=2))
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})
        ]
        self.assertEqual(result, expected)

    def test_islice_single_stop_negative(self):
        result = list(self.db.islice(stop=-1))
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_islice_start_stop_positive(self):
        result = list(self.db.islice(1, 3))
        expected = [
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_islice_start_stop_negative(self):
        result = list(self.db.islice(-3, -1))
        expected = [
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_islice_with_step(self):
        result = list(self.db.islice(0, 4, 2))
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_islice_full_range(self):
        result = list(self.db.islice())
        expected = self.db.all()
        self.assertEqual(result, expected)

    def test_islice_empty(self):
        result = list(self.db.islice(2, 1))
        self.assertEqual(result, [])

    def test_islice_out_of_bounds(self):
        result = list(self.db.islice(5, 10))
        self.assertEqual(result, [])

    def test_islice_negative_out_of_bounds(self):
        result = list(self.db.islice(-10, -5))
        expected = []
        self.assertEqual(result, expected)

    def test_islice_default_start(self):
        result = list(self.db.islice(stop=3))
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
