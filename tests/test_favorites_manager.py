"""Tests unitarios para FavoritesManager.

Este módulo contiene tests para validar el comportamiento del
FavoritesManager, incluyendo carga, guardado, añadido, eliminación
y gestión de favoritos.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from wifi_connector.data.favorites_manager import FavoritesManager
from wifi_connector.data.credentials_manager import CenterCredentials, CredentialsManager


@pytest.fixture
def temp_favorites_path(tmp_path):
    """Proporciona un path temporal para fav.json."""
    return tmp_path / "fav.json"


@pytest.fixture
def mock_credentials_manager():
    """Proporciona un CredentialsManager mockeado con centros de prueba."""
    manager = MagicMock(spec=CredentialsManager)
    manager.get_all_centers.return_value = [
        CenterCredentials("08000001", "Centre 1", "user1", "pass1"),
        CenterCredentials("08000002", "Centre 2", "user2", "pass2"),
        CenterCredentials("08000003", "Centre 3", "user3", "pass3"),
    ]
    return manager


@pytest.fixture
def favorites_manager(temp_favorites_path, mock_credentials_manager):
    """Proporciona una instancia de FavoritesManager con path temporal."""
    return FavoritesManager(temp_favorites_path, mock_credentials_manager)


class TestFavoritesManager:
    """Tests para la clase FavoritesManager."""

    def test_load_favorites_with_valid_file(self, favorites_manager, temp_favorites_path):
        """Test que load_favorites() carga correctamente un archivo JSON válido."""
        # Arrange: crear archivo JSON válido
        valid_data = [
            {"center_code": "08000001", "center_name": "Centre 1", "username": "user1", "password": "pass1"},
            {"center_code": "08000002", "center_name": "Centre 2", "username": "user2", "password": "pass2"},
        ]
        temp_favorites_path.write_text(json.dumps(valid_data, indent=2), encoding="utf-8")

        # Act
        result = favorites_manager.load_favorites()

        # Assert
        assert result is True
        assert len(favorites_manager.get_favorites()) == 2
        assert favorites_manager.is_favorite("08000001")
        assert favorites_manager.is_favorite("08000002")

    def test_load_favorites_with_missing_file(self, favorites_manager, temp_favorites_path):
        """Test que load_favorites() devuelve False cuando el archivo no existe."""
        # Arrange: asegurar que el archivo no existe
        if temp_favorites_path.exists():
            temp_favorites_path.unlink()

        # Act
        result = favorites_manager.load_favorites()

        # Assert
        assert result is False
        assert len(favorites_manager.get_favorites()) == 0

    def test_load_favorites_with_corrupted_json(self, favorites_manager, temp_favorites_path):
        """Test que load_favorites() maneja JSON corrupto sin crashear."""
        # Arrange: crear archivo JSON corrupto
        temp_favorites_path.write_text("{corrupted json[", encoding="utf-8")

        # Act
        result = favorites_manager.load_favorites()

        # Assert
        assert result is False
        assert len(favorites_manager.get_favorites()) == 0

    def test_load_favorites_auto_cleanup_removes_obsoletes(self, favorites_manager, temp_favorites_path):
        """Test que load_favorites() elimina automáticamente centros obsoletos."""
        # Arrange: crear archivo con centro obsoleto
        data_with_obsolete = [
            {"center_code": "08000001", "center_name": "Centre 1", "username": "user1", "password": "pass1"},
            {"center_code": "99999999", "center_name": "Obsolete", "username": "userX", "password": "passX"},
        ]
        temp_favorites_path.write_text(json.dumps(data_with_obsolete, indent=2), encoding="utf-8")

        # Act
        result = favorites_manager.load_favorites()

        # Assert
        assert result is True
        assert len(favorites_manager.get_favorites()) == 1
        assert favorites_manager.is_favorite("08000001")
        assert not favorites_manager.is_favorite("99999999")
        
        # Verificar que se guardó el archivo limpio
        reloaded_data = json.loads(temp_favorites_path.read_text(encoding="utf-8"))
        assert len(reloaded_data) == 1
        assert reloaded_data[0]["center_code"] == "08000001"

    def test_add_favorite_with_valid_center(self, favorites_manager):
        """Test que add_favorite() añade un centro válido."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")

        # Act
        favorites_manager.add_favorite(center)

        # Assert
        assert favorites_manager.is_favorite("08000001")
        assert len(favorites_manager.get_favorites()) == 1

    def test_add_favorite_persists_to_file(self, favorites_manager, temp_favorites_path):
        """Test que add_favorite() persiste inmediatamente en disco."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")

        # Act
        favorites_manager.add_favorite(center)

        # Assert
        assert temp_favorites_path.exists()
        data = json.loads(temp_favorites_path.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["center_code"] == "08000001"

    def test_add_favorite_with_duplicate_is_idempotent(self, favorites_manager):
        """Test que add_favorite() con centro duplicado no genera error."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")
        favorites_manager.add_favorite(center)

        # Act: añadir el mismo centro de nuevo
        favorites_manager.add_favorite(center)

        # Assert: solo debe haber uno
        assert len(favorites_manager.get_favorites()) == 1
        assert favorites_manager.is_favorite("08000001")

    def test_remove_favorite_with_existing_center(self, favorites_manager):
        """Test que remove_favorite() elimina un centro existente."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")
        favorites_manager.add_favorite(center)
        assert favorites_manager.is_favorite("08000001")

        # Act
        favorites_manager.remove_favorite("08000001")

        # Assert
        assert not favorites_manager.is_favorite("08000001")
        assert len(favorites_manager.get_favorites()) == 0

    def test_remove_favorite_persists_to_file(self, favorites_manager, temp_favorites_path):
        """Test que remove_favorite() persiste inmediatamente en disco."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")
        favorites_manager.add_favorite(center)

        # Act
        favorites_manager.remove_favorite("08000001")

        # Assert
        data = json.loads(temp_favorites_path.read_text(encoding="utf-8"))
        assert len(data) == 0

    def test_remove_favorite_with_non_existing_center_is_idempotent(self, favorites_manager):
        """Test que remove_favorite() con centro no existente no genera error."""
        # Act: eliminar centro que no existe
        favorites_manager.remove_favorite("99999999")

        # Assert: no debe crashear
        assert not favorites_manager.is_favorite("99999999")
        assert len(favorites_manager.get_favorites()) == 0

    def test_is_favorite_returns_true_for_favorited_center(self, favorites_manager):
        """Test que is_favorite() devuelve True para centro favoritado."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")
        favorites_manager.add_favorite(center)

        # Act & Assert
        assert favorites_manager.is_favorite("08000001") is True

    def test_is_favorite_returns_false_for_non_favorited_center(self, favorites_manager):
        """Test que is_favorite() devuelve False para centro no favoritado."""
        # Act & Assert
        assert favorites_manager.is_favorite("99999999") is False

    def test_get_favorites_returns_copy(self, favorites_manager):
        """Test que get_favorites() devuelve una copia de la lista."""
        # Arrange
        center = CenterCredentials("08000001", "Centre 1", "user1", "pass1")
        favorites_manager.add_favorite(center)

        # Act
        favorites_list = favorites_manager.get_favorites()
        favorites_list.clear()  # Modificar la copia

        # Assert: la lista interna no debe haberse modificado
        assert len(favorites_manager.get_favorites()) == 1
        assert favorites_manager.is_favorite("08000001")
