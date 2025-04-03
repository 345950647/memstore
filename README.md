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

### 4. Filter First and Last Records

Retrieve the first or last inserted record matching specific conditions:

```python
# Add more records with duplicate names
db.add({'name': 'Bob', 'age': 30, 'city': 'Boston'})  # ID: 1
db.add({'name': 'Alice', 'age': 26, 'city': 'Boston'})  # ID: 2
db.add({'name': 'Charlie', 'age': 35, 'city': 'Chicago'})  # ID: 3

# Get the first inserted Alice (earliest by ID)
first_alice = db.filter_first({'name': 'Alice'})
print(first_alice)  # Output: {'name': 'Alice', 'age': 25, 'city': 'New York'}

# Get the last inserted Alice (latest by ID)
last_alice = db.filter_last({'name': 'Alice'})
print(last_alice)  # Output: {'name': 'Alice', 'age': 26, 'city': 'Boston'}

# Filter first with multiple conditions
first_boston = db.filter_first({'city': 'Boston'})
print(first_boston)  # Output: {'name': 'Bob', 'age': 30, 'city': 'Boston'}

# Filter last with multiple conditions
last_boston = db.filter_last({'city': 'Boston'})
print(last_boston)  # Output: {'name': 'Alice', 'age': 26, 'city': 'Boston'}

# No match returns None
no_match = db.filter_first({'name': 'David'})
print(no_match)  # Output: None
```

### 5. List All Records

Retrieve all records in the database:

```python
all_records = db.all()
for record_id, record in all_records:
    print(f"ID {record_id}: {record}")
# Output:
# ID 0: {'name': 'Alice', 'age': 25, 'city': 'New York'}
# ID 1: {'name': 'Bob', 'age': 30, 'city': 'Boston'}
# ID 2: {'name': 'Alice', 'age': 26, 'city': 'Boston'}
# ID 3: {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
```

### 6. Slice Records with `islice`

Retrieve a subset of records using integer-based slicing with `islice`:

```python
# Slice from start to position 2 (exclusive)
slice_1 = db.islice(stop=2)
print(slice_1)
# Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
#          (1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})]

# Slice from position 1 to 3
slice_2 = db.islice(1, 3)
print(slice_2)
# Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#          (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'})]

# Slice with step (every second record)
slice_3 = db.islice(0, None, 2)
print(slice_3)
# Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
#          (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'})]

# Slice with negative indexes (last two records)
slice_4 = db.islice(-2, None)
print(slice_4)
# Output: [(2, {'name': 'Alice', 'age': 26, 'city': 'Boston'}),
#          (3, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})]
```

### 7. Access Records with `iloc`

Retrieve records by integer position using `iloc`, supporting both single index and slice operations:

```python
# Get a single record by position
record = db.iloc[1]
print(record)  # Output: {'name': 'Bob', 'age': 30, 'city': 'Boston'}

# Get the last record using negative index
last_record = db.iloc[-1]
print(last_record)  # Output: {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}

# Slice records with iloc
slice_iloc = db.iloc[1:3]
print(slice_iloc)
# Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#          (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'})]

# Slice with step using iloc
slice_step = db.iloc[0::2]
print(slice_step)
# Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'}),
#          (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'})]
```

### 8. Delete Records

Remove a record by ID:

```python
success = db.delete(0)
print(f"Delete successful: {success}")  # Output: Delete successful: True
print(db.all())  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#                           (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'}),
#                           (3, {'name': 'Charlie', 'age': 35, 'city': 'Chicago'})]
```

### 9. Manage Indexes

Add or remove indexes dynamically:

```python
# Add a new index
db.add_index('city')
print(db.filter({'city': 'Boston'}))  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'}),
#                                               (2, {'name': 'Alice', 'age': 26, 'city': 'Boston'})]

# Drop an index
db.drop_index('name')
print('name' in db._indexes)  # Output: False
```

---

## Notes

- **Data Structure**: Records are stored as dictionaries with integer IDs assigned sequentially using
  `itertools.count()`. Lower IDs represent earlier insertions, and higher IDs represent later insertions.
- **Indexes**: Only single-field indexes are supported (e.g., `'name'`). Composite indexes are not available.
- **Filtering**:
    - The `filter` method retrieves all records matching specified field-value pairs, using indexes when available for
      efficiency. It works with both indexed and non-indexed fields and returns a list of `(id, record)` tuples.
    - The `filter_first` method retrieves the earliest inserted record (lowest ID) matching the conditions, returning a
      dictionary or `None` if no match.
    - The `filter_last` method retrieves the latest inserted record (highest ID) matching the conditions, returning a
      dictionary or `None` if no match.
- **Slicing with `islice`**: The `islice` method allows positional slicing of records using integer indexes (positive or
  negative), supporting `start`, `stop`, and `step` parameters. It returns a list of `(id, record)` tuples.
- **Positional Access with `iloc`**: The `iloc` property provides a pandas-like interface for accessing records by
  integer position. It supports single integer indexing (returns a record dictionary or `None` if out of range) and
  slicing (returns a list of `(id, record)` tuples).
- **Limitations**: No field validation or update methods are provided. Deletion and retrieval are ID-based or
  filter-based only.
- **Dependencies**: Uses only Python standard library modules.