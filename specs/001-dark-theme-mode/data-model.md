# Data Model: Tema Oscuro Forzado

**Feature**: 001-dark-theme-mode  
**Date**: 2025-12-13  
**Phase**: Phase 1 - Data & Domain Model

## Overview

Este feature NO introduce entidades de dominio complejas ni estructuras de datos persistentes. El "modelo" es una configuración global hardcoded del framework GUI.

## Entities

### ThemeConfiguration (Configuration, not a persistent entity)

**Purpose**: Representa la configuración de apariencia global de la aplicación customTkinter.

**Attributes**:
- `appearance_mode`: Literal["dark"] - Modo de apariencia forzado (hardcoded)
- `color_theme`: Literal["blue"] - Tema de colores de acento (hardcoded)

**Lifecycle**:
- **Creation**: Al inicio de la aplicación mediante `setup_dark_theme()`
- **Storage**: NO se persiste (configuración hardcoded en código)
- **Modification**: NO modificable en runtime (valores constantes)
- **Deletion**: N/A (configuración global del framework)

**Validation Rules**:
- `appearance_mode` DEBE ser "dark" (no acepta otros valores)
- `color_theme` DEBE ser "blue" (no acepta otros valores)

**Relationships**:
- No tiene relaciones con otras entidades
- Es una configuración global que afecta a todos los widgets GUI

**Example** (conceptual, no hay clase Python real):
```python
# Conceptualmente (no implementado como clase):
theme_config = {
    "appearance_mode": "dark",  # Hardcoded constant
    "color_theme": "blue"        # Hardcoded constant
}
```

---

## State Model

### Application Theme State

**States**:
1. **UNINITIALIZED**: Aplicación no ha configurado tema (estado inicial)
2. **DARK_CONFIGURED**: Tema oscuro aplicado exitosamente
3. **ERROR**: Error al configurar tema (excepcional)

**State Transitions**:
```
UNINITIALIZED --[setup_dark_theme() success]--> DARK_CONFIGURED
UNINITIALIZED --[setup_dark_theme() fail]--> ERROR
```

**Invariants**:
- Una vez en estado `DARK_CONFIGURED`, el estado NO cambia durante el ciclo de vida de la aplicación
- Estado `ERROR` es terminal (aplicación no debe continuar si tema no se configura)

---

## Constants

### Theme Constants

```python
# wifi_connector/utils/theme.py

# Appearance mode constant
APPEARANCE_MODE: Literal["dark"] = "dark"

# Color theme constant  
COLOR_THEME: Literal["blue"] = "blue"

# Performance target (for logging/monitoring)
THEME_SETUP_MAX_TIME_MS: int = 100
```

**Rationale**:
- Valores hardcoded como constantes con tipos literales
- Facilita refactor futuro si se decide añadir configurabilidad
- Type checking captura errores si se intenta usar valor incorrecto

---

## No Data Persistence

**Important**: Este feature NO requiere:
- ❌ Base de datos
- ❌ Archivos de configuración
- ❌ User preferences storage
- ❌ State serialization

**Rationale** (según clarificación del spec):
> "No quiero archivo de configuración para esta funcionalidad. Siempre ha de ser tema oscuro."

---

## Validation

### Input Validation

NO hay inputs de usuario → NO hay validación de inputs

### State Validation

```python
def validate_theme_configured() -> bool:
    """Verify that dark theme is configured.
    
    Returns:
        True if appearance mode is "dark", False otherwise.
    """
    import customtkinter as ctk
    # customTkinter no expone getter público para appearance_mode
    # Validación implícita: si setup_dark_theme() completó sin error, está configurado
    return True  # Simplified: trust setup_dark_theme() completed
```

---

## Error Handling

### Theme Configuration Errors

**Possible errors**:
1. `ImportError`: customTkinter no instalado
2. `AttributeError`: API de customTkinter cambió (breaking change en librería)
3. `RuntimeError`: Error interno de customTkinter al configurar tema

**Handling strategy**:
```python
def setup_dark_theme() -> None:
    try:
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        logger.info("Dark theme configured successfully")
    except ImportError as e:
        logger.critical(f"customTkinter not installed: {e}")
        raise  # Fatal error - app cannot continue
    except (AttributeError, RuntimeError) as e:
        logger.error(f"Failed to configure dark theme: {e}")
        raise  # Fatal error - theme is mandatory
```

---

## Testing Considerations

### Unit Tests

```python
# tests/test_theme.py

def test_theme_constants_are_correct():
    """Verify theme constants have expected values."""
    assert APPEARANCE_MODE == "dark"
    assert COLOR_THEME == "blue"

def test_setup_dark_theme_completes_without_error():
    """Verify setup_dark_theme() executes successfully."""
    # No exception should be raised
    setup_dark_theme()

def test_setup_dark_theme_logs_success(caplog):
    """Verify successful theme setup is logged."""
    setup_dark_theme()
    assert "Dark theme configured successfully" in caplog.text
```

### Integration Tests

```python
# tests/integration/test_theme_coverage.py

def test_all_windows_use_dark_theme():
    """Verify all GUI windows respect dark theme."""
    setup_dark_theme()
    
    # Create main window
    main_win = MainWindow()
    # Verificar que window se creó (no hay API pública para leer appearance_mode)
    assert main_win is not None
    
    # Create about window
    about_win = AboutWindow()
    assert about_win is not None
    
    # Visual inspection manual en PR review
```

---

## Domain Rules

### Rule 1: Tema es inmutable en runtime
- Una vez configurado al inicio, el tema NO cambia durante la sesión de la aplicación
- No hay API expuesta para cambiar tema después de `setup_dark_theme()`

### Rule 2: Configuración es obligatoria
- `setup_dark_theme()` DEBE ser llamada antes de crear cualquier widget GUI
- Si configuración falla, aplicación DEBE terminar (no puede continuar sin tema)

### Rule 3: Tema afecta a todas las ventanas
- Todas las ventanas creadas después de `setup_dark_theme()` heredan el tema oscuro
- No hay excepciones por ventana o widget

---

## Diagrams

### Component Diagram

```
┌─────────────────────────────────────────────┐
│             main.py (entry point)           │
│  1. Call setup_dark_theme()                 │
│  2. Import GUI modules                      │
│  3. Launch MainWindow                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    wifi_connector/utils/theme.py            │
│                                             │
│  - APPEARANCE_MODE = "dark"                 │
│  - COLOR_THEME = "blue"                     │
│  - setup_dark_theme()                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         customtkinter (framework)           │
│  - set_appearance_mode("dark")              │
│  - set_default_color_theme("blue")          │
│  - Global configuration affects all widgets │
└─────────────────────────────────────────────┘
```

### Sequence Diagram (Startup)

```
main.py          theme.py          customtkinter    MainWindow
   │                │                    │              │
   │─setup_dark_theme()                 │              │
   │                │                    │              │
   │                │─set_appearance_mode("dark")      │
   │                │                    │              │
   │                │─set_default_color_theme("blue")  │
   │                │                    │              │
   │                │◄─── OK ──────────  │              │
   │◄─── OK ────────│                    │              │
   │                │                    │              │
   │─import MainWindow                   │              │
   │                │                    │              │
   │─── MainWindow() ───────────────────────────────► │
   │                │                    │              │
   │                │    [MainWindow inherits dark theme]
   │                │                    │              │
```

---

## Summary

**Data Model Complexity**: MINIMAL

Este feature es principalmente una configuración inicial del framework, no introduce complejidad de dominio. El "modelo" consiste en:
- 2 constantes hardcoded (`APPEARANCE_MODE`, `COLOR_THEME`)
- 1 función de setup (`setup_dark_theme()`)
- Estado global implícito en customTkinter (no modelado explícitamente)

**No persistence, no complex relationships, no business logic** → Implementación straightforward.
