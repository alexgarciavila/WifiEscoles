"""Clases de excepciones para WiFi Connector.

Este módulo define todas las excepciones personalizadas utilizadas
en la aplicación WiFi Connector.
"""


class WiFiConnectorError(Exception):
    """Excepción base para todos los errores de WiFi Connector.

    Esta es la clase de excepción padre para todas las excepciones
    personalizadas lanzadas por el sistema WiFi Connector. Capturar
    esta excepción capturará todos los errores específicos de WiFi Connector.
    """
    pass


class CredentialsFileError(WiFiConnectorError):
    """Lanzada cuando el archivo de credenciales no se encuentra o no es accesible.

    Esta excepción se lanza cuando el archivo JSON de credenciales
    no existe, no se puede leer, o tiene permisos incorrectos.
    """
    pass


class JSONParseError(WiFiConnectorError):
    """Lanzada cuando el archivo JSON de credenciales no se puede analizar.

    Esta excepción se lanza cuando el archivo JSON está malformado,
    tiene sintaxis inválida, o no contiene la estructura esperada
    y los campos requeridos.
    """
    pass
