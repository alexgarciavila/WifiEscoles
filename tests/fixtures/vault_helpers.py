"""Helpers para construir vaults en formato VLTB para tests."""

import json
import secrets
from typing import Any, Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from wifi_connector.data import vault_manager as vm


def build_encrypted_vault_bytes(
    payload: Dict[str, Any],
    password: str,
    *,
    salt: bytes | None = None,
    nonce: bytes | None = None,
    n: int = 2**15,
    r: int = 8,
    p: int = 1,
) -> bytes:
    """Construye un vault VLTB cifrado desde un payload JSON.

    Args:
        payload: Diccionario con estructura {metadata: {}, centers: []}
        password: Contraseña para cifrar
        salt: Salt opcional (genera aleatorio si None)
        nonce: Nonce opcional (genera aleatorio si None)
        n: Parámetro N de Scrypt (default: 32768)
        r: Parámetro r de Scrypt (default: 8)
        p: Parámetro p de Scrypt (default: 1)

    Returns:
        Bytes del vault cifrado en formato VLTB
    """
    plaintext = json.dumps(payload).encode("utf-8")
    return build_encrypted_vault_bytes_from_plaintext(
        plaintext, password, salt=salt, nonce=nonce, n=n, r=r, p=p
    )


def build_encrypted_vault_bytes_from_plaintext(
    plaintext: bytes,
    password: str,
    *,
    salt: bytes | None = None,
    nonce: bytes | None = None,
    n: int = 2**15,
    r: int = 8,
    p: int = 1,
) -> bytes:
    """Construye un vault VLTB cifrado desde plaintext.

    Args:
        plaintext: Bytes del JSON a cifrar
        password: Contraseña para cifrar
        salt: Salt opcional (genera aleatorio si None)
        nonce: Nonce opcional (genera aleatorio si None)
        n: Parámetro N de Scrypt (default: 32768)
        r: Parámetro r de Scrypt (default: 8)
        p: Parámetro p de Scrypt (default: 1)

    Returns:
        Bytes del vault cifrado en formato VLTB
    """
    # Generar salt y nonce si no se proporcionan
    if salt is None:
        salt = secrets.token_bytes(vm.SALT_LENGTH)
    if nonce is None:
        nonce = secrets.token_bytes(vm.NONCE_LENGTH)

    # Calcular longitud del ciphertext (plaintext + tag)
    ct_len = len(plaintext) + vm.TAG_LENGTH

    # Construir header VLTB
    header = vm.VLTB_HEADER_STRUCT.pack(
        vm.MAGIC,  # magic: b"VLTB"
        1,  # version: 1
        vm.KDF_SCRYPT,  # kdf_type: 1
        vm.AEAD_AESGCM,  # aead_type: 1
        0,  # reserved: 0
        n,  # scrypt N
        r,  # scrypt r
        p,  # scrypt p
        vm.SALT_LENGTH,  # salt_len
        vm.NONCE_LENGTH,  # nonce_len
        ct_len,  # ciphertext_len
    )

    # Derivar clave con Scrypt
    kdf = Scrypt(
        salt=salt,
        length=vm.KEY_LENGTH,
        n=n,
        r=r,
        p=p,
    )
    key = kdf.derive(password.encode("utf-8"))

    # Cifrar con AES-GCM usando header como AAD
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, header)

    # Construir blob final: header + salt + nonce + ciphertext
    return header + salt + nonce + ciphertext


def write_vault_file(tmp_path, payload: Dict[str, Any], password: str) -> Any:
    """Escribe un vault.bin en formato VLTB y retorna el path.

    Args:
        tmp_path: Path del directorio temporal
        payload: Diccionario con estructura {metadata: {}, centers: []}
        password: Contraseña para cifrar

    Returns:
        Path del archivo vault.bin creado
    """
    vault_path = tmp_path / "vault.bin"
    vault_path.write_bytes(build_encrypted_vault_bytes(payload, password))
    return vault_path
