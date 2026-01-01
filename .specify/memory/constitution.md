<!--
Informe de Impacto de Sincronización

- Cambio de versión: plantilla -> 1.0.0
- Principios modificados: [marcador] ->
	- "Calidad de Código" (nuevo)
	- "Estándares de Pruebas" (nuevo)
	- "Consistencia de Experiencia de Usuario" (nuevo)
	- "Rendimiento y Escalabilidad" (nuevo)
	- "Observabilidad y Disciplina de Lanzamiento" (nuevo)
- Secciones añadidas: "Seguridad y Cumplimiento", "Flujo de Desarrollo y Puertas de Calidad"
- Secciones eliminadas: ninguna
- Plantillas que requieren actualización:
	- .specify/templates/plan-template.md: ⚠ pendiente (alinear guía de verificación de constitución)
	- .specify/templates/spec-template.md: ⚠ pendiente (alinear escenarios de usuario y pruebas)
	- .specify/templates/tasks-template.md: ⚠ pendiente (categorías de tareas y puertas de pruebas)
	- .specify/templates/agent-file-template.md: ⚠ pendiente
	- .specify/templates/checklist-template.md: ⚠ pendiente
	- .specify/templates/commands/*.md: ⚠ pendiente (carpeta de comandos no presente o no auditada)
- TODOs de seguimiento:
	- TODO(RATIFICATION_DATE): Fecha de ratificación original desconocida — completar con la fecha de adopción orgánica.

-->

# WifiEscoles Constitution

## Core Principles

### I. Code Quality
Todas las contribuciones DEBEN cumplir estándares claros de legibilidad, mantenibilidad y seguridad.
- Requisitos: el código DEBE seguir las convenciones del proyecto (PEP 8 / black/ruff cuando aplique), incluir type hints en interfaces públicas
- Verificación: todo PR DEBE pasar linting automático y revisión de pares enfocada en diseño y claridad
- Razonamiento: la calidad sostenible reduce deuda técnica y acelera iteración futura

### II. Test Standards
Las pruebas son obligatorias y DEBEN ser comprensibles, rápidas y confiables.
- Requisitos: los unit tests DEBEN cubrir casos críticos; los integration tests DEBEN cubrir contratos y flujos P1; los tests DEBEN ser reproducibles sin dependencia de red externa salvo cuando se simule o se marque explícitamente
- Flujo: preferir TDD para cambios significativos; los tests nuevos DEBEN fallar antes de implementar la funcionalidad (Red-Green-Refactor)
- Métrica: los pipelines DEBEN ejecutar tests y bloquear merges si fallan pruebas críticas

### III. User Experience Consistency
La experiencia de usuario DEBE ser coherente entre iteraciones y plataformas.
- Requisitos: los cambios en UI/UX DEBEN incluir criterios de aceptación explícitos y pruebas de usabilidad (manual o automatizada) para flujos prioritarios
- Diseño: patrones visuales y de interacción DEBEN documentarse en un repositorio accesible (README de `gui/` o docs correspondientes)
- Razonamiento: consistencia reduce errores de usuario y soporte

### IV. Performance & Scalability
Los requisitos de rendimiento son parte integrante de la definición de éxito de la funcionalidad.
- Requisitos: cada especificación DEBE declarar objetivos de rendimiento (ej. latencia p95, uso de memoria) y constraints técnicos; cambios que impacten usuarios concurrentes DEBEN incluir pruebas o benchmarks
- Validación: optimizaciones DEBEN estar respaldadas por mediciones reproducibles y comparativas

### V. Observability & Release Discipline
El software DEBE ser observable y las entregas DEBEN ser controlables y reversibles.
- Requisitos: logging estructurado, métricas clave y trazas mínimas para flujos críticos; despliegues DEBEN incluir rollback plan y checks automáticos post-release
- Gobernanza: incidentes de producción DEBEN seguir el playbook de respuesta y postmortem documentado

## Security & Compliance
Las políticas de seguridad y cumplimiento son obligatorias.
- Requisitos: no embutir credenciales; validar dependencias por vulnerabilidades conocidas; cumplir normativas aplicables (si procede)
- Verificación: escaneo de dependencias y revisión de cambios que afecten datos sensibles

## Development Workflow & Quality Gates
Define cómo se desarrolla, revisa y publica el software.
- Pull Requests: toda contribución DEBE incluir descripción, tests y referencia a issue o tarea
- Revisión de Código: mínimo una aprobación de un revisor técnico para cambios no triviales; cambios críticos DEBEN incluir revisión adicional de seguridad/arquitectura
- CI/CD: los pipelines DEBEN ejecutar lint, tests y checks de seguridad; merges bloqueados si fallan gates críticos

## Governance
Esta constitución establece las normas de gobernanza del proyecto y cómo se ENMIENDAN.
- Enmiendas: cambios a la constitución DEBEN documentarse en una PR que describa el motivo, el impacto y un plan de migración. Para cambios menores (clarificaciones, typos) se aplica PATCH; para añadir o redefinir principios se aplica MINOR; la eliminación o redefinición incompatible de principios aplica MAJOR.
- Aprobación: las enmiendas DEBEN ser aprobadas por la mayoría técnica del equipo de mantenimiento (o por quienes estén listados como responsables en `OWNERS` si existe)
- Revisión de cumplimiento: todas las PRs principales DEBEN referenciar la sección de la constitución relacionada y explicar cómo cumplen las reglas

**Versión**: 1.0.0 | **Ratificada**: TODO(RATIFICATION_DATE): completar fecha de adopción | **Última modificación**: 2025-12-13
