# Quickstart Guide: Favorites Feature

**Feature**: 002-favorite-centers  
**For**: Developers implementing or reviewing this feature  
**Created**: 2025-12-13

---

## 5-Minute Overview

### What This Feature Does

Permite a usuarios marcar centros educativos como favoritos mediante iconos clicables (⭐) en cada fila. Los favoritos se persisten en `Json/favoritos.json` y usuarios pueden alternar entre ver todos los centros o solo favoritos con un botón toggle en la cabecera.

### Key Components

1. **FavoritesManager** (`wifi_connector/data/favorites_manager.py`)
   - Manages favorites persistence
   - Validates favorites against wifi.json
   - Auto-cleans obsolete favorites

2. **MainWindow** (modifications to `wifi_connector/gui/main_window.py`)
   - Adds favorite icon to each center row
   - Adds toggle button in header
   - Filters search within favorites when mode active

3. **favoritos.json** (`Json/favoritos.json`)
   - Stores favorite centers (same format as wifi.json)
   - Created automatically on first favorite

---

## Quick Implementation Guide

### Step 1: Create FavoritesManager

**File**: `wifi_connector/data/favorites_manager.py`

**Key Methods**:
```python
class FavoritesManager:
    def load_favorites(self) -> bool:
        # Load and validate from favoritos.json
        
    def add_favorite(self, center: CenterCredentials) -> None:
        # Add to favorites and persist
        
    def remove_favorite(self, center_code: str) -> None:
        # Remove from favorites and persist
        
    def is_favorite(self, center_code: str) -> bool:
        # Check if center is favorited
        
    def get_favorites(self) -> List[CenterCredentials]:
        # Get all favorites
```

**See**: [contracts/favorites-manager-api.md](contracts/favorites-manager-api.md) for full API

---

### Step 2: Modify MainWindow

**File**: `wifi_connector/gui/main_window.py`

**Changes**:
1. Load fav.png and fav_unchecked.png in `__init__`
2. Initialize FavoritesManager
3. Add toggle button to header
4. Add favorite icon button to each center row
5. Modify `_filter_centers()` to respect view mode

**See**: [contracts/main-window-gui.md](contracts/main-window-gui.md) for detailed changes

---

### Step 3: Add Icons

**Required Files**:
- `images/fav.png` - Filled star (favorite checked) ✅ Already exists
- `images/fav_unchecked.png` - Empty star (favorite unchecked) ✅ Already exists

**Size**: 24×24 pixels recommended for CTkImage

---

### Step 4: Write Tests

**Unit Tests** (`tests/unit/test_favorites_manager.py`):
- Load/save favorites
- Add/remove favorites
- Validation and auto-cleanup

**Integration Tests** (`tests/integration/test_favorites_flow.py`):
- Full flow: mark → toggle view → search → unmark
- Persistence across restarts
- Error handling (corrupted file, etc.)

**See**: [contracts/favorites-manager-api.md#testing-contract](contracts/favorites-manager-api.md#testing-contract)

---

## File Structure

```
wifi_connector/
├── data/
│   ├── credentials_manager.py    # Existing
│   └── favorites_manager.py      # NEW
└── gui/
    └── main_window.py            # Modified

Json/
├── wifi.json                     # Existing (all centers)
└── favoritos.json                # NEW (favorites)

tests/
├── unit/
│   └── test_favorites_manager.py # NEW
└── integration/
    └── test_favorites_flow.py    # NEW
```

---

## Key Design Decisions

### Why FavoritesManager instead of extending CredentialsManager?
- **Separation of concerns**: CredentialsManager handles all centers, FavoritesManager handles favorites
- **Single responsibility**: Each class has one job
- **Pattern consistency**: Follows existing project structure

### Why persist on every add/remove instead of "Save" button?
- **User expectation**: Modern apps auto-save
- **Spec requirement**: FR-008 and Clarifications specify immediate persistence
- **Data safety**: Reduces risk of losing favorites if app crashes

### Why auto-cleanup obsolete favorites silently?
- **Graceful degradation**: App doesn't crash if wifi.json changes
- **User expectation**: Obsolete entries shouldn't accumulate
- **Clarification decision**: Session 2025-12-13 chose Option A (auto-cleanup)

---

## Common Pitfalls & Solutions

### Pitfall 1: Favorite icon not updating after toggle

**Problem**: Icon stays same after click

**Solution**: Ensure `_toggle_favorite()` calls `_refresh_center_list()` or updates icon directly

```python
def _toggle_favorite(self, center: CenterCredentials):
    # Toggle state
    if self.favorites_manager.is_favorite(center.center_code):
        self.favorites_manager.remove_favorite(center.center_code)
    else:
        self.favorites_manager.add_favorite(center)
    
    # IMPORTANT: Refresh UI
    if self.view_mode == "favorites":
        self._refresh_center_list()  # Full refresh (row disappears)
    else:
        self._update_favorite_icon(center.center_code)  # Just icon
```

---

### Pitfall 2: Search doesn't filter favorites

**Problem**: Search shows all centers even in favorites mode

**Solution**: Ensure `_filter_centers()` checks `self.view_mode`

```python
def _filter_centers(self, search_term: str = ""):
    # CRITICAL: Select source based on view mode
    if self.view_mode == "favorites":
        source_centers = self.favorites_manager.get_favorites()
    else:
        source_centers = self.credentials_manager.get_all_centers()
    
    # Then apply search filter...
```

---

### Pitfall 3: favoritos.json not found error on first run

**Problem**: FileNotFoundError on first launch

**Solution**: `load_favorites()` must handle missing file gracefully

```python
def load_favorites(self) -> bool:
    try:
        with open(self.favorites_path) as f:
            data = json.load(f)
        # Process data...
        return True
    except FileNotFoundError:
        self.logger.info("No favorites file, starting with empty list")
        self._favorites = []
        return False  # Not an error, just no favorites yet
```

---

### Pitfall 4: Grid layout breaks after adding favorite icon

**Problem**: Center rows misaligned after adding favorite icon button

**Solution**: Update ALL column indices in `_create_center_row()`

```python
# BEFORE:
code_label.grid(row=row, column=0, ...)  # Code was column 0
name_label.grid(row=row, column=1, ...)  # Name was column 1
connect_btn.grid(row=row, column=2, ...)  # Button was column 2

# AFTER:
fav_button.grid(row=row, column=0, ...)   # NEW: Favorite icon
code_label.grid(row=row, column=1, ...)   # Code shifts to column 1
name_label.grid(row=row, column=2, ...)   # Name shifts to column 2
connect_btn.grid(row=row, column=3, ...)  # Button shifts to column 3
```

---

## Testing Checklist

Before submitting PR:

- [ ] Unit tests pass (`pytest tests/unit/test_favorites_manager.py`)
- [ ] Integration tests pass (`pytest tests/integration/test_favorites_flow.py`)
- [ ] Manual test: Mark center as favorite → icon changes
- [ ] Manual test: Restart app → favorite persists
- [ ] Manual test: Toggle to favorites view → only favorites shown
- [ ] Manual test: Search in favorites → filters correctly
- [ ] Manual test: Unmark favorite in favorites view → row disappears
- [ ] Manual test: Empty favorites → contextual message shown
- [ ] Manual test: Search in favorites with no results → contextual message shown
- [ ] Visual test: Layout doesn't break with 0, 1, 10, 100+ centers

---

## Performance Targets

- Load 100 favorites: <500ms (SC-004)
- Toggle favorite: <50ms (icon update) or <500ms (full refresh)
- Toggle view mode: <100ms
- Search in favorites: <200ms

**How to test**:
```python
import time

start = time.perf_counter()
fav_mgr.load_favorites()
elapsed = (time.perf_counter() - start) * 1000
print(f"Load time: {elapsed:.2f}ms")
```

---

## Debugging Tips

### Enable debug logging

```python
# In wifi_connector/utils/logger.py
logger.setLevel(logging.DEBUG)  # Change from INFO to DEBUG
```

### Check favoritos.json content

```powershell
Get-Content Json/favoritos.json | ConvertFrom-Json | Format-List
```

### Verify icon files exist

```powershell
Test-Path images/fav.png
Test-Path images/fav_unchecked.png
```

### Trace favorite operations

Add logging in FavoritesManager:
```python
def add_favorite(self, center: CenterCredentials):
    self.logger.debug(f"Adding favorite: {center.center_code}")
    # ... rest of method
```

---

## Next Steps After Implementation

1. **Run full test suite**: `pytest --cov=wifi_connector`
2. **Check coverage**: Ensure favorites_manager.py has >80% coverage
3. **Manual testing**: Follow testing checklist above
4. **Code review**: Request review focusing on:
   - Error handling (corrupted file, missing icons)
   - Performance (100+ favorites)
   - UX (contextual messages, icon alignment)
5. **Update documentation**: Add favorites section to user README

---

## Resources

- **Full API Contract**: [contracts/favorites-manager-api.md](contracts/favorites-manager-api.md)
- **GUI Contract**: [contracts/main-window-gui.md](contracts/main-window-gui.md)
- **Data Model**: [data-model.md](data-model.md)
- **Research**: [research.md](research.md)
- **Spec**: [spec.md](spec.md)

---

## Questions?

If you encounter issues not covered here:
1. Check [research.md](research.md) for design rationale
2. Check [data-model.md](data-model.md) for data structures
3. Check [contracts/](contracts/) for API details
4. Review [spec.md](spec.md) edge cases section

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-13
