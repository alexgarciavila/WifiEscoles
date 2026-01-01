# Implementation Plan: Gestión de Centros Favoritos

**Branch**: `002-favorite-centers` | **Date**: 2025-12-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-favorite-centers/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementar funcionalidad para que usuarios puedan marcar centros educativos como favoritos mediante iconos clicables (fav.png/fav_unchecked.png) en cada fila de la lista. Los favoritos se persisten en Json/favoritos.json con la misma estructura que wifi.json. La aplicación incluye un botón toggle en la cabecera para alternar entre vista de todos los centros y solo favoritos. Búsqueda filtra solo dentro de favoritos cuando ese modo está activo. Sistema maneja automáticamente limpieza de favoritos obsoletos y errores de archivo sin crashear.

## Technical Context

**Language/Version**: Python 3.12.10  
**Primary Dependencies**: customtkinter >= 5.2.0, Pillow >= 10.0.0  
**Storage**: JSON files (Json/wifi.json, Json/favoritos.json)  
**Testing**: pytest >= 7.4.0, pytest-cov >= 4.1.0, pytest-mock >= 3.11.0  
**Target Platform**: Windows (primary), cross-platform compatible via customtkinter  
**Project Type**: Single desktop application (wifi_connector/ package)  
**Performance Goals**: <500ms para cargar lista de favoritos incluso con 100+ entradas  
**Constraints**: Cambios en favoritos deben guardar inmediatamente a disco; búsqueda debe filtrar solo favoritos cuando modo activo  
**Scale/Scope**: ~10-100 centros educativos, cientos de favoritos potenciales, 1 usuario por dispositivo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality ✅
- **Requirement**: Código debe seguir PEP 8 / black / ruff, incluir type hints en interfaces públicas
- **Compliance**: Feature añade módulo `favorites_manager.py` con type hints; sigue convenciones existentes del proyecto
- **Status**: PASS

### II. Test Standards ✅
- **Requirement**: Unit tests obligatorios para casos críticos; integration tests para flujos P1; tests reproducibles
- **Compliance**: Plan incluye tests unitarios (FavoritesManager, icono toggle), integration tests (persistencia, sincronización GUI), coverage para casos edge (archivo corrupto, limpieza automática)
- **Status**: PASS

### III. User Experience Consistency ✅
- **Requirement**: Cambios UI/UX deben incluir criterios de aceptación explícitos y pruebas de usabilidad
- **Compliance**: Spec define 9 acceptance scenarios; iconos siguen estilo existente (mismo patrón que botón ayuda); mensajes de error contextuales
- **Status**: PASS

### IV. Performance & Scalability ✅
- **Requirement**: Specs deben declarar objetivos de rendimiento (latencia p95, memoria)
- **Compliance**: SC-004 define <500ms para carga de 100+ favoritos; sin límite técnico de favoritos
- **Status**: PASS

### V. Observability & Release Discipline ✅
- **Requirement**: Logging estructurado, rollback plan para despliegues
- **Compliance**: Feature usa wifi_connector.utils.logger existente; errores de archivo loggean advertencias sin crashear; cambios son aditivos (backwards compatible)
- **Status**: PASS

### Security & Compliance ✅
- **Requirement**: No embutir credenciales; validar dependencias
- **Compliance**: favoritos.json usa misma estructura que wifi.json (ya validada); no añade dependencias externas nuevas
- **Status**: PASS

### Development Workflow & Quality Gates ✅
- **Requirement**: PRs incluyen descripción, tests, referencia a issue; CI/CD ejecuta lint/tests
- **Compliance**: Feature sigue workflow estándar; plan genera tasks.md para tracking; todos los cambios pasan por PR review
- **Status**: PASS

**RESULT**: ✅ **ALL GATES PASS** - Proceed to Phase 0 research

---

### Post-Design Re-Evaluation (Phase 1 Complete)

**Re-checked**: 2025-12-13 after research, data-model, and contracts complete

### I. Code Quality ✅
- **Design Review**: FavoritesManager API contract define type hints completos; sigue patrón de CredentialsManager existente
- **Status**: PASS (no changes)

### II. Test Standards ✅
- **Design Review**: Contracts especifican 10 unit tests + 3 integration tests; quickstart incluye testing checklist
- **Status**: PASS (no changes)

### III. User Experience Consistency ✅
- **Design Review**: GUI contract documenta layout changes detalladamente; mensajes contextuales definidos en contracts; mantiene consistencia visual con botones existentes
- **Status**: PASS (no changes)

### IV. Performance & Scalability ✅
- **Design Review**: Research valida que CTkImage caching + atomic writes cumplen <500ms; data-model especifica O(n) complexity para operaciones clave
- **Status**: PASS (no changes)

### V. Observability & Release Discipline ✅
- **Design Review**: Research define logging strategy (warnings para errores, debug para operations); atomic writes previenen corrupción de archivo
- **Status**: PASS (no changes)

### Security & Compliance ✅
- **Design Review**: Contracts documentan que favoritos.json hereda security posture de wifi.json (plaintext passwords); input validation especificada en data-model
- **Status**: PASS (no changes)

### Development Workflow & Quality Gates ✅
- **Design Review**: Quickstart provee implementation guide + testing checklist; agent context actualizado con nuevas tecnologías
- **Status**: PASS (no changes)

**POST-DESIGN RESULT**: ✅ **ALL GATES STILL PASS** - Ready for Phase 2 (Task Generation via /speckit.tasks)

## Project Structure

### Documentation (this feature)

```text
specs/002-favorite-centers/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
wifi_connector/
├── data/
│   ├── credentials_manager.py    # Existing (load wifi.json)
│   └── favorites_manager.py      # NEW (manage favoritos.json)
├── gui/
│   └── main_window.py            # Modified (add favorite icons + toggle button)
├── utils/
│   ├── logger.py                 # Existing (logging)
│   └── paths.py                  # Existing (file paths)
└── __init__.py

images/
├── fav.png                       # Existing (favorite icon checked)
└── fav_unchecked.png             # Existing (favorite icon unchecked)

Json/
├── wifi.json                     # Existing (all centers)
└── favoritos.json                # NEW (favorite centers)

tests/
├── unit/
│   └── test_favorites_manager.py # NEW (unit tests)
├── integration/
│   └── test_favorites_flow.py    # NEW (integration tests)
└── fixtures/
    └── mock_data.py              # Modified (add favorite fixtures)
```

**Structure Decision**: Single desktop application with wifi_connector/ package. Feature añade nuevo módulo favorites_manager.py en data/ siguiendo patrón existente de credentials_manager.py. GUI changes concentrados en main_window.py para minimizar impacto. Tests siguen estructura unit/integration existente.

## Complexity Tracking

> **No violations detected** - All Constitution gates pass without exceptions. This feature follows established patterns (similar to credentials_manager.py), uses existing dependencies, and adds minimal complexity.
