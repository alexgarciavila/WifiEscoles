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
        self.assertIsNotNone(self.connector.script_dir)
    
    def test_init_default_ssid(self):
        """Test de inicialización con SSID por defecto."""
        connector = ProfileConnector()
        self.assertEqual(connector.ssid, "gencat_ENS_EDU")
    
    def test_init_with_credentials(self):
        """Test de inicialización con credenciales."""
        connector = ProfileConnector(ssid="test_network", username="testuser", password="testpass")
        self.assertEqual(connector.ssid, "test_network")
        self.assertEqual(connector.username, "testuser")
        self.assertEqual(connector.password, "testpass")
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_install_wifi_profile_success(self, mock_exists, mock_run):
        """Test de instalación exitosa del perfil WiFi."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="Perfil agregado", stderr="")
        
        # Ejecutar
        success, message = self.connector._install_wifi_profile()
        
        # Verificar
        self.assertTrue(success)
        self.assertIn("correctament", message)
        mock_run.assert_called_once()
        
        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn('netsh', call_args)
        self.assertIn('wlan', call_args)
        self.assertIn('add', call_args)
        self.assertIn('profile', call_args)
        self.assertIn('user=all', call_args)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_install_wifi_profile_already_exists(self, mock_exists, mock_run):
        """Test cuando el perfil WiFi ya existe."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout="El perfil ya está en la interfaz", 
            stderr=""
        )
        
        # Ejecutar
        success, message = self.connector._install_wifi_profile()
        
        # Verificar - debe ser exitoso aunque retorne código 1
        self.assertTrue(success)
        self.assertIn("ja existia", message)
    
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_install_wifi_profile_file_not_found(self, mock_exists):
        """Test cuando el archivo de perfil no existe."""
        # Configurar mock
        mock_exists.return_value = False
        
        # Ejecutar
        success, message = self.connector._install_wifi_profile()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("no trobat", message)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_install_wifi_profile_netsh_error(self, mock_exists, mock_run):
        """Test cuando netsh falla."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout="Error desconocido", 
            stderr="Error de red"
        )
        
        # Ejecutar
        success, message = self.connector._install_wifi_profile()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("Error", message)
    
    @patch('wifi_connector.core.profile_connector.ET.parse')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
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
    
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_update_credentials_xml_file_not_found(self, mock_exists):
        """Test cuando el archivo credentials.xml no existe."""
        mock_exists.return_value = False
        
        connector = ProfileConnector(username="testuser", password="testpass")
        success, message = connector._update_credentials_xml()
        
        self.assertFalse(success)
        self.assertIn("no trobat", message)
    
    @patch('wifi_connector.core.profile_connector.ET.parse')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
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
    
    @patch('wifi_connector.core.profile_connector.ET.parse')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_update_credentials_xml_parse_error(self, mock_exists, mock_parse):
        """Test cuando hay error al parsear el XML."""
        mock_exists.return_value = True
        mock_parse.side_effect = ET.ParseError("Invalid XML")
        
        connector = ProfileConnector(username="testuser", password="testpass")
        success, message = connector._update_credentials_xml()
        
        self.assertFalse(success)
        self.assertIn("parsejar", message)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_configure_eap_credentials_success(self, mock_exists, mock_run):
        """Test de configuración exitosa de credenciales EAP."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        
        # Ejecutar
        success, message = self.connector._configure_eap_credentials()
        
        # Verificar
        self.assertTrue(success)
        self.assertIn("correctament", message)
        mock_run.assert_called_once()
        
        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn('gencat_ENS_EDU', call_args)
        self.assertIn('1', call_args)
        self.assertIn('/i', call_args)
    
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_configure_eap_credentials_executable_not_found(self, mock_exists):
        """Test cuando el ejecutable WLANSetEAPUserData no existe."""
        # Configurar mock - solo el ejecutable no existe
        mock_exists.side_effect = [False, True]
        
        # Ejecutar
        success, message = self.connector._configure_eap_credentials()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("WLANSetEAPUserData.exe no trobat", message)
    
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_configure_eap_credentials_xml_not_found(self, mock_exists):
        """Test cuando el archivo credentials.xml no existe."""
        # Configurar mock - el ejecutable existe pero el XML no
        mock_exists.side_effect = [True, False]
        
        # Ejecutar
        success, message = self.connector._configure_eap_credentials()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("credentials.xml no trobat", message)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.os.path.exists')
    def test_configure_eap_credentials_command_error(self, mock_exists, mock_run):
        """Test cuando WLANSetEAPUserData falla."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout="", 
            stderr="Error en configurar credencials"
        )
        
        # Ejecutar
        success, message = self.connector._configure_eap_credentials()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("Error de WLANSetEAPUserData", message)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    def test_connect_to_network_success(self, mock_run):
        """Test de conexión exitosa a la red."""
        # Configurar mock
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout="Connectat correctament a gencat_ENS_EDU", 
            stderr=""
        )
        
        # Ejecutar
        success, message = self.connector._connect_to_network()
        
        # Verificar
        self.assertTrue(success)
        self.assertIn("gencat_ENS_EDU", message)
        mock_run.assert_called_once()
        
        # Verificar que el comando contiene los parámetros correctos
        call_args = mock_run.call_args[0][0]
        self.assertIn('netsh', call_args)
        self.assertIn('wlan', call_args)
        self.assertIn('connect', call_args)
        self.assertIn('name=gencat_ENS_EDU', call_args)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    def test_connect_to_network_error(self, mock_run):
        """Test cuando la conexión falla."""
        # Configurar mock
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout="", 
            stderr="No es pot connectar a la xarxa"
        )
        
        # Ejecutar
        success, message = self.connector._connect_to_network()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("Error en connectar", message)
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.time.sleep')
    def test_verify_connection_success(self, mock_sleep, mock_run):
        """Test de verificación exitosa de conexión."""
        # Configurar mock - primera llamada muestra conectado
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SSID: gencat_ENS_EDU\nEstado: conectado",
            stderr=""
        )
        
        # Ejecutar
        success, message = self.connector._verify_connection(max_attempts=3, wait_seconds=1)
        
        # Verificar
        self.assertTrue(success)
        self.assertIn("verificada", message.lower())
        mock_run.assert_called_once()
        mock_sleep.assert_not_called()  # No debe esperar si conecta en primer intento
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.time.sleep')
    def test_verify_connection_authentication_failure(self, mock_sleep, mock_run):
        """Test cuando las credenciales son inválidas."""
        # Configurar mock - muestra desconectado (usando 'disconnected' porque
        # 'desconectado' contiene 'conectado' y el código lo detecta primero)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SSID: gencat_ENS_EDU\nState: disconnected",
            stderr=""
        )
        
        # Ejecutar
        success, message = self.connector._verify_connection(max_attempts=3, wait_seconds=1)
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("credencials", message.lower())
    
    @patch('wifi_connector.core.profile_connector.subprocess.run')
    @patch('wifi_connector.core.profile_connector.time.sleep')
    def test_verify_connection_timeout(self, mock_sleep, mock_run):
        """Test cuando la conexión no se completa."""
        # Configurar mock - siempre muestra autenticando
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SSID: gencat_ENS_EDU\nEstado: autenticando",
            stderr=""
        )
        
        # Ejecutar
        success, message = self.connector._verify_connection(max_attempts=3, wait_seconds=1)
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("verificar", message.lower())
        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Se espera entre intentos
    
    @patch.object(ProfileConnector, '_verify_connection')
    @patch.object(ProfileConnector, '_connect_to_network')
    @patch.object(ProfileConnector, '_configure_eap_credentials')
    @patch.object(ProfileConnector, '_update_credentials_xml')
    @patch.object(ProfileConnector, '_install_wifi_profile')
    def test_connect_via_profile_success_with_credentials(self, mock_install, mock_update, mock_configure, mock_connect, mock_verify):
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
        mock_connect.assert_called_once()
        mock_verify.assert_called_once()
    
    @patch.object(ProfileConnector, '_verify_connection')
    @patch.object(ProfileConnector, '_connect_to_network')
    @patch.object(ProfileConnector, '_configure_eap_credentials')
    @patch.object(ProfileConnector, '_install_wifi_profile')
    def test_connect_via_profile_success_without_credentials(self, mock_install, mock_configure, mock_connect, mock_verify):
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
    
    @patch.object(ProfileConnector, '_install_wifi_profile')
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
    
    @patch.object(ProfileConnector, '_configure_eap_credentials')
    @patch.object(ProfileConnector, '_install_wifi_profile')
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
    
    @patch.object(ProfileConnector, '_connect_to_network')
    @patch.object(ProfileConnector, '_configure_eap_credentials')
    @patch.object(ProfileConnector, '_install_wifi_profile')
    def test_connect_via_profile_fails_at_connect(self, mock_install, mock_configure, mock_connect):
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
    
    @patch.object(ProfileConnector, '_install_wifi_profile')
    def test_connect_via_profile_exception_handling(self, mock_install):
        """Test de manejo de excepciones inesperadas."""
        # Configurar mock para lanzar excepción
        mock_install.side_effect = Exception("Error inesperat")
        
        # Ejecutar
        success, message = self.connector.connect_via_profile()
        
        # Verificar
        self.assertFalse(success)
        self.assertIn("Error inesperat", message)

    @patch.object(ProfileConnector, '_verify_connection')
    @patch.object(ProfileConnector, '_connect_to_network')
    @patch.object(ProfileConnector, '_configure_eap_credentials')
    @patch.object(ProfileConnector, '_install_wifi_profile')
    def test_connect_via_profile_with_progress_callback(self, mock_install, mock_configure, mock_connect, mock_verify):
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
        success, message = connector.connect_via_profile(progress_callback=mock_callback)
        
        # Verificar que el callback se llamó varias veces
        self.assertTrue(success)
        self.assertGreater(mock_callback.call_count, 3)  # Al menos 4 pasos


if __name__ == '__main__':
    unittest.main()
