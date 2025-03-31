from __future__ import annotations

import collections
import itertools
import typing

import llist


class MemStore:
    _Record: collections.namedtuple

    def __init__(self, fields: list[str], indexes: list[str | tuple[str, ...]] | None = None) -> None:
        self._fields: tuple[str, ...] = tuple(fields)
        self._field_indices: dict[str, int] = {field: i for i, field in enumerate(fields)}
        self._Record: collections.namedtuple = collections.namedtuple('Record', fields)
        self._store: dict[int, 'MemStore._Record'] = {}
        self._indexes: dict[str | tuple[str, ...], dict[typing.Any, set[int]]] = collections.defaultdict(
            lambda: collections.defaultdict(set),
        )
        self._id_counter: itertools.count = itertools.count()
        self._insertion_order: llist.dllist = llist.dllist()
        self._inserted_nodes: dict[int, llist.dllistnode] = {}
        self._inserted_set: set[int] = set()
        if indexes:
            for index in indexes:
                self.add_index(index)

    def _validate_value(self, value: dict[str, typing.Any], require_all_fields: bool = False) -> None:
        if not isinstance(value, dict):
            raise ValueError('Value must be a dictionary')
        value_fields: set[str] = set(value.keys())
        if require_all_fields and value_fields != set(self._fields):
            raise ValueError(f'Value must contain all fields: {self._fields}')
        if not require_all_fields and not value_fields.issubset(self._fields):
            raise ValueError(f'Value must contain valid fields from: {self._fields}')

    def _get_index_value(
            self,
            field: str,
            record: 'MemStore._Record',
    ) -> typing.Any:
        return record[self._field_indices[field]]

    def _update_indexes(
            self,
            record_id: int,
            record: 'MemStore._Record',
    ) -> None:
        for fields, index in self._indexes.items():
            index[self._get_index_value(fields, record)].add(record_id)

    def insert(self, value: dict[str, typing.Any]) -> int:
        self._validate_value(value, require_all_fields=True)
        new_id = next(self._id_counter)
        record = self._Record(*(value[field] for field in self._fields))
        self._store[new_id] = record
        self._update_indexes(new_id, record)
        self._inserted_nodes[new_id] = self._insertion_order.append(new_id)
        self._inserted_set.add(new_id)
        return new_id

    def insert_many(self, values: list[dict[str, typing.Any]]) -> list[int]:
        return [self.insert(value) for value in values]

    def get(self, record_id: int) -> 'MemStore._Record' | None:
        return self._store.get(record_id)

    def get_by_index(
            self,
            field: str,
            field_value: typing.Any,
    ) -> list[tuple[int, 'MemStore._Record']]:
        indexes = self._indexes
        if field in indexes:
            index = indexes[field]
            if field_value in index:
                field_indices = self._field_indices
                store = self._store
                result = [
                    (i, store[i]) for i
                    in index[field_value]
                    if i in store and store[i][field_indices[field]] == field_value
                ]
            else:
                result = []
        else:
            result = []
        return result

    def get_by_insertion_order(
            self,
            obj: int | slice = -1,
    ) -> tuple[int, 'MemStore._Record'] | list[tuple[int, 'MemStore._Record']] | None:
        if self._insertion_order:
            if isinstance(obj, int):
                start = obj
                stop = obj + 1 if obj >= 0 else None
                step = 1
            elif isinstance(obj, slice):
                start = obj.start
                stop = obj.stop
                step = obj.step if obj.step is not None else 1
            else:
                raise ValueError('slice_obj must be an integer or slice object')
            store = self._store
            result = [(i, store[i]) for i in list(self._insertion_order)[start:stop:step]]
            if not isinstance(obj, slice):
                result = result[0]
        else:
            result = None
        return result

    def _remove_from_affected_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
            affected_fields: set[str],
    ) -> None:
        for field, index in self._indexes.items():
            if field in affected_fields:
                index_value = self._get_index_value(field, record)
                if id_ in index[index_value]:
                    index[index_value].remove(id_)
                    if not index[index_value]:
                        del index[index_value]

    def _update_affected_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
            affected_fields: set[str],
    ) -> None:
        for field, index in self._indexes.items():
            if field in affected_fields:
                index[self._get_index_value(field, record)].add(id_)

    def update(self, record_id: int, value: dict[str, typing.Any]) -> bool:
        self._validate_value(value)
        store = self._store
        if record_id in store:
            old_record = store[record_id]
            new_record = self._Record(*(value.get(f, old_record[i]) for i, f in enumerate(self._fields)))
            affected_fields = set(value.keys())
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = new_record
            self._update_affected_indexes(record_id, new_record, affected_fields)
            result = True
        else:
            result = False
        return result

    def update_by_index(
            self,
            field: str,
            field_value: typing.Any,
            update_values: dict[str, typing.Any],
    ) -> int:
        self._validate_value(update_values)
        result = 0
        store = self._store
        affected_fields = set(update_values.keys())
        for record_id, old_record in self.get_by_index(field, field_value):
            record = self._Record(*(update_values.get(f, old_record[i]) for i, f in enumerate(self._fields)))
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = record
            self._update_affected_indexes(record_id, record, affected_fields)
            result += 1
        return result

    def _remove_from_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
    ) -> None:
        for fields, index in self._indexes.items():
            index_value = self._get_index_value(fields, record)
            if id_ in index[index_value]:
                index[index_value].remove(id_)
                if not index[index_value]:
                    del index[index_value]

    def delete(
            self,
            id_: int,
    ) -> bool:
        store = self._store
        if id_ in store:
            self._remove_from_indexes(id_, store[id_])
            del store[id_]
            if id_ in self._inserted_set:
                self._insertion_order.remove(self._inserted_nodes[id_])
                del self._inserted_nodes[id_]
                self._inserted_set.remove(id_)
            result = True
        else:
            result = False
        return result

    def all(self) -> list[tuple[int, 'MemStore._Record']]:
        return list(self._store.items())

    def add_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field not in indexes:
            index = indexes[field]
            for record_id, value in self._store.items():
                index[self._get_index_value(field, value)].add(record_id)

    def drop_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field in indexes:
            del indexes[field]
