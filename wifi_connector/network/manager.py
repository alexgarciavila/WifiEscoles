"""
Módulo de gestión de red para WiFi Connector.

Este módulo proporciona funcionalidad para gestionar operaciones de red WiFi
en Windows usando comandos netsh, incluyendo escaneo de redes, gestión de conexiones,
e interacción con el panel de red.
"""

import subprocess
from typing import List
from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


class NetworkManager:
    """
    Gestiona operaciones de red WiFi usando comandos netsh de Windows.

    Proporciona métodos para escanear redes disponibles, verificar disponibilidad
    de redes, desconectarse de redes, y abrir el panel de red de Windows.
    """

    def __init__(self) -> None:
        """Inicializa el NetworkManager."""
        Logger.debug(t.NET_LOG_INIT)

    def get_available_networks(self) -> List[str]:
        """
        Obtiene lista de redes WiFi disponibles.

        Ejecuta comando netsh para escanear redes disponibles y
        parsea la salida para extraer nombres SSID.

        Returns:
            Lista de nombres SSID de redes disponibles. Devuelve lista vacía
            si el comando falla o no se encuentran redes.
        """
        Logger.info(t.NET_LOG_SCANNING)

        try:
            output = self._execute_netsh_command(
                ["wlan", "show", "networks"]
            )
            networks = self._parse_network_list(output)
            Logger.info(t.NET_LOG_FOUND_NETWORKS.format(count=len(networks)))
            Logger.debug(t.NET_LOG_NETWORKS_LIST.format(networks=networks))
            return networks
        except Exception as e:
            Logger.error(
                t.NET_ERROR_GET_NETWORKS.format(error=e),
                exc_info=True
            )
            return []

    def is_network_available(self, ssid: str) -> bool:
        """
        Verifica si una red específica está disponible.

        Args:
            ssid: SSID de la red a verificar

        Returns:
            True si la red está disponible, False en caso contrario
        """
        Logger.debug(t.NET_LOG_CHECKING_NETWORK.format(ssid=ssid))
        networks = self.get_available_networks()
        is_available = ssid in networks

        if is_available:
            Logger.info(t.NET_LOG_NETWORK_AVAILABLE.format(ssid=ssid))
        else:
            Logger.warning(t.NET_LOG_NETWORK_NOT_AVAILABLE.format(ssid=ssid))

        return is_available

    def disconnect(self) -> bool:
        """
        Desconecta de la red WiFi actual.

        Returns:
            True si la desconexión fue exitosa, False en caso contrario
        """
        Logger.info(t.NET_LOG_DISCONNECTING)

        try:
            self._execute_netsh_command(["wlan", "disconnect"])
            Logger.info(t.NET_LOG_DISCONNECT_SUCCESS)
            return True
        except Exception as e:
            Logger.error(
                t.NET_ERROR_DISCONNECT.format(error=e),
                exc_info=True
            )
            return False



    def _execute_netsh_command(self, args: List[str]) -> str:
        """
        Ejecuta comando netsh y devuelve la salida.

        Args:
            args: Lista de argumentos de comando a pasar a netsh

        Returns:
            Salida del comando como cadena decodificada con codificación CP850

        Raises:
            subprocess.CalledProcessError: Si la ejecución del comando falla
        """
        command = ["netsh"] + args
        Logger.debug(t.NET_LOG_EXECUTING_CMD.format(command=' '.join(command)))

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                encoding='cp850'
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            Logger.error(
                t.NET_LOG_CMD_FAILED.format(code=e.returncode)
            )
            Logger.debug(t.NET_LOG_CMD_OUTPUT.format(output=e.output))
            raise

    def _parse_network_list(self, output: str) -> List[str]:
        """
        Parsea la salida de netsh para extraer SSIDs.

        Extrae nombres SSID de líneas que contienen "SSID" seguido de
        dos puntos. Maneja múltiples SSIDs y filtra duplicados.

        Args:
            output: Salida cruda del comando netsh wlan show networks

        Returns:
            Lista de nombres SSID únicos en orden de aparición
        """
        networks = []
        lines = output.split('\n')

        for line in lines:
            line = line.strip()
            if 'SSID' in line and ':' in line:
                if line.startswith('SSID'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        ssid = parts[1].strip()
                        if ssid and ssid not in networks:
                            networks.append(ssid)

        Logger.debug(t.NET_LOG_PARSED_SSIDS.format(count=len(networks)))
        return networks
