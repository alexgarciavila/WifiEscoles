"""Módulo de gestión de credenciales para WiFi Connector.

Este módulo proporciona clases para cargar y gestionar credenciales WiFi
desde archivos JSON, incluyendo funcionalidad de búsqueda y filtrado.
"""

from dataclasses import dataclass
from typing import List, Optional

from wifi_connector.core.exceptions import (
    CredentialsFileError,
    JSONParseError,
    VaultError,
)
from wifi_connector.data.vault_manager import VaultManager
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


@dataclass
class CenterCredentials:
    """Dataclass que representa las credenciales de un centro.

    Atributos:
        center_code: Código único que identifica el centro
        center_name: Nombre descriptivo del centro
        username: Usuario para autenticación WiFi
        password: Contraseña para autenticación WiFi
    """

    center_code: str
    center_name: str
    username: str
    password: str

    def matches_query(self, query: str) -> bool:
        """Verifica si el centro coincide con la consulta de búsqueda.

        Realiza coincidencia insensible a mayúsculas contra el código
        y nombre del centro.

        Args:
            query: Cadena de consulta de búsqueda

        Returns:
            True si la consulta coincide con el código o nombre, False en caso contrario
        """
        query_lower = query.lower()
        return (
            query_lower in self.center_code.lower()
            or query_lower in self.center_name.lower()
        )


class CredentialsManager:
    """Gestor para cargar y acceder a credenciales WiFi desde vault cifrado.

    Proporciona métodos para cargar credenciales desde un vault y
    buscar/filtrar centros por código o nombre.
    """

    def __init__(self, vault_path: Optional[str] = None):
        """Inicializa el gestor de credenciales con la ruta del vault.

        Args:
            vault_path: Ruta al archivo vault.bin que contiene las credenciales.
                       Si es None, usa la ruta por defecto que funciona tanto
                       en modo script como ejecutable.
        """
        if vault_path is None:
            from wifi_connector.utils.paths import get_vault_path

            self.vault_path = str(get_vault_path() / "vault.bin")

        else:
            self.vault_path = vault_path

        self.centers: List[CenterCredentials] = []
        self.vault_metadata: dict = {}
        Logger.debug(t.CREDS_LOG_INIT.format(path=self.vault_path))

    def load_credentials(self, password: str) -> bool:
        """Carga las credenciales desde el vault cifrado.

        Descifra el vault en memoria usando la contraseña proporcionada y
        carga todas las credenciales de los centros.

        Args:
            password: Contraseña del vault

        Returns:
            True si las credenciales se cargaron exitosamente, False en caso contrario

        Raises:
            CredentialsFileError: Si el archivo de vault no se puede encontrar o leer
            JSONParseError: Si el contenido descifrado no es válido
        """
        Logger.info(t.CREDS_LOG_LOADING_VAULT.format(path=self.vault_path))

        try:
            vault_manager = VaultManager(self.vault_path)
            payload = vault_manager.load_vault(password)
            self.vault_metadata = payload.metadata
            return self._load_from_entries(payload.centers)

        except (JSONParseError, VaultError):
            raise

        except Exception as e:
            error_msg = t.CREDS_ERROR_UNEXPECTED.format(error=e)
            Logger.error(error_msg, exc_info=True)
            raise CredentialsFileError(error_msg)

    def _load_from_entries(self, data: list) -> bool:
        """Carga y valida credenciales desde una lista de entradas.

        Args:
            data: Lista de entradas con campos Codi, Centre, Usuari, Contrasenya

        Returns:
            True si las credenciales se cargaron exitosamente
        """
        if not isinstance(data, list):
            raise JSONParseError(
                t.CREDS_ERROR_INVALID_STRUCTURE.format(path=self.vault_path)
            )

        self.centers = []
        for entry in data:
            try:
                center = self._parse_center_entry(entry)
                self.centers.append(center)
            except (KeyError, TypeError) as e:
                Logger.warning(t.CREDS_WARNING_SKIP_ENTRY.format(error=e))
                continue

        Logger.info(t.CREDS_LOG_LOADED_SUCCESS.format(count=len(self.centers)))
        return True

    def get_all_centers(self) -> List[CenterCredentials]:
        """Obtiene la lista de todos los centros.

        Returns:
            Lista de todos los objetos CenterCredentials
        """
        Logger.debug(t.CREDS_LOG_RETURNING_ALL.format(count=len(self.centers)))
        return self.centers.copy()

    def get_center_by_code(self, code: str) -> Optional[CenterCredentials]:
        """Obtiene las credenciales del centro por código.

        Realiza coincidencia exacta insensible a mayúsculas en el código del centro.

        Args:
            code: Código del centro a buscar

        Returns:
            Objeto CenterCredentials si se encuentra, None en caso contrario
        """
        Logger.debug(t.CREDS_LOG_SEARCH_CODE.format(code=code))

        code_lower = code.lower()
        for center in self.centers:
            if center.center_code.lower() == code_lower:
                Logger.debug(t.CREDS_LOG_FOUND_CENTER.format(name=center.center_name))
                return center

        Logger.debug(t.CREDS_LOG_CODE_NOT_FOUND.format(code=code))
        return None

    def get_center_by_name(self, name: str) -> Optional[CenterCredentials]:
        """Obtiene las credenciales del centro por nombre.

        Realiza coincidencia exacta insensible a mayúsculas en el nombre del centro.

        Args:
            name: Nombre del centro a buscar

        Returns:
            Objeto CenterCredentials si se encuentra, None en caso contrario
        """
        Logger.debug(t.CREDS_LOG_SEARCH_NAME.format(name=name))

        name_lower = name.lower()
        for center in self.centers:
            if center.center_name.lower() == name_lower:
                Logger.debug(t.CREDS_LOG_FOUND_CENTER.format(name=center.center_code))
                return center

        Logger.debug(t.CREDS_LOG_NAME_NOT_FOUND.format(name=name))
        return None

    def search_centers(self, query: str) -> List[CenterCredentials]:
        """Busca centros por código o nombre (insensible a mayúsculas).

        Realiza coincidencia parcial insensible a mayúsculas contra el
        código y nombre del centro.

        Args:
            query: Cadena de consulta de búsqueda

        Returns:
            Lista de objetos CenterCredentials que coinciden
        """
        Logger.debug(t.CREDS_LOG_SEARCHING.format(query=query))

        if not query:
            Logger.debug(t.CREDS_LOG_EMPTY_QUERY)
            return self.get_all_centers()

        results = [center for center in self.centers if center.matches_query(query)]

        Logger.debug(t.CREDS_LOG_FOUND_MATCHING.format(count=len(results)))
        return results

    def _parse_center_entry(self, entry: dict) -> CenterCredentials:
        """Parsea una entrada de centro desde JSON.

        Espera formato: {"Codi": "...", "Centre": "...", "Usuari": "...", "Contrasenya": "..."}

        Args:
            entry: Diccionario conteniendo datos del centro

        Returns:
            Objeto CenterCredentials

        Raises:
            KeyError: Si faltan campos requeridos
            TypeError: Si la entrada no es un diccionario
        """
        if not isinstance(entry, dict):
            raise TypeError(t.CREDS_ERROR_NOT_DICT)

        required_fields = ["Codi", "Centre", "Usuari", "Contrasenya"]
        for field in required_fields:
            if field not in entry:
                raise KeyError(t.CREDS_ERROR_MISSING_FIELD.format(field=field))

        return CenterCredentials(
            center_code=str(entry["Codi"]).strip(),
            center_name=str(entry["Centre"]).strip(),
            username=str(entry["Usuari"]).strip(),
            password=str(entry["Contrasenya"]).strip(),
        )
