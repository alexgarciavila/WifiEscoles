"""Unit tests for CredentialsManager and CenterCredentials."""

from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest

from wifi_connector.core.exceptions import (
    CredentialsFileError,
    JSONParseError,
    VaultDecryptionError,
)
from wifi_connector.data.credentials_manager import (
    CenterCredentials,
    CredentialsManager,
)
from tests.fixtures.vault_helpers import write_vault_file


@pytest.fixture
def password():
    return "secret"


@pytest.fixture
def sample_entries():
    return [
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
            "Codi": "17034567",
            "Centre": "Institut Girona",
            "Usuari": "W17034567",
            "Contrasenya": "pass789",
        },
    ]


@pytest.fixture
def vault_payload(sample_entries):
    return {
        "metadata": {"version": "1.0", "source": "tests"},
        "centers": sample_entries,
    }


@pytest.fixture
def vault_file(tmp_path, vault_payload, password):
    return write_vault_file(tmp_path, vault_payload, password)


@pytest.fixture
def loaded_manager(vault_file, password):
    manager = CredentialsManager(vault_path=str(vault_file))
    manager.load_credentials(password)
    return manager


class TestCenterCredentials:
    def test_center_credentials_creation(self):
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

    def test_matches_query_case_insensitive(self):
        center = CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user@testgencat.cat",
            password="pass123",
        )

        assert center.matches_query("INSTITUT") is True
        assert center.matches_query("example") is True


class TestCredentialsManagerInit:
    def test_init_with_default_path(self):
        manager = CredentialsManager()

        assert Path(manager.vault_path).name == "vault.bin"
        assert manager.centers == []

    def test_init_with_custom_path(self, tmp_path):
        vault_path = tmp_path / "custom.bin"
        manager = CredentialsManager(vault_path=str(vault_path))

        assert manager.vault_path == str(vault_path)
        assert manager.centers == []


class TestCredentialsManagerLoadCredentials:
    def test_load_credentials_uses_vault_and_metadata(
        self, vault_file, vault_payload, password
    ):
        manager = CredentialsManager(vault_path=str(vault_file))

        result = manager.load_credentials(password)

        assert result is True
        assert manager.vault_metadata == vault_payload["metadata"]
        assert len(manager.centers) == len(vault_payload["centers"])
        assert manager.centers[0].center_code == "08012345"

    def test_load_credentials_raises_on_bad_vault(self, vault_file):
        manager = CredentialsManager(vault_path=str(vault_file))

        with pytest.raises(VaultDecryptionError):
            manager.load_credentials("wrong")


class TestCredentialsManagerQuerying:
    def test_get_center_by_code(self, loaded_manager):
        center = loaded_manager.get_center_by_code("08012345")

        assert center is not None
        assert center.center_name == "Institut Example"

    def test_get_center_by_name(self, loaded_manager):
        center = loaded_manager.get_center_by_name("Escola Test")

        assert center is not None
        assert center.center_code == "08023456"

    def test_search_centers(self, loaded_manager):
        results = loaded_manager.search_centers("Institut")

        assert len(results) == 2
        assert results[0].center_name == "Institut Example"
        assert results[1].center_name == "Institut Girona"

    def test_search_centers_empty_query_returns_all(self, loaded_manager):
        results = loaded_manager.search_centers("")

        assert results == loaded_manager.get_all_centers()

    def test_get_center_by_code_returns_none_for_missing(self, loaded_manager):
        assert loaded_manager.get_center_by_code("99999999") is None

    def test_get_center_by_name_returns_none_for_missing(self, loaded_manager):
        assert loaded_manager.get_center_by_name("Missing") is None


class TestCredentialsManagerParsing:
    def test_load_from_entries_raises_on_non_list(self, tmp_path):
        manager = CredentialsManager(vault_path=str(tmp_path / "vault.bin"))

        with pytest.raises(JSONParseError):
            manager._load_from_entries(cast(list, "invalid"))

    def test_load_from_entries_skips_invalid_entries(self, tmp_path):
        manager = CredentialsManager(vault_path=str(tmp_path / "vault.bin"))
        entries = [
            {
                "Codi": "08012345",
                "Centre": "Centre",
                "Usuari": "user",
                "Contrasenya": "pass",
            },
            "invalid",
        ]

        assert manager._load_from_entries(entries) is True
        assert len(manager.centers) == 1

    def test_parse_center_entry_requires_dict(self, tmp_path):
        manager = CredentialsManager(vault_path=str(tmp_path / "vault.bin"))

        with pytest.raises(TypeError):
            manager._parse_center_entry(cast(dict, "invalid"))

    def test_parse_center_entry_requires_fields(self, tmp_path):
        manager = CredentialsManager(vault_path=str(tmp_path / "vault.bin"))

        with pytest.raises(KeyError):
            manager._parse_center_entry({"Codi": "08012345"})


class TestCredentialsManagerVaultErrors:
    def test_load_credentials_wraps_unexpected_exception(self, tmp_path):
        manager = CredentialsManager(vault_path=str(tmp_path / "vault.bin"))

        with patch(
            "wifi_connector.data.credentials_manager.VaultManager"
        ) as mock_vault:
            mock_vault.return_value.load_vault.side_effect = Exception("boom")

            with pytest.raises(CredentialsFileError):
                manager.load_credentials("secret")
