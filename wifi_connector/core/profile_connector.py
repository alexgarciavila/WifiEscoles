"""
Módulo para conectar a redes WiFi usando perfiles de red y configuración EAP.
Este módulo usa netsh para gestionar perfiles WiFi y WLANSetEAPUserData para configurar credenciales EAP.
"""

import subprocess
import os
import xml.etree.ElementTree as ET
import time
from dataclasses import dataclass
from typing import Tuple, Optional, Callable
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


@dataclass
class CommandResult:
    """Resultado de ejecutar un comando del sistema."""
    
    returncode: int
    stdout: str
    stderr: str
    
    @property
    def combined_output(self) -> str:
        """Devuelve stdout y stderr combinados en minúsculas."""
        return (self.stdout + " " + self.stderr).lower()
    
    @property
    def raw_error(self) -> str:
        """Devuelve el primer output no vacío (stdout o stderr)."""
        return self.stdout.strip() or self.stderr.strip()


def _decode_windows_output(raw_bytes: bytes) -> str:
    """
    Intenta decodificar la salida de comandos de Windows usando múltiples codificaciones.
    
    Args:
        raw_bytes: Bytes crudos de la salida del comando
    
    Returns:
        String decodificado correctamente
    """
    # Lista de codificaciones comunes en Windows en orden de prioridad
    encodings = ['utf-8', 'cp1252', 'cp850', 'latin-1']
    
    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    
    # Si todo falla, usar utf-8 con reemplazo de caracteres inválidos
    return raw_bytes.decode('utf-8', errors='replace')


class ProfileConnector:
    """Clase para gestionar conexiones WiFi mediante perfiles de red."""
    
    # Patrones que indican avisos de permisos de Windows (sin acentos para compatibilidad de encoding)
    _PERMISSION_WARNING_PATTERNS: tuple[str, ...] = (
        "ubicaci",           # "ubicación" sin acento
        "location",
        "elevaci",           # "elevación" sin acento
        "wlangetavailablenetworklist",
        "acceso denegado",
        "access denied",
        "error 5:",          # Código de error típico de acceso denegado
        "error: 5",
    )
    
    # Namespaces XML para credenciales EAP de Microsoft
    _EAP_NAMESPACES: dict[str, str] = {
        "": "http://www.microsoft.com/provisioning/EapHostUserCredentials",
        "eapCommon": "http://www.microsoft.com/provisioning/EapCommon",
        "baseEap": "http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1",
        "MsPeap": "http://www.microsoft.com/provisioning/MsPeapUserPropertiesV1",
        "MsChapV2": "http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1",
    }
    
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
        self._script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        Logger.info(t.PROFILE_LOG_INIT.format(ssid=ssid, username=username if username else 'No especificat'))
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Propiedades para rutas de archivos
    # ─────────────────────────────────────────────────────────────────────────────
    
    @property
    def _profile_path(self) -> str:
        """Ruta al archivo XML del perfil WiFi."""
        return os.path.join(self._script_dir, "xml", "Wi-Fi-gencat_ENS_EDU.xml")
    
    @property
    def _credentials_path(self) -> str:
        """Ruta al archivo XML de credenciales."""
        return os.path.join(self._script_dir, "xml", "credentials.xml")
    
    @property
    def _eap_executable_path(self) -> str:
        """Ruta al ejecutable WLANSetEAPUserData."""
        return os.path.join(self._script_dir, "wlanseteapuserdata", "WLANSetEAPUserData.exe")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Métodos auxiliares privados
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _run_command(self, command: list[str]) -> CommandResult:
        """
        Ejecuta un comando del sistema y devuelve el resultado decodificado.
        
        Args:
            command: Lista con el comando y sus argumentos
        
        Returns:
            CommandResult con stdout, stderr y returncode
        """
        Logger.debug(t.PROFILE_LOG_CMD_EXECUTING.format(command=' '.join(command)))
        
        result = subprocess.run(
            command,
            capture_output=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        
        return CommandResult(
            returncode=result.returncode,
            stdout=_decode_windows_output(result.stdout),
            stderr=_decode_windows_output(result.stderr),
        )
    
    def _validate_file_exists(self, path: str, error_template: str) -> Optional[str]:
        """
        Valida que un archivo existe.
        
        Args:
            path: Ruta del archivo a validar
            error_template: Plantilla del mensaje de error (debe tener {path})
        
        Returns:
            None si el archivo existe, mensaje de error si no existe
        """
        if not os.path.exists(path):
            error_msg = error_template.format(path=path)
            Logger.error(error_msg)
            return error_msg
        return None
    
    def _has_permission_warning(self, output: str) -> bool:
        """
        Detecta si la salida contiene avisos de permisos de Windows.
        
        Args:
            output: Texto de salida (stdout + stderr) en minúsculas
        
        Returns:
            True si se detectan avisos de permisos de Windows
        """
        return any(pattern in output for pattern in self._PERMISSION_WARNING_PATTERNS)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Método público principal
    # ─────────────────────────────────────────────────────────────────────────────
    
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
                Logger.error(t.PROFILE_LOG_INSTALL_ERROR.format(message=message))
                return False, message
            Logger.info(f"✓ {message}")
            
            if self.username and self.password:
                Logger.info(t.PROFILE_UPDATING_CREDS)
                if progress_callback:
                    progress_callback(t.PROFILE_STEP2)
                success, message = self._update_credentials_xml()
                if not success:
                    Logger.error(t.PROFILE_LOG_UPDATE_ERROR.format(message=message))
                    return False, message
                Logger.info(f"✓ {message}")
            else:
                Logger.warning(t.PROFILE_WARNING_NO_CREDS)
            
            Logger.info(t.PROFILE_CONFIGURING_EAP)
            if progress_callback:
                progress_callback(t.PROFILE_STEP3)
            success, message = self._configure_eap_credentials()
            if not success:
                Logger.error(t.PROFILE_LOG_CONFIG_ERROR.format(message=message))
                return False, message
            Logger.info(f"✓ {message}")
            
            Logger.info(t.PROFILE_CONNECTING)
            if progress_callback:
                progress_callback(t.PROFILE_STEP4)
            connect_success, connect_message = self._connect_to_network()
            if not connect_success:
                Logger.error(t.PROFILE_LOG_CONNECT_ERROR.format(message=connect_message))
                return False, connect_message
            Logger.info(f"✓ {connect_message}")
            
            Logger.info(t.PROFILE_VERIFYING)
            if progress_callback:
                progress_callback(t.PROFILE_STEP5)
            verify_success, verify_message = self._verify_connection()
            
            if verify_success:
                Logger.info(f"✓ {verify_message}")
                Logger.info(f"✓ {t.PROFILE_SUCCESS_COMPLETE}")
                return True, t.PROFILE_SUCCESS_COMPLETE
            else:
                # La verificación falló - comprobar si es por permisos de Windows
                is_permission_issue = "permisos" in verify_message.lower() or "permission" in verify_message.lower()
                
                if is_permission_issue:
                    # Los permisos de Windows impiden verificar, pero la conexión puede estar activa
                    Logger.warning(t.PROFILE_LOG_VERIFY_FAILED.format(message=verify_message))
                    Logger.info(t.PROFILE_LOG_VERIFY_PROBABLY_OK)
                    return True, t.PROFILE_SUCCESS_COMPLETE + " " + t.PROFILE_INFO_VERIFICATION_LIMITED
                else:
                    # Fallo de verificación real (no relacionado con permisos)
                    Logger.error(t.PROFILE_LOG_VERIFY_ERROR.format(message=verify_message))
                    return False, verify_message
            
        except Exception as e:
            error_msg = t.PROFILE_ERROR_UNEXPECTED.format(error=e)
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Métodos de pasos de conexión
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _install_wifi_profile(self) -> Tuple[bool, str]:
        """
        Instala el perfil WiFi para todos los usuarios usando netsh.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se instaló correctamente
        """
        try:
            if error := self._validate_file_exists(self._profile_path, t.PROFILE_ERROR_PROFILE_NOT_FOUND):
                return False, error
            
            command = ["netsh", "wlan", "add", "profile", f"filename={self._profile_path}", "user=all"]
            result = self._run_command(command)
            
            if result.returncode == 0:
                Logger.info(t.PROFILE_SUCCESS_INSTALLED)
                return True, t.PROFILE_SUCCESS_INSTALLED
            
            # Comprobar si el perfil ya existía
            if "ya está" in result.stdout.lower() or "already" in result.stdout.lower():
                Logger.info(t.PROFILE_SUCCESS_EXISTED)
                return True, t.PROFILE_SUCCESS_EXISTED
            
            Logger.error(t.PROFILE_ERROR_NETSH_LOG.format(error=result.raw_error))
            return False, t.PROFILE_ERROR_NETSH
                
        except Exception as e:
            Logger.error(t.PROFILE_ERROR_INSTALL_LOG.format(error=str(e)), exc_info=True)
            return False, t.PROFILE_ERROR_INSTALL
    
    def _update_credentials_xml(self) -> Tuple[bool, str]:
        """
        Actualiza el archivo credentials.xml con el usuario y contraseña proporcionados.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se actualizó correctamente
        """
        try:
            if error := self._validate_file_exists(self._credentials_path, t.PROFILE_ERROR_CREDS_NOT_FOUND):
                return False, error
            
            Logger.debug(t.PROFILE_LOG_PARSING_XML.format(path=self._credentials_path))
            tree = ET.parse(self._credentials_path)
            root = tree.getroot()
            
            # Registrar namespaces para preservar el formato XML
            for prefix, uri in self._EAP_NAMESPACES.items():
                ET.register_namespace(prefix if prefix else "", uri)
            
            username_elem = root.find(".//MsChapV2:Username", self._EAP_NAMESPACES)
            password_elem = root.find(".//MsChapV2:Password", self._EAP_NAMESPACES)
            
            if username_elem is None or password_elem is None:
                Logger.error(t.PROFILE_ERROR_XML_ELEMENTS)
                return False, t.PROFILE_ERROR_XML_ELEMENTS
            
            Logger.debug(t.PROFILE_LOG_UPDATING_USER.format(username=self.username))
            username_elem.text = self.username
            password_elem.text = self.password
            
            tree.write(self._credentials_path, encoding="UTF-8", xml_declaration=True)
            Logger.info(t.PROFILE_LOG_CREDS_UPDATED.format(path=self._credentials_path))
            
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
            if error := self._validate_file_exists(self._eap_executable_path, t.PROFILE_ERROR_EXE_NOT_FOUND):
                return False, error
            
            if error := self._validate_file_exists(self._credentials_path, t.PROFILE_ERROR_CREDS_NOT_FOUND):
                return False, error
            
            command = [self._eap_executable_path, self.ssid, "1", self._credentials_path, "/i"]
            result = self._run_command(command)
            
            if result.returncode == 0:
                Logger.info(t.PROFILE_SUCCESS_EAP)
                return True, t.PROFILE_SUCCESS_EAP
            
            Logger.error(t.PROFILE_ERROR_EAP_LOG.format(error=result.raw_error))
            return False, t.PROFILE_ERROR_EAP
                
        except Exception as e:
            Logger.error(t.PROFILE_ERROR_CONFIG_EAP_LOG.format(error=str(e)), exc_info=True)
            return False, t.PROFILE_ERROR_CONFIG_EAP
    
    def _connect_to_network(self) -> Tuple[bool, str]:
        """
        Conecta a la red WiFi usando netsh.
        
        Returns:
            Tupla (éxito, mensaje) donde éxito es True si se conectó correctamente
        """
        try:
            command = ["netsh", "wlan", "connect", f"name={self.ssid}"]
            result = self._run_command(command)
            
            # Debug: mostrar qué contiene la salida
            Logger.debug(t.PROFILE_LOG_RETURNCODE.format(code=result.returncode))
            Logger.debug(t.PROFILE_LOG_STDOUT.format(output=result.stdout[:200] if result.stdout else '(buit)'))
            Logger.debug(t.PROFILE_LOG_STDERR.format(output=result.stderr[:200] if result.stderr else '(buit)'))
            
            # Detectar avisos de permisos de Windows
            if self._has_permission_warning(result.combined_output):
                Logger.warning(t.PROFILE_WARNING_PERMISSIONS_IGNORED)
                Logger.info(t.PROFILE_INFO_CMD_EXECUTED)
                return True, t.PROFILE_SUCCESS_CMD_PENDING
            
            # Buscar mensajes de error reales (no de permisos)
            stdout_lower = result.stdout.lower()
            has_real_error = (
                ("no se encuentra" in stdout_lower or "not found" in stdout_lower)
                and "ubicación" not in result.combined_output
            ) or (
                ("no disponible" in stdout_lower or "not available" in stdout_lower)
                and "ubicación" not in result.combined_output
            )
            
            if has_real_error:
                Logger.error(t.PROFILE_ERROR_CONNECT_LOG.format(error=result.raw_error))
                return False, t.PROFILE_ERROR_CONNECT
            
            # Buscar mensajes de éxito
            has_success = (
                result.returncode == 0
                or "correctamente" in stdout_lower
                or "successfully" in stdout_lower
            )
            
            if has_success:
                success_msg = t.PROFILE_SUCCESS_COMMAND.format(ssid=self.ssid)
                Logger.info(success_msg)
                return True, success_msg
            
            # Sin éxito claro ni warning conocido -> error
            Logger.error(t.PROFILE_ERROR_CONNECT_LOG.format(error=result.raw_error))
            return False, t.PROFILE_ERROR_CONNECT
                
        except Exception as e:
            Logger.error(t.PROFILE_ERROR_CONNECT_COMMAND_LOG.format(error=str(e)), exc_info=True)
            return False, t.PROFILE_ERROR_CONNECT_COMMAND
    
    def _parse_connection_state(self, output: str) -> Optional[str]:
        """
        Parsea la salida de 'netsh wlan show interfaces' para obtener el estado.
        
        Args:
            output: Salida del comando netsh
        
        Returns:
            Estado de la conexión: 'connected', 'disconnected', 'authenticating', 
            'connecting', o None si no se encuentra
        """
        for line in output.split("\n"):
            line_lower = line.lower()
            if "estado" not in line_lower and "state" not in line_lower:
                continue
            
            if "desconectado" in line_lower or "disconnected" in line_lower:
                return "disconnected"
            if "autenticando" in line_lower or "authenticating" in line_lower:
                return "authenticating"
            if "conectando" in line_lower or "connecting" in line_lower:
                return "connecting"
            if "conectado" in line_lower or "connected" in line_lower:
                return "connected"
        
        return None
    
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
                
                result = self._run_command(["netsh", "wlan", "show", "interfaces"])
                
                # Detectar avisos de permisos de Windows
                if self._has_permission_warning(result.combined_output):
                    Logger.warning(t.PROFILE_WARNING_PERMISSIONS_VERIFY)
                    Logger.info(t.PROFILE_WARNING_PERMISSIONS_MAY_WORK)
                    return False, t.PROFILE_ERROR_PERMISSIONS_VERIFY
                
                if result.returncode != 0:
                    if attempt < max_attempts:
                        time.sleep(wait_seconds)
                    continue
                
                # Verificar que el SSID aparece en la salida
                if self.ssid.lower() not in result.stdout.lower():
                    if attempt < max_attempts:
                        time.sleep(wait_seconds)
                    continue
                
                # Parsear estado de conexión
                state = self._parse_connection_state(result.stdout)
                
                if state == "connected":
                    success_msg = t.PROFILE_SUCCESS_VERIFIED.format(ssid=self.ssid)
                    Logger.info(success_msg)
                    return True, success_msg
                
                if state == "disconnected":
                    error_msg = t.PROFILE_ERROR_AUTH
                    Logger.error(error_msg)
                    return False, error_msg
                
                if state == "authenticating":
                    Logger.debug(t.PROFILE_LOG_STATE_AUTH.format(attempt=attempt))
                elif state == "connecting":
                    Logger.debug(t.PROFILE_LOG_STATE_CONNECTING.format(attempt=attempt))
                
                if attempt < max_attempts:
                    time.sleep(wait_seconds)
            
            error_msg = t.PROFILE_ERROR_NO_VERIFY.format(ssid=self.ssid, attempts=max_attempts)
            Logger.warning(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = t.PROFILE_ERROR_VERIFY.format(error=str(e))
            Logger.error(error_msg, exc_info=True)
            return False, error_msg
