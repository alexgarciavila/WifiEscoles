# Feature Specification: Tema Oscuro Forzado

**Feature Branch**: `001-dark-theme-mode`  
**Created**: 2025-12-13  
**Status**: Draft  
**Input**: User description: "Tengo una aplicación legacy que se encarga de conectar a la wifi de los centros educativos usando mschav2 junto a una libreria externa y un csv de configuracion dado. Necesito añadir nuevas funciones a la aplicacion, como que el tema sea siempre oscuro indistintamente del sistema."

## Clarifications

### Session 2025-12-13

- Q: ¿Qué framework GUI específico usa actualmente la aplicación WifiEscoles? → A: customTkinter
- Q: ¿Dónde se persiste actualmente la configuración de tema? → A: No quiero archivo de configuración para esta funcionalidad. Siempre ha de ser tema oscuro.
- Q: ¿Qué color theme específico de customTkinter deseas usar? → A: blue (default)
- Q: ¿Qué tiempo de aplicación del tema es realmente aceptable? → A: instantáneo (<100ms)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Aplicar Tema Oscuro Permanente (Priority: P1)

Como usuario de la aplicación WifiEscoles, quiero que la interfaz gráfica muestre siempre un tema oscuro, independientemente de la configuración del sistema operativo, para trabajar en condiciones de baja luminosidad sin forzar la vista.

**Why this priority**: Es la funcionalidad principal solicitada y mejora directamente la experiencia de usuario en entornos educativos donde a menudo se trabaja con luminosidad reducida. Puede entregarse como funcionalidad standalone.

**Independent Test**: Puede probarse completamente al iniciar la aplicación en un sistema con tema claro y verificar que la aplicación se muestra en tema oscuro. También verificar que al cambiar el tema del sistema operativo, la aplicación mantiene el tema oscuro.

**Acceptance Scenarios**:

1. **Given** el usuario tiene el sistema operativo configurado en tema claro, **When** el usuario inicia la aplicación WifiEscoles, **Then** la aplicación se muestra con tema oscuro
2. **Given** la aplicación está ejecutándose con tema oscuro, **When** el usuario cambia el tema del sistema operativo a claro o viceversa, **Then** la aplicación mantiene el tema oscuro sin cambios
3. **Given** el usuario reinicia la aplicación, **When** la aplicación se vuelve a abrir, **Then** se muestra con tema oscuro desde el inicio
4. **Given** la aplicación tiene ventanas secundarias (about, settings, dialogs), **When** el usuario abre cualquier ventana secundaria, **Then** todas las ventanas muestran el tema oscuro consistentemente

---

### User Story 2 - Contraste y Legibilidad en Tema Oscuro (Priority: P2)

Como usuario, quiero que todos los elementos de la interfaz (texto, botones, campos de entrada, mensajes de estado) sean claramente legibles en tema oscuro, para poder operar la aplicación eficientemente.

**Why this priority**: Garantiza la usabilidad del tema oscuro y debe implementarse junto con P1 para asegurar una experiencia de usuario completa desde el primer momento.

**Independent Test**: Puede probarse navegando por todas las pantallas de la aplicación, probando estados de hover/focus/disabled en controles, y verificando que todos los textos son legibles (contraste mínimo WCAG AA).

**Acceptance Scenarios**:

1. **Given** la aplicación está en tema oscuro, **When** el usuario ve la ventana principal con todos los controles (botones, campos, listas), **Then** todos los elementos tienen contraste suficiente y son legibles
2. **Given** la aplicación muestra mensajes de estado (éxito, error, advertencia), **When** estos mensajes aparecen en tema oscuro, **Then** los colores son distinguibles y el texto es legible
3. **Given** el usuario interactúa con elementos (hover, focus, disabled), **When** estos estados se activan, **Then** los cambios visuales son perceptibles en tema oscuro
4. **Given** la aplicación tiene campos de entrada de texto, **When** el usuario introduce texto, **Then** el texto es claramente visible contra el fondo oscuro del campo

---

### Edge Cases

- ¿Qué ocurre si el framework customTkinter no soporta el tema oscuro en alguna versión específica o tiene bugs conocidos? → **Mitigación**: Especificar versión mínima customTkinter >= 5.0.0 en requirements.txt
- ¿Qué sucede con capturas de pantalla o elementos gráficos que puedan incluir fondos claros (imágenes, iconos)? → **Aceptado**: Imágenes/iconos custom no se modifican automáticamente; se espera que sean compatibles con tema oscuro o se documenten excepciones
- ¿Cómo se manejan los diálogos del sistema operativo (file pickers, message boxes nativos) que no respetan el tema de la aplicación? → **Limitación conocida**: Diálogos nativos del SO no son controlables por la aplicación; se aceptan como excepción visual
- ¿Qué ocurre si existen widgets tkinter legacy (`tk.Label`, `tk.Button`) que no usan customTkinter? → **Acción requerida**: Durante implementación, auditar código GUI y migrar widgets legacy a equivalentes customTkinter para garantizar consistencia de tema

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La aplicación DEBE aplicar un tema oscuro a toda la interfaz gráfica al iniciar, ignorando la configuración de tema del sistema operativo
- **FR-002**: La aplicación DEBE mantener el tema oscuro activo durante toda la sesión, sin cambios automáticos basados en eventos del sistema
- **FR-003**: La aplicación DEBE aplicar el tema oscuro a todas las ventanas, diálogos y componentes visuales (ventana principal, ventana about, diálogos de configuración)
- **FR-004**: La aplicación DEBE asegurar contraste suficiente entre texto y fondo en todos los componentes para garantizar legibilidad (mínimo WCAG AA 4.5:1 para texto normal)
- **FR-005**: La aplicación DEBE aplicar colores consistentes en tema oscuro para estados visuales (hover, focus, disabled, active)
- **FR-006**: La aplicación DEBE registrar en log cualquier error relacionado con la aplicación del tema (problemas con widgets no compatibles, errores de rendering)
- **FR-007**: Si la configuración del tema falla al arranque, la aplicación NO DEBE continuar y DEBE terminar con mensaje de error claro (fail-fast strategy)

### Key Entities

- **Theme Mode**: Modo de apariencia forzado a "dark" en customTkinter. Se aplica mediante `ctk.set_appearance_mode("dark")` al inicio de la aplicación sin opciones de configuración.
- **GUI Components**: Cada ventana, diálogo y widget de la interfaz que respeta automáticamente el tema oscuro de customTkinter. Incluye: ventana principal, ventana about, diálogos de configuración, botones (CTkButton), campos de texto (CTkEntry), listas, labels (CTkLabel), status bar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El tema oscuro se aplica instantáneamente al iniciar la aplicación (tiempo de aplicación <100ms, imperceptible para el usuario)
- **SC-002**: El 100% de las ventanas y diálogos de la aplicación se muestran con tema oscuro consistente
- **SC-003**: Todos los elementos de texto tienen un contraste mínimo de 4.5:1 contra el fondo (verificable con herramientas de contraste)
- **SC-004**: Los usuarios reportan mejora en la comodidad visual al usar la aplicación en entornos de baja luminosidad (medible mediante encuesta post-implementación)

## Assumptions

- La aplicación usa **customTkinter >= 5.0.0** como framework GUI, que proporciona soporte nativo para temas oscuros mediante el método `set_appearance_mode("dark")` (API estable desde v5.0)
- El color theme usado será **"blue"** (default de customTkinter), que proporciona acentos azules con buena legibilidad y cumple WCAG AA por diseño
- El tema oscuro es **permanente y hardcoded** (no hay archivo de configuración ni opción de cambio por parte del usuario)
- Se asume que customTkinter aplicará automáticamente los colores de tema oscuro a todos los widgets nativos (CTkButton, CTkEntry, CTkLabel, etc.)
- Se asume que todos los widgets personalizados (si existen) también respetarán el tema oscuro de customTkinter
- Se asume que la GUI existente usa widgets customTkinter (no widgets tkinter legacy) - si existen widgets `tk.*` legacy, deberán auditarse y migrarse durante implementación
- Se asume impacto de memoria/recursos negligible (<1MB, <10ms en performance)

## Out of Scope

- Creación de una opción de configuración para que el usuario elija entre tema claro/oscuro/sistema (esto sería una feature futura)
- Implementación de temas personalizables con paletas de colores definidas por el usuario
- Animaciones de transición entre temas
- Soporte para temas de alto contraste adicionales (más allá del tema oscuro estándar)
- Cambios en la lógica de negocio de conexión WiFi (mschav2, parsing de CSV, etc.)
