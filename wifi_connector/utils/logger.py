"""
Módulo de utilidad de logging para WiFi Connector.

Este módulo proporciona una interfaz centralizada de logging con soporte para
logging en consola y archivo, niveles de log configurables, y formato
consistente en toda la aplicación.
"""

import logging
from typing import Optional


class Logger:
    """
    Utilidad centralizada de logging para el sistema WiFi Connector.

    Proporciona métodos estáticos para registrar logs en diferentes niveles con
    formato consistente y soporte para salida en consola y archivo.
    """

    _logger: Optional[logging.Logger] = None
    _is_setup: bool = False

    @classmethod
    def setup(cls, level: str = "INFO", log_file: Optional[str] = None) -> None:
        """
        Configura el sistema de logging.

        Args:
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Ruta opcional al archivo de log.
                     Si es None, crea un archivo con marca de tiempo en la carpeta Logs.
        """
        if cls._is_setup:
            return

        cls._logger = logging.getLogger("wifi_connector")
        cls._logger.setLevel(getattr(logging, level.upper()))

        cls._logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

        file_handler = None
        if log_file is None:
            from wifi_connector.utils.paths import get_logs_folder
            from datetime import datetime

            logs_folder = get_logs_folder()
            try:
                logs_folder.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%d-%m-%Y")
                log_file = str(logs_folder / f"{timestamp}.log")
            except OSError:
                log_file = None

        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
            except OSError:
                file_handler = None

        if file_handler:
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            cls._logger.addHandler(file_handler)

        cls._is_setup = True

    @classmethod
    def _ensure_setup(cls) -> None:
        """Asegura que el logger está configurado antes de usar."""
        if not cls._is_setup:
            cls.setup()

    @classmethod
    def info(cls, message: str) -> None:
        """
        Registra mensaje de información.

        Args:
            message: Mensaje a registrar
        """
        cls._ensure_setup()
        if cls._logger:
            cls._logger.info(message)
        else:
            logging.info(message)

    @classmethod
    def error(cls, message: str, exc_info: bool = False) -> None:
        """
        Registra mensaje de error.

        Args:
            message: Mensaje de error a registrar
            exc_info: Incluir información de excepción si es True
        """
        cls._ensure_setup()
        if cls._logger:
            cls._logger.error(message, exc_info=exc_info)
        else:
            logging.error(message, exc_info=exc_info)

    @classmethod
    def debug(cls, message: str) -> None:
        """
        Registra mensaje de depuración.

        Args:
            message: Mensaje de depuración a registrar
        """
        cls._ensure_setup()
        if cls._logger:
            cls._logger.debug(message)
        else:
            logging.debug(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """
        Registra mensaje de advertencia.

        Args:
            message: Mensaje de advertencia a registrar
        """
        cls._ensure_setup()
        if cls._logger:
            cls._logger.warning(message)
        else:
            logging.warning(message)

    @classmethod
    def critical(cls, message: str, exc_info: bool = False) -> None:
        """
        Registra mensaje crítico.

        Args:
            message: Mensaje crítico a registrar
            exc_info: Incluir información de excepción si es True
        """
        cls._ensure_setup()
        if cls._logger:
            cls._logger.critical(message, exc_info=exc_info)
        else:
            logging.critical(message, exc_info=exc_info)
