"""Módulo de traducciones para el texto de la GUI.

Este módulo contiene todas las cadenas de texto utilizadas en la GUI en catalán.
"""

# Título de ventana
WINDOW_TITLE = "Connector WiFi"
WINDOW_TITLE_MAIN = "WiFi de Centres Educatius"
HELP_BUTTON = "?"

# Sección de búsqueda
SEARCH_LABEL = "Cerca:"
SEARCH_PLACEHOLDER = "Introdueix el codi o el nom de centre..."

# Lista de centros
CENTERS_TITLE = "Centres Educatius"
CENTERS_TAB = "Centres"
CENTER_COUNT = "centres trobats"
NO_RESULTS = "No s'han trobat resultats"
NO_FAVORITES = "No tens cap centre favorit. Marca'n alguns amb ⭐"
NO_FAVORITES_SEARCH = (
    "No hi ha resultats a favorits per '{query}'. Prova a buscar en tots els centres."
)
SHOWING_FIRST_CENTERS = (
    "⚠️ Mostrant els primers {max} de {total} centres. Fes servir la cerca per filtrar."
)
SHOWING_CENTERS = "Mostrant {count} centres"

# Panel de centro seleccionado
SELECTED_CENTER_TITLE = "Centre Seleccionat"
CREDENTIALS_TITLE = "Credencials"
CENTER_CODE_LABEL = "Codi:"
CENTER_NAME_LABEL = "Nom:"
USERNAME_LABEL = "Usuari:"
PASSWORD_LABEL = "Contrasenya:"

# Botones
CONNECT_BUTTON = "Connectar"
DISCONNECT_BUTTON = "Desconnectar"
OPEN_LOGS_BUTTON = "Obrir Logs"
COPY_BUTTON = "Copiar"
SHOW_PASSWORD = "Mostrar"
HIDE_PASSWORD = "Ocultar"

# Mensajes de estado
STATUS_READY = "Preparat"
STATUS_CONNECTING = "Connectant..."
STATUS_CONNECTED = "Connectat"
STATUS_DISCONNECTED = "Desconnectat"
STATUS_ERROR = "Error"
STATUS_SELECT_CENTER = "Selecciona un centre per connectar"
STATUS_LOADING = "Carregant credencials..."
STATUS_LOADED = "Carregat {count} centres"
STATUS_LOADED_SEARCH = (
    "Carregat {count} centres. Utilitza la cerca per trobar el teu centre."
)

# Mensajes de conexión
MSG_CONNECTING_TO = "Connectant a {network}..."
MSG_CONNECTION_SUCCESS = "Connexió iniciada correctament"
MSG_CONNECTION_FAILED = "Error en la connexió: {error}"
MSG_DISCONNECTION_SUCCESS = "Desconnectat correctament"
MSG_DISCONNECTION_FAILED = "Error en desconnectar"

# Mensajes de error
ERROR_NO_CENTER_SELECTED = "Si us plau, selecciona un centre primer"
ERROR_ALREADY_CONNECTING = "Ja hi ha una connexió en curs"
ERROR_LOAD_CREDENTIALS = "Error en carregar les credencials: {error}"

# Mensajes del conector de perfiles
PROFILE_STARTING = "Iniciant connexió per perfil..."
PROFILE_STEP1 = "Pas 1/5: Instal·lant perfil WiFi..."
PROFILE_STEP2 = "Pas 2/5: Actualitzant credencials..."
PROFILE_STEP3 = "Pas 3/5: Configurant credencials EAP..."
PROFILE_STEP4 = "Pas 4/5: Connectant a la xarxa..."
PROFILE_STEP5 = "Pas 5/5: Verificant connexió..."

PROFILE_INSTALLING = "Instal·lant perfil WiFi..."
PROFILE_UPDATING_CREDS = "Actualitzant credencials en XML..."
PROFILE_CONFIGURING_EAP = "Configurant credencials EAP..."
PROFILE_CONNECTING = "Connectant a la xarxa..."
PROFILE_VERIFYING = "Verificant estat de connexió..."

PROFILE_SUCCESS_INSTALLED = "Perfil WiFi instal·lat correctament"
PROFILE_SUCCESS_EXISTED = "Perfil WiFi ja existia (actualitzat)"
PROFILE_SUCCESS_DELETED = "Perfil WiFi existent eliminat correctament"
PROFILE_INFO_NO_EXISTING_PROFILE = "No existia perfil previ per eliminar"
PROFILE_SUCCESS_UPDATED = "Credencials actualitzades en XML"
PROFILE_SUCCESS_EAP = "Credencials EAP configurades correctament"
PROFILE_SUCCESS_CONNECTED = "Connectat exitosament a '{ssid}'"
PROFILE_SUCCESS_COMMAND = "Comanda de connexió executada per '{ssid}'"
PROFILE_SUCCESS_VERIFIED = "Connexió verificada: Connectat a '{ssid}'"
PROFILE_SUCCESS_COMPLETE = "Connexió completada i verificada exitosament"

PROFILE_ERROR_PROFILE_NOT_FOUND = "Arxiu de perfil no trobat: {path}"
PROFILE_ERROR_NETSH = "Error de xarxa. Revisa els logs per a més detalls."
PROFILE_ERROR_NETSH_LOG = "Error de netsh: {error}"
PROFILE_ERROR_INSTALL = "Error en instal·lar perfil. Revisa els logs per a més detalls."
PROFILE_ERROR_INSTALL_LOG = "Error en instal·lar perfil: {error}"
PROFILE_ERROR_DELETE_LOG = "Error en eliminar perfil existent: {error}"
PROFILE_LOG_DELETING_PROFILE = "Eliminant perfil WiFi existent: {ssid}"
PROFILE_ERROR_CREDS_NOT_FOUND = "Arxiu credentials.xml no trobat: {path}"
PROFILE_ERROR_PARSING_XML = "Error en parsejar XML: {error}"
PROFILE_ERROR_UPDATE_CREDS = "Error en actualitzar credentials.xml: {error}"
PROFILE_ERROR_XML_ELEMENTS = "No s'han trobat elements Username/Password en el XML"
PROFILE_ERROR_EXE_NOT_FOUND = "Executable WLANSetEAPUserData.exe no trobat: {path}"
PROFILE_ERROR_EAP = (
    "Error en configurar credencials. Revisa els logs per a més detalls."
)
PROFILE_ERROR_EAP_LOG = "Error de WLANSetEAPUserData: {error}"
PROFILE_ERROR_CONFIG_EAP = (
    "Error en configurar credencials EAP. Revisa els logs per a més detalls."
)
PROFILE_ERROR_CONFIG_EAP_LOG = "Error en configurar credencials EAP: {error}"
PROFILE_ERROR_CONNECT = (
    "Error en connectar a la xarxa. Revisa els logs per a més detalls."
)
PROFILE_ERROR_CONNECT_LOG = "Error en connectar: {error}"
PROFILE_ERROR_CONNECT_COMMAND = (
    "Error en executar comanda de connexió. Revisa els logs per a més detalls."
)
PROFILE_ERROR_CONNECT_COMMAND_LOG = "Error en executar comanda de connexió: {error}"
PROFILE_ERROR_VERIFY = "Error en verificar connexió: {error}"
PROFILE_ERROR_NO_VERIFY = "No s'ha pogut verificar la connexió a '{ssid}' després de {attempts} intents. La xarxa pot estar autenticant o les credencials són incorrectes."
PROFILE_ERROR_AUTH = "Error d'autenticació: Credencials invàlides o xarxa no disponible"
PROFILE_ERROR_UNEXPECTED = "Error inesperat durant la connexió: {error}"

PROFILE_WARNING_NO_CREDS = (
    "No s'han proporcionat credencials, utilitzant les del XML existent"
)
PROFILE_WARNING_PERMISSIONS_IGNORED = (
    "Avís de permisos de Windows (ignorat, la connexió pot funcionar)"
)
PROFILE_WARNING_PERMISSIONS_VERIFY = (
    "No es pot verificar automàticament degut a restriccions de permisos de Windows"
)
PROFILE_WARNING_PERMISSIONS_MAY_WORK = "La connexió pot haver-se establert correctament"

PROFILE_INFO_CMD_EXECUTED = (
    "Comanda executada, la verificació posterior determinarà el resultat"
)
PROFILE_INFO_VERIFICATION_LIMITED = "(verificació limitada per permisos)"

PROFILE_SUCCESS_CMD_PENDING = "Comanda de connexió executada (verificació pendent)"
PROFILE_ERROR_PERMISSIONS_VERIFY = (
    "No es pot verificar degut a permisos de Windows (la connexió pot estar activa)"
)

PROFILE_LOG_INIT = "ProfileConnector inicialitzat per SSID: {ssid}, Usuari: {username}"
PROFILE_LOG_STARTING = "=== Iniciant Mètode de Connexió per Perfil ==="
PROFILE_LOG_VERIFYING = "Verificant connexió a '{ssid}' (màxim {attempts} intents)..."
PROFILE_LOG_ATTEMPT = "Intent {attempt}/{max_attempts}..."
PROFILE_LOG_STATE_AUTH = "Estat: Autenticant... (intent {attempt})"
PROFILE_LOG_STATE_CONNECTING = "Estat: Connectant... (intent {attempt})"
PROFILE_LOG_CMD_EXECUTING = "Executant comanda: {command}"
PROFILE_LOG_CREDS_UPDATED = "Credencials actualitzades a {path}"
PROFILE_LOG_PARSING_XML = "Parsejant XML: {path}"
PROFILE_LOG_UPDATING_USER = "Actualitzant usuari: {username}"
PROFILE_LOG_RETURNCODE = "returncode: {code}"
PROFILE_LOG_STDOUT = "stdout: {output}"
PROFILE_LOG_STDERR = "stderr: {output}"
PROFILE_LOG_INSTALL_ERROR = "Error en instal·lar perfil: {message}"
PROFILE_LOG_UPDATE_ERROR = "Error en actualitzar credencials: {message}"
PROFILE_LOG_CONFIG_ERROR = "Error en configurar credencials: {message}"
PROFILE_LOG_CONNECT_ERROR = "Error en connectar: {message}"
PROFILE_LOG_VERIFY_ERROR = "Error de verificació: {message}"
PROFILE_LOG_VERIFY_FAILED = "No s'ha pogut verificar: {message}"
PROFILE_LOG_VERIFY_PROBABLY_OK = "La connexió probablement s'ha establert correctament"

# Mensajes de limpieza de credenciales
PROFILE_CLEAN_TEMPLATE_NOT_FOUND = "Plantilla de credencials no trobada: {path}"
PROFILE_CLEAN_FILE_NOT_EXISTS = "Arxiu de credencials no existeix: {path}"
PROFILE_CLEAN_SUCCESS = "Arxiu credentials.xml restaurat a configuració per defecte"
PROFILE_CLEAN_ERROR = "Error en netejar credentials.xml: {error}"
PROFILE_CLEAN_ERROR_ON_CLOSE = "Error en netejar credencials al tancar: {error}"

# Mensajes del gestor de credenciales
CREDS_LOG_INIT = "CredentialsManager inicialitzat amb ruta: {path}"
CREDS_LOG_LOADING = "Carregant credencials des de {path}"
CREDS_LOG_LOADING_VAULT = "Carregant credencials des de vault: {path}"
CREDS_LOG_JSON_LOADED = "Arxiu JSON carregat exitosament"
CREDS_LOG_LOADED_SUCCESS = "Carregat {count} centres exitosament"
CREDS_LOG_RETURNING_ALL = "Retornant tots els {count} centres"
CREDS_LOG_SEARCH_CODE = "Cercant centre per codi: {code}"
CREDS_LOG_FOUND_CENTER = "Centre trobat: {name}"
CREDS_LOG_CODE_NOT_FOUND = "Centre amb codi '{code}' no trobat"
CREDS_LOG_SEARCH_NAME = "Cercant centre per nom: {name}"
CREDS_LOG_NAME_NOT_FOUND = "Centre amb nom '{name}' no trobat"
CREDS_LOG_SEARCHING = "Cercant centres amb consulta: {query}"
CREDS_LOG_EMPTY_QUERY = "Consulta buida, retornant tots els centres"
CREDS_LOG_FOUND_MATCHING = "Trobats {count} centres coincidents"
CREDS_WARNING_SKIP_ENTRY = "Ometent entrada de centre invàlida: {error}"

CREDS_ERROR_FILE_NOT_FOUND = "Arxiu de credencials no trobat: {path}"
CREDS_ERROR_INVALID_JSON = "JSON invàlid a {path}: {error}"
CREDS_ERROR_UNEXPECTED = "Error inesperat carregant credencials: {error}"
CREDS_ERROR_INVALID_STRUCTURE = (
    "Estructura de credencials invàlida a {path}: s'esperava un array"
)
CREDS_ERROR_NOT_DICT = "L'entrada de centre ha de ser un diccionari"
CREDS_ERROR_MISSING_FIELD = "Falta el camp requerit: {field}"

# Mensajes del vault
VAULT_DIALOG_TITLE = "Accés al vault"
VAULT_PROMPT_TITLE = "Introdueix la contrasenya del vault"
VAULT_PROMPT_MESSAGE = "La informació sensible està xifrada en un vault.\nIntrodueix la contrasenya per continuar."
VAULT_PASSWORD_PLACEHOLDER = "Contrasenya del vault"
VAULT_UNLOCK_BUTTON = "Desbloquejar"
VAULT_CANCEL_BUTTON = "Cancel·lar"
VAULT_ERROR_TITLE = "Error de vault"
VAULT_ERROR_INVALID_PASSWORD = "Contrasenya incorrecta. Torna-ho a provar."
VAULT_ERROR_UNREADABLE = "No s'ha pogut llegir el vault: {error}"
VAULT_ERROR_UNLOCK_ABORTED = "Vault no desbloquejat"

VAULT_STATUS_LOADED = "Vault {version} carregat ({generated_at})"
VAULT_STATUS_LOADED_VERSION = "Vault {version} carregat"
VAULT_STATUS_LOADED_GENERIC = "Vault carregat"

VAULT_LOG_INIT = "VaultManager inicialitzat amb ruta: {path}"
VAULT_LOG_DECRYPTED = "Vault descifrat correctament"
VAULT_LOG_LOADED = "Vault carregat amb {count} centres"
VAULT_LOG_PASSWORD_CANCELLED = "Contrasenya del vault cancel·lada per l'usuari"
VAULT_LOG_INVALID_PASSWORD = "Contrasenya del vault invàlida"
VAULT_LOG_LOAD_ERROR = "Error carregant el vault: {error}"

VAULT_ERROR_FILE_NOT_FOUND = "Arxiu de vault no trobat: {path}"
VAULT_ERROR_FILE_READ = "Error en llegir el vault: {path} ({error})"
VAULT_ERROR_INVALID_FORMAT = "Format de vault invàlid"
VAULT_ERROR_INVALID_MAGIC = "Magic del vault invàlid"
VAULT_ERROR_INVALID_JSON = "JSON invàlid dins el vault: {error}"
VAULT_ERROR_INVALID_STRUCTURE = "Estructura de vault invàlida"
VAULT_ERROR_METADATA_INVALID = "Metadades del vault invàlides"
VAULT_ERROR_MISSING_CENTERS = "El vault no conté la llista de centres"
VAULT_ERROR_DECRYPT_FAILED = "Error en descifrar el vault: {error}"

# Mensajes del gestor de red
NET_LOG_INIT = "NetworkManager inicialitzat"
NET_LOG_SCANNING = "Escanejant xarxes WiFi disponibles"
NET_LOG_FOUND_NETWORKS = "Trobades {count} xarxes disponibles"
NET_LOG_NETWORKS_LIST = "Xarxes: {networks}"
NET_LOG_CHECKING_NETWORK = "Comprovant si la xarxa '{ssid}' està disponible"
NET_LOG_NETWORK_AVAILABLE = "Xarxa '{ssid}' està disponible"
NET_LOG_NETWORK_NOT_AVAILABLE = "Xarxa '{ssid}' no està disponible"
NET_LOG_DISCONNECTING = "Intentant desconnectar de la xarxa WiFi"
NET_LOG_DISCONNECT_SUCCESS = "Desconnectat exitosament de la xarxa WiFi"
NET_LOG_EXECUTING_CMD = "Executant comanda: {command}"
NET_LOG_CMD_FAILED = "Comanda netsh ha fallat amb codi de retorn {code}"
NET_LOG_CMD_OUTPUT = "Sortida de la comanda: {output}"
NET_LOG_PARSED_SSIDS = "Parseats {count} SSIDs únics de la sortida"

NET_ERROR_GET_NETWORKS = "Error en obtenir xarxes disponibles: {error}"
NET_ERROR_DISCONNECT = "Error en desconnectar de la xarxa: {error}"

# Mensajes de log de MainWindow
MAIN_LOG_INIT = "Inicialitzant MainWindow"
MAIN_LOG_ICON_SET = "Icona de finestra establerta des de: {path}"
MAIN_LOG_ICON_NOT_FOUND = "Arxiu d'icona no trobat: {path}"
MAIN_LOG_ICON_ERROR = "No s'ha pogut establir la icona de la finestra: {error}"
MAIN_LOG_LOAD_ERROR = "Error en carregar les credencials: {error}"
MAIN_LOG_INIT_SUCCESS = "MainWindow inicialitzat exitosament"
MAIN_LOG_STARTING_GUI = "Iniciant bucle principal de la GUI"
MAIN_LOG_STATUS_UPDATE = "Actualitzant estat: {type} - {message}"
MAIN_LOG_SETUP_UI = "Configurant components de la interfície"
MAIN_LOG_UI_COMPLETE = "Configuració de la interfície completada"
MAIN_LOG_CREATE_SEARCH = "Creant marc de cerca"
MAIN_LOG_SEARCH_CREATED = "Marc de cerca creat"
MAIN_LOG_SEARCH_CHANGED = "Consulta de cerca canviada: {query}"
MAIN_LOG_FILTERING = "Filtrant centres amb consulta: '{query}'"
MAIN_LOG_FOUND_MATCHING = "Trobats {count} centres coincidents"
MAIN_LOG_CREATE_TABLE = "Creant taula de centres"
MAIN_LOG_TABLE_CREATED = "Taula de centres creada"
MAIN_LOG_POPULATING = "Omplint taula de centres amb {count} centres"
MAIN_LOG_TABLE_POPULATED = "Taula de centres omplerta"
MAIN_LOG_CENTER_SELECTED = "Centre seleccionat: {code} - {name}"
MAIN_LOG_CREATE_CREDS_PANEL = "Creant panell de credencials"
MAIN_LOG_CREDS_PANEL_CREATED = "Panell de credencials creat"
MAIN_LOG_USERNAME_COPIED = "Nom d'usuari copiat al porta-retalls"
MAIN_LOG_PASSWORD_COPIED = "Contrasenya copiada al porta-retalls"
MAIN_LOG_CREATE_BUTTONS = "Creant botons d'acció"
MAIN_LOG_BUTTONS_CREATED = "Botons d'acció creats"
MAIN_LOG_CREATE_STATUS = "Creant barra d'estat"
MAIN_LOG_STATUS_CREATED = "Barra d'estat creada"
MAIN_LOG_CONNECT_NO_CENTER = "Connectar clicat però no hi ha centre seleccionat"
MAIN_LOG_CONNECT_IN_PROGRESS = "Connexió ja en curs"
MAIN_LOG_CONNECT_CLICKED = "Botó de connectar clicat per al centre: {code}"
MAIN_LOG_PROFILE_CLICKED = "Botó de Connectar via Perfil clicat"
MAIN_LOG_PROFILE_NO_CENTER = (
    "Connectar via Perfil clicat però no hi ha centre seleccionat"
)
MAIN_LOG_PROFILE_STARTING = "Iniciant connexió basada en perfil per al centre: {code}"
MAIN_LOG_PROFILE_ERROR = "Error en la connexió via perfil: {error}"
MAIN_LOG_PROFILE_COMPLETED = "Fil de connexió per perfil completat"
MAIN_LOG_LOGS_CLICKED = "Botó d'Obrir Logs clicat"
MAIN_LOG_LOGS_OPENED = "Carpeta de logs oberta: {path}"
MAIN_LOG_LOGS_ERROR = "Error en obrir la carpeta de logs: {error}"
MAIN_LOG_DISCONNECT_CLICKED = "Botó de desconnectar clicat"
MAIN_LOG_DISCONNECT_IN_PROGRESS = (
    "No es pot desconnectar mentre la connexió està en curs"
)
MAIN_LOG_DISCONNECT_ERROR = "Error durant la desconnexió: {error}"

# Mensajes de main.py
APP_STARTING = "Iniciant aplicació WiFi Connector"
APP_CLOSED = "Aplicació WiFi Connector tancada normalment"
APP_INTERRUPTED = "Aplicació interrompuda per l'usuari (Ctrl+C)"
APP_ERROR_START = "Error en iniciar WiFi Connector: {error}"
APP_ERROR_MESSAGE = "Error: No s'ha pogut iniciar l'aplicació WiFi Connector"
APP_ERROR_DETAILS = "Detalls: {error}"
APP_ERROR_CHECK_LOGS = "Si us plau, revisa els logs per a més informació."

# Mensajes de búsqueda
SEARCH_PROMPT = "Escriu a la cerca per trobar el teu centre educatiu"
SEARCH_PROMPT_HINT = "Utilitza la cerca per filtrar els {count} centres disponibles"

# Mensajes de error de configuración (config.py)
CONFIG_ERROR_PAUSE_NEGATIVE = (
    "pause_duration ha de ser no negatiu, s'ha obtingut {value}"
)
CONFIG_ERROR_WAIT_NEGATIVE = (
    "credential_dialog_wait_time ha de ser no negatiu, s'ha obtingut {value}"
)
CONFIG_ERROR_FILE_NOT_FOUND = "Arxiu de configuració no trobat: {path}"
CONFIG_ERROR_UNSUPPORTED_FORMAT = "Format d'arxiu no suportat: {suffix}. Utilitza .json"

# Mensajes de error de favoritos (favorites_manager.py)
FAV_ERROR_SAVE_FAILED = "Error en desar els favorits: {error}"
FAV_ERROR_INVALID_ENTRY_FORMAT = "Format de favorit no reconegut"

# Mensajes de log de favoritos (favorites_manager.py)
FAV_LOG_LOADED = "Carregats {count} favorit(s)"
FAV_LOG_AUTO_CLEANUP = "Auto-neteja: eliminats {count} favorit(s) obsolet(s)"
FAV_LOG_ADDED = "Afegit a favorits: {code} - {name}"
FAV_LOG_REMOVED = "Eliminat de favorits: {code}"
FAV_LOG_SAVED = "Favorits desats correctament a {path}: {count} centre(s)"
FAV_LOG_FILE_NOT_EXISTS = (
    "L'arxiu de favorits no existeix: {path}, iniciant amb llista buida"
)
FAV_LOG_INVALID_FORMAT = (
    "fav.json té format invàlid (s'esperava array), iniciant amb llista buida"
)
FAV_LOG_OBSOLETE_REMOVED = "Favorit obsolet eliminat: {code}"
FAV_LOG_INVALID_ENTRY = "Entrada invàlida a fav.json ignorada: {error}"
FAV_LOG_FORMAT_MIGRATED = "Format de fav.json migrat a llista de codis"
FAV_LOG_PARSE_ERROR = "Error en parsejar fav.json: {error}, iniciant amb llista buida"
FAV_LOG_UNEXPECTED_ERROR = "Error inesperat en carregar favorits: {error}"
FAV_LOG_INVALID_CENTER = "Intent d'afegir centre no vàlid a favorits: {code}"
FAV_LOG_ALREADY_FAVORITE = "El centre ja és favorit: {code}"
FAV_LOG_ERROR_SAVING_ADD = "Error en desar favorits després d'afegir: {error}"
FAV_LOG_NOT_FAVORITE = "El centre no està a favorits: {code}"
FAV_LOG_ERROR_SAVING_REMOVE = "Error en desar favorits després d'eliminar: {error}"
FAV_LOG_ATTEMPTING_SAVE = "Intentant desar {count} favorits a: {path}"
FAV_LOG_DIR_CONFIRMED = "Directori confirmat: {path}"
FAV_LOG_WRITING_TEMP = "Escrivint arxiu temporal: {path}"
FAV_LOG_RENAMING = "Reanomenant {temp} a {final}"
FAV_LOG_ERROR_SAVING = "Error en desar favorits a {path}: {error}"

# Mensajes de log de vista de favoritos (main_window.py)
VIEW_LOG_SWITCHED_FAVORITES = "Canviat al mode de visualització de favorits"
VIEW_LOG_SWITCHED_ALL = "Canviat al mode de visualització de tots els centres"
VIEW_LOG_FAV_ADDED = "Afegit {code} a favorits"
VIEW_LOG_FAV_REMOVED = "Eliminat {code} de favorits"

# Mensajes adicionales de main_window.py
MAIN_LOG_FAV_ICONS_LOADED = "Icones de favorits carregades correctament"
MAIN_LOG_FAV_ICONS_NOT_FOUND = (
    "Icones de favorits no trobades: {fav_path}, {fav_unchecked_path}"
)
MAIN_LOG_ERROR_LOADING_ICONS = "Error en carregar icones de favorits: {error}"
MAIN_LOG_FILTERING_FAVORITES = (
    "Filtrant en mode favorits, llista base té {count} centres"
)
MAIN_LOG_FILTERING_ALL = "Filtrant en mode tots, llista base té {count} centres"
MAIN_LOG_ERROR_TOGGLE_FAV = "Error en canviar favorit per a {code}: {error}"
MAIN_LOG_ERROR_TOGGLE_VIEW = "Error en canviar mode de vista: {error}"
MAIN_LOG_OPENING_ABOUT = "Obrint finestra Acerca de"
MAIN_LOG_ERROR_OPENING_ABOUT = "Error en obrir finestra Acerca de: {error}"
MAIN_LOG_CONNECTION_THREAD_COMPLETED = "Fil de connexió completat"
MAIN_LOG_CONNECTION_THREAD_STARTED = "Fil de connexió iniciat"
MAIN_LOG_WINDOW_CLOSE_REQUESTED = "Tancament de finestra sol·licitat"
MAIN_LOG_CONNECTION_IN_PROGRESS = "Connexió en curs, esperant finalització"
MAIN_LOG_WINDOW_CLOSED = "Finestra tancada"

# Mensajes de theme.py
THEME_LOG_CONFIGURED = "Tema fosc configurat correctament"
THEME_ERROR_NOT_INSTALLED = "customTkinter no està instal·lat: {error}"
THEME_ERROR_SETUP = "Error en configurar el tema fosc: {error}"

# Mensajes de estado de la interfaz (update_status en main_window.py)
STATUS_ERROR_LOAD_CREDS = "Error en carregar les credencials: {error}"
STATUS_FAV_REMOVED = "Centre {code} eliminat de favorits"
STATUS_FAV_ADDED = "Centre {code} afegit a favorits"
STATUS_ERROR_TOGGLE_FAV = "Error en modificar favorit: {error}"
STATUS_SHOWING_FAVORITES = "Mostrant només els centres favorits"
STATUS_SHOWING_ALL = "Mostrant tots els centres"
STATUS_ERROR_TOGGLE_VIEW = "Error en canviar el mode de vista: {error}"
STATUS_USERNAME_COPIED = "Usuari copiat al portapapers"
STATUS_PASSWORD_COPIED = "Contrasenya copiada al portapapers"
STATUS_ERROR_NO_CENTER = "Si us plau, selecciona un centre primer"
STATUS_CONNECTING_STARTING = "Realitzant la connexió"
STATUS_CONNECTING_PROFILE = "Connectant via perfil de Windows..."
STATUS_ERROR_OPEN_LOGS = "Error en obrir logs: {error}"
STATUS_ERROR_OPEN_ABOUT = "Error en obrir finestra About: {error}"
STATUS_ERROR_DISCONNECT_IN_PROGRESS = "No es pot desconnectar mentre es fa la connexió"
STATUS_DISCONNECTING = "Desconnectant..."
STATUS_DISCONNECTED_SUCCESS = "Desconnectat correctament"
STATUS_DISCONNECTED_ERROR = "Error en desconnectar"
STATUS_ERROR_DISCONNECT = "Error en desconnectar: {error}"
STATUS_ERROR_CONNECTION_CHECK_LOGS = (
    "Error de connexió. Revisa els Logs per més detalls."
)
STATUS_ERROR_CONNECTION_FAILED = "Connection error: {error}"
# About window
ABOUT_TITLE = "WiFi de Centres Educatius"
ABOUT_VERSION = "Versió 2.0.0"
ABOUT_DEVELOPER = "Desenvolupat per:"
ABOUT_DEVELOPER_NAME = "Àlex Garcia Vilà"
ABOUT_LINKEDIN = "Veure Perfil de LinkedIn"
ABOUT_PORTFOLIO = "Visita el meu portafolis"
ABOUT_VAULT_INFO = "Vault {version} ({generated_at})"
ABOUT_VAULT_INFO_VERSION = "Vault {version}"


# Mensajes de log para errores de conexión
MAIN_LOG_CONNECTION_ERROR = "Error en la connexió: {error}"
