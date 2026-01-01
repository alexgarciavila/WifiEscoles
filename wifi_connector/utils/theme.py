"""Módulo de configuración de tema oscuro para la aplicación.

Este módulo proporciona la configuración centralizada del tema oscuro
forzado en toda la aplicación usando customTkinter.
"""

from __future__ import annotations

from typing import Literal

import customtkinter as ctk

from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


# Constantes de configuración del tema (hardcoded)
APPEARANCE_MODE: Literal["dark"] = "dark"
COLOR_THEME: Literal["blue"] = "blue"
THEME_SETUP_MAX_TIME_MS: int = 100


def setup_dark_theme() -> None:
    """Configura el tema oscuro para toda la aplicación.
    
    Esta función DEBE ser llamada antes de crear cualquier widget de
    customTkinter. Aplica el modo de apariencia oscuro global y el tema
    de colores azul.
    
    Raises:
        ImportError: Si customTkinter no está instalado.
        AttributeError: Si la API de customTkinter cambió (breaking change).
        RuntimeError: Si ocurre un error interno de customTkinter.
        
    Efectos secundarios:
        - Registra mensaje de éxito/fallo usando wifi_connector.utils.logger
        - Modifica la configuración global de apariencia de customTkinter
        
    Example:
        >>> from wifi_connector.utils.theme import setup_dark_theme
        >>> setup_dark_theme()  # Configurar antes de crear ventanas
        >>> # Ahora es seguro crear ventanas GUI
    """
    try:
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        Logger.info(t.THEME_LOG_CONFIGURED)
    except ImportError as e:
        Logger.critical(t.THEME_ERROR_NOT_INSTALLED.format(error=e))
        raise
    except (AttributeError, RuntimeError) as e:
        Logger.error(t.THEME_ERROR_SETUP.format(error=e))
        raise
