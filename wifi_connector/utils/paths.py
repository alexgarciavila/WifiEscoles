"""Utilidades de rutas para manejar archivos en modo desarrollo y ejecutable (exe).

Este módulo proporciona utilidades para localizar correctamente archivos de recursos
al ejecutar como script de Python o como ejecutable de PyInstaller.
"""

import os
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
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
    
    return base_path


def get_json_path() -> Path:
    """Obtiene la ruta a la carpeta Json.
    
    Cuando se ejecuta como ejecutable, busca la carpeta Json junto al archivo .exe.
    Cuando se ejecuta como script, usa una ruta relativa.
    
    Returns:
        Objeto Path apuntando al directorio Json
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / 'Json'
    else:
        return Path('Json')


def get_wifi_json_path() -> Path:
    """Obtiene la ruta al archivo wifi.json.
    
    Returns:
        Objeto Path apuntando a wifi.json
    """
    return get_json_path() / 'wifi.json'





def get_debug_folder() -> Path:
    """Obtiene la ruta a la carpeta de depuración.
    
    La carpeta de depuración se crea en el directorio de trabajo actual,
    no en la ruta base, para que sea accesible al usuario.
    
    Returns:
        Objeto Path apuntando al directorio de depuración
    """
    return Path.cwd() / 'debug'


def get_logs_folder() -> Path:
    """Obtiene la ruta a la carpeta de Logs.
    
    La carpeta de Logs se crea en el directorio de trabajo actual,
    no en la ruta base, para que sea accesible al usuario.
    
    Returns:
        Objeto Path apuntando al directorio de Logs
    """
    return Path.cwd() / 'Logs'
