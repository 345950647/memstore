from __future__ import annotations

import collections
import functools
import itertools
import typing


class ILoc:
    def __init__(
            self,
            store: 'MemStore',
    ):
        self.store = store

    def __getitem__(
            self,
            item: int | slice,
    ) -> dict[typing.Any, typing.Any] | list[tuple[int, dict[typing.Any, typing.Any]]] | None:
        if isinstance(item, int):
            if item == -1:
                item = self.store.islice(start=item)
            else:
                item = self.store.islice(start=item, stop=item + 1)
            if item:
                item = item[0][1]
            else:
                item = None
        elif isinstance(item, slice):
            item = self.store.islice(start=item.start, stop=item.stop, step=item.step)
        else:
            raise TypeError(f'Expected int or slice, got {type(item).__name__}')
        return item


class MemStore:
    def __init__(
            self,
            indexes: list[typing.Any] | None = None,
    ) -> None:
        self._data: dict[int, dict[typing.Any, typing.Any]] = {}
        self._indexes: dict[
            typing.Any,
            dict[typing.Any, set[int]],
        ] = collections.defaultdict(lambda: collections.defaultdict(set))
        self._ident_counter: itertools.count = itertools.count()
        if indexes is not None:
            [self.add_index(index) for index in indexes]

    def add(
            self,
            values: dict,
    ) -> int:
        ident = next(self._ident_counter)
        self._data[ident] = values
        [index[values[field]].add(ident) for field, index in self._indexes.items() if field in values]
        return ident

    def get(self, ident: int) -> dict[typing.Any, typing.Any] | None:
        return self._data.get(ident)

    def _filter(
            self,
            values: dict[typing.Any, typing.Any],
    ) -> set[int]:
        indexes = self._indexes
        idents = set.intersection(*(
            indexes[field].get(value, set()) if field in indexes
            else {ident for ident, values in self._data.items() if field in values and values[field] == value}
            for field, value in values.items()
        ))
        return idents

    def filter(
            self,
            values: dict[typing.Any, typing.Any],
    ) -> list[tuple[int, dict[typing.Any, typing.Any]]]:
        data = self._data
        result = [(ident, data[ident]) for ident in sorted(self._filter(values))]
        return result

    def filter_last(
            self,
            values: dict[typing.Any, typing.Any],
    ) -> dict[typing.Any, typing.Any] | None:
        idents = self._filter(values)
        if idents:
            result = self._data.get(max(idents))
        else:
            result = None
        return result

    def filter_first(
            self,
            values: dict[typing.Any, typing.Any],
    ) -> dict[typing.Any, typing.Any] | None:
        idents = self._filter(values)
        if idents:
            result = self._data.get(min(idents))
        else:
            result = None
        return result

    def islice(self, start=None, stop=None, step=None) -> list[tuple[int, dict[typing.Any, typing.Any]]]:
        data = self._data
        result = list(itertools.islice(data.items(), *slice(start, stop, step).indices(len(data))))
        return result

    @functools.cached_property
    def iloc(self) -> ILoc:
        return ILoc(self)

    def all(self) -> list[tuple[int, dict[typing.Any, typing.Any]]]:
        return list(self._data.items())

    def delete(
            self,
            ident: int,
    ) -> bool:
        data = self._data
        if ident in data:
            values = data[ident]
            for field, index in self._indexes.items():
                if field in values:
                    value = values[field]
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
            [index[values[field]].add(ident) for ident, values in self._data.items() if field in values]

    def drop_index(
            self,
            field: typing.Any,
    ) -> None:
        indexes = self._indexes
        if field in indexes:
            del indexes[field]
