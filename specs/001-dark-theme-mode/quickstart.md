# Quickstart: Tema Oscuro Forzado

**Feature**: 001-dark-theme-mode  
**Estimated Time**: 15-20 minutos  
**Prerequisites**: Python 3.12+, customTkinter instalado

## Objetivo

Verificar que la implementación del tema oscuro forzado funciona correctamente en la aplicación WifiEscoles.

---

## 1. Setup Local

### 1.1 Checkout Branch

```bash
git checkout 001-dark-theme-mode
```

### 1.2 Verificar Dependencias

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Verificar customTkinter instalado
pip list | Select-String customtkinter

# Si no está, instalar
pip install customtkinter>=5.0.0
```

### 1.3 Verificar Archivos Nuevos/Modificados

```bash
# Listar archivos del feature
git diff --name-status main...HEAD

# Esperado:
# A    wifi_connector/utils/theme.py          # [NEW]
# A    wifi_connector/gui/README.md           # [NEW]
# M    main.py                                 # [MODIFIED]
# M    wifi_connector/gui/main_window.py      # [MODIFIED - si necesario]
# A    tests/test_theme.py                    # [NEW]
# A    tests/integration/test_theme_coverage.py  # [NEW]
```

---

## 2. Run Application (Manual Test)

### 2.1 Iniciar Aplicación

```bash
# Desde el directorio raíz del proyecto
python main.py
```

### 2.2 Verificaciones Visuales

**Check 1: Ventana Principal**
- ✅ Fondo oscuro (#1a1a1a o similar)
- ✅ Texto claro (#ffffff o #e0e0e0)
- ✅ Botones con acento azul
- ✅ Sin elementos con fondo blanco/claro

**Check 2: Ventana About**
```bash
# En la aplicación, abrir About (menú o botón)
```
- ✅ Fondo oscuro consistente
- ✅ Texto legible con buen contraste
- ✅ Sin diferencias visuales vs ventana principal

**Check 3: Diálogos/Popups**
```bash
# Probar cualquier diálogo de la app
```
- ✅ Tema oscuro aplicado
- ✅ Contraste suficiente

**Check 4: Estados de Widgets**
```bash
# Interactuar con controles
```
- ✅ Hover: cambio visual perceptible
- ✅ Focus: indicador visual claro
- ✅ Disabled: distinguible de enabled

### 2.3 Verificar Tiempo de Inicio

```bash
# Medir tiempo hasta que ventana aparece
# Debe ser instantáneo (<1 segundo total, tema <100ms)
```

---

## 3. Run Tests

### 3.1 Unit Tests

```bash
# Ejecutar tests del módulo theme
pytest tests/test_theme.py -v

# Esperado:
# test_constants_have_expected_values PASSED
# test_setup_completes_without_error PASSED
# test_setup_logs_success PASSED
```

### 3.2 Integration Tests

```bash
# Ejecutar tests de cobertura de tema
pytest tests/integration/test_theme_coverage.py -v

# Esperado:
# test_all_windows_use_dark_theme PASSED
```

### 3.3 Full Test Suite

```bash
# Ejecutar todos los tests para verificar no-regression
pytest tests/ -v

# Todos los tests existentes DEBEN pasar
# Nuevos tests de tema DEBEN pasar
```

---

## 4. Verificar Logs

### 4.1 Revisar Log de Tema

```bash
# Si la app genera logs en archivo
cat Logs/*.log | Select-String "theme"

# Esperado:
# INFO - Dark theme configured successfully
```

### 4.2 Verificar No Hay Errores

```bash
# Buscar errores relacionados con tema
cat Logs/*.log | Select-String "ERROR|CRITICAL" | Select-String "theme"

# Esperado: Sin resultados
```

---

## 5. Verificar Contraste WCAG AA

### 5.1 Capturar Screenshots

```bash
# Tomar capturas de pantalla de:
# 1. Ventana principal
# 2. Ventana about
# 3. Cualquier diálogo
```

### 5.2 Usar Herramienta de Contraste

**Opción A: WebAIM Contrast Checker**
1. Visitar https://webaim.org/resources/contrastchecker/
2. Ingresar colores:
   - Background: `#1a1a1a` (o color de fondo observado)
   - Foreground: `#ffffff` (o color de texto observado)
3. Verificar ratio ≥ 4.5:1 para texto normal

**Opción B: Color Contrast Analyzer (Desktop)**
1. Descargar: https://www.tpgi.com/color-contrast-checker/
2. Usar eyedropper para medir colores de la app
3. Verificar compliance WCAG AA

### 5.3 Verificar Criterios

- ✅ Texto normal: ratio ≥ 4.5:1
- ✅ Texto grande (>18pt): ratio ≥ 3:1
- ✅ Elementos UI: ratio ≥ 3:1

---

## 6. Verificar Performance

### 6.1 Benchmark Startup Time

```python
# Crear script temporal: benchmark_startup.py
import time
from wifi_connector.utils.theme import setup_dark_theme

start = time.perf_counter()
setup_dark_theme()
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"Theme setup time: {elapsed_ms:.2f}ms")
assert elapsed_ms < 100, f"Too slow: {elapsed_ms}ms > 100ms"
print("✅ Performance target met")
```

```bash
# Ejecutar benchmark
python benchmark_startup.py

# Esperado:
# Theme setup time: 0.xx ms
# ✅ Performance target met
```

---

## 7. Verificar Código

### 7.1 Revisar Implementación

```bash
# Verificar módulo theme
cat wifi_connector/utils/theme.py

# Checklist:
# ✅ Imports correctos (customtkinter, logger)
# ✅ Constantes APPEARANCE_MODE = "dark"
# ✅ Constantes COLOR_THEME = "blue"
# ✅ Función setup_dark_theme() con docstring
# ✅ Try-except para manejo de errores
# ✅ Logging de éxito/error
```

### 7.2 Verificar Entry Point

```bash
# Verificar main.py
cat main.py | Select-String -Context 5,5 "setup_dark_theme"

# Checklist:
# ✅ setup_dark_theme() llamada ANTES de imports GUI
# ✅ Try-except envuelve startup
# ✅ Manejo de errores fatal (sys.exit)
```

### 7.3 Verificar Documentación

```bash
# Verificar README de GUI
cat wifi_connector/gui/README.md

# Checklist:
# ✅ Documenta que tema es forzado a oscuro
# ✅ Explica por qué no hay configuración
# ✅ Referencia a customTkinter
```

---

## 8. Smoke Tests (End-to-End)

### 8.1 Test: Iniciar Aplicación con Sistema en Tema Claro

```bash
# 1. Configurar Windows en tema claro (Settings > Personalization > Colors > Light)
# 2. Iniciar aplicación
python main.py

# Verificar:
# ✅ App se muestra en tema oscuro (ignora tema del sistema)
```

### 8.2 Test: Cambiar Tema del Sistema mientras App Corre

```bash
# 1. Iniciar app (tema oscuro aplicado)
# 2. Cambiar Windows a tema claro
# 3. Verificar app mantiene tema oscuro sin cambios
```

### 8.3 Test: Reiniciar Aplicación

```bash
# 1. Cerrar app
# 2. Reiniciar app
python main.py

# Verificar:
# ✅ Tema oscuro se aplica nuevamente
# ✅ Comportamiento consistente (no aleatorio)
```

---

## 9. Common Issues & Troubleshooting

### Issue 1: App muestra tema claro

**Síntoma**: Ventana aparece con fondo blanco/claro

**Diagnóstico**:
```bash
# Verificar setup_dark_theme() fue llamado
python -c "from wifi_connector.utils.theme import setup_dark_theme; setup_dark_theme(); print('OK')"
```

**Fix**:
- Verificar que `setup_dark_theme()` se llama en `main.py` ANTES de imports GUI
- Verificar que no hay excepción silenciada

---

### Issue 2: Widgets legacy sin tema

**Síntoma**: Algunos widgets tienen fondo claro

**Diagnóstico**:
```bash
# Buscar widgets tkinter legacy
grep -r "import tkinter" wifi_connector/gui/ | grep -v customtkinter
grep -r "tk\." wifi_connector/gui/ | grep -v "customtkinter"
```

**Fix**:
- Migrar widgets `tk.*` a equivalentes `ctk.*`
- Ver [research.md](research.md) sección "Widgets legacy"

---

### Issue 3: Tests fallan

**Síntoma**: `pytest` reporta errores

**Diagnóstico**:
```bash
pytest tests/test_theme.py -v --tb=short
```

**Fix común**:
- Verificar customTkinter instalado: `pip install customtkinter>=5.0.0`
- Verificar imports correctos en tests

---

## 10. Acceptance Checklist

Antes de marcar el feature como completo, verificar:

### User Story 1: Aplicar Tema Oscuro Permanente (P1)
- ✅ App inicia con tema oscuro independiente del sistema (AC1)
- ✅ Cambiar tema del sistema no afecta app (AC2)
- ✅ Reiniciar app mantiene tema oscuro (AC3)
- ✅ Todas las ventanas (main, about, dialogs) usan tema oscuro (AC4)

### User Story 2: Contraste y Legibilidad (P2)
- ✅ Todos los elementos tienen contraste suficiente (AC1)
- ✅ Mensajes de estado son distinguibles (AC2)
- ✅ Estados hover/focus/disabled son perceptibles (AC3)
- ✅ Campos de entrada tienen texto visible (AC4)

### Functional Requirements
- ✅ FR-001: Tema oscuro aplicado al iniciar
- ✅ FR-002: Tema mantenido durante sesión
- ✅ FR-003: Todas ventanas usan tema oscuro
- ✅ FR-004: Contraste WCAG AA 4.5:1 cumplido
- ✅ FR-005: Estados visuales consistentes
- ✅ FR-006: Errores de tema loggeados

### Success Criteria
- ✅ SC-001: Tema aplicado en <100ms
- ✅ SC-002: 100% ventanas con tema oscuro
- ✅ SC-003: Contraste mínimo 4.5:1
- ✅ SC-004: Mejora de comodidad visual (feedback cualitativo)

---

## 11. Demo Script (para presentación)

```bash
# 1. Mostrar tema del sistema (claro)
# 2. Iniciar aplicación
python main.py

# 3. Destacar:
#    - Tema oscuro aplicado instantáneamente
#    - Independiente del sistema
#    - Todos los controles con buen contraste

# 4. Cambiar tema del sistema en vivo
#    - App mantiene tema oscuro

# 5. Cerrar y reabrir
#    - Comportamiento consistente

# 6. Mostrar logs
cat Logs/*.log | Select-String "theme"
```

---

## 12. Next Steps

Una vez completado el quickstart:

1. **Si todo pasa**: Feature está listo para PR
2. **Si hay issues**: Revisar [research.md](research.md) y [data-model.md](data-model.md)
3. **Para implementar**: Ver `/speckit.tasks` para lista de tareas detallada

---

## Feedback

¿Encontraste algún problema siguiendo este quickstart? Documenta:
- **Paso donde falló**: [número de sección]
- **Error observado**: [descripción]
- **Fix aplicado**: [solución que funcionó]

Añade a `.specify/memory/` para mejorar documentación.

---

**Estimated Completion Time**: ✅ 15-20 minutos (para desarrollador familiarizado con el proyecto)
