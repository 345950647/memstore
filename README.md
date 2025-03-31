# MemStore

`MemStore` is a lightweight in-memory database written in Python. It supports key-value storage, indexing, and retrieval
by insertion order. It uses `collections.namedtuple` for records and `llist.dllist` to maintain insertion order.

---

## Installation

To use `MemStore`, install the required dependency:

```shell
pip install llist
```

---

## Usage Examples

### 1. Initialize the Database

Create a database with fields and optional indexes:

```python
from mem_store import MemStore

# Initialize with fields 'name', 'age', 'city' and indexes on 'name' and ('name', 'age')
db = MemStore(fields=['name', 'age', 'city'], indexes=['name', ('name', 'age')])
```

### 2. Insert Records

Add single or multiple records:

```python
# Insert a single record
record_id = db.insert({'name': 'Alice', 'age': 25, 'city': 'New York'})
print(f"Inserted record with ID: {record_id}")  # Output: Inserted record with ID: 0

# Insert multiple records
record_ids = db.insert_many([
    {'name': 'Bob', 'age': 30, 'city': 'Boston'},
    {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
])
print(f"Inserted records with IDs: {record_ids}")  # Output: Inserted records with IDs: [1, 2]
```

### 3. Query Records

Retrieve records by ID, insertion order, or index:

```python
# Get by ID
record = db.get(0)
print(record)  # Output: Record(name='Alice', age=25, city='New York')

# Get by insertion order (last record)
last_record = db.get_by_insertion_order(-1)
print(last_record)  # Output: (2, Record(name='Charlie', age=35, city='Chicago'))

# Get by insertion order (slice)
slice_records = db.get_by_insertion_order(slice(0, 2))
print(slice_records)  # Output: [(0, Record(name='Alice', ...)), (1, Record(name='Bob', ...))]

# Get by index
alice_records = db.get_by_index('name', 'Alice')
print(alice_records)  # Output: [(0, Record(name='Alice', age=25, city='New York'))]

bob_by_composite = db.get_by_index(('name', 'age'), ('Bob', 30))
print(bob_by_composite)  # Output: [(1, Record(name='Bob', age=30, city='Boston'))]
```

### 4. Update Records

Update a single record or multiple records by index:

```python
# Update a single record
success = db.update(0, {'age': 26})
print(f"Update successful: {success}")  # Output: Update successful: True
print(db.get(0))  # Output: Record(name='Alice', age=26, city='New York')

# Update by index
updated_count = db.update_by_index('name', 'Bob', {'city': 'Seattle'})
print(f"Updated {updated_count} records")  # Output: Updated 1 records
print(db.get(1))  # Output: Record(name='Bob', age=30, city='Seattle')
```

### 5. Delete Records

Remove a record by ID:

```python
success = db.delete(2)
print(f"Delete successful: {success}")  # Output: Delete successful: True
print(db.all())  # Output: [(0, Record(...)), (1, Record(...))]
```

### 6. List All Records

Retrieve all records in the database:

```python
all_records = db.all()
for record_id, record in all_records:
    print(f"ID {record_id}: {record}")
# Output:
# ID 0: Record(name='Alice', age=26, city='New York')
# ID 1: Record(name='Bob', age=30, city='Seattle')
```

### 7. Manage Indexes

Add or remove indexes dynamically:

```python
# Add a new index
db.add_index('city')
print(db.get_by_index('city', 'New York'))  # Output: [(0, Record(name='Alice', ...))]

# Drop an index
db.drop_index('name')
print('name' in db._indexes)  # Output: False
```

---

## Notes

- Field Validation: When inserting, all fields must match the initialized fields. Updates can use a subset of fields.
- Indexes: Supports single-field indexes (e.g., 'name') and composite indexes (e.g., ('name', 'age')).
- Exceptions: Invalid inputs (e.g., non-dict values, invalid fields) raise ValueError.