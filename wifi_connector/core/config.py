"""Gestión de configuración para WiFi Connector.

Este módulo proporciona la dataclass Config para gestionar los parámetros
de configuración del sistema con soporte para cargar desde archivos y validación.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from wifi_connector.utils import translations as t


@dataclass
class Config:
    """Parámetros de configuración para el sistema WiFi Connector.

    Atributos:
        pause_duration: Duración de pausa entre operaciones (segundos)
        credential_dialog_wait_time: Tiempo de espera para diálogo de credenciales (segundos)
        debug_mode: Habilitar modo depuración con logs adicionales
    """

    pause_duration: float = 0.5
    credential_dialog_wait_time: int = 1
    debug_mode: bool = False

    def __post_init__(self):
        """Valida los valores de configuración después de la inicialización."""
        self._validate()

    def _validate(self) -> None:
        """Valida los parámetros de configuración.

        Raises:
            ValueError: Si algún valor de configuración es inválido
        """


        if self.pause_duration < 0:
            raise ValueError(
                t.CONFIG_ERROR_PAUSE_NEGATIVE.format(value=self.pause_duration)
            )



        if self.credential_dialog_wait_time < 0:
            raise ValueError(
                t.CONFIG_ERROR_WAIT_NEGATIVE.format(
                    value=self.credential_dialog_wait_time
                )
            )

    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Carga la configuración desde un archivo JSON.

        Args:
            path: Ruta al archivo de configuración (.json)

        Returns:
            Instancia de Config cargada desde el archivo

        Raises:
            FileNotFoundError: Si el archivo de configuración no existe
            ValueError: Si el formato del archivo no es soportado o el contenido es inválido
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(t.CONFIG_ERROR_FILE_NOT_FOUND.format(path=path))

        suffix = file_path.suffix.lower()

        if suffix != '.json':
            raise ValueError(t.CONFIG_ERROR_UNSUPPORTED_FORMAT.format(suffix=suffix))

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)



        return cls(**data)

    @classmethod
    def default(cls) -> 'Config':
        """Crea configuración con valores por defecto.

        Returns:
            Instancia de Config con valores por defecto
        """
        return cls()
