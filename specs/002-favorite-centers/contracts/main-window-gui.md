# MainWindow GUI Contract (Favorites Extension)

**Module**: `wifi_connector.gui.main_window`  
**Feature**: 002-favorite-centers  
**Created**: 2025-12-13

---

## Overview

This contract documents the GUI changes to MainWindow for favorites functionality. It EXTENDS existing MainWindow behavior without breaking current functionality.

---

## New Instance Variables

```python
class MainWindow(ctk.CTk):
    # Existing variables...
    
    # NEW for favorites
    favorites_manager: FavoritesManager
    view_mode: str  # "all" or "favorites"
    toggle_button: ctk.CTkButton
    fav_icon: ctk.CTkImage
    fav_unchecked_icon: ctk.CTkImage
```

**Initialization** (in `__init__`):
```python
# Load icons
self.fav_icon = ctk.CTkImage(
    light_image=Image.open("images/fav.png"),
    size=(24, 24)
)
self.fav_unchecked_icon = ctk.CTkImage(
    light_image=Image.open("images/fav_unchecked.png"),
    size=(24, 24)
)

# Initialize favorites manager
self.favorites_manager = FavoritesManager(
    Path("Json/favoritos.json"),
    self.credentials_manager
)
self.favorites_manager.load_favorites()

# Initialize view mode
self.view_mode = "all"
```

---

## Modified Methods

### `__init__` (Extended)

**Changes**:
- Load fav.png and fav_unchecked.png icons
- Initialize FavoritesManager
- Call `load_favorites()`
- Add toggle button to header frame
- Set initial view_mode = "all"

**Impact**: Low - Additions at end of __init__, no breaking changes

---

### `_create_header` (Extended)

**Changes**:
- Add toggle button after search field, before help button

**Layout**:
```
[Logo] [Search Field] [🌟 Toggle] [? Help] [X About]
```

**Implementation**:
```python
# After search field creation...

self.toggle_button = ctk.CTkButton(
    header_frame,
    text="",
    image=self.fav_unchecked_icon,
    width=40,
    height=40,
    command=self._toggle_view_mode,
    fg_color="transparent",
    hover_color=("gray70", "gray30")
)
self.toggle_button.grid(row=0, column=2, padx=5)

# Help button moves to column=3, About button to column=4
```

**Impact**: Medium - Requires adjusting existing button column positions

---

### `_create_center_row` (Extended)

**Changes**:
- Add favorite icon button as first element (column 0)
- Shift existing elements to column 1, 2, 3...

**New Layout per Row**:
```
[⭐ Fav Icon] [Code] [Name] [Connect Button]
```

**Implementation**:
```python
def _create_center_row(self, parent, center: CenterCredentials, row: int):
    # NEW: Favorite icon button
    is_fav = self.favorites_manager.is_favorite(center.center_code)
    fav_button = ctk.CTkButton(
        parent,
        text="",
        image=self.fav_icon if is_fav else self.fav_unchecked_icon,
        width=30,
        height=30,
        command=lambda c=center: self._toggle_favorite(c),
        fg_color="transparent",
        hover_color=("gray70", "gray30")
    )
    fav_button.grid(row=row, column=0, padx=(5,2), pady=5, sticky="w")
    
    # EXISTING: Code label (now column 1 instead of 0)
    code_label = ctk.CTkLabel(parent, text=center.center_code, width=100)
    code_label.grid(row=row, column=1, padx=5, pady=5, sticky="w")
    
    # EXISTING: Name label (now column 2 instead of 1)
    name_label = ctk.CTkLabel(parent, text=center.center_name, width=300)
    name_label.grid(row=row, column=2, padx=5, pady=5, sticky="w")
    
    # EXISTING: Connect button (now column 3 instead of 2)
    connect_btn = ctk.CTkButton(
        parent,
        text="Connectar",
        command=lambda c=center: self._connect_to_center(c),
        width=120
    )
    connect_btn.grid(row=row, column=3, padx=5, pady=5, sticky="e")
```

**Impact**: Medium - Changes grid layout, requires testing visual alignment

---

### `_filter_centers` (Modified)

**Changes**:
- Consider `view_mode` when selecting source centers

**Implementation**:
```python
def _filter_centers(self, search_term: str = ""):
    """Filter centers based on search term and view mode"""
    # MODIFIED: Select source based on view mode
    if self.view_mode == "favorites":
        source_centers = self.favorites_manager.get_favorites()
    else:
        source_centers = self.credentials_manager.get_all_centers()
    
    # EXISTING: Apply search filter
    if search_term:
        search_lower = search_term.lower()
        filtered = [
            c for c in source_centers
            if search_lower in c.center_name.lower()
            or search_lower in c.center_code.lower()
        ]
    else:
        filtered = source_centers
    
    # MODIFIED: Handle empty results with contextual messages
    self._update_display(filtered)
```

**Impact**: Medium - Core filtering logic changes, requires careful testing

---

### `_update_display` (Extended)

**Changes**:
- Add contextual messages for empty lists

**Implementation**:
```python
def _update_display(self, centers: List[CenterCredentials]):
    """Update center list display"""
    self._clear_center_list()
    
    # NEW: Handle empty results with contextual messages
    if not centers:
        search_term = self.search_entry.get()
        
        if self.view_mode == "favorites" and search_term:
            # Búsqueda en favoritos sin resultados
            msg = (
                f"No hi ha resultats a favorits per '{search_term}'.\n"
                "Prova a buscar en tots els centres."
            )
        elif self.view_mode == "favorites":
            # Sin favoritos
            msg = (
                "No tens centres marcats com a favorits.\n"
                "Fes clic a l'icona ⭐ per afegir-ne."
            )
        else:
            # Búsqueda en todos sin resultados
            msg = f"No s'han trobat centres per '{search_term}'."
        
        self._show_empty_message(msg)
        return
    
    # EXISTING: Render center list
    for idx, center in enumerate(centers):
        self._create_center_row(self.scrollable_frame, center, idx)
```

**Impact**: Low - Adds new code paths, doesn't break existing behavior

---

## New Methods

### `_toggle_favorite`

```python
def _toggle_favorite(self, center: CenterCredentials) -> None:
    """Toggle favorite status for a center"""
    if self.favorites_manager.is_favorite(center.center_code):
        self.favorites_manager.remove_favorite(center.center_code)
    else:
        self.favorites_manager.add_favorite(center)
    
    # If in favorites view and center was removed, refresh list
    if self.view_mode == "favorites":
        self._refresh_center_list()
    else:
        # Just update the icon in current row
        self._update_favorite_icon(center.center_code)
```

**Purpose**: Handle click on favorite icon in center row

**Behavior**:
- Toggles favorite state via FavoritesManager
- Refreshes list if in favorites mode (row disappears)
- Updates icon only if in all centers mode

---

### `_toggle_view_mode`

```python
def _toggle_view_mode(self) -> None:
    """Toggle between all centers and favorites view"""
    # Toggle mode
    self.view_mode = "favorites" if self.view_mode == "all" else "all"
    
    # Update toggle button icon
    if self.view_mode == "favorites":
        self.toggle_button.configure(image=self.fav_icon)
    else:
        self.toggle_button.configure(image=self.fav_unchecked_icon)
    
    # Clear search field (FR-011)
    self.search_entry.delete(0, 'end')
    
    # Refresh list
    self._refresh_center_list()
```

**Purpose**: Handle click on toggle button in header

**Behavior**:
- Switches view_mode state
- Updates toggle button icon
- Clears search field (as per FR-011)
- Refreshes entire center list

---

### `_refresh_center_list`

```python
def _refresh_center_list(self) -> None:
    """Refresh the center list based on current view mode and search"""
    search_term = self.search_entry.get()
    self._filter_centers(search_term)
```

**Purpose**: Convenience method to re-render list

**Used By**:
- `_toggle_view_mode()`
- `_toggle_favorite()` (when in favorites mode)
- Search entry callback (existing)

---

### `_update_favorite_icon`

```python
def _update_favorite_icon(self, center_code: str) -> None:
    """Update favorite icon for a specific center without full refresh"""
    is_fav = self.favorites_manager.is_favorite(center_code)
    icon = self.fav_icon if is_fav else self.fav_unchecked_icon
    
    # Find button in scrollable_frame and update image
    # Note: May require tracking button references or full refresh
    # For simplicity, can call _refresh_center_list() instead
    self._refresh_center_list()
```

**Purpose**: Update single icon without full list refresh (optimization)

**Note**: Initial implementation may just call `_refresh_center_list()` for simplicity. Optimization can come later.

---

### `_show_empty_message`

```python
def _show_empty_message(self, message: str) -> None:
    """Show centered message when list is empty"""
    msg_label = ctk.CTkLabel(
        self.scrollable_frame,
        text=message,
        font=ctk.CTkFont(size=14),
        text_color="gray"
    )
    msg_label.pack(pady=50)
```

**Purpose**: Display contextual message when no centers to show

**Used By**: `_update_display()`

---

## Event Handlers

### Favorite Icon Click
- **Trigger**: User clicks ⭐ icon next to a center
- **Handler**: `_toggle_favorite(center)`
- **Flow**: Toggle favorite → Update FavoritesManager → Refresh UI

### Toggle Button Click
- **Trigger**: User clicks 🌟 button in header
- **Handler**: `_toggle_view_mode()`
- **Flow**: Toggle mode → Update icon → Clear search → Refresh list

### Search Entry Modified
- **Trigger**: User types in search field (EXISTING)
- **Handler**: `_filter_centers()` (MODIFIED to respect view_mode)
- **Flow**: Get source centers (all or favorites) → Filter → Update display

---

## Layout Changes Summary

**Header** (before → after):
```
Before: [Logo] [Search] [Help] [About]
After:  [Logo] [Search] [Toggle] [Help] [About]
```

**Center Row** (before → after):
```
Before: [Code] [Name] [Connect]
After:  [Fav] [Code] [Name] [Connect]
```

**Impact**: Requires adjusting grid column indices for existing elements

---

## Dependencies

**New Dependencies**:
- `wifi_connector.data.favorites_manager.FavoritesManager`
- `PIL.Image` (already used for logo, now for fav icons)

**Existing Dependencies** (unchanged):
- `wifi_connector.data.credentials_manager.CredentialsManager`
- `customtkinter` (CTkButton, CTkImage, etc.)

---

## Testing Contract

**Unit Tests Must Cover**:
1. `_toggle_favorite()` adds favorite when not favorited
2. `_toggle_favorite()` removes favorite when favorited
3. `_toggle_view_mode()` switches between "all" and "favorites"
4. `_toggle_view_mode()` clears search field
5. `_filter_centers()` uses all centers when mode = "all"
6. `_filter_centers()` uses favorites when mode = "favorites"
7. `_show_empty_message()` displays correct message for each scenario

**Integration Tests Must Cover**:
1. Full flow: mark favorite → toggle to favorites view → verify center visible
2. Full flow: unmark favorite in favorites view → verify center disappears
3. Search in favorites mode → verify only favorites filtered
4. Toggle modes → verify icon changes and list refreshes

**Visual Tests** (manual):
1. Favorite icons align correctly with center rows
2. Toggle button matches style of help button
3. Empty messages display centered and readable
4. No layout breaks with 0, 1, 10, 100+ centers

---

## Performance Considerations

- **Icon loading**: Load once in `__init__`, cache as CTkImage
- **List refresh**: O(n) where n = centers to display (acceptable for <1000 centers)
- **Favorite check**: O(m) where m = favorites count (typically <100)

**Expected Performance**:
- Toggle view mode: <100ms
- Toggle favorite: <50ms (icon update only) or <500ms (full refresh in favorites mode)
- Search in favorites: <200ms for 100+ favorites

---

## Backward Compatibility

**Breaking Changes**: None

**Additions**:
- New instance variables (no impact on existing code)
- New methods (no impact on existing code)
- Modified methods maintain existing signatures and behavior for non-favorite flows

**Migration**: Existing users will see new features but no disruption to current workflows

---

## Security Considerations

- **No new vulnerabilities**: Feature uses existing FavoritesManager which handles validation
- **UI validation**: Favorite icon buttons only call FavoritesManager methods (no direct file I/O)

**Risk Level**: LOW

---

## Example Usage (from User Perspective)

1. **Mark as favorite**: Click ⭐ icon next to "Institut Exemple" → Icon changes to filled star
2. **View favorites**: Click 🌟 button in header → List shows only favorited centers
3. **Search in favorites**: Type "Exemple" in search field → Only favorites matching "Exemple" shown
4. **Unmark favorite**: Click filled star next to center → Center disappears from list (in favorites mode)
5. **Return to all**: Click 🌟 button again → List shows all centers, search cleared

---

## Version History

- **v1.0.0** (2025-12-13): Initial contract definition
