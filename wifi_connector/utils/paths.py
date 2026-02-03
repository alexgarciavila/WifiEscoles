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

    Nota: esta ruta se mantiene por compatibilidad, pero el uso de Json
    queda obsoleto en favor del vault cifrado.

    Returns:
        Objeto Path apuntando al directorio Json
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "Json"
    return get_base_path() / "Json"


def get_vault_path() -> Path:
    """Obtiene la ruta a la carpeta vault.

    Cuando se ejecuta como ejecutable, busca la carpeta vault junto al .exe.
    Cuando se ejecuta como script, usa una ruta relativa al proyecto.

    Returns:
        Objeto Path apuntando al directorio vault
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "vault"
    return get_base_path() / "vault"


def get_favorites_path() -> Path:
    """Obtiene la ruta al archivo de favoritos.

    Guarda el archivo dentro de la carpeta vault/ tanto en modo ejecutable
    como en modo desarrollo.

    Returns:
        Objeto Path apuntando al archivo vault/fav.json
    """
    return get_vault_path() / "fav.json"


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
