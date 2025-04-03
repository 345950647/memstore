import unittest

from memstore import MemStore


class TestMemStoreIloc(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name'])
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
        self.db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        self.db.add({'name': 'David', 'age': 40, 'city': 'Seattle'})
        self.db.add({'name': 'Alice', 'age': 26, 'city': 'Boston'})

    def test_iloc_single_positive(self):
        result = self.db.iloc[1]
        expected = {'name': 'Bob', 'age': 30, 'city': 'Boston'}
        self.assertEqual(result, expected)

    def test_iloc_single_negative(self):
        result = self.db.iloc[-1]
        expected = {'name': 'Alice', 'age': 26, 'city': 'Boston'}
        self.assertEqual(result, expected)

    def test_iloc_single_zero(self):
        result = self.db.iloc[0]
        expected = {'name': 'Alice', 'age': 25, 'city': 'New York'}
        self.assertEqual(result, expected)

    def test_iloc_slice_positive(self):
        result = self.db.iloc[1:3]
        expected = [
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_slice_negative(self):
        result = self.db.iloc[-3:-1]
        expected = [
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
            (3, {'name': 'David', 'age': 40, 'city': 'Seattle'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_slice_full(self):
        result = self.db.iloc[:]
        expected = self.db.all()
        self.assertEqual(result, expected)

    def test_iloc_slice_with_step(self):
        result = self.db.iloc[0:5:2]
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
            (4, {'name': 'Alice', 'age': 26, 'city': 'Boston'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_out_of_bounds(self):
        result = self.db.iloc[5]
        self.assertIsNone(result)
        result = self.db.iloc[-6]
        self.assertIsNone(result)

    def test_iloc_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            self.db.iloc["not_an_index"]
        self.assertEqual(str(cm.exception), "Expected int or slice, got str")

    def test_iloc_after_modification(self):
        self.db.delete(1)
        result = self.db.iloc[1]
        expected = {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
        self.assertEqual(result, expected)
        result = self.db.iloc[:]
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
            (3, {'name': 'David', 'age': 40, 'city': 'Seattle'}),
            (4, {'name': 'Alice', 'age': 26, 'city': 'Boston'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_empty_store(self):
        empty_db = MemStore()
        result = empty_db.iloc[0]
        self.assertIsNone(result)
        result = empty_db.iloc[:]
        self.assertEqual(result, [])

    def test_iloc_single_after_all_deleted(self):
        for i in range(5):
            self.db.delete(i)
        result = self.db.iloc[0]
        self.assertIsNone(result)

    def test_iloc_slice_empty_range(self):
        result = self.db.iloc[2:1]
        self.assertEqual(result, [])

    def test_iloc_with_filter_interaction(self):
        filtered = self.db.filter({'city': 'Boston'})
        self.assertEqual(self.db.iloc[1], filtered[0][1])

    def test_iloc_with_filter_first(self):
        first_alice = self.db.filter_first({'name': 'Alice'})
        self.assertEqual(self.db.iloc[0], first_alice)
        self.assertIsNone(self.db.filter_first({'name': 'Unknown'}))

    def test_iloc_with_filter_last(self):
        last_alice = self.db.filter_last({'name': 'Alice'})
        self.assertEqual(self.db.iloc[-1], last_alice)
        self.assertIsNone(self.db.filter_last({'name': 'Unknown'}))


if __name__ == "__main__":
    unittest.main()
