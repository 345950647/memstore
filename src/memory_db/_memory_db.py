from __future__ import annotations

import collections
import itertools

import llist


class MemoryDB:
    _Record: collections.namedtuple

    def __init__(self, fields: list[str], indexes: list[str | tuple[str, ...]] | None = None) -> None:
        self._fields: tuple[str, ...] = tuple(fields)
        self._field_indices: dict[str, int] = {field: i for i, field in enumerate(fields)}
        self._Record: collections.namedtuple = collections.namedtuple('Record', fields)
        self._store: dict[int, 'MemoryDB._Record'] = {}
        self._indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = collections.defaultdict(
            lambda: collections.defaultdict(set))
        self._id_counter: itertools.count = itertools.count()
        self._insertion_order: llist.dllist = llist.dllist()
        self._inserted_nodes: dict[int, llist.dllistnode] = {}
        self._inserted_set: set[int] = set()
        if indexes:
            for index in indexes:
                self.add_index(index)

    def _validate_value(self, value: dict[str, object], require_all_fields: bool = False) -> None:
        if not isinstance(value, dict):
            raise ValueError('Value must be a dictionary')
        value_fields: set[str] = set(value.keys())
        if require_all_fields and value_fields != set(self._fields):
            raise ValueError(f'Value must contain all fields: {self._fields}')
        if not require_all_fields and not value_fields.issubset(self._fields):
            raise ValueError(f'Value must contain valid fields from: {self._fields}')

    def _normalize_fields(self, fields: str | tuple[str, ...]) -> str | tuple[str, ...]:
        if isinstance(fields, str):
            result: str | tuple[str, ...] = fields
        elif isinstance(fields, tuple):
            result: str | tuple[str, ...] = fields
        else:
            raise ValueError('Fields must be a string (single index) or tuple (composite index)')
        if not all(f in self._fields for f in (result if isinstance(result, tuple) else (result,))):
            raise ValueError(f'Index fields must be in {self._fields}')
        return result

    def insert(self, value: dict[str, object]) -> int:
        self._validate_value(value, require_all_fields=True)
        fields: tuple[str, ...] = self._fields
        store: dict[int, 'MemoryDB._Record'] = self._store
        id_counter: itertools.count = self._id_counter
        new_id: int = next(id_counter)
        record: 'MemoryDB._Record' = self._Record(*(value[field] for field in fields))
        store[new_id] = record
        self._update_indexes(new_id, record)
        node: llist.dllistnode = self._insertion_order.append(new_id)
        self._inserted_nodes[new_id] = node
        self._inserted_set.add(new_id)
        return new_id

    def insert_many(self, values: list[dict[str, object]]) -> list[int]:
        result: list[int] = []
        fields: tuple[str, ...] = self._fields
        store: dict[int, 'MemoryDB._Record'] = self._store
        id_counter: itertools.count = self._id_counter
        Record: collections.namedtuple = self._Record
        for value in values:
            self._validate_value(value, require_all_fields=True)
            new_id: int = next(id_counter)
            record: 'MemoryDB._Record' = Record(*(value[field] for field in fields))
            store[new_id] = record
            self._update_indexes(new_id, record)
            node: llist.dllistnode = self._insertion_order.append(new_id)
            self._inserted_nodes[new_id] = node
            self._inserted_set.add(new_id)
            result.append(new_id)
        return result

    def get(self, record_id: int) -> 'MemoryDB._Record' | None:
        store: dict[int, 'MemoryDB._Record'] = self._store
        result: 'MemoryDB._Record' | None = store.get(record_id)
        return result

    def get_by_insertion_order(
            self,
            slice_obj: int | slice = -1,
    ) -> tuple[int, 'MemoryDB._Record'] | list[tuple[int, 'MemoryDB._Record']] | None:
        store: dict[int, 'MemoryDB._Record'] = self._store
        result: tuple[int, 'MemoryDB._Record'] | list[tuple[int, 'MemoryDB._Record']] | None = None
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

            ids_list: list[int] = list(self._insertion_order)
            sliced_ids: list[int] = ids_list[slice_start:slice_stop:slice_step]
            result_list: list[tuple[int, 'MemoryDB._Record']] = [(record_id, store[record_id]) for record_id in
                                                                 sliced_ids]
            if isinstance(slice_obj, slice) and len(result_list) > 1:
                result = result_list
            elif result_list:
                result = result_list[0]
        return result

    def update(self, record_id: int, value: dict[str, object]) -> bool:
        result: bool = False
        store: dict[int, 'MemoryDB._Record'] = self._store
        fields: tuple[str, ...] = self._fields
        self._validate_value(value)
        if record_id in store:
            old_record: 'MemoryDB._Record' = store[record_id]
            new_values: list[object] = [value.get(field, old_record[i]) for i, field in enumerate(fields)]
            new_record: 'MemoryDB._Record' = self._Record(*new_values)
            affected_fields: set[str] = set(value.keys())
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = new_record
            self._update_affected_indexes(record_id, new_record, affected_fields)
            result = True
        return result

    def update_by_index(
            self,
            fields: str | tuple[str, ...],
            field_values: object | tuple[object, ...],
            update_values: dict[str, object],
    ) -> int:
        result: int = 0
        store: dict[int, 'MemoryDB._Record'] = self._store
        self._validate_value(update_values)
        matches: list[tuple[int, 'MemoryDB._Record']] = self.get_by_index(fields, field_values)
        affected_fields: set[str] = set(update_values.keys())
        for record_id, old_record in matches:
            new_values: list[object] = [update_values.get(field, old_record[i]) for i, field in enumerate(self._fields)]
            new_record: 'MemoryDB._Record' = self._Record(*new_values)
            self._remove_from_affected_indexes(record_id, old_record, affected_fields)
            store[record_id] = new_record
            self._update_affected_indexes(record_id, new_record, affected_fields)
            result += 1
        return result

    def delete(self, record_id: int) -> bool:
        result: bool = False
        store: dict[int, 'MemoryDB._Record'] = self._store
        if record_id in store:
            value: 'MemoryDB._Record' = store[record_id]
            self._remove_from_indexes(record_id, value)
            del store[record_id]
            if record_id in self._inserted_set:
                node: llist.dllistnode = self._inserted_nodes[record_id]
                self._insertion_order.remove(node)
                del self._inserted_nodes[record_id]
                self._inserted_set.remove(record_id)
            result = True
        return result

    def all(self) -> list[tuple[int, 'MemoryDB._Record']]:
        store: dict[int, 'MemoryDB._Record'] = self._store
        result: list[tuple[int, 'MemoryDB._Record']] = list(store.items())
        return result

    def add_index(self, fields: str | tuple[str, ...]) -> None:
        fields_tuple: str | tuple[str, ...] = self._normalize_fields(fields)
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        if fields_tuple not in indexes:
            _ = indexes[fields_tuple]
            store: dict[int, 'MemoryDB._Record'] = self._store
            for record_id, value in store.items():
                index_value: object = self._get_index_value(fields_tuple, value)
                indexes[fields_tuple][index_value].add(record_id)

    def drop_index(self, fields: str | tuple[str, ...]) -> None:
        fields_tuple: str | tuple[str, ...] = self._normalize_fields(fields)
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        index_to_drop: str | tuple[str, ...] | None = self._find_best_index(fields_tuple)
        if index_to_drop and index_to_drop in indexes:
            del indexes[index_to_drop]

    def get_by_index(
            self,
            fields: str | tuple[str, ...],
            field_values: object | tuple[object, ...],
    ) -> list[tuple[int, 'MemoryDB._Record']]:
        result: list[tuple[int, 'MemoryDB._Record']] = []
        fields_tuple: str | tuple[str, ...] = self._normalize_fields(fields)
        field_values_tuple: tuple[object, ...] = field_values if isinstance(field_values, tuple) else (field_values,)
        if len((fields_tuple,) if isinstance(fields_tuple, str) else fields_tuple) != len(field_values_tuple):
            raise ValueError('Fields and values must have the same length')
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        store: dict[int, 'MemoryDB._Record'] = self._store
        field_indices: dict[str, int] = self._field_indices
        best_index: str | tuple[str, ...] | None = self._find_best_index(fields_tuple)
        if best_index:
            index_values: object = field_values_tuple[0] if isinstance(fields_tuple, str) else tuple(field_values_tuple)
            if index_values in indexes[best_index]:
                record_ids: set[int] = indexes[best_index][index_values]
                result = [(record_id, store[record_id]) for record_id in record_ids if record_id in store and all(
                    store[record_id][field_indices[f]] == v
                    for f, v
                    in zip((fields_tuple,) if isinstance(fields_tuple, str) else fields_tuple, field_values_tuple)
                )]
        return result

    def _find_best_index(self, fields: str | tuple[str, ...]) -> str | tuple[str, ...] | None:
        result: str | tuple[str, ...] | None = None
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        for index_fields in indexes:
            if index_fields == fields:
                result = index_fields
                break
        return result

    def _get_index_value(self, fields: str | tuple[str, ...], value: 'MemoryDB._Record') -> object:
        field_indices: dict[str, int] = self._field_indices
        if isinstance(fields, str):
            result: object = value[field_indices[fields]]
        else:
            indices: list[int] = [field_indices[field] for field in fields]
            result: tuple[object, ...] = tuple(value[i] for i in indices)
        return result

    def _update_indexes(self, record_id: int, value: 'MemoryDB._Record') -> None:
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        for fields in indexes:
            index_value: object = self._get_index_value(fields, value)
            _ = indexes[fields]
            indexes[fields][index_value].add(record_id)

    def _remove_from_indexes(self, record_id: int, value: 'MemoryDB._Record') -> None:
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        for fields in indexes:
            index_value: object = self._get_index_value(fields, value)
            field_index: dict[object, set[int]] = indexes[fields]
            if record_id in field_index[index_value]:
                field_index[index_value].remove(record_id)
                if not field_index[index_value]:
                    del field_index[index_value]

    def _update_affected_indexes(self, record_id: int, value: 'MemoryDB._Record', affected_fields: set[str]) -> None:
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        for fields in indexes:
            if any(field in affected_fields for field in (fields if isinstance(fields, tuple) else (fields,))):
                index_value: object = self._get_index_value(fields, value)
                _ = indexes[fields]
                indexes[fields][index_value].add(record_id)

    def _remove_from_affected_indexes(
            self,
            record_id: int,
            value: 'MemoryDB._Record',
            affected_fields: set[str],
    ) -> None:
        indexes: dict[str | tuple[str, ...], dict[object, set[int]]] = self._indexes
        for fields in indexes:
            if any(field in affected_fields for field in (fields if isinstance(fields, tuple) else (fields,))):
                index_value: object = self._get_index_value(fields, value)
                field_index: dict[object, set[int]] = indexes[fields]
                if record_id in field_index[index_value]:
                    field_index[index_value].remove(record_id)
                    if not field_index[index_value]:
                        del field_index[index_value]
