# MemStore

`MemStore` is a lightweight in-memory database written in Python. It supports key-value storage with integer IDs,
single-field indexing, filtering by field values, and slicing records using integer-based positions. It uses
dictionaries for data storage and retrieval.

---

## Installation

Since `MemStore` is a single-class implementation, you can simply include it in your project. No external package
installation is required. Alternatively, if packaged:

```shell
pip install memstore
```

---

## Usage Examples

### 1. Initialize the Database

Create a database with optional indexes:

```python
from memstore import MemStore

# Initialize with indexes on 'name' and 'age'
db = MemStore(indexes=['name', 'age'])
```

### 2. Insert Records

Add a single record and get its ID:

```python
# Insert a single record
record_id = db.add({'name': 'Alice', 'age': 25, 'city': 'New York'})
print(f"Inserted record with ID: {record_id}")  # Output: Inserted record with ID: 0
```

### 3. Query Records

Retrieve records by ID or filter by field values:

```python
# Get by ID
record = db.get(0)
print(record)  # Output: {'name': 'Alice', 'age': 25, 'city': 'New York'}

# Filter by indexed field
alice_records = db.filter({'name': 'Alice'})
print(alice_records)  # Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'})]

# Filter by non-indexed field
ny_records = db.filter({'city': 'New York'})
print(ny_records)  # Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'})]

# Filter with multiple conditions (mixed indexed and non-indexed)
alice_25_records = db.filter({'name': 'Alice', 'age': 25})
print(alice_25_records)  # Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'})]
```

### 4. List All Records

Retrieve all records in the database:

```python
db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})
all_records = db.all()
for record_id, record in all_records:
    print(f"ID {record_id}: {record}")
# Output:
# ID 0: {'name': 'Alice', 'age': 25, 'city': 'New York'}
# ID 1: {'name': 'Bob', 'age': 30, 'city': 'Boston'}
```

### 5. Slice Records

Retrieve a subset of records using integer-based slicing with `islice`:

```python
# Add more records for slicing examples
db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})
db.add({'name': 'David', 'age': 40, 'city': 'Seattle'})

# Slice from start to position 2 (exclusive)
slice_1 = list(db.islice(stop=2))
print(slice_1)
# Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
#          (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})]

# Slice from position 1 to 3
slice_2 = list(db.islice(1, 3))
print(slice_2)
# Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#          (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})]

# Slice with step (every second record)
slice_3 = list(db.islice(0, None, 2))
print(slice_3)
# Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
#          (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})]

# Slice with negative indexes (last two records)
slice_4 = list(db.islice(-2, None))
print(slice_4)
# Output: [(2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
#          (3, {'name': 'David', 'age': 40, 'city': 'Seattle'})]
```

### 6. Delete Records

Remove a record by ID:

```python
success = db.delete(0)
print(f"Delete successful: {success}")  # Output: Delete successful: True
print(db.all())  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#                           (2, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}),
#                           (3, {'name': 'David', 'age': 40, 'city': 'Seattle'})]
```

### 7. Manage Indexes

Add or remove indexes dynamically:

```python
# Add a new index
db.add_index('city')
print(db.filter({'city': 'Boston'}))  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})]

# Drop an index
db.drop_index('name')
print('name' in db._indexes)  # Output: False
```

---

## Notes

- **Data Structure**: Records are stored as dictionaries with integer IDs assigned sequentially.
- **Indexes**: Only single-field indexes are supported (e.g., `'name'`). Composite indexes are not available.
- **Filtering**: The `filter` method retrieves records matching all specified field-value pairs, using indexes when
  available for efficiency. It works with both indexed and non-indexed fields.
- **Slicing**: The `islice` method allows positional slicing of records using integer indexes (positive or negative),
  supporting `start`, `stop`, and `step` parameters. It returns an iterator, which can be converted to a list if needed.
- **Limitations**: No field validation or update methods are provided. Deletion and retrieval are ID-based or
  filter-based only.
- **Dependencies**: Uses only Python standard library modules (`collections`, `functools`, `itertools`, `operator`,
  `typing`).