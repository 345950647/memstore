from __future__ import annotations

import itertools
import unittest

import llist

import memory_db


class TestMemoryDB(unittest.TestCase):
    def setUp(self):
        self.db = memory_db.MemoryDB(['name', 'age', 'city'], indexes=['name', ('name', 'age')])
        self.db.insert({'name': 'Alice', 'age': 25, 'city': 'New York'})
        self.db.insert({'name': 'Bob', 'age': 30, 'city': 'Boston'})

    def test_init(self):
        db = memory_db.MemoryDB(['x', 'y'])
        self.assertEqual(db._fields, ('x', 'y'))
        self.assertEqual(db._field_indices, {'x': 0, 'y': 1})
        self.assertTrue(hasattr(db, '_Record'))
        self.assertEqual(db._store, {})
        self.assertEqual(db._indexes, {})
        self.assertIsInstance(db._id_counter, itertools.count)
        self.assertIsInstance(db._insertion_order, llist.dllist)
        self.assertEqual(db._inserted_nodes, {})
        self.assertEqual(db._inserted_set, set())  # 修复：使用 set() 而不是 {}

    def test_init_with_indexes(self):
        self.assertEqual(set(self.db._indexes.keys()), {'name', ('name', 'age')})
        self.assertIn('Alice', self.db._indexes['name'])
        self.assertIn(('Bob', 30), self.db._indexes[('name', 'age')])

    def test_validate_value(self):
        self.db._validate_value({'name': 'Charlie', 'age': 35, 'city': 'Chicago'}, True)
        self.db._validate_value({'name': 'Charlie'}, False)

        with self.assertRaises(ValueError) as cm:
            self.db._validate_value("not_a_dict", True)
        self.assertEqual(str(cm.exception), 'Value must be a dictionary')

        with self.assertRaises(ValueError) as cm:
            self.db._validate_value({'name': 'Charlie', 'invalid': 1}, False)
        self.assertEqual(str(cm.exception), "Value must contain valid fields from: ('name', 'age', 'city')")

        with self.assertRaises(ValueError) as cm:
            self.db._validate_value({'name': 'Charlie'}, True)
        self.assertEqual(str(cm.exception), "Value must contain all fields: ('name', 'age', 'city')")

    def test_normalize_fields(self):
        self.assertEqual(self.db._normalize_fields('name'), 'name')
        self.assertEqual(self.db._normalize_fields(('name', 'age')), ('name', 'age'))

        with self.assertRaises(ValueError) as cm:
            self.db._normalize_fields(['invalid'])
        self.assertEqual(str(cm.exception), 'Fields must be a string (single index) or tuple (composite index)')

        with self.assertRaises(ValueError) as cm:
            self.db._normalize_fields('invalid')
        self.assertEqual(str(cm.exception), "Index fields must be in ('name', 'age', 'city')")

    def test_insert(self):
        new_id = self.db.insert({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
        self.assertEqual(new_id, 2)
        self.assertEqual(self.db._store[2], self.db._Record('Charlie', 35, 'Chicago'))
        self.assertIn(2, self.db._inserted_set)
        self.assertEqual(self.db._insertion_order.last.value, 2)
        self.assertIn(('Charlie', 35), self.db._indexes[('name', 'age')])

    def test_insert_many(self):
        ids = self.db.insert_many([
            {'name': 'Charlie', 'age': 35, 'city': 'Chicago'},
            {'name': 'David', 'age': 40, 'city': 'Denver'}
        ])
        self.assertEqual(ids, [2, 3])
        self.assertEqual(self.db._store[2], self.db._Record('Charlie', 35, 'Chicago'))
        self.assertEqual(self.db._store[3], self.db._Record('David', 40, 'Denver'))
        self.assertEqual(list(self.db._insertion_order), [0, 1, 2, 3])

    def test_get(self):
        record = self.db.get(0)
        self.assertEqual(record, self.db._Record('Alice', 25, 'New York'))
        self.assertIsNone(self.db.get(999))

    def test_get_by_insertion_order(self):
        self.assertEqual(self.db.get_by_insertion_order(-1), (1, self.db._Record('Bob', 30, 'Boston')))
        self.assertEqual(self.db.get_by_insertion_order(0), (0, self.db._Record('Alice', 25, 'New York')))
        self.assertEqual(self.db.get_by_insertion_order(slice(0, 2)), [
            (0, self.db._Record('Alice', 25, 'New York')),
            (1, self.db._Record('Bob', 30, 'Boston')),
        ])
        self.assertEqual(self.db.get_by_insertion_order(slice(1, 2)), [(1, self.db._Record('Bob', 30, 'Boston'))])

        empty_db = memory_db.MemoryDB(['name', 'age'])
        self.assertIsNone(empty_db.get_by_insertion_order(-1))

        with self.assertRaises(ValueError):
            self.db.get_by_insertion_order("invalid")

    def test_update(self):
        success = self.db.update(0, {'age': 26})
        self.assertTrue(success)
        self.assertEqual(self.db._store[0], self.db._Record('Alice', 26, 'New York'))
        self.assertFalse(self.db.update(999, {'age': 27}))

    def test_update_by_index(self):
        count = self.db.update_by_index('name', 'Bob', {'city': 'Seattle'})
        self.assertEqual(count, 1)
        self.assertEqual(self.db._store[1], self.db._Record('Bob', 30, 'Seattle'))

        count = self.db.update_by_index(('name', 'age'), ('Alice', 25), {'city': 'LA'})
        self.assertEqual(count, 1)
        self.assertEqual(self.db._store[0], self.db._Record('Alice', 25, 'LA'))

    def test_delete(self):
        success = self.db.delete(0)
        self.assertTrue(success)
        self.assertNotIn(0, self.db._store)
        self.assertNotIn(0, self.db._inserted_set)
        self.assertEqual(list(self.db._insertion_order), [1])
        self.assertFalse(self.db.delete(999))

    def test_all(self):
        self.assertEqual(self.db.all(), [
            (0, self.db._Record('Alice', 25, 'New York')),
            (1, self.db._Record('Bob', 30, 'Boston')),
        ])

    def test_add_index(self):
        self.db.add_index('city')
        self.assertIn('city', self.db._indexes)
        self.assertIn('New York', self.db._indexes['city'])
        self.db.add_index('city')

    def test_drop_index(self):
        self.db.drop_index('name')
        self.assertNotIn('name', self.db._indexes)
        self.db.drop_index('invalid')  # 不存在的索引应无影响

    def test_get_by_index(self):
        result = self.db.get_by_index('name', 'Alice')
        self.assertEqual(result, [(0, self.db._Record('Alice', 25, 'New York'))])

        result = self.db.get_by_index(('name', 'age'), ('Bob', 30))
        self.assertEqual(result, [(1, self.db._Record('Bob', 30, 'Boston'))])

        with self.assertRaises(ValueError):
            self.db.get_by_index('name', ('Bob', 30))

    def test_find_best_index(self):
        self.assertEqual(self.db._find_best_index('name'), 'name')
        self.assertEqual(self.db._find_best_index(('name', 'age')), ('name', 'age'))
        self.assertIsNone(self.db._find_best_index('city'))

    def test_get_index_value(self):
        record = self.db._Record('Alice', 25, 'New York')
        self.assertEqual(self.db._get_index_value('name', record), 'Alice')
        self.assertEqual(self.db._get_index_value(('name', 'age'), record), ('Alice', 25))

    def test_update_indexes(self):
        record = self.db._Record('Charlie', 35, 'Chicago')
        self.db._update_indexes(2, record)
        self.assertIn(2, self.db._indexes['name']['Charlie'])
        self.assertIn(2, self.db._indexes[('name', 'age')][('Charlie', 35)])

    def test_remove_from_indexes(self):
        record = self.db._Record('Alice', 25, 'New York')
        self.db._remove_from_indexes(0, record)
        self.assertNotIn(0, self.db._indexes['name']['Alice'])
        self.assertNotIn(0, self.db._indexes[('name', 'age')][('Alice', 25)])

    def test_update_affected_indexes(self):
        record = self.db._Record('Alice', 26, 'New York')
        self.db._update_affected_indexes(0, record, {'age'})
        self.assertIn(0, self.db._indexes[('name', 'age')][('Alice', 26)])

    def test_remove_from_affected_indexes(self):
        record = self.db._Record('Alice', 25, 'New York')
        self.db._remove_from_affected_indexes(0, record, {'age'})
        self.assertNotIn(0, self.db._indexes[('name', 'age')][('Alice', 25)])


if __name__ == '__main__':
    unittest.main()
