"""Módulo de gestión de favoritos para WiFi Connector.

Este módulo proporciona la clase FavoritesManager para gestionar centros educativos
marcados como favoritos, incluyendo persistencia en Json/fav.json y validación
contra el catálogo completo de centros.
"""

import json
from pathlib import Path
from typing import List

from wifi_connector.data.credentials_manager import CenterCredentials, CredentialsManager
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


class FavoritesManager:
    """Gestiona la persistencia y estado de centros favoritos.

    Esta clase maneja la carga, guardado, adición y eliminación de centros favoritos,
    asegurando que los favoritos se validen contra wifi.json y se persistan
    automáticamente en fav.json.

    Attributes:
        favorites_path: Path al archivo fav.json
        credentials_manager: Referencia a CredentialsManager para validación
        _favorites: Lista interna de centros favoritos
    """

    def __init__(
        self,
        favorites_path: Path,
        credentials_manager: CredentialsManager
    ) -> None:
        """Inicializa el gestor de favoritos.

        Args:
            favorites_path: Path al archivo fav.json
            credentials_manager: Referencia a CredentialsManager para validación
        """
        self.favorites_path = favorites_path
        self.credentials_manager = credentials_manager
        self._favorites: List[CenterCredentials] = []

    def load_favorites(self) -> bool:
        """Carga y valida favoritos desde fav.json.

        Lee el archivo fav.json, valida que cada centro existe en wifi.json,
        y elimina automáticamente favoritos obsoletos (auto-cleanup).

        Returns:
            True si la carga fue exitosa (incluso si el archivo está vacío),
            False si el archivo no existe o el JSON es inválido.

        Side Effects:
            - Puede escribir a fav.json si se detectan favoritos obsoletos
            - Actualiza self._favorites con la lista de favoritos válidos
            - Registra warnings para favoritos obsoletos o errores de parsing
        """
        try:
            if not self.favorites_path.exists():
                Logger.info(t.FAV_LOG_FILE_NOT_EXISTS.format(path=self.favorites_path))
                self._favorites = []
                return False

            with open(self.favorites_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                Logger.warning(t.FAV_LOG_INVALID_FORMAT)
                self._favorites = []
                return False

            # Obtener códigos válidos de wifi.json para validación
            valid_codes = {c.center_code for c in self.credentials_manager.get_all_centers()}

            # Filtrar favoritos obsoletos
            valid_favorites = []
            for item in data:
                try:
                    center = CenterCredentials(
                        center_code=item['center_code'],
                        center_name=item['center_name'],
                        username=item['username'],
                        password=item['password']
                    )
                    if center.center_code in valid_codes:
                        valid_favorites.append(center)
                    else:
                        Logger.debug(t.FAV_LOG_OBSOLETE_REMOVED.format(code=center.center_code, name=center.center_name))
                except (KeyError, TypeError) as e:
                    Logger.warning(t.FAV_LOG_INVALID_ENTRY.format(error=e))
                    continue

            # Si se removieron favoritos obsoletos, volver a guardar archivo limpio
            if len(valid_favorites) < len(data):
                removed_count = len(data) - len(valid_favorites)
                Logger.warning(t.FAV_LOG_AUTO_CLEANUP.format(count=removed_count))
                self._save_favorites(valid_favorites)

            self._favorites = valid_favorites
            Logger.info(t.FAV_LOG_LOADED.format(count=len(self._favorites)))
            return True

        except json.JSONDecodeError as e:
            Logger.warning(t.FAV_LOG_PARSE_ERROR.format(error=e))
            self._favorites = []
            return False
        except Exception as e:
            Logger.error(t.FAV_LOG_UNEXPECTED_ERROR.format(error=e))
            self._favorites = []
            return False

    def add_favorite(self, center: CenterCredentials) -> None:
        """Añade un centro a favoritos y persiste inmediatamente.

        Args:
            center: CenterCredentials a añadir a favoritos

        Side Effects:
            - Actualiza self._favorites
            - Escribe a favoritos.json
            - Registra operación en logs
        """
        # Verificar que el centro existe en wifi.json
        valid_codes = {c.center_code for c in self.credentials_manager.get_all_centers()}
        if center.center_code not in valid_codes:
            Logger.warning(t.FAV_LOG_INVALID_CENTER.format(code=center.center_code))
            return

        # Verificar si ya es favorito
        if self.is_favorite(center.center_code):
            Logger.debug(t.FAV_LOG_ALREADY_FAVORITE.format(code=center.center_code))
            return

        # Añadir a favoritos
        self._favorites.append(center)
        Logger.info(t.FAV_LOG_ADDED.format(code=center.center_code, name=center.center_name))

        # Persistir inmediatamente
        try:
            self._save_favorites(self._favorites)
        except Exception as e:
            Logger.error(t.FAV_LOG_ERROR_SAVING_ADD.format(error=e))
            # Mantener estado en memoria incluso si escritura falla
            pass

    def remove_favorite(self, center_code: str) -> None:
        """Elimina un centro de favoritos y persiste inmediatamente.

        Args:
            center_code: Código único del centro a eliminar

        Side Effects:
            - Actualiza self._favorites
            - Escribe a favoritos.json
            - Registra operación en logs
        """
        # Buscar y eliminar favorito
        original_count = len(self._favorites)
        self._favorites = [f for f in self._favorites if f.center_code != center_code]

        if len(self._favorites) == original_count:
            # No se encontró el favorito
            Logger.debug(t.FAV_LOG_NOT_FAVORITE.format(code=center_code))
            return

        Logger.info(t.FAV_LOG_REMOVED.format(code=center_code))

        try:
            self._save_favorites(self._favorites)
        except Exception as e:
            Logger.error(t.FAV_LOG_ERROR_SAVING_REMOVE.format(error=e))
            # Mantener estado en memoria incluso si escritura falla
            pass

    def is_favorite(self, center_code: str) -> bool:
        """Verifica si un centro está marcado como favorito.

        Args:
            center_code: Código único del centro a verificar

        Returns:
            True si el centro es favorito, False en caso contrario
        """
        return any(f.center_code == center_code for f in self._favorites)

    def get_favorites(self) -> List[CenterCredentials]:
        """Obtiene todos los centros favoritos.

        Returns:
            Lista de CenterCredentials favoritos (copia, no referencia)
        """
        return self._favorites.copy()

    def _save_favorites(self, favorites: List[CenterCredentials]) -> None:
        """Persiste favoritos a disco usando escritura atómica.

        Usa escritura atómica (temp file + rename) para prevenir corrupción
        si la aplicación crashea durante la escritura.

        Args:
            favorites: Lista de CenterCredentials a guardar

        Raises:
            IOError: Si la escritura falla
        """
        try:
            Logger.debug(t.FAV_LOG_ATTEMPTING_SAVE.format(count=len(favorites), path=self.favorites_path))
            
            # Crear directorio Json/ si no existe
            self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
            Logger.debug(t.FAV_LOG_DIR_CONFIRMED.format(path=self.favorites_path.parent))

            # Serializar a JSON
            data = [
                {
                    'center_code': f.center_code,
                    'center_name': f.center_name,
                    'username': f.username,
                    'password': f.password
                }
                for f in favorites
            ]

            # Escritura atómica: temp file + rename
            temp_path = self.favorites_path.with_suffix('.tmp')
            Logger.debug(t.FAV_LOG_WRITING_TEMP.format(path=temp_path))
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            Logger.debug(t.FAV_LOG_RENAMING.format(temp=temp_path, final=self.favorites_path))
            temp_path.replace(self.favorites_path)

            Logger.info(t.FAV_LOG_SAVED.format(path=self.favorites_path, count=len(favorites)))

        except Exception as e:
            Logger.error(t.FAV_LOG_ERROR_SAVING.format(path=self.favorites_path, error=e), exc_info=True)
            raise IOError(t.FAV_ERROR_SAVE_FAILED.format(error=e)) from e
