from __future__ import annotations

import collections
import itertools
import typing


class MemStore:
    def __init__(
            self,
            fields: list[str],
            indexes: list[str | tuple[str, ...]] | None = None,
    ) -> None:
        Record = collections.namedtuple('Record', fields)

        self.Record: collections.namedtuple = Record

        self._fields: tuple[str, ...] = tuple(fields)
        self._data: dict[int, Record] = {}
        self._indexes: dict[
            str,
            dict[typing.Any, set[int]],
        ] = collections.defaultdict(lambda: collections.defaultdict(set))
        self._ident_counter: itertools.count = itertools.count()
        if indexes:
            [self.add_index(index) for index in indexes]

    def insert(
            self,
            values: dict[str, typing.Any],
    ) -> int:
        ident = next(self._ident_counter)
        record = self.Record(*(values[field] if field in values else None for field in self._fields))
        self._data[ident] = record
        [index[record[field]].add(ident) for field, index in self._indexes.items()]
        return ident

    def insert_many(
            self,
            values: list[dict[str, typing.Any]],
    ) -> list[int]:
        return [self.insert(value) for value in values]

    def get(self, ident: int) -> 'MemStore.Record' | None:
        return self._data.get(ident)

    def get_by_index(
            self,
            field: str,
            value: typing.Any,
    ) -> list[tuple[int, typing.NamedTuple]]:
        indexes = self._indexes
        if field in indexes:
            index = indexes[field]
            if value in index:
                data = self._data
                result = [(ident, data[ident]) for ident in index[value]]
            else:
                result = []
        else:
            result = []
        return result

    def all(self) -> list[tuple[int, 'MemStore.Record']]:
        return list(self._data.items())

    def delete(
            self,
            ident: int,
    ) -> bool:
        data = self._data
        if ident in data:
            record = data[ident]
            for field, index in self._indexes.items():
                value = record[field]
                idents = index[value]
                if ident in idents:
                    idents.remove(ident)
                    if not idents:
                        del index[value]
            del data[ident]
            result = True
        else:
            result = False
        return result

    def add_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field not in indexes:
            index = indexes[field]
            [index[record[field]].add(ident) for ident, record in self._data.items()]

    def drop_index(
            self,
            field: str,
    ) -> None:
        indexes = self._indexes
        if field in indexes:
            del indexes[field]
