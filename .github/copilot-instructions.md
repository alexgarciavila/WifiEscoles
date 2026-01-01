# GitHub Copilot Instructions for Python Projects

## Idioma y comunicación
- Si el usuario habla en **castellano**, responde en **castellano**.
- Si el usuario habla en **catalán**, responde en **catalán**.
- En el código (nombres de variables, funciones y clases) usa **inglés técnico**.
- Los **docstrings y comentarios** deben estar en el mismo idioma que el usuario esté usando en ese momento.

## Estilo general
- Usa siempre la **versión más alta de Python disponible en el entorno**, sin fijar número concreto.
- Sigue **PEP 8** y formateo compatible con **black**:
  - Longitud de línea recomendada: 88 caracteres.
  - Usa **comillas dobles** (`"`) según la convención de *black*.
- Prioriza código **claro y legible** frente a soluciones innecesariamente complejas.

## Tipado y diseño de código
- Usa **type hints** en funciones y métodos públicos, y en internos cuando aporten claridad.
- Usa `from __future__ import annotations` cuando simplifique la definición de tipos.
- Prefiere **programación orientada a objetos**, usando clases y métodos para estructurar la lógica.
- Usa funciones libres como helpers cuando tenga sentido, pero prioriza agrupar comportamiento relacionado dentro de clases.
- Evita efectos secundarios al importar módulos; usa `if __name__ == "__main__":` para el código ejecutable.
- Sugiere `@dataclass` para modelos de datos simples solo cuando aporte claridad.
- Para funciones y métodos internos o privados, usa la **convención de guion bajo**:
  - `_internal_function()` o `_internal_method()` para elementos internos.
  - `__private_method()` únicamente cuando sea un método verdaderamente privado dentro de una clase.

## Librerías y dependencias
- Prioriza la **biblioteca estándar** antes de añadir dependencias externas.
- Si propones una librería de terceros:
  - Debe estar extendida y mantenida.
  - Incluye un comentario tipo: `# Requires 'requests' in requirements.txt`.
- Evita dependencias pesadas sin motivo claro.

## Manejo de errores y seguridad
- Evita capturar excepciones genéricas (`except Exception:`); prefiere excepciones específicas.
- No uses `eval` ni `exec` salvo casos estrictamente justificados.
- No hardcodees credenciales o secretos; usa variables de entorno.
- Usa context managers al trabajar con ficheros.

## Logging
- Usa siempre la librería estándar `logging` en lugar de `print()` para registrar información en aplicaciones y librerías.
- En cada módulo, define un logger de módulo:
  - `logger = logging.getLogger(__name__)`.
- La configuración global del logging (niveles, handlers, formato) debe hacerse solo en los puntos de entrada:
  - `src/main.py`, `src/cli/main.py`, `src/api/*`, o `src/gui/app.py`.
- Niveles de logging recomendados:
  - `logger.debug(...)` → información detallada para depuración.
  - `logger.info(...)` → eventos normales del flujo de la aplicación.
  - `logger.warning(...)` → situaciones anómalas pero no críticas.
  - `logger.error(...)` → errores que impiden completar una operación.
  - `logger.critical(...)` → fallos graves que comprometen el funcionamiento.
- Prefiere el formateo perezoso de mensajes cuando se construyen cadenas costosas:
  - `logger.debug("User %s logged in", user_id)` en lugar de f-strings si el rendimiento es relevante.
- No registres datos sensibles (contraseñas, tokens, información personal).

## Tests y calidad
- Usa **pytest** salvo que el proyecto utilice otro framework.
- Estilo de tests recomendado:
  - Nombres descriptivos (`test_function_does_expected_thing`).
  - Patrón Arrange–Act–Assert.
- Evita mocks innecesarios si se pueden usar funciones puras.
- Evita depender de red o APIs externas en los tests salvo que sea necesario.

## Estructura del proyecto
- Prefiere una estructura **modular y orientada a objetos** clara:
  - Código fuente dentro de un paquete (`src/` o nombre del proyecto).
  - Organiza el código en **múltiples módulos y paquetes**, evitando concentrar toda la lógica en un solo archivo.
  - Prioriza diseñar **clases con métodos** para la lógica de negocio, en lugar de scripts puramente procedimentales.
  - Ejemplo de estructura recomendada:
    - `src/domain/models.py` (clases de dominio)
    - `src/services/use_cases.py` (clases de servicio/casos de uso)
    - `src/infrastructure/repositories.py` (acceso a BD, APIs, etc.)
    - `src/main.py` (punto de entrada principal del proyecto)
    - `src/cli/main.py` si existe CLI.
    - `src/api/routes.py` si existe API.
    - `src/gui/app.py` si existe interfaz gráfica (GUI).

### Reglas para puntos de entrada
- `src/main.py` **no debe contener lógica de negocio**.
  - Solo debe realizar orquestación: leer configuración, inicializar clases principales y delegar.
  - La lógica real debe estar en clases dentro de `domain/`, `services/` o `infrastructure/`.
- Para CLI:
  - Usa `if __name__ == "__main__":` en `src/cli/main.py`.
  - El módulo debe delegar a una clase o función en `services/`.
- Para API:
  - Define routers, controladores o endpoints en `src/api/`.
  - Mantén la lógica de negocio **fuera** de la capa API.
- Para GUI:
  - Sitúa el código de la interfaz en `src/gui/`.
  - Sigue el patrón MVC/MVP/MVVM cuando sea posible:
    - **Vista (GUI)** → interacción con el usuario.
    - **Modelo (domain/)** → reglas y datos.
    - **Controlador/Presenter/ViewModel (services/)** → puente entre GUI y lógica.
  - Evita mezclar lógica de negocio con código de interfaz gráfica.

- Tests en `tests/`, con una estructura paralela a la de `src/`.
- Siempre que sea posible, divide el código en **varios archivos y carpetas**, evitando módulos gigantes.
- Sugiere extraer código repetido a **clases, métodos o módulos auxiliares**.
- No propongas grandes refactors salvo petición explícita.

## Trabajo con código existente
- Respeta el estilo del código ya escrito.
- Cuando mejores una función:
  - Mantén la firma salvo petición explícita.
  - Procura que los cambios sean pequeños y fáciles de revisar.
- Si se pide refactor:
  - Divide en pasos pequeños y coherentes.
  - No mezcles cambios funcionales con cambios de estilo.

## Documentación y comentarios
- Usa docstrings en funciones y clases públicas:
  - Qué hace la función o clase.
  - Parámetros y retorno (si no es obvio).
- Los docstrings deben estar en el **idioma del usuario** (castellano o catalán según corresponda).
- Escribe comentarios solo cuando aporten contexto o explicaciones no triviales.
- Evita comentarios redundantes que describan código evidente.

## Rendimiento y legibilidad
- No optimices prematuramente.
- Prefiere comprensiones cuando son claras; usa bucles cuando sean más legibles.
- La claridad prevalece sobre micro-optimizaciones.

## Integración con herramientas
- Ten en cuenta herramientas como **black**, **isort**, **ruff**, **flake8**, **pylint**, **mypy** o **pyright**.
- Evita sugerencias que generen avisos típicos de linters.

## Comportamiento general
- Prioriza siempre:
  1. **Corrección**.
  2. **Claridad**.
  3. **Consistencia**.
- En caso de duda, elige la solución más simple y mantenible.
- Adecúa las sugerencias al archivo y al contexto del proyecto.
