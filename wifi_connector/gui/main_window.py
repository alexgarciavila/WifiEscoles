"""Módulo de ventana principal para la GUI de WiFi Connector.

Este módulo proporciona la clase MainWindow que implementa la interfaz
gráfica de usuario principal para la aplicación WiFi Connector.
"""

import threading
from typing import Optional, List
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
import os

from wifi_connector.data.credentials_manager import (
    CredentialsManager,
    CenterCredentials,
)
from wifi_connector.data.favorites_manager import FavoritesManager
from wifi_connector.core.profile_connector import ProfileConnector
from wifi_connector.network.manager import NetworkManager

from wifi_connector.utils.logger import Logger
from wifi_connector.utils.paths import get_base_path, get_json_path
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

        # Cargar iconos de favoritos
        try:
            fav_path = get_base_path() / "images" / "fav.png"
            fav_unchecked_path = get_base_path() / "images" / "fav_unchecked.png"

            if fav_path.exists() and fav_unchecked_path.exists():
                self.fav_icon = ctk.CTkImage(
                    light_image=Image.open(fav_path),
                    dark_image=Image.open(fav_path),
                    size=(20, 20),
                )
                self.fav_unchecked_icon = ctk.CTkImage(
                    light_image=Image.open(fav_unchecked_path),
                    dark_image=Image.open(fav_unchecked_path),
                    size=(20, 20),
                )
                Logger.info(t.MAIN_LOG_FAV_ICONS_LOADED)
            else:
                Logger.warning(
                    t.MAIN_LOG_FAV_ICONS_NOT_FOUND.format(
                        fav_path=fav_path, fav_unchecked_path=fav_unchecked_path
                    )
                )
                self.fav_icon = None
                self.fav_unchecked_icon = None
        except Exception as e:
            Logger.error(t.MAIN_LOG_ERROR_LOADING_ICONS.format(error=e), exc_info=True)
            self.fav_icon = None
            self.fav_unchecked_icon = None

        self.credentials_manager = CredentialsManager()

        # Inicializar FavoritesManager
        favorites_path = get_json_path() / "fav.json"

        self.favorites_manager = FavoritesManager(
            favorites_path, self.credentials_manager
        )

        self.profile_connector: Optional[ProfileConnector] = None

        self.selected_center: Optional[CenterCredentials] = None
        self.all_centers: List[CenterCredentials] = []
        self.is_connecting = False
        self.view_mode = "all"  # "all" o "favorites"

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

            # Cargar favoritos después de las credenciales
            self.favorites_manager.load_favorites()

            self._populate_centers_table([], show_prompt=True)
            self.update_status(
                f"Carregat {len(self.all_centers)} centres. Utilitza la cerca per trobar el teu centre.",
                "info",
            )
        except Exception as e:
            Logger.error(t.MAIN_LOG_LOAD_ERROR.format(error=e))
            self.update_status(t.STATUS_ERROR_LOAD_CREDS.format(error=e), "error")

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

        color_map = {"success": "#2ecc71", "error": "#e74c3c", "info": "#3498db"}

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
            text=t.WINDOW_TITLE_MAIN,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(side="left", expand=True)

        # Botón Acerca de
        about_btn = ctk.CTkButton(
            header_frame,
            text=t.HELP_BUTTON,
            width=30,
            height=30,
            corner_radius=5,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self._on_about_clicked,
        )
        about_btn.pack(side="right", padx=4, pady=4)

        # Botón de alternancia para vista de favoritos
        self.toggle_button = ctk.CTkButton(
            header_frame,
            text="",
            image=self.fav_unchecked_icon,
            width=30,
            height=30,
            corner_radius=5,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self._toggle_view_mode,
        )
        self.toggle_button.pack(side="right", padx=4, pady=4)

        # Crear marco de búsqueda
        self._create_search_frame(main_container)

        # Crear tabla de centros
        self._create_centers_table(main_container)

        # Crear panel de visualización de credenciales
        self._create_credentials_panel(main_container)

        # Crear botones de acción
        self._create_action_buttons(main_container)

        # Crear barra de estado
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

        # Etiqueta de búsqueda
        search_label = ctk.CTkLabel(
            search_frame, text=t.SEARCH_LABEL, font=ctk.CTkFont(size=14)
        )
        search_label.pack(side="left", padx=(10, 5))

        # Campo de entrada de búsqueda
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text=t.SEARCH_PLACEHOLDER, width=400
        )
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # Vincular evento de búsqueda
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
        """Filtra y actualiza la tabla de centros según la consulta y el modo de vista.

        Args:
            query: Cadena de texto de búsqueda.
        """
        Logger.debug(t.MAIN_LOG_FILTERING.format(query=query))

        # Determinar la lista base según el modo de vista
        if self.view_mode == "favorites":
            base_centers = self.favorites_manager.get_favorites()
            Logger.debug(t.MAIN_LOG_FILTERING_FAVORITES.format(count=len(base_centers)))
        else:
            base_centers = self.all_centers
            Logger.debug(t.MAIN_LOG_FILTERING_ALL.format(count=len(base_centers)))

        if not query:
            # Sin consulta de búsqueda
            if self.view_mode == "favorites":
                # Mostrar favoritos sin búsqueda
                if not base_centers:
                    # Sin favoritos todavía
                    self._populate_centers_table([], show_prompt=False)
                    if self.center_count_label:
                        self.center_count_label.configure(
                            text=t.NO_FAVORITES, text_color="#f39c12"
                        )
                else:
                    # Mostrar todos los favoritos
                    self._populate_centers_table(base_centers)
            else:
                # Modo todos sin búsqueda - mostrar mensaje
                self._populate_centers_table([], show_prompt=True)
                if self.center_count_label:
                    self.center_count_label.configure(
                        text=t.SEARCH_PROMPT_HINT.format(count=len(self.all_centers)),
                        text_color="#3498db",
                    )
            return

        # Aplicar consulta de búsqueda a los centros base
        if self.view_mode == "favorites":
            # Buscar dentro de favoritos
            filtered_centers = [
                center
                for center in base_centers
                if query.lower() in center.center_code.lower()
                or query.lower() in center.center_name.lower()
            ]

            if not filtered_centers:
                # Sin resultados en favoritos - mostrar mensaje contextual
                self._populate_centers_table([], show_prompt=False)
                if self.center_count_label:
                    self.center_count_label.configure(
                        text=t.NO_FAVORITES_SEARCH.format(query=query),
                        text_color="#f39c12",
                    )
            else:
                self._populate_centers_table(filtered_centers)
        else:
            # Buscar en todos los centros
            filtered_centers = self.credentials_manager.search_centers(query)
            Logger.debug(t.MAIN_LOG_FOUND_MATCHING.format(count=len(filtered_centers)))
            self._populate_centers_table(filtered_centers)

    def _create_centers_table(self, parent: ctk.CTkFrame) -> None:
        """Crea el widget de lista/tabla de centros con scroll.

        Args:
            parent: Frame padre donde adjuntar la tabla de centros.
        """
        Logger.debug(t.MAIN_LOG_CREATE_TABLE)

        # Crear marco para encabezado de tabla y contador
        table_header_frame = ctk.CTkFrame(parent)
        table_header_frame.pack(fill="x", pady=(0, 5))

        # Título de la tabla
        table_title = ctk.CTkLabel(
            table_header_frame,
            text=t.CENTERS_TAB,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        table_title.pack(side="left", padx=10)

        # Etiqueta de contador de centros
        self.center_count_label = ctk.CTkLabel(
            table_header_frame, text="", font=ctk.CTkFont(size=12), text_color="#95a5a6"
        )
        self.center_count_label.pack(side="left", padx=10)

        # Crear marco desplazable para centros con altura reducida para panel de credenciales
        self.centers_frame = ctk.CTkScrollableFrame(parent, height=180)
        self.centers_frame.pack(fill="both", expand=True, pady=(0, 10))

        Logger.debug(t.MAIN_LOG_TABLE_CREATED)

    def _populate_centers_table(
        self, centers: List[CenterCredentials], show_prompt: bool = False
    ) -> None:
        """Rellena la tabla con los datos de los centros.

        Args:
            centers: Lista de CenterCredentials a mostrar.
            show_prompt: Si es True, muestra mensaje de búsqueda en lugar de "Sin resultados".
        """
        Logger.debug(t.MAIN_LOG_POPULATING.format(count=len(centers)))

        # Limpiar widgets existentes (tanto marcos como botones)
        for widget in self.center_buttons:
            widget.destroy()
        self.center_buttons.clear()

        # Restablecer posición de desplazamiento al inicio para corregir error al filtrar de lista larga a corta
        if self.centers_frame and hasattr(self.centers_frame, "_parent_canvas"):
            self.centers_frame._parent_canvas.yview_moveto(0)

        if not centers:
            if show_prompt:
                # Mostrar mensaje de búsqueda
                prompt_label = ctk.CTkLabel(
                    self.centers_frame,
                    text=t.SEARCH_PROMPT,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#3498db",
                )
                prompt_label.pack(pady=40)
                self.center_buttons.append(prompt_label)

                # Actualizar etiqueta de contador para el mensaje
                if self.center_count_label:
                    self.center_count_label.configure(
                        text=t.SEARCH_PROMPT_HINT.format(count=len(self.all_centers)),
                        text_color="#3498db",
                    )
            else:
                # Mostrar mensaje "Sin resultados"
                no_results_label = ctk.CTkLabel(
                    self.centers_frame,
                    text=t.NO_RESULTS,
                    font=ctk.CTkFont(size=14),
                    text_color="#95a5a6",
                )
                no_results_label.pack(pady=20)
                self.center_buttons.append(no_results_label)

                # Actualizar etiqueta de contador para sin resultados
                if self.center_count_label:
                    self.center_count_label.configure(
                        text=t.NO_RESULTS, text_color="#e74c3c"
                    )
            return

        # Limitar la visualización a los primeros 20 centros por rendimiento
        MAX_DISPLAY = 20
        centers_to_display = centers[:MAX_DISPLAY]

        # Crear una fila para cada centro
        for center in centers_to_display:
            center_frame = self._create_center_row(center)
            # Almacenar el marco para poder destruirlo después
            self.center_buttons.append(center_frame)

        # Actualizar etiqueta de contador con advertencia de truncamiento si es necesario
        if self.center_count_label:
            if len(centers) > MAX_DISPLAY:
                self.center_count_label.configure(
                    text=t.SHOWING_FIRST_CENTERS.format(
                        max=MAX_DISPLAY, total=len(centers)
                    ),
                    text_color="#f39c12",
                )
            else:
                self.center_count_label.configure(
                    text=t.SHOWING_CENTERS.format(count=len(centers)),
                    text_color="#95a5a6",
                )

        Logger.debug(t.MAIN_LOG_TABLE_POPULATED)

    def _create_center_row(self, center: CenterCredentials) -> ctk.CTkFrame:
        """Crea una fila para un centro con botón de favorito y botón de selección.

        Args:
            center: Objeto CenterCredentials para el que crear la fila.

        Returns:
            El frame creado que contiene la fila.
        """
        # Crear marco para cada fila de centro
        center_frame = ctk.CTkFrame(self.centers_frame)
        center_frame.pack(fill="x", padx=5, pady=1)

        # Crear botón de favorito (solo si se cargaron los iconos)
        if self.fav_icon and self.fav_unchecked_icon:
            is_fav = self.favorites_manager.is_favorite(center.center_code)
            fav_button = ctk.CTkButton(
                center_frame,
                text="",
                image=self.fav_icon if is_fav else self.fav_unchecked_icon,
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("#d0d0d0", "#3a3a3a"),
                command=lambda c=center: self._toggle_favorite(c),
            )
            fav_button.pack(side="left", padx=(5, 0))

        # Crear botón con información del centro
        center_text = f"{center.center_code} - {center.center_name}"
        center_button = ctk.CTkButton(
            center_frame,
            text=center_text,
            command=lambda c=center: self._on_center_selected(c),
            anchor="w",
            fg_color="transparent",
            hover_color=("#3b8ed0", "#1f6aa5"),
            text_color=("gray10", "gray90"),
            height=28,
        )
        center_button.pack(side="left", fill="x", expand=True, padx=5, pady=4)

        return center_frame

    def _toggle_favorite(self, center: CenterCredentials) -> None:
        """Alterna el estado de favorito de un centro.

        Args:
            center: Centro cuyo estado de favorito se va a alternar.
        """
        try:
            if self.favorites_manager.is_favorite(center.center_code):
                self.favorites_manager.remove_favorite(center.center_code)
                Logger.info(t.VIEW_LOG_FAV_REMOVED.format(code=center.center_code))
                self.update_status(
                    t.STATUS_FAV_REMOVED.format(code=center.center_code), "info"
                )
            else:
                self.favorites_manager.add_favorite(center)
                Logger.info(t.VIEW_LOG_FAV_ADDED.format(code=center.center_code))
                self.update_status(
                    t.STATUS_FAV_ADDED.format(code=center.center_code), "success"
                )

            # Actualizar la vista actual para refrescar el icono
            query = self.search_entry.get() if self.search_entry else ""
            self._filter_centers(query)
        except Exception as e:
            Logger.error(
                t.MAIN_LOG_ERROR_TOGGLE_FAV.format(code=center.center_code, error=e),
                exc_info=True,
            )
            self.update_status(t.STATUS_ERROR_TOGGLE_FAV.format(error=e), "error")

    def _toggle_view_mode(self) -> None:
        """Alterna entre el modo de vista 'all' y 'favorites'."""
        try:
            if self.view_mode == "all":
                # Cambiar a modo favoritos
                self.view_mode = "favorites"
                self.toggle_button.configure(image=self.fav_icon)
                Logger.info(t.VIEW_LOG_SWITCHED_FAVORITES)
                self.update_status(t.STATUS_SHOWING_FAVORITES, "info")
            else:
                # Cambiar a modo todos los centros
                self.view_mode = "all"
                self.toggle_button.configure(image=self.fav_unchecked_icon)
                Logger.info(t.VIEW_LOG_SWITCHED_ALL)
                self.update_status(t.STATUS_SHOWING_ALL, "info")

            # Actualizar la vista actual
            query = self.search_entry.get() if self.search_entry else ""
            self._filter_centers(query)
        except Exception as e:
            Logger.error(t.MAIN_LOG_ERROR_TOGGLE_VIEW.format(error=e), exc_info=True)
            self.update_status(t.STATUS_ERROR_TOGGLE_VIEW.format(error=e), "error")

    def _on_center_selected(self, center: CenterCredentials) -> None:
        """Maneja la selección de un centro de la lista.

        Args:
            center: Objeto CenterCredentials seleccionado.
        """
        Logger.info(
            t.MAIN_LOG_CENTER_SELECTED.format(
                code=center.center_code, name=center.center_name
            )
        )

        self.selected_center = center

        # Resaltar el botón seleccionado buscándolo en los marcos
        expected_text = f"{center.center_code} - {center.center_name}"

        for widget in self.center_buttons:
            if isinstance(widget, ctk.CTkFrame):
                # Obtener el botón dentro del marco
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkButton):
                        button_text = child.cget("text")

                        if button_text == expected_text:
                            # Resaltar botón seleccionado
                            child.configure(
                                fg_color=("#3b8ed0", "#1f6aa5"), text_color="white"
                            )
                        else:
                            # Restablecer otros botones
                            child.configure(
                                fg_color="transparent", text_color=("gray10", "gray90")
                            )

        # Mostrar y actualizar panel de credenciales
        if self.credentials_panel:
            self.credentials_panel.pack(fill="x", pady=(0, 10))

            # Actualizar campo de nombre de usuario
            if self.username_entry:
                self.username_entry.configure(state="normal")
                self.username_entry.delete(0, "end")
                self.username_entry.insert(0, center.username)
                self.username_entry.configure(state="readonly")

            # Actualizar campo de contraseña
            if self.password_entry:
                self.password_entry.configure(state="normal")
                self.password_entry.delete(0, "end")
                self.password_entry.insert(0, center.password)
                self.password_entry.configure(state="readonly")

            # Forzar la ventana a actualizar el diseño
            self.window.update_idletasks()

        self.update_status(f"Seleccionat: {center.center_name}", "info")

    def _create_credentials_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el panel de visualización de credenciales con botones de copiar.

        Args:
            parent: Frame padre donde adjuntar el panel de credenciales.
        """
        Logger.debug(t.MAIN_LOG_CREATE_CREDS_PANEL)

        # Crear marco principal de credenciales
        self.credentials_panel = ctk.CTkFrame(parent)
        self.credentials_panel.pack(fill="x", pady=(0, 10))

        # Título
        credentials_title = ctk.CTkLabel(
            self.credentials_panel,
            text=t.CREDENTIALS_TITLE,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        credentials_title.pack(anchor="w", padx=10, pady=(10, 5))

        # Fila de nombre de usuario
        username_frame = ctk.CTkFrame(self.credentials_panel)
        username_frame.pack(fill="x", padx=10, pady=5)

        username_label = ctk.CTkLabel(
            username_frame,
            text=t.USERNAME_LABEL,
            font=ctk.CTkFont(size=12),
            width=80,
            anchor="w",
        )
        username_label.pack(side="left", padx=(5, 10))

        self.username_entry = ctk.CTkEntry(
            username_frame, font=ctk.CTkFont(size=12), state="readonly"
        )
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        copy_username_btn = ctk.CTkButton(
            username_frame,
            text=t.COPY_BUTTON,
            command=self._copy_username,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
        )
        copy_username_btn.pack(side="left", padx=5)

        # Fila de contraseña
        password_frame = ctk.CTkFrame(self.credentials_panel)
        password_frame.pack(fill="x", padx=10, pady=(5, 10))

        password_label = ctk.CTkLabel(
            password_frame,
            text=t.PASSWORD_LABEL,
            font=ctk.CTkFont(size=12),
            width=80,
            anchor="w",
        )
        password_label.pack(side="left", padx=(5, 10))

        self.password_entry = ctk.CTkEntry(
            password_frame,
            font=ctk.CTkFont(size=12),
            state="readonly",
            show="•",  # Ocultar caracteres de contraseña
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.toggle_password_btn = ctk.CTkButton(
            password_frame,
            text=t.SHOW_PASSWORD,
            command=self._toggle_password_visibility,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
            anchor="center",
        )
        self.toggle_password_btn.pack(side="left", padx=5)

        copy_password_btn = ctk.CTkButton(
            password_frame,
            text=t.COPY_BUTTON,
            command=self._copy_password,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
        )
        copy_password_btn.pack(side="left", padx=5)

        # Ocultar el panel inicialmente
        self.credentials_panel.pack_forget()

        Logger.debug(t.MAIN_LOG_CREDS_PANEL_CREATED)

    def _copy_username(self) -> None:
        """Copia el nombre de usuario al portapapeles."""
        if self.selected_center:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.selected_center.username)
            self.update_status(t.STATUS_USERNAME_COPIED, "success")
            Logger.info(t.MAIN_LOG_USERNAME_COPIED)

    def _copy_password(self) -> None:
        """Copia la contraseña al portapapeles."""
        if self.selected_center:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.selected_center.password)
            self.update_status(t.STATUS_PASSWORD_COPIED, "success")
            Logger.info(t.MAIN_LOG_PASSWORD_COPIED)

    def _toggle_password_visibility(self) -> None:
        """Alterna la visibilidad de la contraseña entre oculta y visible."""
        if self.password_entry.cget("show") == "•":
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(text=t.HIDE_PASSWORD)
        else:
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(text=t.SHOW_PASSWORD)

    def _create_action_buttons(self, parent: ctk.CTkFrame) -> None:
        """Crea los botones de Conectar, Desconectar y Abrir Logs.

        Args:
            parent: Frame padre donde adjuntar los botones.
        """
        Logger.debug(t.MAIN_LOG_CREATE_BUTTONS)

        # Crear marco para botones (centrado)
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(0, 10))

        # Crear marco interno para centrar botones
        inner_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        inner_frame.pack(expand=True)

        # Botón Conectar vía Perfil
        self.connect_profile_button = ctk.CTkButton(
            inner_frame,
            text=t.CONNECT_BUTTON,
            command=self._on_connect_profile_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#229954",
        )
        self.connect_profile_button.pack(side="left", padx=5)

        # Botón Desconectar
        self.disconnect_button = ctk.CTkButton(
            inner_frame,
            text=t.DISCONNECT_BUTTON,
            command=self._on_disconnect_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
        )
        self.disconnect_button.pack(side="left", padx=5)

        # Botón Abrir Logs
        self.open_logs_button = ctk.CTkButton(
            inner_frame,
            text=t.OPEN_LOGS_BUTTON,
            command=self._on_open_logs_clicked,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
        )
        self.open_logs_button.pack(side="left", padx=5)

        Logger.debug(t.MAIN_LOG_BUTTONS_CREATED)

    def _create_status_bar(self, parent: ctk.CTkFrame) -> None:
        """Crea el área de visualización del estado.

        Args:
            parent: Frame padre donde adjuntar la barra de estado.
        """
        Logger.debug(t.MAIN_LOG_CREATE_STATUS)

        # Crear marco para estado
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x")

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=t.STATUS_READY,
            font=ctk.CTkFont(size=12),
            text_color="#95a5a6",
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=5, pady=5)

        Logger.debug(t.MAIN_LOG_STATUS_CREATED)

    def _on_connect_profile_clicked(self) -> None:
        """Maneja el clic del botón Conectar para iniciar la conexión basada en perfil."""
        Logger.info(t.MAIN_LOG_PROFILE_CLICKED)

        # Verificar si hay un centro seleccionado
        if not self.selected_center:
            Logger.warning(t.MAIN_LOG_PROFILE_NO_CENTER)
            self.update_status(t.STATUS_ERROR_NO_CENTER, "error")
            return

        if self.is_connecting:
            Logger.warning(t.MAIN_LOG_CONNECT_IN_PROGRESS)
            self.update_status(t.STATUS_CONNECTING_STARTING, "info")
            return

        # Deshabilitar botón y mostrar estado de carga
        if self.connect_profile_button:
            self.connect_profile_button.configure(
                state="disabled", text=t.STATUS_CONNECTING
            )

        self.update_status(t.STATUS_CONNECTING_PROFILE, "info")

        # Ejecutar conexión en hilo en segundo plano
        def profile_connection_worker():
            try:
                self.is_connecting = True
                Logger.info(
                    t.MAIN_LOG_PROFILE_STARTING.format(
                        code=self.selected_center.center_code
                    )
                )

                # Definir callback de progreso para actualizar GUI en tiempo real
                def update_progress(message: str):
                    self.window.after(
                        0, lambda msg=message: self.update_status(msg, "info")
                    )

                # Crear ProfileConnector con credenciales del centro seleccionado
                profile_connector = ProfileConnector(
                    ssid="gencat_ENS_EDU",
                    username=self.selected_center.username,
                    password=self.selected_center.password,
                )
                success, message = profile_connector.connect_via_profile(
                    progress_callback=update_progress
                )

                # Actualizar UI en el hilo principal
                if success:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            "Connectat correctament via perfil!", "success"
                        ),
                    )
                else:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            f"Error de connexió: {message}", "error"
                        ),
                    )

            except Exception as e:
                Logger.error(t.MAIN_LOG_PROFILE_ERROR.format(error=e), exc_info=True)
                error_msg = f"Error de connexió: {str(e)}"
                self.window.after(0, lambda: self.update_status(error_msg, "error"))

            finally:
                # Restablecer estado de conexión y botón
                self.is_connecting = False

                def reset_button():
                    if self.connect_profile_button:
                        self.connect_profile_button.configure(
                            state="normal", text=t.CONNECT_BUTTON
                        )

                self.window.after(0, reset_button)
                Logger.info(t.MAIN_LOG_PROFILE_COMPLETED)

        # Iniciar hilo
        connection_thread = threading.Thread(
            target=profile_connection_worker, daemon=True
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

            # Crear carpeta si no existe
            if not logs_folder.exists():
                logs_folder.mkdir(parents=True, exist_ok=True)

            # Abrir carpeta en el Explorador de Windows
            subprocess.run(["explorer", str(logs_folder)], shell=True)
            Logger.info(t.MAIN_LOG_LOGS_OPENED.format(path=logs_folder))

        except Exception as e:
            Logger.error(t.MAIN_LOG_LOGS_ERROR.format(error=e))
            self.update_status(t.STATUS_ERROR_OPEN_LOGS.format(error=e), "error")

    def _on_about_clicked(self) -> None:
        """Maneja el clic del botón Acerca de para abrir la ventana About."""
        Logger.info(t.MAIN_LOG_OPENING_ABOUT)
        try:
            AboutWindow(self.window)
        except Exception as e:
            Logger.error(t.MAIN_LOG_ERROR_OPENING_ABOUT.format(error=e))
            self.update_status(t.STATUS_ERROR_OPEN_ABOUT.format(error=e), "error")

    def _on_disconnect_clicked(self) -> None:
        """Maneja el clic del botón Desconectar para desconectarse de la red."""
        Logger.info(t.MAIN_LOG_DISCONNECT_CLICKED)

        if self.is_connecting:
            Logger.warning(t.MAIN_LOG_DISCONNECT_IN_PROGRESS)
            self.update_status(t.STATUS_ERROR_DISCONNECT_IN_PROGRESS, "error")
            return

        self.update_status(t.STATUS_DISCONNECTING, "info")

        # Ejecutar desconexión en hilo en segundo plano para evitar bloquear la GUI
        def disconnect_worker():
            try:
                network_manager = NetworkManager()

                if network_manager.disconnect():
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            t.STATUS_DISCONNECTED_SUCCESS, "success"
                        ),
                    )
                else:
                    self.window.after(
                        0,
                        lambda: self.update_status(
                            t.STATUS_DISCONNECTED_ERROR, "error"
                        ),
                    )
            except Exception as e:
                Logger.error(t.MAIN_LOG_DISCONNECT_ERROR.format(error=e))
                self.window.after(
                    0,
                    lambda: self.update_status(
                        t.STATUS_ERROR_DISCONNECT.format(error=e), "error"
                    ),
                )

        disconnect_thread = threading.Thread(target=disconnect_worker, daemon=True)
        disconnect_thread.start()

    def _on_window_close(self) -> None:
        """Maneja el evento de cierre de ventana de forma controlada."""
        Logger.info(t.MAIN_LOG_WINDOW_CLOSE_REQUESTED)

        if self.is_connecting:
            Logger.warning(t.MAIN_LOG_CONNECTION_IN_PROGRESS)
            self.update_status("Espera que la connexió es realitzi...", "info")
            # En una aplicación de producción, podrías querer cancelar el hilo
            # Por ahora, simplemente dejaremos que se complete

        self.window.destroy()
        Logger.info(t.MAIN_LOG_WINDOW_CLOSED)
