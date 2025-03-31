from __future__ import annotations

import collections
import itertools
import typing


class MemStore:
    def __init__(
            self,
            indexes: list[str | tuple[str, ...]] | None = None,
    ) -> None:
        self._data: dict[int, dict] = {}
        self._indexes: dict[
            typing.Any,
            dict[typing.Any, set[int]],
        ] = collections.defaultdict(lambda: collections.defaultdict(set))
        self._ident_counter: itertools.count = itertools.count()
        if indexes:
            [self.add_index(index) for index in indexes]

    def insert(
            self,
            values: dict,
    ) -> int:
        ident = next(self._ident_counter)
        self._data[ident] = values
        [index[values.get(field)].add(ident) for field, index in self._indexes.items()]
        return ident

    def insert_many(
            self,
            values: list[dict],
    ) -> list[int]:
        return [self.insert(value) for value in values]

    def get(self, ident: int) -> dict | None:
        return self._data.get(ident)

    def get_by_index(
            self,
            field: typing.Any,
            value: typing.Any,
    ) -> list[tuple[int, dict]]:
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

    def all(self) -> list[tuple[int, dict]]:
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
            field: typing.Any,
    ) -> None:
        indexes = self._indexes
        if field not in indexes:
            index = indexes[field]
            [index[record[field]].add(ident) for ident, record in self._data.items()]

    def drop_index(
            self,
            field: typing.Any,
    ) -> None:
        indexes = self._indexes
        if field in indexes:
            del indexes[field]
