"""Tests unitarios para las clases CredentialsManager y CenterCredentials."""

import json
import pytest
from pathlib import Path
from wifi_connector.data.credentials_manager import (
    CenterCredentials,
    CredentialsManager,
)
from wifi_connector.core.exceptions import CredentialsFileError, JSONParseError


class TestCenterCredentials:
    """Tests para la dataclass CenterCredentials."""

    def test_center_credentials_creation(self):
        """Verifica la creación de un objeto CenterCredentials."""
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.center_code == "08012345"
        assert center.center_name == "Institut Example"
        assert center.username == "user@testgencat.cat"
        assert center.password == "pass123"

    def test_matches_query_with_code_match(self):
        """Verifica que matches_query devuelve True cuando la consulta coincide con el código."""
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.matches_query("08012345") is True
        assert center.matches_query("0801") is True
        assert center.matches_query("2345") is True

    def test_matches_query_with_name_match(self):
        """Verifica que matches_query devuelve True cuando la consulta coincide con el nombre."""
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.matches_query("Institut") is True
        assert center.matches_query("Example") is True
        assert center.matches_query("Institut Example") is True

    def test_matches_query_case_insensitive(self):
        """Verifica que matches_query no distingue mayúsculas/minúsculas."""
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.matches_query("INSTITUT") is True
        assert center.matches_query("example") is True
        assert center.matches_query("InStItUt") is True

    def test_matches_query_no_match(self):
        """Verifica que matches_query devuelve False cuando no hay coincidencia."""
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.matches_query("99999") is False
        assert center.matches_query("Escola") is False
        assert center.matches_query("Barcelona") is False


class TestCredentialsManagerInit:
    """Tests para la inicialización de CredentialsManager."""

    def test_init_with_default_path(self):
        """Verifica la inicialización con ruta por defecto."""
        manager = CredentialsManager()

        assert manager.json_path.endswith("Json\\Wifi.json")
        assert manager.centers == []

    def test_init_with_custom_path(self):
        """Verifica la inicialización con ruta personalizada."""
        manager = CredentialsManager(json_path="custom\\path.json")

        assert manager.json_path == "custom\\path.json"
        assert manager.centers == []


class TestCredentialsManagerLoadCredentials:
    """Tests para el método CredentialsManager.load_credentials()."""

    def test_load_credentials_from_valid_json(self, tmp_path):
        """Verifica la carga de credenciales desde un archivo JSON válido."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        result = manager.load_credentials()

        assert result is True
        assert len(manager.centers) == 2
        assert manager.centers[0].center_code == "08012345"
        assert manager.centers[0].center_name == "Institut Example"
        assert manager.centers[1].center_code == "08023456"
        assert manager.centers[1].center_name == "Escola Test"

    def test_load_credentials_raises_error_for_missing_file(self):
        """Verifica que load_credentials lanza CredentialsFileError para archivo inexistente."""
        manager = CredentialsManager(json_path="nonexistent.json")

        with pytest.raises(CredentialsFileError):
            manager.load_credentials()

    def test_load_credentials_raises_error_for_malformed_json(self, tmp_path):
        """Verifica que load_credentials lanza JSONParseError para JSON malformado."""
        json_file = tmp_path / "Wifi.json"
        json_file.write_text("{ invalid json }", encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))

        with pytest.raises(JSONParseError):
            manager.load_credentials()

    def test_load_credentials_raises_error_for_non_array_json(self, tmp_path):
        """Verifica que load_credentials lanza JSONParseError cuando el JSON no es un array."""
        json_file = tmp_path / "Wifi.json"
        json_data = {"centers": []}
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))

        with pytest.raises(JSONParseError):
            manager.load_credentials()

    def test_load_credentials_skips_invalid_entries(self, tmp_path):
        """Verifica que load_credentials salta entradas inválidas."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {"Codi": "08023456"},
            {
                "Codi": "08034567",
                "Centre": "Escola Valid",
                "Usuari": "W08034567",
                "Contrasenya": "pass789",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        result = manager.load_credentials()

        assert result is True
        assert len(manager.centers) == 2
        assert manager.centers[0].center_code == "08012345"
        assert manager.centers[1].center_code == "08034567"


class TestCredentialsManagerGetAllCenters:
    """Tests para el método CredentialsManager.get_all_centers()."""

    def test_get_all_centers_returns_empty_list_when_no_centers_loaded(self):
        """Verifica que get_all_centers devuelve lista vacía sin centros cargados."""
        manager = CredentialsManager()

        centers = manager.get_all_centers()

        assert centers == []

    def test_get_all_centers_returns_all_loaded_centers(self, tmp_path):
        """Verifica que get_all_centers devuelve todos los centros cargados."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        centers = manager.get_all_centers()

        assert len(centers) == 2
        assert centers[0].center_code == "08012345"
        assert centers[1].center_code == "08023456"

    def test_get_all_centers_returns_copy(self, tmp_path):
        """Verifica que get_all_centers devuelve una copia, no la lista original."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        centers = manager.get_all_centers()
        centers.clear()

        assert len(manager.centers) == 1


class TestCredentialsManagerGetCenterByCode:
    """Tests para el método CredentialsManager.get_center_by_code()."""

    def test_get_center_by_code_finds_exact_match(self, tmp_path):
        """Verifica que get_center_by_code encuentra coincidencia exacta."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_code("08012345")

        assert center is not None
        assert center.center_code == "08012345"
        assert center.center_name == "Institut Example"

    def test_get_center_by_code_case_insensitive(self, tmp_path):
        """Verifica que get_center_by_code no distingue mayúsculas/minúsculas."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "ABC123",
                "Centre": "Institut Example",
                "Usuari": "WABC123",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_code("abc123")

        assert center is not None
        assert center.center_code == "ABC123"

    def test_get_center_by_code_returns_none_for_invalid_code(self, tmp_path):
        """Verifica que get_center_by_code devuelve None cuando no encuentra el código."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_code("99999999")

        assert center is None


class TestCredentialsManagerGetCenterByName:
    """Tests para el método CredentialsManager.get_center_by_name()."""

    def test_get_center_by_name_finds_exact_match(self, tmp_path):
        """Verifica que get_center_by_name encuentra coincidencia exacta."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_name("Institut Example")

        assert center is not None
        assert center.center_code == "08012345"
        assert center.center_name == "Institut Example"

    def test_get_center_by_name_case_insensitive(self, tmp_path):
        """Verifica que get_center_by_name no distingue mayúsculas/minúsculas."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_name("institut example")

        assert center is not None
        assert center.center_name == "Institut Example"

    def test_get_center_by_name_returns_none_for_invalid_name(self, tmp_path):
        """Verifica que get_center_by_name devuelve None cuando no encuentra el nombre."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        center = manager.get_center_by_name("Nonexistent School")

        assert center is None


class TestCredentialsManagerSearchCenters:
    """Tests para el método CredentialsManager.search_centers()."""

    def test_search_centers_with_code_partial_match(self, tmp_path):
        """Verifica que search_centers encuentra centros con coincidencia parcial de código."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
            {
                "Codi": "17012345",
                "Centre": "Institut Girona",
                "Usuari": "W17012345",
                "Contrasenya": "pass789",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        results = manager.search_centers("0801")

        assert len(results) == 1
        assert results[0].center_code == "08012345"

    def test_search_centers_with_name_partial_match(self, tmp_path):
        """Verifica que search_centers encuentra centros con coincidencia parcial de nombre."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
            {
                "Codi": "17012345",
                "Centre": "Institut Girona",
                "Usuari": "W17012345",
                "Contrasenya": "pass789",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        results = manager.search_centers("Institut")

        assert len(results) == 2
        assert results[0].center_name == "Institut Example"
        assert results[1].center_name == "Institut Girona"

    def test_search_centers_case_insensitive(self, tmp_path):
        """Verifica que search_centers no distingue mayúsculas/minúsculas."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        results = manager.search_centers("INSTITUT")

        assert len(results) == 1
        assert results[0].center_name == "Institut Example"

    def test_search_centers_returns_empty_list_for_no_match(self, tmp_path):
        """Verifica que search_centers devuelve lista vacía cuando no hay coincidencias."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            }
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        results = manager.search_centers("Nonexistent")

        assert results == []

    def test_search_centers_returns_all_for_empty_query(self, tmp_path):
        """Verifica que search_centers devuelve todos los centros con consulta vacía."""
        json_file = tmp_path / "Wifi.json"
        json_data = [
            {
                "Codi": "08012345",
                "Centre": "Institut Example",
                "Usuari": "W08012345",
                "Contrasenya": "pass123",
            },
            {
                "Codi": "08023456",
                "Centre": "Escola Test",
                "Usuari": "W08023456",
                "Contrasenya": "pass456",
            },
        ]
        json_file.write_text(json.dumps(json_data), encoding="utf-8")

        manager = CredentialsManager(json_path=str(json_file))
        manager.load_credentials()

        results = manager.search_centers("")

        assert len(results) == 2
