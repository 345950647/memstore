# MemStore

`MemStore` is a lightweight in-memory database written in Python. It supports key-value storage with integer IDs,
single-field indexing, and basic CRUD operations. It uses dictionaries for data storage and retrieval.

---

## Installation

Since `MemStore` is a single-class implementation, you can simply include it in your project. No external package
installation is required. Alternatively, if packaged:

```shell
pip install mem-store
```

---

## Usage Examples

### 1. Initialize the Database

Create a database with optional indexes:

```python
from mem_store import MemStore

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

Retrieve records by ID or index:

```python
# Get by ID
record = db.get(0)
print(record)  # Output: {'name': 'Alice', 'age': 25, 'city': 'New York'}

# Get by index
alice_records = db.get_by_index('name', 'Alice')
print(alice_records)  # Output: [(0, {'name': 'Alice', 'age': 25, 'city': 'New York'})]
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

### 5. Delete Records

Remove a record by ID:

```python
success = db.delete(0)
print(f"Delete successful: {success}")  # Output: Delete successful: True
print(db.all())  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})]
```

### 6. Manage Indexes

Add or remove indexes dynamically:

```python
# Add a new index
db.add_index('city')
print(db.get_by_index('city', 'Boston'))  # Output: [(1, {'name': 'Bob', 'age': 30, 'city': 'Boston'})]

# Drop an index
db.drop_index('name')
print('name' in db._indexes)  # Output: False
```

---

## Notes

- **Data Structure**: Records are stored as dictionaries with integer IDs assigned sequentially.
- **Indexes**: Only single-field indexes are supported (e.g., `'name'`). Composite indexes are not available.
- **Limitations**: No field validation or update methods are provided. Deletion and retrieval are ID-based or
  index-based only.
- **Dependencies**: Uses only Python standard library modules (`collections`, `itertools`, `typing`).