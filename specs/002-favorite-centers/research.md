# Research: Gestión de Centros Favoritos

**Feature**: 002-favorite-centers  
**Created**: 2025-12-13  
**Purpose**: Resolver incógnitas técnicas identificadas en Technical Context y validar decisiones de diseño

---

## Q1: ¿Cómo persistir favoritos.json con la misma estructura que wifi.json?

### Decision
Usar módulo `favorites_manager.py` siguiendo el patrón de `credentials_manager.py` existente.

### Rationale
- **Consistencia**: El proyecto ya tiene `CredentialsManager` que maneja wifi.json con métodos `load_credentials()`, `get_all_centers()`, etc.
- **Reutilización**: Misma estructura JSON permite reutilizar validación y serialización
- **Mantenibilidad**: Patrón conocido reduce curva de aprendizaje

### Alternatives Considered
- **A. Extender CredentialsManager**: Rechazado porque mezcla responsabilidades (todos los centros vs solo favoritos)
- **B. Módulo genérico JSON**: Rechazado porque pierde type safety y validaciones específicas de dominio

### Implementation Notes
```python
# wifi_connector/data/favorites_manager.py
from typing import List
from wifi_connector.data.credentials_manager import CenterCredentials
import json
from pathlib import Path

class FavoritesManager:
    def __init__(self, favorites_path: Path):
        self.favorites_path = favorites_path
        self._favorites: List[CenterCredentials] = []
    
    def load_favorites(self) -> bool:
        """Load favorites from favoritos.json"""
        
    def add_favorite(self, center: CenterCredentials) -> None:
        """Add center to favorites and persist"""
        
    def remove_favorite(self, center_code: str) -> None:
        """Remove center from favorites and persist"""
        
    def is_favorite(self, center_code: str) -> bool:
        """Check if center is favorited"""
        
    def get_favorites(self) -> List[CenterCredentials]:
        """Get all favorite centers"""
```

---

## Q2: ¿Cómo integrar iconos clicables en cada fila de MainWindow sin romper layout existente?

### Decision
Usar `CTkButton` con imagen como primer elemento de cada fila en el scrollable frame, antes del label de código de centro.

### Rationale
- **customTkinter compatible**: CTkButton soporta `image` parameter para iconos PNG
- **Click handling**: CTkButton tiene `command` callback nativo
- **Layout preservation**: Añadir como primer elemento de `grid()` no afecta otros widgets

### Alternatives Considered
- **A. CTkLabel con bind("<Button-1>")**: Rechazado porque CTkLabel no tiene estados hover/pressed nativos
- **B. Canvas personalizado**: Rechazado por complejidad innecesaria cuando CTkButton cumple requisito

### Implementation Notes
```python
# En MainWindow._create_center_row()
fav_icon = ctk.CTkButton(
    parent_frame,
    text="",
    image=self._get_favorite_icon(center.center_code),
    width=30,
    height=30,
    command=lambda c=center: self._toggle_favorite(c)
)
fav_icon.grid(row=row, column=0, padx=5, pady=5)

# Código existente se desplaza a column=1, column=2, etc.
```

### Visual Reference
Botón ayuda existente usa este mismo patrón (CTkButton con imagen circular).

---

## Q3: ¿Cómo implementar toggle button en header para alternar entre modos?

### Decision
Usar `CTkButton` con imagen dinámica que cambia entre fav.png y fav_unchecked.png según modo activo.

### Rationale
- **Consistencia visual**: Mismo estilo que botón ayuda (?) existente
- **Estado visual claro**: Icono fav.png cuando muestra favoritos, fav_unchecked.png cuando muestra todos
- **UX intuitiva**: Usuario ve inmediatamente qué modo está activo

### Alternatives Considered
- **A. CTkSwitch**: Rechazado porque no soporta imágenes personalizadas
- **B. CTkSegmentedButton**: Rechazado porque diseño no coincide con estilo de header existente
- **C. Dos botones separados**: Rechazado por ocupar más espacio y ser menos intuitivo

### Implementation Notes
```python
# En MainWindow.__init__()
self.view_mode = "all"  # "all" o "favorites"
self.toggle_button = ctk.CTkButton(
    header_frame,
    text="",
    image=self.fav_unchecked_icon,  # Inicial
    width=40,
    height=40,
    command=self._toggle_view_mode
)

def _toggle_view_mode(self):
    self.view_mode = "favorites" if self.view_mode == "all" else "all"
    self._update_toggle_icon()
    self._refresh_center_list()
```

---

## Q4: ¿Cómo filtrar búsqueda solo en favoritos cuando modo favoritos está activo?

### Decision
Modificar método `_filter_centers()` existente para considerar `self.view_mode` y filtrar desde lista de favoritos en vez de todos los centros.

### Rationale
- **Código centralizado**: Un solo método maneja toda la lógica de filtrado
- **Evita duplicación**: No necesita crear `_filter_favorites()` separado
- **Comportamiento claro**: Búsqueda siempre respeta modo activo

### Alternatives Considered
- **A. Dos métodos separados**: Rechazado porque duplica lógica de búsqueda (case-insensitive, normalización, etc.)
- **B. Búsqueda siempre global**: Rechazado porque contradice User Story 3 (búsqueda filtrada en favoritos)

### Implementation Notes
```python
def _filter_centers(self, search_term: str):
    """Filter centers based on search and view mode"""
    if self.view_mode == "favorites":
        source_centers = self.favorites_manager.get_favorites()
    else:
        source_centers = self.credentials_manager.get_all_centers()
    
    filtered = [
        c for c in source_centers 
        if search_term.lower() in c.center_name.lower() 
        or search_term.lower() in c.center_code.lower()
    ]
    self._update_display(filtered)
```

---

## Q5: ¿Cómo manejar limpieza automática de favoritos obsoletos sin impacto en UX?

### Decision
Validar y limpiar favoritos obsoletos al cargar `favoritos.json`, antes de mostrar GUI. Logging silencioso sin UI interruption.

### Rationale
- **Performance**: Limpieza en startup evita chequeos repetidos durante uso
- **UX no invasivo**: Usuario no ve mensajes de error por favoritos antiguos
- **Data integrity**: Archivo queda limpio automáticamente

### Alternatives Considered
- **A. Validar en cada operación**: Rechazado por overhead de performance
- **B. Mostrar diálogo al usuario**: Rechazado porque interrumpe flujo (violación de SC-005: graceful recovery)
- **C. Nunca limpiar**: Rechazado porque acumula basura indefinidamente

### Implementation Notes
```python
def load_favorites(self) -> bool:
    """Load and validate favorites from favoritos.json"""
    try:
        with open(self.favorites_path) as f:
            data = json.load(f)
        
        # Obtener códigos válidos de wifi.json
        valid_codes = {c.center_code for c in self.credentials_manager.get_all_centers()}
        
        # Filtrar favoritos obsoletos
        valid_favorites = [
            CenterCredentials(**item) 
            for item in data 
            if item.get('center_code') in valid_codes
        ]
        
        # Si se removieron favoritos obsoletos, re-guardar
        if len(valid_favorites) < len(data):
            self.logger.warning(f"Removed {len(data) - len(valid_favorites)} obsolete favorites")
            self._save_favorites(valid_favorites)
        
        self._favorites = valid_favorites
        return True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        self.logger.warning(f"Could not load favorites: {e}")
        self._favorites = []
        return False
```

---

## Q6: ¿Cómo manejar mensaje contextual cuando búsqueda en favoritos no arroja resultados?

### Decision
Añadir label informativo temporal que reemplaza la lista vacía cuando búsqueda en modo favoritos no arroja resultados.

### Rationale
- **UX clara**: Usuario entiende por qué no ve resultados (está filtrando solo favoritos)
- **Actionable**: Mensaje sugiere acción ("buscar en todos los centros")
- **No invasivo**: No requiere diálogo modal, solo label en área de contenido

### Alternatives Considered
- **A. Lista vacía silenciosa**: Rechazado porque usuario puede confundirse
- **B. Auto-expandir a todos los centros**: Rechazado porque cambia comportamiento sin confirmación del usuario (violación de expectativas)
- **C. Diálogo modal**: Rechazado por ser demasiado invasivo para caso no crítico

### Implementation Notes
```python
def _update_display(self, centers: List[CenterCredentials]):
    """Update center list display"""
    self._clear_center_list()
    
    if not centers:
        if self.view_mode == "favorites" and self.search_entry.get():
            # Búsqueda en favoritos sin resultados
            msg = f"No hi ha resultats a favorits per '{self.search_entry.get()}'.\nProva a buscar en tots els centres."
            self._show_empty_message(msg)
        elif self.view_mode == "favorites":
            # Sin favoritos
            msg = "No tens centres marcats com a favorits.\nFes clic a l'icona ★ per afegir-ne."
            self._show_empty_message(msg)
        return
    
    # Renderizar lista de centros...
```

---

## Technology Stack Validation

### customTkinter Image Support
- **Required**: CTkButton con `image` parameter para PNG icons
- **Current**: customtkinter >= 5.2.0 (soportado desde v5.0+)
- **Status**: ✅ Compatible

### PIL/Pillow for Image Loading
- **Required**: Pillow >= 10.0.0 para cargar PNG icons
- **Current**: Pillow >= 10.0.0 (ya en requirements.txt)
- **Method**: `ctk.CTkImage(light_image=Image.open("fav.png"), size=(24, 24))`
- **Status**: ✅ Compatible

### JSON Persistence
- **Required**: Python json module (stdlib)
- **Current**: Python 3.12.10 (json incluido)
- **Status**: ✅ Compatible

### File Paths Management
- **Required**: pathlib.Path para rutas cross-platform
- **Current**: wifi_connector.utils.paths ya usa pathlib
- **Status**: ✅ Compatible

---

## Best Practices Research

### JSON File Handling
- **Pattern**: Atomic writes usando temporary file + rename
- **Rationale**: Evita corrupción si app crashea durante escritura
- **Implementation**:
  ```python
  def _save_favorites(self, favorites: List[CenterCredentials]):
      temp_path = self.favorites_path.with_suffix('.tmp')
      with open(temp_path, 'w', encoding='utf-8') as f:
          json.dump([f.__dict__ for f in favorites], f, indent=2)
      temp_path.replace(self.favorites_path)  # Atomic on Windows/Unix
  ```

### GUI State Management
- **Pattern**: Single source of truth (`self.view_mode`) + reactive updates
- **Rationale**: Evita desincronización entre estado y UI
- **Implementation**: Cada cambio de estado llama a `_refresh_center_list()` para re-renderizar

### Error Handling Strategy
- **Pattern**: Try-except con logging + graceful degradation
- **Rationale**: Feature no debe bloquear app si favoritos.json falla
- **Implementation**: Si load falla → continuar con lista vacía de favoritos

---

## Performance Considerations

### Icon Caching
- **Decision**: Cargar fav.png y fav_unchecked.png una vez en `__init__`, reutilizar CTkImage instances
- **Rationale**: Evita I/O repetido y memory leaks
- **Expected Impact**: Reduce tiempo de render de lista de O(n*2) a O(n) I/O calls

### List Rendering Optimization
- **Decision**: Reutilizar patrón existente de MainWindow (scrollable frame con grid)
- **Rationale**: Ya probado con 100+ centros sin degradación
- **Expected Impact**: Cumple SC-004 (<500ms para 100+ favoritos)

---

## Dependencies Validation

**No new external dependencies required**:
- customtkinter >= 5.2.0 ✅ (existing)
- Pillow >= 10.0.0 ✅ (existing)
- pytest >= 7.4.0 ✅ (existing, for tests)

**Stdlib only**:
- json (persistence)
- pathlib (file paths)
- typing (type hints)

---

## Conclusion

Todas las incógnitas técnicas han sido resueltas. Las decisiones tomadas:
1. Siguen patrones existentes del proyecto (FavoritesManager ~ CredentialsManager)
2. Usan APIs nativas de customtkinter (CTkButton, CTkImage)
3. No añaden dependencias externas
4. Cumplen objetivos de performance (SC-004)
5. Implementan graceful error handling (SC-005)

**Status**: ✅ Ready for Phase 1 (Design)
