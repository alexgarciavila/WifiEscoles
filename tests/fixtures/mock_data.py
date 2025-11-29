"""
Fixtures de test y datos mock para tests de WiFi Connector.

Este módulo proporciona fixtures reutilizables para testear todos
los componentes del sistema WiFi Connector.
"""

import numpy as np
import pytest
from wifi_connector.core.config import Config
from wifi_connector.data.credentials_manager import CenterCredentials


@pytest.fixture
def mock_config():
    """Proporciona configuración de test con valores seguros por defecto."""
    return Config(
        pause_duration=0.1,
        credential_dialog_wait_time=1,
        debug_mode=True
    )


@pytest.fixture
def mock_netsh_output():
    """Proporciona salida de ejemplo de netsh wlan show networks."""
    return """
Interface name : Wi-Fi
There are 4 networks currently visible.

SSID 1 : gencat_ENS_EDU
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : CCMP

SSID 2 : OtherNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP

SSID 3 : gencat_PORTAL
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None

SSID 4 : TestNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
"""


@pytest.fixture
def mock_netsh_output_empty():
    """Proporciona salida de netsh sin redes."""
    return """
Interface name : Wi-Fi
There are 0 networks currently visible.
"""


@pytest.fixture
def mock_windows_version_10():
    """Proporciona cadena de versión de Windows 10."""
    return "10.0.19044"


@pytest.fixture
def mock_windows_version_11():
    """Proporciona cadena de versión de Windows 11."""
    return "10.0.22000"


@pytest.fixture
def mock_credentials_json():
    """Proporciona estructura de datos JSON de credenciales de ejemplo."""
    return {
        "centers": [
            {
                "center_code": "08012345",
                "center_name": "Institut Example Barcelona",
                "username": "user@gencat.cat",
                "password": "password123"
            },
            {
                "center_code": "08023456",
                "center_name": "Escola Example Girona",
                "username": "user2@gencat.cat",
                "password": "password456"
            },
            {
                "center_code": "17034567",
                "center_name": "Col·legi Test Lleida",
                "username": "user3@gencat.cat",
                "password": "password789"
            },
            {
                "center_code": "25045678",
                "center_name": "Institut Prova Tarragona",
                "username": "user4@gencat.cat",
                "password": "password000"
            }
        ]
    }


@pytest.fixture
def mock_credentials_json_invalid():
    """Proporciona JSON de credenciales inválido (campos requeridos faltantes)."""
    return {
        "centers": [
            {
                "center_code": "08012345",
                "center_name": "Institut Example"
            }
        ]
    }


@pytest.fixture
def mock_credentials_json_malformed():
    """Proporciona cadena JSON malformada."""
    return '{"centers": [{"center_code": "08012345", "center_name": "Test"'


@pytest.fixture
def mock_center_credentials():
    """Proporciona objeto CenterCredentials de ejemplo."""
    return CenterCredentials(
        center_code="08012345",
        center_name="Institut Example Barcelona",
        username="user@gencat.cat",
        password="password123"
    )


@pytest.fixture
def mock_center_credentials_list():
    """Proporciona lista de objetos CenterCredentials."""
    return [
        CenterCredentials(
            center_code="08012345",
            center_name="Institut Example Barcelona",
            username="user@gencat.cat",
            password="password123"
        ),
        CenterCredentials(
            center_code="08023456",
            center_name="Escola Example Girona",
            username="user2@gencat.cat",
            password="password456"
        ),
        CenterCredentials(
            center_code="17034567",
            center_name="Col·legi Test Lleida",
            username="user3@gencat.cat",
            password="password789"
        )
    ]


@pytest.fixture
def sample_wifi_json_path(tmp_path):
    """Crea un archivo wifi.json temporal de ejemplo para tests."""
    import json
    
    json_data = {
        "centers": [
            {
                "center_code": "08012345",
                "center_name": "Institut Example Barcelona",
                "username": "user@gencat.cat",
                "password": "password123"
            },
            {
                "center_code": "08023456",
                "center_name": "Escola Example Girona",
                "username": "user2@gencat.cat",
                "password": "password456"
            }
        ]
    }
    
    json_file = tmp_path / "wifi.json"
    json_file.write_text(json.dumps(json_data, indent=2))
    return str(json_file)
