"""Tests for VaultManager."""

import pytest

from wifi_connector.core.exceptions import VaultDecryptionError, VaultFormatError
from wifi_connector.data.vault_manager import (
    MAGIC,
    NONCE_LENGTH,
    SALT_LENGTH,
    VLTB_HEADER_SIZE,
    VLTB_HEADER_STRUCT,
    VaultManager,
)
from tests.fixtures.vault_helpers import (
    build_encrypted_vault_bytes_from_plaintext,
    write_vault_file,
)


def test_load_vault_success_with_metadata_and_centers(tmp_path):
    payload = {
        "metadata": {"version": "1.0", "source": "test"},
        "centers": [
            {
                "Codi": "08000001",
                "Centre": "Centre 1",
                "Usuari": "u1",
                "Contrasenya": "p1",
            },
            {
                "Codi": "08000002",
                "Centre": "Centre 2",
                "Usuari": "u2",
                "Contrasenya": "p2",
            },
        ],
    }
    vault_path = write_vault_file(tmp_path, payload, "secret")

    manager = VaultManager(str(vault_path))
    result = manager.load_vault("secret")

    assert result.metadata == payload["metadata"]
    assert result.centers == payload["centers"]


def test_load_vault_invalid_password(tmp_path):
    payload = {"metadata": {}, "centers": []}
    vault_path = write_vault_file(tmp_path, payload, "secret")

    manager = VaultManager(str(vault_path))

    with pytest.raises(VaultDecryptionError):
        manager.load_vault("wrong")


def test_load_vault_invalid_magic(tmp_path):
    """Test que rechaza vaults con magic header inválido."""
    # Crear un header falso con magic incorrecto (mínimo 32 bytes)
    invalid = b"BADM".ljust(
        VLTB_HEADER_SIZE + SALT_LENGTH + NONCE_LENGTH + 100, b"\x00"
    )
    vault_path = tmp_path / "vault.bin"
    vault_path.write_bytes(invalid)

    manager = VaultManager(str(vault_path))

    with pytest.raises(VaultFormatError):
        manager.load_vault("secret")


def test_load_vault_invalid_format_too_short(tmp_path):
    """Test que rechaza vaults demasiado cortos (menos de 32 bytes)."""
    vault_path = tmp_path / "vault.bin"
    vault_path.write_bytes(b"short")  # Menos de VLTB_HEADER_SIZE

    manager = VaultManager(str(vault_path))

    with pytest.raises(VaultFormatError):
        manager.load_vault("secret")


def test_load_vault_invalid_json(tmp_path):
    encrypted = build_encrypted_vault_bytes_from_plaintext(b"not json", "secret")
    vault_path = tmp_path / "vault.bin"
    vault_path.write_bytes(encrypted)

    manager = VaultManager(str(vault_path))

    with pytest.raises(VaultFormatError):
        manager.load_vault("secret")
