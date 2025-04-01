import unittest

from memstore import MemStore


class TestMemStoreIloc(unittest.TestCase):
    def setUp(self):
        self.db = MemStore(indexes=['name'])
        self.db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
        self.db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        self.db.add({'name': 'David', 'age': 40, 'city': 'Seattle'})

    def test_iloc_single_positive(self):
        result = self.db.iloc[1]
        expected = {'name': 'Bob', 'age': 30, 'city': 'Boston'}
        self.assertEqual(result, expected)

    def test_iloc_single_negative(self):
        result = self.db.iloc[-1]
        expected = {'name': 'David', 'age': 40, 'city': 'Seattle'}
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
            (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_slice_full(self):
        result = self.db.iloc[:]
        expected = self.db.all()
        self.assertEqual(result, expected)

    def test_iloc_slice_with_step(self):
        result = self.db.iloc[0:4:2]
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        ]
        self.assertEqual(result, expected)

    def test_iloc_out_of_bounds(self):
        self.assertIsNone(self.db.iloc[4])
        self.assertIsNone(self.db.iloc[-5])

    def test_iloc_invalid_type(self):
        with self.assertRaises(TypeError):
            self.db.iloc["not_an_index"]

    def test_iloc_after_modification(self):
        self.db.delete(1)
        result = self.db.iloc[1]
        expected = {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
        self.assertEqual(result, expected)
        result = self.db.iloc[:]
        expected = [
            (0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
            (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
            (3, {'name': 'David', 'age': 40, 'city': 'Seattle'})
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
