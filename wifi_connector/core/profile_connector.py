"""
Módulo para conectar a redes WiFi usando perfiles de red y configuración EAP.
Este módulo usa netsh para gestionar perfiles WiFi y WLANSetEAPUserData para configurar credenciales EAP.
"""

import subprocess
import os
import xml.etree.ElementTree as ET
import time
from typing import Tuple, Optional, Callable
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


class ProfileConnector:
    """Clase para gestionar conexiones WiFi mediante perfiles de red."""
    
    def __init__(self, ssid: str = "gencat_ENS_EDU", username: Optional[str] = None, password: Optional[str] = None):
        """
        Inicializa el conector de perfiles.
        
        Args:
            ssid: Nombre de la red WiFi (SSID). Por defecto "gencat_ENS_EDU"
            username: Usuario para autenticación EAP (opcional)
            password: Contraseña para autenticación EAP (opcional)
        """
        self.ssid = ssid
        self.username = username
        self.password = password
        self.script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        Logger.info(t.PROFILE_LOG_INIT.format(ssid=ssid, username=username if username else 'No especificado'))
    
    def connect_via_profile(self, progress_callback: Optional[Callable[[str], None]] = None) -> Tuple[bool, str]:
        """
        Conecta a la red WiFi usando método de perfil (netsh + WLANSetEAPUserData).
        
        Este método:
        1. Instala el perfil WiFi desde el archivo XML
        1.5. Actualiza las credenciales en el XML si se proporcionaron
        2. Configura las credenciales EAP usando WLANSetEAPUserData
        3. Conecta a la red usando netsh
        4. Verifica que la conexión se estableció correctamente
        
        Args:
            progress_callback: Función opcional para reportar progreso a la GUI
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si la conexión fue exitosa
        """
        try:
            Logger.info(t.PROFILE_LOG_STARTING)
            if progress_callback:
                progress_callback(t.PROFILE_STARTING)
            
            Logger.info(t.PROFILE_INSTALLING)
            if progress_callback:
                progress_callback(t.PROFILE_STEP1)
            success, message = self._install_wifi_profile()
            if not success:
                Logger.error(f"Error al instalar perfil: {message}")
                return False, message
            Logger.info(f"✓ {message}")
            
            if self.username and self.password:
                Logger.info(t.PROFILE_UPDATING_CREDS)
                if progress_callback:
                    progress_callback(t.PROFILE_STEP2)
                success, message = self._update_credentials_xml()
                if not success:
                    Logger.error(f"Error al actualizar credenciales: {message}")
                    return False, message
                Logger.info(f"✓ {message}")
            else:
                Logger.warning(t.PROFILE_WARNING_NO_CREDS)
            
            Logger.info(t.PROFILE_CONFIGURING_EAP)
            if progress_callback:
                progress_callback(t.PROFILE_STEP3)
            success, message = self._configure_eap_credentials()
            if not success:
                Logger.error(f"Error al configurar credenciales: {message}")
                return False, message
            Logger.info(f"✓ {message}")
            
            Logger.info(t.PROFILE_CONNECTING)
            if progress_callback:
                progress_callback(t.PROFILE_STEP4)
            success, message = self._connect_to_network()
            if not success:
                Logger.error(f"Error al conectar: {message}")
                return False, message
            Logger.info(f"✓ {message}")
            
            Logger.info(t.PROFILE_VERIFYING)
            if progress_callback:
                progress_callback(t.PROFILE_STEP5)
            success, message = self._verify_connection()
            if not success:
                Logger.error(f"Error de verificación: {message}")
                return False, message
            Logger.info(f"✓ {message}")
            
            Logger.info(f"✓ {t.PROFILE_SUCCESS_COMPLETE}")
            return True, t.PROFILE_SUCCESS_COMPLETE
            
        except Exception as e:
            error_msg = t.PROFILE_ERROR_UNEXPECTED.format(error=e)
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _install_wifi_profile(self) -> Tuple[bool, str]:
        """
        Instala el perfil WiFi para todos los usuarios usando netsh.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se instaló correctamente
        """
        try:
            profile_path = os.path.join(self.script_dir, 'xml', 'Wi-Fi-gencat_ENS_EDU.xml')
            
            if not os.path.exists(profile_path):
                error_msg = t.PROFILE_ERROR_PROFILE_NOT_FOUND.format(path=profile_path)
                Logger.error(error_msg)
                return False, error_msg
            
            command = ['netsh', 'wlan', 'add', 'profile', f'filename={profile_path}', 'user=all']
            Logger.debug(f"Ejecutando comando: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                encoding='cp850',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                Logger.info(t.PROFILE_SUCCESS_INSTALLED)
                return True, t.PROFILE_SUCCESS_INSTALLED
            else:
                if "ya está" in result.stdout.lower() or "already" in result.stdout.lower():
                    Logger.info(t.PROFILE_SUCCESS_EXISTED)
                    return True, t.PROFILE_SUCCESS_EXISTED
                error_msg = t.PROFILE_ERROR_NETSH.format(error=result.stdout.strip() or result.stderr.strip())
                Logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = t.PROFILE_ERROR_INSTALL.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _update_credentials_xml(self) -> Tuple[bool, str]:
        """
        Actualiza el archivo credentials.xml con el usuario y contraseña proporcionados.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se actualizó correctamente
        """
        try:
            credentials_path = os.path.join(self.script_dir, 'xml', 'credentials.xml')
            
            if not os.path.exists(credentials_path):
                error_msg = t.PROFILE_ERROR_CREDS_NOT_FOUND.format(path=credentials_path)
                Logger.error(error_msg)
                return False, error_msg
            
            Logger.debug(f"Parseando XML: {credentials_path}")
            tree = ET.parse(credentials_path)
            root = tree.getroot()
            
            namespaces = {
                '': 'http://www.microsoft.com/provisioning/EapHostUserCredentials',
                'eapCommon': 'http://www.microsoft.com/provisioning/EapCommon',
                'baseEap': 'http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1',
                'MsPeap': 'http://www.microsoft.com/provisioning/MsPeapUserPropertiesV1',
                'MsChapV2': 'http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1'
            }
            
            for prefix, uri in namespaces.items():
                if prefix:
                    ET.register_namespace(prefix, uri)
                else:
                    ET.register_namespace('', uri)
            
            username_elem = root.find('.//MsChapV2:Username', namespaces)
            password_elem = root.find('.//MsChapV2:Password', namespaces)
            
            if username_elem is None or password_elem is None:
                error_msg = t.PROFILE_ERROR_XML_ELEMENTS
                Logger.error(error_msg)
                return False, error_msg
            
            Logger.debug(f"Actualizando usuario: {self.username}")
            username_elem.text = self.username
            password_elem.text = self.password
            
            tree.write(credentials_path, encoding='UTF-8', xml_declaration=True)
            Logger.info(f"Credenciales actualizadas en {credentials_path}")
            
            return True, t.PROFILE_SUCCESS_UPDATED
            
        except ET.ParseError as e:
            error_msg = t.PROFILE_ERROR_PARSING_XML.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
        except Exception as e:
            error_msg = t.PROFILE_ERROR_UPDATE_CREDS.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _configure_eap_credentials(self) -> Tuple[bool, str]:
        """
        Configura las credenciales EAP usando WLANSetEAPUserData.exe.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se configuró correctamente
        """
        try:
            executable_path = os.path.join(self.script_dir, 'wlanseteapuserdata', 'WLANSetEAPUserData.exe')
            credentials_path = os.path.join(self.script_dir, 'xml', 'credentials.xml')
            
            if not os.path.exists(executable_path):
                error_msg = t.PROFILE_ERROR_EXE_NOT_FOUND.format(path=executable_path)
                Logger.error(error_msg)
                return False, error_msg
            
            if not os.path.exists(credentials_path):
                error_msg = t.PROFILE_ERROR_CREDS_NOT_FOUND.format(path=credentials_path)
                Logger.error(error_msg)
                return False, error_msg
            
            command = [
                executable_path,
                self.ssid,
                '1',
                credentials_path,
                '/i'
            ]
            Logger.debug(f"Ejecutando comando: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                Logger.info(t.PROFILE_SUCCESS_EAP)
                return True, t.PROFILE_SUCCESS_EAP
            else:
                error_msg = t.PROFILE_ERROR_EAP.format(error=result.stdout.strip() or result.stderr.strip())
                Logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = t.PROFILE_ERROR_CONFIG_EAP.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _connect_to_network(self) -> Tuple[bool, str]:
        """
        Conecta a la red WiFi usando netsh.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se conectó correctamente
        """
        try:
            command = ['netsh', 'wlan', 'connect', f'name={self.ssid}']
            Logger.debug(f"Ejecutando comando: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                encoding='cp850',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                if "correctamente" in result.stdout.lower() or "successfully" in result.stdout.lower():
                    success_msg = t.PROFILE_SUCCESS_CONNECTED.format(ssid=self.ssid)
                    Logger.info(success_msg)
                    return True, success_msg
                success_msg = t.PROFILE_SUCCESS_COMMAND.format(ssid=self.ssid)
                Logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = t.PROFILE_ERROR_CONNECT.format(error=result.stdout.strip() or result.stderr.strip())
                Logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = t.PROFILE_ERROR_CONNECT_COMMAND.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _verify_connection(self, max_attempts: int = 3, wait_seconds: int = 3) -> Tuple[bool, str]:
        """
        Verifica que la conexión WiFi se estableció correctamente.
        
        Usa 'netsh wlan show interfaces' para comprobar el estado real de la conexión.
        Espera hasta max_attempts intentos para que la conexión se complete.
        
        Args:
            max_attempts: Número máximo de intentos de verificación (por defecto 3)
            wait_seconds: Segundos entre cada intento (por defecto 3)
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si está conectado
        """
        try:
            Logger.info(t.PROFILE_LOG_VERIFYING.format(ssid=self.ssid, attempts=max_attempts))
            
            for attempt in range(1, max_attempts + 1):
                Logger.debug(t.PROFILE_LOG_ATTEMPT.format(attempt=attempt, max_attempts=max_attempts))
                
                command = ['netsh', 'wlan', 'show', 'interfaces']
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding='cp850',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    
                    if self.ssid.lower() in output:
                        if 'estado' in output or 'state' in output:
                            for line in result.stdout.split('\n'):
                                line_lower = line.lower()
                                if 'estado' in line_lower or 'state' in line_lower:
                                    if 'desconectado' in line_lower or 'disconnected' in line_lower:
                                        error_msg = t.PROFILE_ERROR_AUTH
                                        Logger.error(error_msg)
                                        return False, error_msg
                                    elif 'autenticando' in line_lower or 'authenticating' in line_lower:
                                        Logger.debug(t.PROFILE_LOG_STATE_AUTH.format(attempt=attempt))
                                        break
                                    elif 'conectando' in line_lower or 'connecting' in line_lower:
                                        Logger.debug(t.PROFILE_LOG_STATE_CONNECTING.format(attempt=attempt))
                                        break
                                    elif 'conectado' in line_lower or 'connected' in line_lower:
                                        success_msg = t.PROFILE_SUCCESS_VERIFIED.format(ssid=self.ssid)
                                        Logger.info(success_msg)
                                        return True, success_msg
                
                if attempt < max_attempts:
                    time.sleep(wait_seconds)
            
            error_msg = t.PROFILE_ERROR_NO_VERIFY.format(ssid=self.ssid, attempts=max_attempts)
            Logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = t.PROFILE_ERROR_VERIFY.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
