# Data Model: Gestión de Centros Favoritos

**Feature**: 002-favorite-centers  
**Created**: 2025-12-13  
**Purpose**: Definir entidades, relaciones y estructura de datos para favoritos

---

## Entities

### FavoriteCenter

**Description**: Representa un centro educativo marcado como favorito por el usuario.

**Attributes**:
- `center_code: str` - Código único del centro (ej: "08012345")
- `center_name: str` - Nombre del centro educativo
- `username: str` - Usuario para autenticación WiFi
- `password: str` - Contraseña para autenticación WiFi

**Validation Rules**:
- `center_code` MUST match regex `^\d{8}$` (8 dígitos)
- `center_name` MUST NOT be empty
- `username` and `password` MUST NOT be empty
- All string fields MUST be trimmed (no leading/trailing whitespace)

**Source**: Subconjunto de `CenterCredentials` desde wifi.json

**Example**:
```json
{
  "center_code": "08012345",
  "center_name": "Institut Exemple",
  "username": "user@gencat.cat",
  "password": "SecurePass123"
}
```

---

### ViewMode

**Description**: Modo de visualización actual de la lista de centros en la GUI.

**States**:
- `ALL_CENTERS` - Muestra todos los centros disponibles de wifi.json
- `FAVORITES_ONLY` - Muestra solo centros marcados como favoritos

**Default**: `ALL_CENTERS`

**Transitions**:
- `ALL_CENTERS` → `FAVORITES_ONLY`: Usuario hace clic en toggle button
- `FAVORITES_ONLY` → `ALL_CENTERS`: Usuario hace clic en toggle button (mismo botón)

**Effects**:
- Afecta qué centros se muestran en la lista scrollable
- Afecta comportamiento de búsqueda (filtra solo dentro del conjunto visible)
- Afecta icono del toggle button (fav.png vs fav_unchecked.png)

---

## Relationships

```
wifi.json (all centers)
    |
    | contains
    ↓
CenterCredentials [1..*]
    |
    | subset of
    ↓
favoritos.json (favorite centers)
    |
    | persists
    ↓
FavoriteCenter [0..*]
```

**Constraints**:
- Todo `FavoriteCenter` MUST existir en wifi.json (validated on load)
- Si centro es eliminado de wifi.json, se elimina automáticamente de favoritos.json (auto-cleanup)
- Un centro puede aparecer máximo 1 vez en favoritos.json (unique by center_code)

---

## Data Structures

### favoritos.json Format

**Location**: `Json/favoritos.json`

**Structure**: Array de objetos FavoriteCenter

**Example**:
```json
[
  {
    "center_code": "08012345",
    "center_name": "Institut Exemple",
    "username": "user@gencat.cat",
    "password": "SecurePass123"
  },
  {
    "center_code": "08067890",
    "center_name": "Escola Mostra",
    "username": "admin@gencat.cat",
    "password": "Pass456"
  }
]
```

**Schema Validation**:
- MUST be valid JSON array
- Each element MUST have all 4 required fields
- Empty array `[]` is valid (no favorites)
- File MAY not exist (treated as empty array)

---

### In-Memory State

**FavoritesManager** maintains:
```python
class FavoritesManager:
    _favorites: List[CenterCredentials]  # Loaded favorites
    favorites_path: Path                  # Path to favoritos.json
    credentials_manager: CredentialsManager  # Reference for validation
```

**MainWindow** maintains:
```python
class MainWindow:
    view_mode: str                       # "all" or "favorites"
    favorites_manager: FavoritesManager  # Favorites state
    displayed_centers: List[CenterCredentials]  # Currently visible centers
```

---

## State Transitions

### Marking a Center as Favorite

**Trigger**: Usuario hace clic en icono fav_unchecked.png junto a un centro

**Flow**:
1. MainWindow captura click → `_toggle_favorite(center)`
2. FavoritesManager valida que center existe en wifi.json
3. FavoritesManager añade center a `_favorites` list
4. FavoritesManager persiste a favoritos.json (atomic write)
5. MainWindow actualiza icono a fav.png
6. MainWindow NO cambia lista visible (solo icono)

**Postconditions**:
- favoritos.json contiene el nuevo centro
- Icono en fila del centro muestra fav.png
- Si app reinicia, centro sigue marcado como favorito

---

### Unmarking a Center as Favorite

**Trigger**: Usuario hace clic en icono fav.png junto a un centro favorito

**Flow**:
1. MainWindow captura click → `_toggle_favorite(center)`
2. FavoritesManager remueve center de `_favorites` list
3. FavoritesManager persiste a favoritos.json (atomic write)
4. MainWindow actualiza icono a fav_unchecked.png
5. Si view_mode == "favorites": MainWindow remueve fila de la lista

**Postconditions**:
- favoritos.json NO contiene el centro
- Si modo ALL_CENTERS: icono muestra fav_unchecked.png
- Si modo FAVORITES_ONLY: centro desaparece de lista

---

### Switching View Mode

**Trigger**: Usuario hace clic en toggle button en header

**Flow**:
1. MainWindow captura click → `_toggle_view_mode()`
2. MainWindow toggle `view_mode` ("all" ↔ "favorites")
3. MainWindow actualiza icono del toggle button
4. MainWindow limpia campo de búsqueda (FR-011)
5. MainWindow llama `_refresh_center_list()`
6. Lista se re-renderiza con centros del modo activo

**Postconditions**:
- view_mode refleja nuevo estado
- Toggle button muestra icono correcto
- Lista muestra centros correctos (todos o solo favoritos)
- Campo búsqueda está vacío

---

### Loading Favorites on Startup

**Trigger**: MainWindow.__init__()

**Flow**:
1. MainWindow instancia FavoritesManager
2. FavoritesManager llama `load_favorites()`
3. Si favoritos.json existe:
   - Parse JSON
   - Validar cada centro contra wifi.json
   - Filtrar centros obsoletos (auto-cleanup)
   - Si hubo cleanup, re-guardar archivo
   - Cargar favoritos válidos a `_favorites`
4. Si favoritos.json NO existe o está corrupto:
   - Log warning
   - Inicializar `_favorites = []`
   - NO crashear app
5. MainWindow continúa con inicialización normal

**Postconditions**:
- `_favorites` contiene solo centros válidos
- favoritos.json está limpio (sin obsoletos)
- App funciona incluso si favoritos.json falla

---

## Error Handling

### Corrupted favoritos.json

**Scenario**: JSON inválido, campos faltantes, tipos incorrectos

**Handling**:
1. FavoritesManager captura `json.JSONDecodeError`
2. Log warning: "Could not load favorites: {error}"
3. Inicializar `_favorites = []`
4. App continúa sin favoritos
5. Próximo add/remove recrea archivo válido

**User Impact**: Pierde favoritos previos, pero app no crashea

---

### favoritos.json Deleted While Running

**Scenario**: Usuario elimina archivo manualmente durante ejecución

**Handling**:
1. Próximo `add_favorite()` o `remove_favorite()` detecta ausencia
2. `_save_favorites()` crea nuevo archivo
3. Solo favoritos de sesión actual se persisten
4. No hay error visible para usuario

**User Impact**: Favoritos de sesión se preservan, previos se pierden

---

### Center No Longer in wifi.json

**Scenario**: Centro favorito es eliminado de wifi.json (actualización del catálogo)

**Handling**:
1. `load_favorites()` valida cada center_code contra wifi.json
2. Centros no existentes se omiten de `_favorites`
3. favoritos.json se actualiza automáticamente
4. Log warning: "Removed X obsolete favorites"

**User Impact**: Favoritos obsoletos desaparecen silenciosamente

---

## Performance Considerations

### Memory Footprint
- **Favorites list**: ~500 bytes por centro × 100 centros = ~50 KB
- **Icons**: 2 × CTkImage (~10 KB cada) = ~20 KB
- **Total**: <100 KB adicional en memoria

### Disk I/O
- **Read**: 1 vez al startup (load_favorites)
- **Write**: Cada vez que usuario marca/desmarca favorito (atomic write <1ms)
- **File size**: ~200 bytes por centro × 100 centros = ~20 KB

### UI Rendering
- **List refresh**: O(n) donde n = número de centros visibles
- **Expected**: <500ms para 100 centros (SC-004)
- **Optimization**: Reutilizar CTkImage instances (icons cached)

---

## Security Considerations

### Credential Storage
- **Risk**: favoritos.json contiene passwords en plaintext
- **Mitigation**: Mismo nivel de seguridad que wifi.json (precedente existente)
- **Scope**: Out of scope para esta feature (no introducir nueva vulnerabilidad)

### File Permissions
- **Assumption**: Usuario tiene permisos de escritura en Json/
- **Handling**: Si write falla, log error y continuar (no crashear)

### Input Validation
- **Required**: Validar center_code, center_name, username, password antes de persistir
- **Implementation**: Reutilizar validación existente de CenterCredentials

---

## Conclusion

El modelo de datos:
- ✅ Reutiliza estructura existente (CenterCredentials)
- ✅ Define transiciones de estado claras
- ✅ Maneja errores gracefully sin crashear
- ✅ Cumple objetivos de performance
- ✅ No introduce vulnerabilidades nuevas

**Status**: ✅ Ready for contract definition
