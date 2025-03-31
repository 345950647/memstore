from __future__ import annotations

import collections
import itertools
import typing


class MemStore:
    _Record: collections.namedtuple

    def __init__(
            self,
            fields: list[str],
            indexes: list[str | tuple[str, ...]] | None = None,
    ) -> None:
        self._fields: tuple[str, ...] = tuple(fields)
        self._Record: collections.namedtuple = collections.namedtuple('Record', fields)
        self._data: dict[int, 'MemStore._Record'] = {}
        self._indexes: dict[
            str,
            dict[typing.Any, set[int]],
        ] = collections.defaultdict(lambda: collections.defaultdict(set))
        self._id_counter: itertools.count = itertools.count()
        if indexes:
            for index in indexes:
                self.add_index(index)

    def _update_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
    ) -> None:
        for field, index in self._indexes.items():
            index[record[field]].add(id_)

    def insert(self, value: dict[str, typing.Any]) -> int:
        id_ = next(self._id_counter)
        record = self._Record(*(value[field] for field in self._fields))
        self._data[id_] = record
        self._update_indexes(id_, record)
        return id_

    def insert_many(self, values: list[dict[str, typing.Any]]) -> list[int]:
        return [self.insert(value) for value in values]

    def get(self, record_id: int) -> 'MemStore._Record' | None:
        return self._data.get(record_id)

    def get_by_index(
            self,
            field: str,
            value: typing.Any,
    ) -> list[tuple[int, 'MemStore._Record']]:
        indexes = self._indexes
        if field in indexes:
            index = indexes[field]
            if value in index:
                data = self._data
                result = [(i, data[i]) for i in index[value]]
            else:
                result = []
        else:
            result = []
        return result

    def _remove_from_affected_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
            affected_fields: set[str],
    ) -> None:
        for field, index in self._indexes.items():
            if field in affected_fields:
                value = record[field]
                if id_ in index[value]:
                    index[value].remove(id_)
                    if not index[value]:
                        del index[value]

    def _update_affected_indexes(
            self,
            id_: int,
            record: 'MemStore._Record',
            affected_fields: set[str],
    ) -> None:
        for field, index in self._indexes.items():
            if field in affected_fields:
                index[record[field]].add(id_)

    def update(self, record_id: int, value: dict[str, typing.Any]) -> bool:
        store = self._data
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
        result = 0
        store = self._data
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
        for field, index in self._indexes.items():
            value = record[field]
            if id_ in index[value]:
                index[value].remove(id_)
                if not index[value]:
                    del index[value]

    def delete(
            self,
            id_: int,
    ) -> bool:
        data = self._data
        if id_ in data:
            self._remove_from_indexes(id_, data[id_])
            del data[id_]
            result = True
        else:
            result = False
        return result

    def all(self) -> list[tuple[int, 'MemStore._Record']]:
        return list(self._data.items())

    def add_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field not in indexes:
            index = indexes[field]
            for id_, record in self._data.items():
                index[record[field]].add(id_)

    def drop_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field in indexes:
            del indexes[field]
