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

    def insert(self, value: dict[str, typing.Any]) -> int:
        self._validate_value(value, require_all_fields=True)
        new_id: int = next(self._id_counter)
        record: 'MemStore._Record' = self._Record(*(value[field] for field in self._fields))
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
            fields: str | tuple[str, ...],
            field_values: typing.Any | tuple[typing.Any, ...],
    ) -> list[tuple[int, 'MemStore._Record']]:
        indexes: dict[str | tuple[str, ...], dict[typing.Any, set[int]]] = self._indexes
        if fields in indexes:
            index = indexes[fields]
            if field_values in index:
                field_indices: dict[str, int] = self._field_indices
                store: dict[int, 'MemStore._Record'] = self._store
                if isinstance(fields, str):
                    result = [
                        (i, store[i])
                        for i
                        in index[field_values]
                        if i in store and store[i][field_indices[fields]] == field_values
                    ]
                else:
                    result = [
                        (i, store[i])
                        for i
                        in index[field_values]
                        if i in store and all(store[i][field_indices[f]] == v for f, v in zip(fields, field_values))
                    ]
            else:
                result = []
        else:
            result = []
        return result

    def get_by_insertion_order(
            self,
            slice_obj: int | slice = -1,
    ) -> tuple[int, 'MemStore._Record'] | list[tuple[int, 'MemStore._Record']] | None:
        if self._insertion_order:
            if isinstance(slice_obj, int):
                slice_start: int = slice_obj
                slice_stop: int | None = slice_obj + 1 if slice_obj >= 0 else None
                slice_step: int = 1
            elif isinstance(slice_obj, slice):
                slice_start: int | None = slice_obj.start
                slice_stop: int | None = slice_obj.stop
                slice_step: int = slice_obj.step if slice_obj.step is not None else 1
            else:
                raise ValueError('slice_obj must be an integer or slice object')
            store: dict[int, 'MemStore._Record'] = self._store
            result_list: list[tuple[int, 'MemStore._Record']] = [
                (record_id, store[record_id])
                for record_id
                in list(self._insertion_order)[slice_start:slice_stop:slice_step]
            ]
            if isinstance(slice_obj, slice):
                result = result_list
            elif result_list:
                result = result_list[0]
            else:
                result = None
        else:
            result = None
        return result

    def update(self, record_id: int, value: dict[str, typing.Any]) -> bool:
        self._validate_value(value)
        store: dict[int, 'MemStore._Record'] = self._store
        if record_id in store:
            old_record: 'MemStore._Record' = store[record_id]
            new_record: 'MemStore._Record' = self._Record(
                *(value.get(field, old_record[i]) for i, field in enumerate(self._fields))
            )
            affected_fields: set[str] = set(value.keys())
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = new_record
            self._update_affected_indexes(record_id, new_record, affected_fields)
            result = True
        else:
            result = False
        return result

    def update_by_index(
            self,
            fields: str | tuple[str, ...],
            field_values: typing.Any | tuple[typing.Any, ...],
            update_values: dict[str, typing.Any],
    ) -> int:
        self._validate_value(update_values)
        result: int = 0
        store: dict[int, 'MemStore._Record'] = self._store
        affected_fields: set[str] = set(update_values.keys())
        for record_id, old_record in self.get_by_index(fields, field_values):
            new_values: list[typing.Any] = [
                update_values.get(field, old_record[i]) for i, field in enumerate(self._fields)
            ]
            new_record: 'MemStore._Record' = self._Record(*new_values)
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = new_record
            self._update_affected_indexes(record_id, new_record, affected_fields)
            result += 1
        return result

    def delete(self, record_id: int) -> bool:
        store: dict[int, 'MemStore._Record'] = self._store
        if record_id in store:
            self._remove_from_indexes(record_id, store[record_id])
            del store[record_id]
            if record_id in self._inserted_set:
                node: llist.dllistnode = self._inserted_nodes[record_id]
                self._insertion_order.remove(node)
                del self._inserted_nodes[record_id]
                self._inserted_set.remove(record_id)
            result = True
        else:
            result = False
        return result

    def all(self) -> list[tuple[int, 'MemStore._Record']]:
        return list(self._store.items())

    def _get_index_value(self, fields: str | tuple[str, ...], value: 'MemStore._Record') -> typing.Any:
        field_indices = self._field_indices
        if isinstance(fields, str):
            result: typing.Any = value[field_indices[fields]]
        else:
            result: tuple[typing.Any, ...] = tuple(value[field_indices[field]] for field in fields)
        return result

    def add_index(self, fields: str | tuple[str, ...]) -> None:
        indexes: dict[str | tuple[str, ...], dict[typing.Any, set[int]]] = self._indexes
        if fields not in indexes:
            index = indexes[fields]
            for record_id, value in self._store.items():
                index[self._get_index_value(fields, value)].add(record_id)

    def drop_index(self, fields: str | tuple[str, ...]) -> None:
        indexes: dict[str | tuple[str, ...], dict[typing.Any, set[int]]] = self._indexes
        if fields in indexes:
            del indexes[fields]

    def _update_indexes(self, record_id: int, value: 'MemStore._Record') -> None:
        for fields, index in self._indexes.items():
            index[self._get_index_value(fields, value)].add(record_id)

    def _remove_from_indexes(self, record_id: int, value: 'MemStore._Record') -> None:
        for fields, index in self._indexes.items():
            index_value: typing.Any = self._get_index_value(fields, value)
            if record_id in index[index_value]:
                index[index_value].remove(record_id)
                if not index[index_value]:
                    del index[index_value]

    def _update_affected_indexes(self, record_id: int, value: 'MemStore._Record', affected_fields: set[str]) -> None:
        for fields, index in self._indexes.items():
            if any(field in affected_fields for field in (fields if isinstance(fields, tuple) else (fields,))):
                index[self._get_index_value(fields, value)].add(record_id)

    def _remove_from_affected_indexes(
            self,
            record_id: int,
            value: 'MemStore._Record',
            affected_fields: set[str],
    ) -> None:
        for fields, index in self._indexes.items():
            if any(field in affected_fields for field in (fields if isinstance(fields, tuple) else (fields,))):
                index_value: typing.Any = self._get_index_value(fields, value)
                if record_id in index[index_value]:
                    index[index_value].remove(record_id)
                    if not index[index_value]:
                        del index[index_value]
