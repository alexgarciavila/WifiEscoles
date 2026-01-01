# FavoritesManager API Contract

**Module**: `wifi_connector.data.favorites_manager`  
**Feature**: 002-favorite-centers  
**Created**: 2025-12-13

---

## Class: FavoritesManager

**Purpose**: Manage favorite centers persistence and state.

**Responsibilities**:
- Load favorites from favoritos.json
- Add/remove centers from favorites
- Validate favorites against wifi.json
- Persist changes atomically to disk

---

## Constructor

```python
def __init__(
    self,
    favorites_path: Path,
    credentials_manager: CredentialsManager
) -> None:
```

**Parameters**:
- `favorites_path` - Path to favoritos.json file (typically `Json/favoritos.json`)
- `credentials_manager` - Reference to CredentialsManager for validation

**Postconditions**:
- Instance initialized with empty favorites list
- No file I/O occurs (deferred to `load_favorites()`)

**Example**:
```python
from pathlib import Path
from wifi_connector.data.favorites_manager import FavoritesManager
from wifi_connector.data.credentials_manager import CredentialsManager

creds_mgr = CredentialsManager(Path("Json/wifi.json"))
fav_mgr = FavoritesManager(
    Path("Json/favoritos.json"),
    creds_mgr
)
```

---

## Method: load_favorites

```python
def load_favorites(self) -> bool:
```

**Purpose**: Load and validate favorites from favoritos.json

**Behavior**:
1. Read favoritos.json
2. Parse JSON array
3. Validate each center against wifi.json (center_code exists)
4. Filter out obsolete centers
5. If obsolete centers found, re-save cleaned list
6. Load valid favorites into `_favorites`

**Returns**:
- `True` - Favorites loaded successfully (even if empty list)
- `False` - File not found or JSON parse error

**Side Effects**:
- May write to favoritos.json if auto-cleanup occurs
- Logs warnings for obsolete favorites or parse errors

**Error Handling**:
- `FileNotFoundError` → return False, initialize empty list
- `json.JSONDecodeError` → return False, log warning, initialize empty list
- Does NOT raise exceptions

**Example**:
```python
if fav_mgr.load_favorites():
    print(f"Loaded {len(fav_mgr.get_favorites())} favorites")
else:
    print("No favorites file or parse error, starting fresh")
```

---

## Method: add_favorite

```python
def add_favorite(self, center: CenterCredentials) -> None:
```

**Purpose**: Add center to favorites and persist immediately

**Parameters**:
- `center` - CenterCredentials instance to add

**Preconditions**:
- `center.center_code` MUST exist in wifi.json (validated)

**Behavior**:
1. Validate center exists in wifi.json
2. If already favorited (by center_code), do nothing
3. Add to `_favorites` list
4. Persist to favoritos.json atomically

**Side Effects**:
- Writes to favoritos.json
- Updates in-memory `_favorites` list

**Error Handling**:
- If center not in wifi.json → log warning, do nothing
- If write fails → log error, state remains in-memory but not persisted

**Example**:
```python
center = creds_mgr.get_center_by_code("08012345")
fav_mgr.add_favorite(center)
```

---

## Method: remove_favorite

```python
def remove_favorite(self, center_code: str) -> None:
```

**Purpose**: Remove center from favorites and persist immediately

**Parameters**:
- `center_code` - Unique center code (8 digits)

**Behavior**:
1. Find center in `_favorites` by center_code
2. If not found, do nothing
3. Remove from `_favorites` list
4. Persist to favoritos.json atomically

**Side Effects**:
- Writes to favoritos.json
- Updates in-memory `_favorites` list

**Error Handling**:
- If center_code not in favorites → do nothing (idempotent)
- If write fails → log error, state remains in-memory but not persisted

**Example**:
```python
fav_mgr.remove_favorite("08012345")
```

---

## Method: is_favorite

```python
def is_favorite(self, center_code: str) -> bool:
```

**Purpose**: Check if center is currently favorited

**Parameters**:
- `center_code` - Unique center code to check

**Returns**:
- `True` - Center is in favorites
- `False` - Center is not in favorites

**Performance**: O(n) where n = number of favorites (typically <100)

**Example**:
```python
if fav_mgr.is_favorite("08012345"):
    icon = fav_icon
else:
    icon = fav_unchecked_icon
```

---

## Method: get_favorites

```python
def get_favorites(self) -> List[CenterCredentials]:
```

**Purpose**: Get all favorite centers

**Returns**: List of CenterCredentials instances (may be empty)

**Notes**:
- Returns copy of internal list (modifications don't affect state)
- Order is insertion order (order centers were favorited)

**Example**:
```python
for center in fav_mgr.get_favorites():
    print(f"{center.center_code}: {center.center_name}")
```

---

## Method: _save_favorites (Private)

```python
def _save_favorites(self, favorites: List[CenterCredentials]) -> None:
```

**Purpose**: Persist favorites to disk atomically

**Parameters**:
- `favorites` - List of CenterCredentials to save

**Behavior**:
1. Serialize to JSON (indent=2 for readability)
2. Write to temporary file (.tmp extension)
3. Atomic rename to favoritos.json
4. Log success

**Atomicity**: Uses `Path.replace()` which is atomic on Windows/Unix

**Error Handling**:
- If write fails → log error, raise IOError
- Calling code MUST handle IOError gracefully

**Not part of public API** - internal implementation detail

---

## Dependencies

**Required**:
- `wifi_connector.data.credentials_manager.CredentialsManager` (validation)
- `wifi_connector.data.credentials_manager.CenterCredentials` (data model)
- `wifi_connector.utils.logger.Logger` (logging)
- `pathlib.Path` (file paths)
- `json` (serialization)
- `typing` (type hints)

**Optional**: None

---

## File Format Contract

**favoritos.json**:
```json
[
  {
    "center_code": "string (8 digits)",
    "center_name": "string (non-empty)",
    "username": "string (non-empty)",
    "password": "string (non-empty)"
  }
]
```

**Invariants**:
- MUST be valid JSON array
- Each element MUST have all 4 fields
- `center_code` MUST match `^\d{8}$`
- Empty array `[]` is valid
- File MAY not exist (treated as empty array)

---

## Thread Safety

**Not thread-safe** - Assumes single-threaded GUI application.

If concurrent access needed in future:
- Add `threading.Lock` around `_favorites` access
- Use file locking for favoritos.json writes

---

## Performance Guarantees

- `is_favorite()`: O(n) where n = favorites count
- `add_favorite()`: O(n) + disk I/O (~1ms)
- `remove_favorite()`: O(n) + disk I/O (~1ms)
- `get_favorites()`: O(n) for list copy
- `load_favorites()`: O(n*m) where n = favorites, m = wifi.json entries

**Expected**: All operations <10ms for n <100

---

## Testing Contract

**Unit Tests Must Cover**:
1. load_favorites() with valid file
2. load_favorites() with missing file
3. load_favorites() with corrupted JSON
4. load_favorites() with obsolete centers (auto-cleanup)
5. add_favorite() with valid center
6. add_favorite() with duplicate center (idempotent)
7. remove_favorite() with existing center
8. remove_favorite() with non-existing center (idempotent)
9. is_favorite() for favorited and non-favorited centers
10. get_favorites() returns copy not reference

**Integration Tests Must Cover**:
1. Full flow: load → add → remove → persist → reload
2. Atomic write behavior (simulate crash during write)
3. Auto-cleanup of obsolete favorites on load

---

## Security Considerations

- **Passwords in plaintext**: favoritos.json contains passwords (same as wifi.json)
- **File permissions**: Relies on OS file permissions (no explicit encryption)
- **Input validation**: Validates center_code format before persistence

**Risk Level**: MEDIUM (inherits wifi.json security posture)

---

## Example Usage

```python
from pathlib import Path
from wifi_connector.data.credentials_manager import CredentialsManager
from wifi_connector.data.favorites_manager import FavoritesManager

# Initialize
creds_mgr = CredentialsManager(Path("Json/wifi.json"))
creds_mgr.load_credentials()

fav_mgr = FavoritesManager(Path("Json/favoritos.json"), creds_mgr)
fav_mgr.load_favorites()

# Add favorite
center = creds_mgr.get_center_by_code("08012345")
fav_mgr.add_favorite(center)

# Check if favorite
if fav_mgr.is_favorite("08012345"):
    print("Center is favorited!")

# Get all favorites
for fav in fav_mgr.get_favorites():
    print(f"⭐ {fav.center_name}")

# Remove favorite
fav_mgr.remove_favorite("08012345")
```

---

## Version History

- **v1.0.0** (2025-12-13): Initial contract definition
