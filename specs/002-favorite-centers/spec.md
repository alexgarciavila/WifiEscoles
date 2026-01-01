# Feature Specification: Gestión de Centros Favoritos

**Feature Branch**: `002-favorite-centers`  
**Created**: 2025-12-13  
**Status**: Draft  
**Input**: User description: "Los usuarios han de poder seleccionar centros como favoritos. Cada centro tendrá un icono que está en la carpeta images del proyecto. Cuando está desmarcado se muestra el icono fav_unchecked.png y cuando está seleccionado se muestra fav.png. Si un usuario marca uno o varios centros, su información se guardará en la carpeta json en un archivo json llamado favoritos.json con la misma estructura que se usa en wifi.json. La aplicación tendrá un icono con fav.png o fav_unchecked.png según corresponda, a la izquierda del icono de ayuda, siguiendo el mismo estilo. Si el usuario hace clic en ese icono, se cargarán los centros de favoritos.json en vez de los de wifi.json. El icono funciona como un switch para mostrar centros favoritos y todos los centros."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Marcar y Desmarcar Favoritos (Priority: P1)

Los usuarios pueden marcar centros educativos específicos como favoritos mediante un icono visual junto a cada centro en la lista. Al hacer clic en el icono, el centro se añade o elimina de favoritos inmediatamente.

**Why this priority**: Esta es la funcionalidad básica que permite a los usuarios gestionar sus favoritos. Sin esta capacidad, la feature no aporta valor.

**Independent Test**: Buscar un centro específico, hacer clic en su icono de favorito, verificar que el icono cambia de fav_unchecked.png a fav.png. Hacer clic de nuevo y verificar que vuelve a fav_unchecked.png. Los cambios deben ser inmediatos sin necesidad de reiniciar la aplicación.

**Acceptance Scenarios**:

1. **Given** un centro visible en la lista, **When** el usuario hace clic en el icono de favorito (fav_unchecked.png), **Then** el icono cambia a fav.png y el centro se guarda en favoritos.json
2. **Given** un centro marcado como favorito (fav.png visible), **When** el usuario hace clic en el icono, **Then** el icono cambia a fav_unchecked.png y el centro se elimina de favoritos.json
3. **Given** múltiples centros en la lista, **When** el usuario marca varios como favoritos, **Then** todos los centros marcados muestran fav.png y se persisten en favoritos.json
4. **Given** un centro marcado como favorito, **When** el usuario reinicia la aplicación, **Then** el centro sigue mostrando fav.png

---

### User Story 2 - Filtrar Vista por Favoritos (Priority: P2)

Los usuarios pueden alternar entre ver todos los centros educativos disponibles o solo sus centros favoritos mediante un botón toggle en la cabecera de la aplicación.

**Why this priority**: Proporciona acceso rápido a los centros más utilizados, mejorando la experiencia de usuarios frecuentes. Depende de P1 para tener favoritos que mostrar.

**Independent Test**: Marcar 2-3 centros como favoritos, hacer clic en el botón toggle de la cabecera, verificar que solo se muestran los centros favoritos. Hacer clic de nuevo y verificar que se muestran todos los centros.

**Acceptance Scenarios**:

1. **Given** la aplicación muestra todos los centros, **When** el usuario hace clic en el botón toggle (con icono fav_unchecked.png), **Then** la lista muestra solo centros favoritos y el botón cambia a fav.png
2. **Given** la aplicación muestra solo favoritos (botón con fav.png), **When** el usuario hace clic en el botón toggle, **Then** la lista muestra todos los centros y el botón cambia a fav_unchecked.png
3. **Given** el usuario no tiene centros favoritos, **When** activa el filtro de favoritos, **Then** se muestra mensaje "No tens centres marcats com a favorits"
4. **Given** la aplicación está en modo favoritos, **When** el usuario realiza una búsqueda, **Then** la búsqueda filtra solo dentro de favoritos

---

### User Story 3 - Gestión de Favoritos con Búsqueda (Priority: P3)

Cuando el usuario está en modo de vista de favoritos, la funcionalidad de búsqueda filtra únicamente dentro de los centros favoritos, facilitando encontrar un favorito específico cuando hay muchos.

**Why this priority**: Mejora la usabilidad para usuarios con muchos favoritos. Es una optimización sobre la funcionalidad básica.

**Independent Test**: Marcar 10+ centros como favoritos, activar vista de favoritos, buscar por nombre de uno de los favoritos, verificar que solo aparecen resultados de favoritos.

**Acceptance Scenarios**:

1. **Given** usuario en modo favoritos con 10+ centros favoritos, **When** escribe en el campo de búsqueda, **Then** solo se filtran centros dentro de favoritos
2. **Given** usuario en modo favoritos con búsqueda activa, **When** cambia a modo todos los centros, **Then** la búsqueda se limpia y muestra todos los centros
3. **Given** usuario buscando en modo favoritos, **When** desmarca un favorito visible en resultados, **Then** el centro desaparece de los resultados inmediatamente

---

### Edge Cases

- **Favoritos vacíos**: ¿Qué se muestra cuando no hay centros favoritos y se activa el filtro?
  - Mostrar mensaje informativo: "No tens centres marcats com a favorits. Fes clic a l'icona ★ al costat de qualsevol centre per afegir-lo als teus favorits."

- **Archivo corrupto**: ¿Qué ocurre si favoritos.json está corrupto o tiene formato inválido?
  - Sistema debe detectar error de parsing, mostrar advertencia en logs, crear nuevo favoritos.json vacío y continuar funcionando

- **Sincronización**: ¿Qué pasa si favoritos.json se elimina manualmente mientras la app está corriendo?
  - Al guardar siguiente favorito, se recrea el archivo. No afecta funcionamiento actual de la app

- **Centros no existentes**: ¿Qué pasa si un favorito guardado ya no existe en wifi.json?
  - Al cargar favoritos, validar que cada centro existe en wifi.json. Si no existe, eliminarlo automáticamente de favoritos.json para evitar acumulación de favoritos obsoletos

- **Límite de favoritos**: ¿Hay un límite máximo de centros favoritos?
  - No hay límite técnico. Sistema debe manejar cientos de favoritos sin degradación de performance

- **Búsqueda sin resultados en favoritos**: ¿Qué se muestra cuando búsqueda en modo favoritos no arroja resultados?
  - Mostrar mensaje contextual: "No hi ha resultats a favorits per '[término de búsqueda]'. Prova a buscar en tots els centres." para orientar al usuario

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEBE proporcionar un icono clicable junto a cada centro en la lista para marcar/desmarcar como favorito
- **FR-002**: Sistema DEBE usar fav_unchecked.png cuando centro NO es favorito y fav.png cuando SÍ es favorito
- **FR-003**: Sistema DEBE persistir centros favoritos en Json/favoritos.json usando la misma estructura de datos que wifi.json
- **FR-004**: Sistema DEBE cargar favoritos existentes al iniciar la aplicación y mantener sincronizado el estado visual
- **FR-005**: Sistema DEBE proporcionar un botón toggle en la cabecera (a la izquierda del botón de ayuda) para alternar entre vista de todos los centros y solo favoritos
- **FR-006**: Botón toggle DEBE mostrar fav_unchecked.png cuando se muestran todos los centros y fav.png cuando se muestran solo favoritos
- **FR-007**: Sistema DEBE actualizar la lista visible inmediatamente cuando usuario activa/desactiva filtro de favoritos
- **FR-008**: Sistema DEBE crear Json/favoritos.json automáticamente si no existe
- **FR-009**: Sistema DEBE manejar errores de lectura/escritura de favoritos.json sin crashear la aplicación
- **FR-010**: Búsqueda DEBE filtrar solo dentro de favoritos cuando vista de favoritos está activa
- **FR-011**: Al cambiar entre modos (todos/favoritos), búsqueda DEBE limpiarse automáticamente
- **FR-012**: Sistema DEBE mostrar mensaje contextual cuando búsqueda en modo favoritos no arroja resultados: "No hi ha resultats a favorits per '[término]'. Prova a buscar en tots els centres."

### Key Entities *(include if feature involves data)*

- **FavoriteCenter**: Representa un centro marcado como favorito
  - Atributos: center_code, center_name, username, password (misma estructura que CenterCredentials)
  - Persiste en: Json/favoritos.json
  - Relación: Subconjunto de centros disponibles en wifi.json

- **ViewMode**: Modo de visualización actual de la lista
  - Estados: ALL_CENTERS (todos), FAVORITES_ONLY (solo favoritos)
  - Afecta: Lista visible, comportamiento de búsqueda, apariencia del botón toggle

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuarios pueden marcar/desmarcar un centro como favorito con un solo clic y el cambio es visible inmediatamente
- **SC-002**: Sistema persiste favoritos correctamente - favoritos marcados siguen presentes después de reiniciar la aplicación
- **SC-003**: Usuarios pueden alternar entre vista de todos los centros y solo favoritos con un solo clic en el botón toggle
- **SC-004**: Vista de favoritos se carga en menos de 500ms incluso con 100+ favoritos
- **SC-005**: Sistema recupera gracefully de errores de archivo (favoritos.json corrupto/faltante) sin perder datos de sesión actual

## Assumptions *(optional)*

- Iconos fav.png y fav_unchecked.png ya existen en carpeta images/
- Estructura de favoritos.json es idéntica a wifi.json (lista de objetos con center_code, center_name, username, password)
- Usuario tiene permisos de escritura en carpeta Json/
- Favoritos son locales al dispositivo (no hay sincronización entre dispositivos)

## Out of Scope *(optional)*

- **Sincronización cloud**: Favoritos no se sincronizan entre dispositivos
- **Organización de favoritos**: No hay carpetas, categorías o ordenamiento personalizado de favoritos
- **Exportar/importar favoritos**: No hay funcionalidad para compartir favoritos con otros usuarios
- **Búsqueda avanzada**: No hay filtros adicionales como fecha de añadido, frecuencia de uso, etc.
- **Notificaciones**: No hay alertas cuando un centro favorito cambia sus credenciales
- **Analytics**: No se rastrean métricas de uso de favoritos

## Clarifications *(optional)*

### Session 2025-12-13

- Q: Cuando se carga favoritos.json y un centro con center_code ya no existe en wifi.json actual, ¿se debe mantener indefinidamente en favoritos.json o limpiarlo automáticamente? → A: Limpiar automáticamente - eliminarlo de favoritos.json al detectar que ya no existe, evitando acumulación de favoritos obsoletos
- Q: Cuando usuario está en modo "solo favoritos" y realiza búsqueda sin resultados, ¿qué experiencia debe tener? → A: Mensaje contextual - mostrar "No hi ha resultats a favorits per '[término]'. Prova a buscar en tots els centres." con sugerencia para desactivar filtro

> **Ubicación de iconos de favorito en lista**: El icono de favorito (★) se ubicará **a la izquierda del código de centro** en cada fila de la lista

> **Comportamiento del botón toggle sin favoritos**: Cuando no hay favoritos guardados, el botón toggle estará visible pero al hacer clic mostrará el mensaje de favoritos vacíos

> **Persistencia durante sesión**: Cambios en favoritos se guardan inmediatamente a disco (no hay botón "Guardar")

> **Validación de centros**: Al cargar favoritos.json, se valida que cada center_code existe en wifi.json. Si no existe, se elimina automáticamente de favoritos.json (limpieza automática)

> **Estilo del botón toggle**: Botón toggle seguirá el mismo estilo que botón de ayuda (?) - botón circular pequeño con icono

