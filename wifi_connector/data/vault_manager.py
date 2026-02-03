"""Gestión de vault cifrado para credenciales WiFi Connector.

Este módulo proporciona utilidades para descifrar el vault en memoria
y obtener la estructura de datos equivalente a wifi.json.
"""

from dataclasses import dataclass
import json
from pathlib import Path
import struct
from typing import Any, Dict, List

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from wifi_connector.core.exceptions import (
    VaultDecryptionError,
    VaultFileError,
    VaultFormatError,
)
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


# Constantes formato VLTB
MAGIC = b"VLTB"
VLTB_HEADER_STRUCT = struct.Struct(">4sBBBBIIIIII")
VLTB_HEADER_SIZE = 32

# Constantes criptográficas
KEY_LENGTH = 32
SALT_LENGTH = 16
NONCE_LENGTH = 12
TAG_LENGTH = 16

# Tipos de algoritmos VLTB
KDF_SCRYPT = 1
AEAD_AESGCM = 1


@dataclass
class VaultPayload:
    """Representa el contenido descifrado del vault."""

    metadata: Dict[str, Any]
    centers: List[Dict[str, Any]]


class VaultManager:
    """Gestor para cargar y descifrar el vault binario."""

    def __init__(self, vault_path: str) -> None:
        self.vault_path = Path(vault_path)
        Logger.debug(t.VAULT_LOG_INIT.format(path=self.vault_path))

    def load_vault(self, password: str) -> VaultPayload:
        """Carga y descifra el vault usando la contraseña proporcionada.

        Args:
            password: Contraseña del vault

        Returns:
            VaultPayload con metadatos y centros

        Raises:
            VaultFileError: Si el archivo de vault no existe o no se puede leer
            VaultDecryptionError: Si la contraseña es inválida o el vault no se puede descifrar
            VaultFormatError: Si el vault no tiene el formato esperado
        """
        if not self.vault_path.exists():
            raise VaultFileError(
                t.VAULT_ERROR_FILE_NOT_FOUND.format(path=self.vault_path)
            )

        try:
            encrypted = self.vault_path.read_bytes()
        except Exception as e:
            raise VaultFileError(
                t.VAULT_ERROR_FILE_READ.format(path=self.vault_path, error=e)
            ) from e

        payload = self._decrypt_payload(encrypted, password)
        Logger.info(t.VAULT_LOG_DECRYPTED)

        if isinstance(payload, dict):
            metadata = payload.get("metadata") or {}
            centers = payload.get("centers") or payload.get("centres")
            if centers is None:
                raise VaultFormatError(t.VAULT_ERROR_MISSING_CENTERS)
        elif isinstance(payload, list):
            metadata = {}
            centers = payload
        else:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_STRUCTURE)

        if not isinstance(metadata, dict):
            raise VaultFormatError(t.VAULT_ERROR_METADATA_INVALID)

        if not isinstance(centers, list):
            raise VaultFormatError(t.VAULT_ERROR_INVALID_STRUCTURE)

        Logger.info(t.VAULT_LOG_LOADED.format(count=len(centers)))
        return VaultPayload(metadata=metadata, centers=centers)

    def _decrypt_payload(self, encrypted: bytes, password: str) -> Any:
        """Descifra el payload en formato VLTB y devuelve el JSON decodificado.

        Args:
            encrypted: Bytes del archivo vault completo
            password: Contraseña del vault

        Returns:
            Diccionario parseado del JSON descifrado

        Raises:
            VaultFormatError: Si el formato del vault es inválido
            VaultDecryptionError: Si la contraseña es incorrecta
        """
        # Validar longitud mínima
        if len(encrypted) < VLTB_HEADER_SIZE:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_FORMAT)

        # Parsear header VLTB (32 bytes)
        header = encrypted[:VLTB_HEADER_SIZE]
        try:
            (
                magic,
                version,
                kdf_type,
                aead_type,
                reserved,
                n,
                r,
                p,
                salt_len,
                nonce_len,
                ct_len,
            ) = VLTB_HEADER_STRUCT.unpack(header)
        except struct.error as e:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_FORMAT) from e

        # Validar magic header
        if magic != MAGIC:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_MAGIC)

        # Validar longitud total esperada
        expected_len = VLTB_HEADER_SIZE + salt_len + nonce_len + ct_len
        if len(encrypted) != expected_len:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_FORMAT)

        # Extraer componentes del vault
        offset = VLTB_HEADER_SIZE
        salt = encrypted[offset : offset + salt_len]
        offset += salt_len
        nonce = encrypted[offset : offset + nonce_len]
        offset += nonce_len
        ciphertext = encrypted[offset : offset + ct_len]

        # Derivar clave con Scrypt
        key = self._derive_key(password, salt, n, r, p)

        # Desencriptar con AES-GCM usando header completo como AAD
        try:
            plaintext = AESGCM(key).decrypt(nonce, ciphertext, header)
        except InvalidTag as e:
            raise VaultDecryptionError(t.VAULT_ERROR_INVALID_PASSWORD) from e
        except Exception as e:
            raise VaultDecryptionError(
                t.VAULT_ERROR_DECRYPT_FAILED.format(error=e)
            ) from e

        # Parsear JSON
        try:
            return json.loads(plaintext.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise VaultFormatError(t.VAULT_ERROR_INVALID_JSON.format(error=e)) from e

    @staticmethod
    def _derive_key(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
        """Deriva la clave usando Scrypt (formato VLTB).

        Args:
            password: Contraseña del vault
            salt: Salt para el KDF
            n: Parámetro de coste CPU/memoria de Scrypt
            r: Parámetro de tamaño de bloque de Scrypt
            p: Parámetro de paralelización de Scrypt

        Returns:
            Clave derivada de 32 bytes
        """
        kdf = Scrypt(
            salt=salt,
            length=KEY_LENGTH,
            n=n,
            r=r,
            p=p,
        )
        return kdf.derive(password.encode("utf-8"))
