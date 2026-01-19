"""Utilidades de rutas para manejar archivos en modo desarrollo y ejecutable (exe).

Este módulo proporciona utilidades para localizar correctamente archivos de recursos
al ejecutar como script de Python o como ejecutable de PyInstaller.
"""

import sys
from pathlib import Path


def get_base_path() -> Path:
    """Obtiene la ruta base de la aplicación.

    Cuando se ejecuta como script, devuelve el directorio raíz del proyecto.
    Cuando se ejecuta como ejecutable de PyInstaller, devuelve la carpeta temporal
    donde PyInstaller extrae los archivos.

    Returns:
        Objeto Path apuntando al directorio base
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent


def get_json_path() -> Path:
    """Obtiene la ruta a la carpeta Json.

    Cuando se ejecuta como ejecutable, busca la carpeta Json junto al archivo .exe.
    Cuando se ejecuta como script, usa una ruta relativa.

    Returns:
        Objeto Path apuntando al directorio Json
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "Json"
    return get_base_path() / "Json"


def get_logs_folder() -> Path:
    """Obtiene la ruta a la carpeta de Logs.

    Cuando se ejecuta como ejecutable, busca la carpeta Logs junto al archivo .exe.
    Cuando se ejecuta como script, usa el directorio de trabajo actual.

    Returns:
        Objeto Path apuntando al directorio de Logs
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "Logs"
    return Path.cwd() / "Logs"
