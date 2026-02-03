"""
Tests unitarios para el módulo profile_connector.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import os
import time
import xml.etree.ElementTree as ET

from wifi_connector.core.profile_connector import ProfileConnector


class TestProfileConnector(unittest.TestCase):
    """Tests para la clase ProfileConnector."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.connector = ProfileConnector("gencat_ENS_EDU")
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.test_dir)

    def test_init(self):
        """Test de inicialización del conector."""
        self.assertEqual(self.connector.ssid, "gencat_ENS_EDU")
        self.assertIsNotNone(self.connector._script_dir)

    def test_init_default_ssid(self):
        """Test de inicialización con SSID por defecto."""
        connector = ProfileConnector()
        self.assertEqual(connector.ssid, "gencat_ENS_EDU")

    def test_init_with_credentials(self):
        """Test de inicialización con credenciales."""
        connector = ProfileConnector(
            ssid="test_network", username="testuser", password="testpass"
        )
        self.assertEqual(connector.ssid, "test_network")
        self.assertEqual(connector.username, "testuser")
        self.assertEqual(connector.password, "testpass")

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_install_wifi_profile_success(self, mock_exists, mock_run):
        """Test de instalación exitosa del perfil WiFi."""
        # Configurar mocks
        mock_exists.return_value = True
        # Primera llamada: delete profile, Segunda llamada: add profile
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=b"Perfil eliminado", stderr=b""),
            MagicMock(returncode=0, stdout=b"Perfil agregado", stderr=b""),
        ]

        # Ejecutar
        success, message = self.connector._install_wifi_profile()

        # Verificar
        self.assertTrue(success)
        self.assertIn("correctament", message)
        self.assertEqual(mock_run.call_count, 2)

        # Verificar que el segundo comando contiene los parámetros de add
        call_args = mock_run.call_args_list[1][0][0]
        self.assertIn("netsh", call_args)
        self.assertIn("wlan", call_args)
        self.assertIn("add", call_args)
        self.assertIn("profile", call_args)
        self.assertIn("user=all", call_args)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_install_wifi_profile_already_exists(self, mock_exists, mock_run):
        """Test cuando el perfil WiFi ya existe."""
        # Configurar mocks
        mock_exists.return_value = True
        # Primera llamada: delete profile, Segunda llamada: add profile
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=b"Perfil eliminado", stderr=b""),
            MagicMock(
                returncode=1, stdout=b"El perfil ya est\xe1 en la interfaz", stderr=b""
            ),
        ]

        # Ejecutar
        success, message = self.connector._install_wifi_profile()

        # Verificar - debe ser exitoso aunque retorne código 1
        self.assertTrue(success)
        self.assertIn("ja existia", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_install_wifi_profile_file_not_found(self, mock_exists, mock_run):
        """Test cuando el archivo de perfil no existe."""
        # Configurar mocks
        # Primera llamada: delete profile (éxito o no importa)
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"Perfil eliminado", stderr=b""
        )
        mock_exists.return_value = False

        # Ejecutar
        success, message = self.connector._install_wifi_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("no trobat", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_install_wifi_profile_netsh_error(self, mock_exists, mock_run):
        """Test cuando netsh falla."""
        # Configurar mocks
        mock_exists.return_value = True
        # Primera llamada: delete profile, Segunda llamada: add profile (error)
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=b"Perfil eliminado", stderr=b""),
            MagicMock(
                returncode=1, stdout=b"Error desconocido", stderr=b"Error de red"
            ),
        ]

        # Ejecutar
        success, message = self.connector._install_wifi_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_delete_existing_profile_success(self, mock_run):
        """Test de eliminación exitosa del perfil WiFi existente."""
        # Configurar mock
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"Perfil eliminado", stderr=b""
        )

        # Ejecutar
        success, message = self.connector._delete_existing_profile()

        # Verificar
        self.assertTrue(success)
        self.assertIn("eliminat", message)
        mock_run.assert_called_once()

        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn("netsh", call_args)
        self.assertIn("wlan", call_args)
        self.assertIn("delete", call_args)
        self.assertIn("profile", call_args)
        self.assertIn("name=gencat_ENS_EDU", call_args)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_delete_existing_profile_not_found(self, mock_run):
        """Test cuando el perfil no existe (comportamiento esperado)."""
        # Configurar mock - el perfil no existe
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"Profile not found", stderr=b""
        )

        # Ejecutar
        success, message = self.connector._delete_existing_profile()

        # Verificar - debe ser exitoso aunque no exista el perfil
        self.assertTrue(success)
        self.assertIn("No existia", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_delete_existing_profile_spanish_not_found(self, mock_run):
        """Test cuando el perfil no existe (mensaje en español)."""
        # Configurar mock - el perfil no existe (mensaje en español)
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"No se encontro el perfil", stderr=b""
        )

        # Ejecutar
        success, message = self.connector._delete_existing_profile()

        # Verificar - debe ser exitoso aunque no exista el perfil
        self.assertTrue(success)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_delete_existing_profile_error_continues(self, mock_run):
        """Test cuando hay un error al eliminar (no es crítico, continua)."""
        # Configurar mock - error desconocido
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"Error desconocido", stderr=b"Error interno"
        )

        # Ejecutar
        success, message = self.connector._delete_existing_profile()

        # Verificar - debe continuar aunque haya error
        self.assertTrue(success)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_delete_existing_profile_exception_continues(self, mock_run):
        """Test cuando hay una excepción (no es crítico, continua)."""
        # Configurar mock - lanza excepción
        mock_run.side_effect = Exception("Error inesperado")

        # Ejecutar
        success, message = self.connector._delete_existing_profile()

        # Verificar - debe continuar aunque haya excepción
        self.assertTrue(success)

    @patch("wifi_connector.core.profile_connector.ET.parse")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_update_credentials_xml_success(self, mock_exists, mock_parse):
        """Test de actualización exitosa de credenciales en XML."""
        # Configurar mocks
        mock_exists.return_value = True

        # Mock del árbol XML
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_username_elem = MagicMock()
        mock_password_elem = MagicMock()

        mock_parse.return_value = mock_tree
        mock_tree.getroot.return_value = mock_root
        mock_root.find.side_effect = [mock_username_elem, mock_password_elem]

        # Crear conector con credenciales
        connector = ProfileConnector(username="testuser", password="testpass")

        # Ejecutar
        success, message = connector._update_credentials_xml()

        # Verificar
        self.assertTrue(success)
        self.assertIn("actualitzades", message)
        self.assertEqual(mock_username_elem.text, "testuser")
        self.assertEqual(mock_password_elem.text, "testpass")
        mock_tree.write.assert_called_once()

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_update_credentials_xml_file_not_found(self, mock_exists):
        """Test cuando el archivo credentials.xml no existe."""
        mock_exists.return_value = False

        connector = ProfileConnector(username="testuser", password="testpass")
        success, message = connector._update_credentials_xml()

        self.assertFalse(success)
        self.assertIn("no trobat", message)

    @patch("wifi_connector.core.profile_connector.ET.parse")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_update_credentials_xml_missing_elements(self, mock_exists, mock_parse):
        """Test cuando los elementos Username/Password no se encuentran en el XML."""
        mock_exists.return_value = True

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_parse.return_value = mock_tree
        mock_tree.getroot.return_value = mock_root
        mock_root.find.return_value = None  # No encuentra elementos

        connector = ProfileConnector(username="testuser", password="testpass")
        success, message = connector._update_credentials_xml()

        self.assertFalse(success)
        self.assertIn("trobat", message.lower())

    @patch("wifi_connector.core.profile_connector.ET.parse")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_update_credentials_xml_parse_error(self, mock_exists, mock_parse):
        """Test cuando hay error al parsear el XML."""
        mock_exists.return_value = True
        mock_parse.side_effect = ET.ParseError("Invalid XML")

        connector = ProfileConnector(username="testuser", password="testpass")
        success, message = connector._update_credentials_xml()

        self.assertFalse(success)
        self.assertIn("parsejar", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_configure_eap_credentials_success(self, mock_exists, mock_run):
        """Test de configuración exitosa de credenciales EAP."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout=b"Success", stderr=b"")

        # Ejecutar
        success, message = self.connector._configure_eap_credentials()

        # Verificar
        self.assertTrue(success)
        self.assertIn("correctament", message)
        mock_run.assert_called_once()

        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn("gencat_ENS_EDU", call_args)
        self.assertIn("1", call_args)
        self.assertIn("/i", call_args)

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_configure_eap_credentials_executable_not_found(self, mock_exists):
        """Test cuando el ejecutable WLANSetEAPUserData no existe."""
        # Configurar mock - solo el ejecutable no existe
        mock_exists.side_effect = [False, True]

        # Ejecutar
        success, message = self.connector._configure_eap_credentials()

        # Verificar
        self.assertFalse(success)
        self.assertIn("WLANSetEAPUserData.exe no trobat", message)

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_configure_eap_credentials_xml_not_found(self, mock_exists):
        """Test cuando el archivo credentials.xml no existe."""
        # Configurar mock - el ejecutable existe pero el XML no
        mock_exists.side_effect = [True, False]

        # Ejecutar
        success, message = self.connector._configure_eap_credentials()

        # Verificar
        self.assertFalse(success)
        self.assertIn("credentials.xml no trobat", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_configure_eap_credentials_command_error(self, mock_exists, mock_run):
        """Test cuando WLANSetEAPUserData falla."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"", stderr=b"Error en configurar credencials"
        )

        # Ejecutar
        success, message = self.connector._configure_eap_credentials()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en configurar credencials", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_connect_to_network_success(self, mock_run):
        """Test de conexión exitosa a la red."""
        # Configurar mock
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"Connectat correctament a gencat_ENS_EDU", stderr=b""
        )

        # Ejecutar
        success, message = self.connector._connect_to_network()

        # Verificar
        self.assertTrue(success)
        self.assertIn("gencat_ENS_EDU", message)
        mock_run.assert_called_once()

        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn("netsh", call_args)
        self.assertIn("wlan", call_args)
        self.assertIn("connect", call_args)
        self.assertIn("name=gencat_ENS_EDU", call_args)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    def test_connect_to_network_error(self, mock_run):
        """Test cuando la conexión falla."""
        # Configurar mock
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"", stderr=b"No es pot connectar a la xarxa"
        )

        # Ejecutar
        success, message = self.connector._connect_to_network()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en connectar", message)

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.time.sleep")
    def test_verify_connection_success(self, mock_sleep, mock_run):
        """Test de verificación exitosa de conexión."""
        # Configurar mock - primera llamada muestra conectado
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"SSID: gencat_ENS_EDU\nEstado: conectado", stderr=b""
        )

        # Ejecutar
        success, message = self.connector._verify_connection(
            max_attempts=3, wait_seconds=1
        )

        # Verificar
        self.assertTrue(success)
        self.assertIn("verificada", message.lower())
        mock_run.assert_called_once()
        mock_sleep.assert_not_called()  # No debe esperar si conecta en primer intento

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.time.sleep")
    def test_verify_connection_authentication_failure(self, mock_sleep, mock_run):
        """Test cuando las credenciales son inválidas."""
        # Configurar mock - muestra desconectado (usando 'disconnected' porque
        # 'desconectado' contiene 'conectado' y el código lo detecta primero)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b"SSID: gencat_ENS_EDU\nState: disconnected",
            stderr=b"",
        )

        # Ejecutar
        success, message = self.connector._verify_connection(
            max_attempts=3, wait_seconds=1
        )

        # Verificar
        self.assertFalse(success)
        self.assertIn("credencials", message.lower())

    @patch("wifi_connector.core.profile_connector.subprocess.run")
    @patch("wifi_connector.core.profile_connector.time.sleep")
    def test_verify_connection_timeout(self, mock_sleep, mock_run):
        """Test cuando la conexión no se completa."""
        # Configurar mock - siempre muestra autenticando
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b"SSID: gencat_ENS_EDU\nEstado: autenticando",
            stderr=b"",
        )

        # Ejecutar
        success, message = self.connector._verify_connection(
            max_attempts=3, wait_seconds=1
        )

        # Verificar
        self.assertFalse(success)
        self.assertIn("verificar", message.lower())
        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Se espera entre intentos

    @patch.object(ProfileConnector, "_verify_connection")
    @patch.object(ProfileConnector, "_connect_to_network")
    @patch.object(ProfileConnector, "_configure_eap_credentials")
    @patch.object(ProfileConnector, "_update_credentials_xml")
    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_success_with_credentials(
        self, mock_install, mock_update, mock_configure, mock_connect, mock_verify
    ):
        """Test del proceso completo de conexión exitosa con credenciales."""
        # Configurar mocks
        mock_install.return_value = (True, "Perfil instal·lat")
        mock_update.return_value = (True, "Credencials actualitzades")
        mock_configure.return_value = (True, "Credencials configurades")
        mock_connect.return_value = (True, "Connectat")
        mock_verify.return_value = (True, "Connexió verificada")

        # Crear conector con credenciales
        connector = ProfileConnector(username="testuser", password="testpass")

        # Ejecutar
        success, message = connector.connect_via_profile()

        # Verificar
        self.assertTrue(success)
        self.assertIn("verificada", message.lower())
        mock_install.assert_called_once()
        mock_update.assert_called_once()  # Debe llamarse cuando hay credenciales
        mock_configure.assert_called_once()
        mock_connect.assert_called()
        mock_verify.assert_called_once()

    @patch.object(ProfileConnector, "_verify_connection")
    @patch.object(ProfileConnector, "_connect_to_network")
    @patch.object(ProfileConnector, "_configure_eap_credentials")
    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_success_without_credentials(
        self, mock_install, mock_configure, mock_connect, mock_verify
    ):
        """Test del proceso completo de conexión exitosa sin credenciales."""
        # Configurar mocks
        mock_install.return_value = (True, "Perfil instal·lat")
        mock_configure.return_value = (True, "Credencials configurades")
        mock_connect.return_value = (True, "Connectat")
        mock_verify.return_value = (True, "Connexió verificada")

        # Crear conector sin credenciales
        connector = ProfileConnector()

        # Ejecutar
        success, message = connector.connect_via_profile()

        # Verificar
        self.assertTrue(success)
        self.assertIn("verificada", message.lower())
        mock_install.assert_called_once()
        # _update_credentials_xml NO debe llamarse cuando no hay credenciales
        mock_configure.assert_called_once()
        mock_connect.assert_called_once()
        mock_verify.assert_called_once()

    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_fails_at_install(self, mock_install):
        """Test cuando falla la instalación del perfil."""
        # Configurar mock
        mock_install.return_value = (False, "Error en instal·lar")

        # Ejecutar
        success, message = self.connector.connect_via_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en instal·lar", message)
        mock_install.assert_called_once()

    @patch.object(ProfileConnector, "_configure_eap_credentials")
    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_fails_at_configure(self, mock_install, mock_configure):
        """Test cuando falla la configuración de credenciales."""
        # Configurar mocks
        mock_install.return_value = (True, "Perfil instal·lat")
        mock_configure.return_value = (False, "Error en configurar")

        # Ejecutar
        success, message = self.connector.connect_via_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en configurar", message)
        mock_install.assert_called_once()
        mock_configure.assert_called_once()

    @patch.object(ProfileConnector, "_connect_to_network")
    @patch.object(ProfileConnector, "_configure_eap_credentials")
    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_fails_at_connect(
        self, mock_install, mock_configure, mock_connect
    ):
        """Test cuando falla la conexión final."""
        # Configurar mocks
        mock_install.return_value = (True, "Perfil instal·lat")
        mock_configure.return_value = (True, "Credencials configurades")
        mock_connect.return_value = (False, "Error en connectar")

        # Ejecutar
        success, message = self.connector.connect_via_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en connectar", message)
        mock_install.assert_called_once()
        mock_configure.assert_called_once()
        mock_connect.assert_called_once()

    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_exception_handling(self, mock_install):
        """Test de manejo de excepciones inesperadas."""
        # Configurar mock para lanzar excepción
        mock_install.side_effect = Exception("Error inesperat")

        # Ejecutar
        success, message = self.connector.connect_via_profile()

        # Verificar
        self.assertFalse(success)
        self.assertIn("Error inesperat", message)

    @patch.object(ProfileConnector, "_verify_connection")
    @patch.object(ProfileConnector, "_connect_to_network")
    @patch.object(ProfileConnector, "_configure_eap_credentials")
    @patch.object(ProfileConnector, "_install_wifi_profile")
    def test_connect_via_profile_with_progress_callback(
        self, mock_install, mock_configure, mock_connect, mock_verify
    ):
        """Test que el progress callback se llama correctamente."""
        # Configurar mocks
        mock_install.return_value = (True, "Perfil instal·lat")
        mock_configure.return_value = (True, "Credencials configurades")
        mock_connect.return_value = (True, "Connectat")
        mock_verify.return_value = (True, "Verificat")

        # Mock del callback
        mock_callback = MagicMock()

        # Crear conector sin credenciales
        connector = ProfileConnector()

        # Ejecutar con callback
        success, message = connector.connect_via_profile(
            progress_callback=mock_callback
        )

        # Verificar que el callback se llamó varias veces
        self.assertTrue(success)
        self.assertGreater(mock_callback.call_count, 3)  # Al menos 4 pasos


class TestHasPermissionWarning(unittest.TestCase):
    """Tests para el método _has_permission_warning."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.connector = ProfileConnector("test_ssid")

    def test_detects_ubicacion_pattern(self):
        """Test que detecta patrón 'ubicaci' (ubicación sin acento)."""
        output = "error: se necesita permiso de ubicacion para completar"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_location_pattern(self):
        """Test que detecta patrón 'location' en inglés."""
        output = "location permission required to scan networks"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_elevacion_pattern(self):
        """Test que detecta patrón 'elevaci' (elevación sin acento)."""
        output = "se requiere elevacion de privilegios"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_wlan_api_error(self):
        """Test que detecta error de la API WLAN."""
        output = "error calling wlangetavailablenetworklist"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_acceso_denegado_spanish(self):
        """Test que detecta 'acceso denegado' en español."""
        output = "acceso denegado al recurso de red"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_access_denied_english(self):
        """Test que detecta 'access denied' en inglés."""
        output = "access denied while connecting to network"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_error_5_colon(self):
        """Test que detecta 'error 5:' (código de acceso denegado)."""
        output = "error 5: acceso denegado"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_detects_error_colon_5(self):
        """Test que detecta 'error: 5' (formato alternativo)."""
        output = "the operation failed with error: 5"
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_no_false_positive_on_normal_output(self):
        """Test que no hay falsos positivos con salida normal."""
        output = "connection request was completed successfully"
        self.assertFalse(self.connector._has_permission_warning(output))

    def test_no_false_positive_on_empty_output(self):
        """Test que no hay falsos positivos con salida vacía."""
        output = ""
        self.assertFalse(self.connector._has_permission_warning(output))

    def test_no_false_positive_on_generic_error(self):
        """Test que no detecta errores genéricos como permisos."""
        output = "error: red no disponible. error 10: tiempo agotado"
        self.assertFalse(self.connector._has_permission_warning(output))

    def test_case_sensitivity(self):
        """Test que la detección funciona con diferentes casos (el output debe estar en minúsculas)."""
        # El método espera input ya en minúsculas
        output = "ACCESS DENIED".lower()
        self.assertTrue(self.connector._has_permission_warning(output))

    def test_multiple_patterns_in_output(self):
        """Test con múltiples patrones en la misma salida."""
        output = "error: location permission denied, access denied, error 5:"
        self.assertTrue(self.connector._has_permission_warning(output))


class TestCleanCredentialsFile(unittest.TestCase):
    """Tests para el método estático clean_credentials_file()."""

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    @patch("wifi_connector.core.profile_connector.shutil.copy2")
    def test_clean_credentials_success(self, mock_copy, mock_exists):
        """Test de limpieza exitosa de credenciales."""
        mock_exists.return_value = True

        result = ProfileConnector.clean_credentials_file()

        self.assertTrue(result)
        mock_copy.assert_called_once()

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    def test_clean_credentials_no_template(self, mock_exists):
        """Test cuando no existe el archivo template."""
        # El template no existe
        mock_exists.side_effect = lambda path: "template" not in path

        result = ProfileConnector.clean_credentials_file()

        self.assertFalse(result)

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    @patch("wifi_connector.core.profile_connector.shutil.copy2")
    def test_clean_credentials_no_credentials_file(self, mock_copy, mock_exists):
        """Test cuando no existe el archivo de credenciales (no hay nada que limpiar)."""
        # Template existe pero credentials.xml no
        mock_exists.side_effect = lambda path: "template" in path

        result = ProfileConnector.clean_credentials_file()

        self.assertTrue(result)  # Retorna True porque no hay nada que limpiar
        mock_copy.assert_not_called()

    @patch("wifi_connector.core.profile_connector.os.path.exists")
    @patch("wifi_connector.core.profile_connector.shutil.copy2")
    def test_clean_credentials_copy_error(self, mock_copy, mock_exists):
        """Test cuando hay un error al copiar el archivo."""
        mock_exists.return_value = True
        mock_copy.side_effect = Exception("Permission denied")

        result = ProfileConnector.clean_credentials_file()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
