"""Módulo de ventana principal para la GUI de WiFi Connector.

Este módulo proporciona la clase MainWindow que implementa la interfaz
gráfica de usuario principal para la aplicación WiFi Connector.
"""

import threading
from typing import Optional, List
import customtkinter as ctk
from PIL import Image, ImageTk
import os

from wifi_connector.data.credentials_manager import (
    CredentialsManager,
    CenterCredentials
)
from wifi_connector.core.profile_connector import ProfileConnector
from wifi_connector.core.config import Config
from wifi_connector.utils.logger import Logger
from wifi_connector.utils.paths import get_base_path
from wifi_connector.utils import translations as t
from wifi_connector.gui.about import AboutWindow


class MainWindow:
    """Ventana principal de la GUI para la aplicación WiFi Connector.

    Proporciona una interfaz moderna para seleccionar centros y conectarse
    a redes WiFi usando customTkinter.
    """

    def __init__(self):
        """Inicializa la ventana principal de la GUI."""
        Logger.info(t.MAIN_LOG_INIT)

        self.window = ctk.CTk()
        self.window.title("Wifi de Centres Educatius de Catalunya")
        self.window.geometry("700x600")
        self.window.minsize(700, 600)

        try:
            ico_path = get_base_path() / "images" / "wifi_icon.ico"
            if ico_path.exists():
                self.window.iconbitmap(str(ico_path))
                Logger.info(t.MAIN_LOG_ICON_SET.format(path=ico_path))
            else:
                Logger.warning(t.MAIN_LOG_ICON_NOT_FOUND.format(path=ico_path))
        except Exception as e:
            Logger.error(t.MAIN_LOG_ICON_ERROR.format(error=e), exc_info=True)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.credentials_manager = CredentialsManager()
        self.profile_connector: Optional[ProfileConnector] = None

        self.selected_center: Optional[CenterCredentials] = None
        self.all_centers: List[CenterCredentials] = []
        self.is_connecting = False

        self.search_entry: Optional[ctk.CTkEntry] = None
        self.centers_frame: Optional[ctk.CTkScrollableFrame] = None
        self.credentials_panel: Optional[ctk.CTkFrame] = None
        self.username_entry: Optional[ctk.CTkEntry] = None
        self.password_entry: Optional[ctk.CTkEntry] = None
        self.disconnect_button: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.center_count_label: Optional[ctk.CTkLabel] = None
        self.center_buttons: List[ctk.CTkButton] = []

        self._setup_ui()

        try:
            self.credentials_manager.load_credentials()
            self.all_centers = self.credentials_manager.get_all_centers()
            
            self._populate_centers_table([], show_prompt=True)
            self.update_status(
                f"Carregat {len(self.all_centers)} centres. Utilitza la cerca per trobar el teu centre.",
                "info"
            )
        except Exception as e:
            Logger.error(t.MAIN_LOG_LOAD_ERROR.format(error=e))
            self.update_status(f"Error en carregar les credencials: {e}", "error")

        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        Logger.info(t.MAIN_LOG_INIT_SUCCESS)

    def run(self) -> None:
        """Inicia el bucle principal de la GUI."""
        Logger.info(t.MAIN_LOG_STARTING_GUI)
        self.window.mainloop()

    def update_status(self, message: str, status_type: str) -> None:
        """Actualiza la etiqueta de estado con mensaje y código de color.

        Args:
            message: Mensaje de estado a mostrar
            status_type: Tipo de estado - "success", "error", o "info"
        """
        Logger.debug(t.MAIN_LOG_STATUS_UPDATE.format(type=status_type, message=message))

        color_map = {
            "success": "#2ecc71",
            "error": "#e74c3c",
            "info": "#3498db"
        }

        color = color_map.get(status_type, "#95a5a6")

        if self.status_label:
            self.status_label.configure(text=message, text_color=color)

    def _setup_ui(self) -> None:
        """Configura todos los componentes de la UI."""
        Logger.debug(t.MAIN_LOG_SETUP_UI)

        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="WiFi de Centres Educatius",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", expand=True)

        # About button (circular with ?)
        about_btn = ctk.CTkButton(
            header_frame,
            text="?",
            width=30,
            height=30,
            corner_radius=5,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self._on_about_clicked
        )
        about_btn.pack(side="right", padx=4, pady=4)

        # Create search frame
        self._create_search_frame(main_container)

        # Create centers table
        self._create_centers_table(main_container)

        # Create credentials display panel
        self._create_credentials_panel(main_container)

        # Create action buttons
        self._create_action_buttons(main_container)

        # Create status bar
        self._create_status_bar(main_container)

        Logger.debug(t.MAIN_LOG_UI_COMPLETE)

    def _create_search_frame(self, parent: ctk.CTkFrame) -> None:
        """Crea el frame de entrada de búsqueda.

        Args:
            parent: Frame padre donde adjuntar el frame de búsqueda.
        """
        Logger.debug(t.MAIN_LOG_CREATE_SEARCH)

        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", pady=(0, 10))

        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="Cerca:",
            font=ctk.CTkFont(size=14)
        )
        search_label.pack(side="left", padx=(10, 5))

        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Introdueix el codi o el nom de centre...",
            width=400
        )
        self.search_entry.pack(
            side="left", padx=(
                0, 10), fill="x", expand=True)

        # Bind search event
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        Logger.debug(t.MAIN_LOG_SEARCH_CREATED)

    def _on_search_changed(self, event) -> None:
        """Maneja los cambios en la entrada de búsqueda para filtrado en tiempo real.

        Args:
            event: Objeto evento de Tkinter.
        """
        query = self.search_entry.get() if self.search_entry else ""
        Logger.debug(t.MAIN_LOG_SEARCH_CHANGED.format(query=query))
        self._filter_centers(query)

    def _filter_centers(self, query: str) -> None:
        """Filtra y actualiza la tabla de centros según la consulta.

        Args:
            query: Cadena de texto de búsqueda.
        """
        Logger.debug(t.MAIN_LOG_FILTERING.format(query=query))

        if not query:
            # Don't show centers if query is empty - show prompt instead
            self._populate_centers_table([], show_prompt=True)
            # Update count label with search prompt
            if self.center_count_label:
                self.center_count_label.configure(
                    text=t.SEARCH_PROMPT_HINT.format(count=len(self.all_centers)),
                    text_color="#3498db"
                )
            return
        
        # Filter centers using CredentialsManager
        filtered_centers = self.credentials_manager.search_centers(query)

        Logger.debug(t.MAIN_LOG_FOUND_MATCHING.format(count=len(filtered_centers)))

        # Update the centers table
        self._populate_centers_table(filtered_centers)

    def _create_centers_table(self, parent: ctk.CTkFrame) -> None:
        """Crea el widget de lista/tabla de centros con scroll.

        Args:
            parent: Frame padre donde adjuntar la tabla de centros.
        """
        Logger.debug(t.MAIN_LOG_CREATE_TABLE)

        # Create frame for table header and count
        table_header_frame = ctk.CTkFrame(parent)
        table_header_frame.pack(fill="x", pady=(0, 5))

        # Table title
        table_title = ctk.CTkLabel(
            table_header_frame,
            text="Centres",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        table_title.pack(side="left", padx=10)

        # Center count label
        self.center_count_label = ctk.CTkLabel(
            table_header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#95a5a6"
        )
        self.center_count_label.pack(side="left", padx=10)

        # Create scrollable frame for centers with reduced height for credentials panel
        self.centers_frame = ctk.CTkScrollableFrame(
            parent,
            height=180
        )
        self.centers_frame.pack(fill="both", expand=True, pady=(0, 10))

        Logger.debug(t.MAIN_LOG_TABLE_CREATED)

    def _populate_centers_table(
        self,
        centers: List[CenterCredentials],
        show_prompt: bool = False
    ) -> None:
        """Rellena la tabla con los datos de los centros.

        Args:
            centers: Lista de CenterCredentials a mostrar.
            show_prompt: Si es True, muestra mensaje de búsqueda en lugar de "Sin resultados".
        """
        Logger.debug(t.MAIN_LOG_POPULATING.format(count=len(centers)))

        # Clear existing widgets (both frames and buttons)
        for widget in self.center_buttons:
            widget.destroy()
        self.center_buttons.clear()

        # Reset scroll position to top to fix bug when filtering from long list to short list
        if self.centers_frame and hasattr(self.centers_frame, '_parent_canvas'):
            self.centers_frame._parent_canvas.yview_moveto(0)

        if not centers:
            if show_prompt:
                # Show search prompt message
                prompt_label = ctk.CTkLabel(
                    self.centers_frame,
                    text=t.SEARCH_PROMPT,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#3498db"
                )
                prompt_label.pack(pady=40)
                self.center_buttons.append(prompt_label)
                
                # Update count label for prompt
                if self.center_count_label:
                    self.center_count_label.configure(
                        text=t.SEARCH_PROMPT_HINT.format(count=len(self.all_centers)),
                        text_color="#3498db"
                    )
            else:
                # Show "No results found" message
                no_results_label = ctk.CTkLabel(
                    self.centers_frame,
                    text="No s'han trobat resultats",
                    font=ctk.CTkFont(size=14),
                    text_color="#95a5a6"
                )
                no_results_label.pack(pady=20)
                self.center_buttons.append(no_results_label)

                # Update count label for no results
                if self.center_count_label:
                    self.center_count_label.configure(
                        text="No s'han trobat resultats",
                        text_color="#e74c3c"
                    )
            return

        # Limit display to first 20 centers for performance
        MAX_DISPLAY = 20
        centers_to_display = centers[:MAX_DISPLAY]
        
        # Create a button for each center
        for center in centers_to_display:
            # Create frame for each center row
            center_frame = ctk.CTkFrame(self.centers_frame)
            center_frame.pack(fill="x", padx=5, pady=1)

            # Create button with center info
            center_text = f"{center.center_code} - {center.center_name}"
            center_button = ctk.CTkButton(
                center_frame,
                text=center_text,
                command=lambda c=center: self._on_center_selected(c),
                anchor="w",
                fg_color="transparent",
                hover_color=("#3b8ed0", "#1f6aa5"),
                text_color=("gray10", "gray90"),
                height=28
            )
            center_button.pack(fill="x", padx=5, pady=4)

            # Store the frame (not the button) so we can destroy it later
            self.center_buttons.append(center_frame)

        # Update count label with truncation warning if needed
        if self.center_count_label:
            if len(centers) > MAX_DISPLAY:
                self.center_count_label.configure(
                    text=f"⚠️ Mostrant els primers {MAX_DISPLAY} de {len(centers)} centres. Fes servir la cerca per filtrar.",
                    text_color="#f39c12"
                )
            else:
                self.center_count_label.configure(
                    text=f"Mostrant {len(centers)} centres",
                    text_color="#95a5a6"
                )

        Logger.debug(t.MAIN_LOG_TABLE_POPULATED)

    def _on_center_selected(self, center: CenterCredentials) -> None:
        """Maneja la selección de un centro de la lista.

        Args:
            center: Objeto CenterCredentials seleccionado.
        """
        Logger.info(
            t.MAIN_LOG_CENTER_SELECTED.format(code=center.center_code, name=center.center_name))

        self.selected_center = center

        # Highlight selected button by finding it in the frames
        expected_text = f"{center.center_code} - {center.center_name}"
        
        for widget in self.center_buttons:
            if isinstance(widget, ctk.CTkFrame):
                # Get the button inside the frame
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkButton):
                        button_text = child.cget("text")
                        
                        if button_text == expected_text:
                            # Highlight selected button
                            child.configure(
                                fg_color=("#3b8ed0", "#1f6aa5"),
                                text_color="white"
                            )
                        else:
                            # Reset other buttons
                            child.configure(
                                fg_color="transparent",
                                text_color=("gray10", "gray90")
                            )

        # Show and update credentials panel
        if self.credentials_panel:
            self.credentials_panel.pack(fill="x", pady=(0, 10))
            
            # Update username field
            if self.username_entry:
                self.username_entry.configure(state="normal")
                self.username_entry.delete(0, "end")
                self.username_entry.insert(0, center.username)
                self.username_entry.configure(state="readonly")
            
            # Update password field
            if self.password_entry:
                self.password_entry.configure(state="normal")
                self.password_entry.delete(0, "end")
                self.password_entry.insert(0, center.password)
                self.password_entry.configure(state="readonly")
            
            # Force window to update layout
            self.window.update_idletasks()

        self.update_status(
            f"Seleccionat: {center.center_name}",
            "info"
        )

    def _create_credentials_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el panel de visualización de credenciales con botones de copiar.

        Args:
            parent: Frame padre donde adjuntar el panel de credenciales.
        """
        Logger.debug(t.MAIN_LOG_CREATE_CREDS_PANEL)

        # Create main credentials frame
        self.credentials_panel = ctk.CTkFrame(parent)
        self.credentials_panel.pack(fill="x", pady=(0, 10))

        # Title
        credentials_title = ctk.CTkLabel(
            self.credentials_panel,
            text="Credencials",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        credentials_title.pack(anchor="w", padx=10, pady=(10, 5))

        # Username row
        username_frame = ctk.CTkFrame(self.credentials_panel)
        username_frame.pack(fill="x", padx=10, pady=5)

        username_label = ctk.CTkLabel(
            username_frame,
            text="Usuari:",
            font=ctk.CTkFont(size=12),
            width=80,
            anchor="w"
        )
        username_label.pack(side="left", padx=(5, 10))

        self.username_entry = ctk.CTkEntry(
            username_frame,
            font=ctk.CTkFont(size=12),
            state="readonly"
        )
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        copy_username_btn = ctk.CTkButton(
            username_frame,
            text="Copiar",
            command=self._copy_username,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        copy_username_btn.pack(side="left", padx=5)

        # Password row
        password_frame = ctk.CTkFrame(self.credentials_panel)
        password_frame.pack(fill="x", padx=10, pady=(5, 10))

        password_label = ctk.CTkLabel(
            password_frame,
            text="Contrasenya:",
            font=ctk.CTkFont(size=12),
            width=80,
            anchor="w"
        )
        password_label.pack(side="left", padx=(5, 10))

        self.password_entry = ctk.CTkEntry(
            password_frame,
            font=ctk.CTkFont(size=12),
            state="readonly",
            show="•"  # Hide password characters
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))



        self.toggle_password_btn = ctk.CTkButton(
            password_frame,
            text="Mostrar",
            command=self._toggle_password_visibility,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
            anchor="center"
        )
        self.toggle_password_btn.pack(side="left", padx=5)

        copy_password_btn = ctk.CTkButton(
            password_frame,
            text="Copiar",
            command=self._copy_password,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        copy_password_btn.pack(side="left", padx=5)

        # Initially hide the panel
        self.credentials_panel.pack_forget()

        Logger.debug(t.MAIN_LOG_CREDS_PANEL_CREATED)

    def _copy_username(self) -> None:
        """Copia el nombre de usuario al portapapeles."""
        if self.selected_center:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.selected_center.username)
            self.update_status("Usuari copiat al portapapers", "success")
            Logger.info(t.MAIN_LOG_USERNAME_COPIED)

    def _copy_password(self) -> None:
        """Copia la contraseña al portapapeles."""
        if self.selected_center:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.selected_center.password)
            self.update_status("Contrasenya copiada al portapapers", "success")
            Logger.info(t.MAIN_LOG_PASSWORD_COPIED)

    def _toggle_password_visibility(self) -> None:
        """Alterna la visibilidad de la contraseña entre oculta y visible."""
        if self.password_entry.cget("show") == "•":
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(text="Ocultar")
        else:
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(text="Mostrar")

    def _create_action_buttons(self, parent: ctk.CTkFrame) -> None:
        """Crea los botones de Conectar, Desconectar y Abrir Logs.

        Args:
            parent: Frame padre donde adjuntar los botones.
        """
        Logger.debug(t.MAIN_LOG_CREATE_BUTTONS)

        # Create frame for buttons (centered)
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(0, 10))
        
        # Create inner frame to center buttons
        inner_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        inner_frame.pack(expand=True)

        # Connect via Profile button
        self.connect_profile_button = ctk.CTkButton(
            inner_frame,
            text="Connectar",
            command=self._on_connect_profile_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        self.connect_profile_button.pack(side="left", padx=5)

        # Disconnect button
        self.disconnect_button = ctk.CTkButton(
            inner_frame,
            text="Desconnectar",
            command=self._on_disconnect_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.disconnect_button.pack(side="left", padx=5)
        
        # Open Logs button
        self.open_logs_button = ctk.CTkButton(
            inner_frame,
            text="Obrir Logs",
            command=self._on_open_logs_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        self.open_logs_button.pack(side="left", padx=5)

        Logger.debug(t.MAIN_LOG_BUTTONS_CREATED)

    def _create_status_bar(self, parent: ctk.CTkFrame) -> None:
        """Crea el área de visualización del estado.

        Args:
            parent: Frame padre donde adjuntar la barra de estado.
        """
        Logger.debug(t.MAIN_LOG_CREATE_STATUS)

        # Create frame for status
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x")

        # Status label
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Preparat",
            font=ctk.CTkFont(size=12),
            text_color="#95a5a6",
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=5, pady=5)

        Logger.debug(t.MAIN_LOG_STATUS_CREATED)

    def _on_connect_profile_clicked(self) -> None:
        """Maneja el clic del botón Conectar para iniciar la conexión basada en perfil."""
        Logger.info(t.MAIN_LOG_PROFILE_CLICKED)
        
        # Check if a center is selected
        if not self.selected_center:
            Logger.warning(t.MAIN_LOG_PROFILE_NO_CENTER)
            self.update_status("Si us plau, selecciona un centre primer", "error")
            return
        
        if self.is_connecting:
            Logger.warning(t.MAIN_LOG_CONNECT_IN_PROGRESS)
            self.update_status("Realitzant la connexió", "info")
            return

        # Disable button and show loading state
        if self.connect_profile_button:
            self.connect_profile_button.configure(
                state="disabled",
                text="Connectant..."
            )

        self.update_status("Connectant via perfil de Windows...", "info")
        
        # Run connection in background thread
        def profile_connection_worker():
            try:
                self.is_connecting = True
                Logger.info(t.MAIN_LOG_PROFILE_STARTING.format(code=self.selected_center.center_code))
                
                # Define progress callback to update GUI in real-time
                def update_progress(message: str):
                    self.window.after(
                        0,
                        lambda msg=message: self.update_status(msg, "info")
                    )
                
                # Create ProfileConnector with credentials from selected center
                profile_connector = ProfileConnector(
                    ssid="gencat_ENS_EDU",
                    username=self.selected_center.username,
                    password=self.selected_center.password
                )
                success, message = profile_connector.connect_via_profile(progress_callback=update_progress)
                
                # Update UI on main thread
                if success:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            "Connectat correctament via perfil!",
                            "success"
                        )
                    )
                else:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            f"Error de connexió: {message}",
                            "error"
                        )
                    )
                    
            except Exception as e:
                Logger.error(t.MAIN_LOG_PROFILE_ERROR.format(error=e), exc_info=True)
                error_msg = f"Error de connexió: {str(e)}"
                self.window.after(
                    0,
                    lambda: self.update_status(error_msg, "error")
                )
                
            finally:
                # Reset connection state and button
                self.is_connecting = False
                
                def reset_button():
                    if self.connect_profile_button:
                        self.connect_profile_button.configure(
                            state="normal",
                            text="Connectar"
                        )
                        
                self.window.after(0, reset_button)
                Logger.info(t.MAIN_LOG_PROFILE_COMPLETED)
        
        # Start thread
        connection_thread = threading.Thread(
            target=profile_connection_worker,
            daemon=True
        )
        connection_thread.start()

    def _on_open_logs_clicked(self) -> None:
        """Maneja el clic del botón Abrir Logs para abrir la carpeta de logs."""
        Logger.info(t.MAIN_LOG_LOGS_CLICKED)
        
        try:
            import os
            import subprocess
            from wifi_connector.utils.paths import get_logs_folder
            
            logs_folder = get_logs_folder()
            
            # Create folder if it doesn't exist
            if not logs_folder.exists():
                logs_folder.mkdir(parents=True, exist_ok=True)
            
            # Open folder in Windows Explorer
            subprocess.run(['explorer', str(logs_folder)], shell=True)
            Logger.info(t.MAIN_LOG_LOGS_OPENED.format(path=logs_folder))
            
        except Exception as e:
            Logger.error(t.MAIN_LOG_LOGS_ERROR.format(error=e))
            self.update_status(f"Error en obrir logs: {e}", "error")

    def _on_about_clicked(self) -> None:
        """Maneja el clic del botón Acerca de para abrir la ventana About."""
        Logger.info("Opening About window")
        try:
            AboutWindow(self.window)
        except Exception as e:
            Logger.error(f"Error opening About window: {e}")
            self.update_status(f"Error en obrir finestra About: {e}", "error")
    
    def _on_disconnect_clicked(self) -> None:
        """Maneja el clic del botón Desconectar para desconectarse de la red."""
        Logger.info(t.MAIN_LOG_DISCONNECT_CLICKED)

        if self.is_connecting:
            Logger.warning(t.MAIN_LOG_DISCONNECT_IN_PROGRESS)
            self.update_status(
                "No es pot desconnectar mentre es fa la connexió",
                "error"
            )
            return

        self.update_status("Desconnectant...", "info")

        # Create a simple ProfileConnector instance for disconnection
        # We don't need a specific SSID for disconnection
        try:
            config = Config.default()
            connector = ProfileConnector("", config)

            if connector.disconnect():
                self.update_status("Desconnectat correctament", "success")
            else:
                self.update_status("Error en desconnectar", "error")
        except Exception as e:
            Logger.error(t.MAIN_LOG_DISCONNECT_ERROR.format(error=e))
            self.update_status(f"Error en desconnectar: {e}", "error")

    def _start_connection_thread(
        self,
        credentials: CenterCredentials
    ) -> None:
        """Inicia la conexión en un hilo en segundo plano para evitar bloquear la GUI.

        Args:
            credentials: Objeto CenterCredentials con la información de conexión.
        """
        Logger.info(
            f"Starting connection thread for center: "
            f"{credentials.center_code}"
        )

        self.is_connecting = True

        # Define the connection worker function
        def connection_worker():
            try:
                # Update status - using after() to ensure thread safety
                self.window.after(
                    0,
                    lambda: self.update_status(
                        "Inicialitzat WiFi de Centres Educatius...",
                        "info"
                    )
                )

                # Create ProfileConnector with appropriate SSID
                # For gencat networks, we'll use a generic SSID pattern
                ssid = "gencat_ENS_EDU"  # Default SSID for gencat networks
                config = Config.default()

                self.profile_connector = ProfileConnector(ssid, config)

                # Update status
                self.window.after(
                    0,
                    lambda: self.update_status(
                        f"Connectant a {ssid}...",
                        "info"
                    )
                )

                # Attempt connection
                success = self.profile_connector.connect(
                    credentials.username,
                    credentials.password
                )

                # Update UI based on result
                if success:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            f"Connectat correctament a {ssid}!",
                            "success"
                        )
                    )
                else:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            "Error de connexió. Revisa els Logs per més detalls.",
                            "error"
                        )
                    )

            except Exception as e:
                Logger.error(f"Error en la connexió: {e}", exc_info=True)
                error_msg = f"Connection error: {str(e)}"
                self.window.after(
                    0,
                    lambda: self.update_status(error_msg, "error")
                )

            finally:
                # Reset connection state and button
                self.is_connecting = False

                def reset_button():
                    if self.connect_button:
                        self.connect_button.configure(
                            state="normal",
                            text="Connectar"
                        )

                self.window.after(0, reset_button)

                Logger.info("Connection thread completed")

        # Start the connection thread
        connection_thread = threading.Thread(
            target=connection_worker,
            daemon=True
        )
        connection_thread.start()

        Logger.debug("Connection thread started")

    def _on_window_close(self) -> None:
        """Maneja el evento de cierre de ventana de forma controlada."""
        Logger.info("Window close requested")

        if self.is_connecting:
            Logger.warning("Connection in progress, waiting for completion")
            self.update_status(
                "Espera que la connexió es realitzi...",
                "info"
            )
            # In a production app, you might want to cancel the thread
            # For now, we'll just let it complete

        self.window.destroy()
        Logger.info("Window closed")
