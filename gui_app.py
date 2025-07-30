import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QDialog,
    QListWidget,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from spotify_api import get_playlist_data, sp_user
from playlist_analyzer import Playlist
from utils import format_duration_ms
import re


class PlayLabApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayLab - Analizador de Playlists de Spotify")
        self.setGeometry(100, 100, 950, 750)  # Ventana un poco más grande
        self.setMinimumSize(750, 600)  # Tamaño mínimo
        self.current_playlist = None  # Para almacenar la playlist analizada
        self.init_ui()

    def init_ui(self):
        # Estilo general del fondo de la aplicación
        self.setStyleSheet(
            """
            QWidget {
                background-color: #191414; /* Fondo oscuro Spotify */
                color: #FFFFFF; /* Texto blanco por defecto */
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                color: #E0E0E0; /* Texto ligeramente gris para labels por defecto */
            }
            /* Estilo para los títulos de las secciones/cards */
            QLabel#sectionTitle {
                color: #1DB954; /* Verde Spotify */
                font-weight: bold;
                font-size: 14pt;
                margin-bottom: 5px;
            }
            /* Estilo para los nombres de las estadísticas (ej: "Pistas:", "Duración Total:") */
            QLabel.stat_name {
                color: #B3B3B3; /* Gris más suave para los nombres de las stats */
                font-size: 10pt;
            }
            /* Estilo para los valores de las estadísticas (ej: "150", "2h 30m") */
            QLabel.stat_value {
                color: #FFFFFF; /* Blanco puro para los valores */
                font-weight: bold;
                font-size: 13pt; /* Un poco más grande para los valores */
            }
            /* Estilo específico para los títulos de las canciones/álbumes */
            QLabel.title_value {
                color: #1DB954; /* Verde Spotify para títulos clave */
                font-weight: bold;
                font-size: 12pt;
            }
        """
        )

        # Layout principal (Vertical)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)  # Márgenes generosos
        main_layout.setSpacing(25)  # Espacio entre secciones principales

        # Título de la aplicación
        title_label = QLabel("PlayLab")
        title_font = QFont("Arial", 42, QFont.Bold)  # Más grande
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1DB954; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Instrucciones
        instructions_label = QLabel("Pega aquí la URL de tu playlist de Spotify:")
        instructions_label.setFont(QFont("Arial", 11))
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #B3B3B3;")
        main_layout.addWidget(instructions_label)

        # Campo de entrada de URL y botón de análisis (Horizontal)
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Ej: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        )
        self.url_input.setFont(QFont("Arial", 10))
        self.url_input.setFixedHeight(45)  # Más alto
        self.url_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #535353;
                border-radius: 22px; /* Más redondeado, como píldora */
                padding: 10px 20px;
                background-color: #282828;
                color: white;
                selection-background-color: #1DB954;
            }
        """
        )
        input_layout.addWidget(self.url_input)

        self.analyze_button = QPushButton("Analizar Playlist")
        self.analyze_button.setFont(QFont("Arial", 13, QFont.Bold))  # Fuente más grande
        self.analyze_button.setFixedHeight(45)
        self.analyze_button.setCursor(Qt.PointingHandCursor)
        self.analyze_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1DB954; /* Verde Spotify */
                color: white;
                border-radius: 22px; /* Más redondeado */
                padding: 10px 25px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #1ED760; /* Verde más claro al pasar el ratón */
            }
            QPushButton:pressed {
                background-color: #179B4B; /* Verde más oscuro al presionar */
            }
            QPushButton:disabled {
                background-color: #4a4a4a;
                color: #888888;
            }
        """
        )
        self.analyze_button.clicked.connect(self.analyze_playlist)
        input_layout.addWidget(self.analyze_button)
        main_layout.addLayout(input_layout)

        # Área de resultados - Ahora un QScrollArea que contiene un layout dinámico
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # No horizontal scroll
        self.results_scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
            }
            QScrollArea > QWidget {
                background-color: #191414;
            }
            QScrollBar:vertical {
                border: none;
                background: #282828;
                width: 8px; /* Más delgado */
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #535353;
                min-height: 20px;
                border-radius: 4px; /* Más redondeado */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
            }
        """
        )

        self.results_content_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_content_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(15)  # Espacio entre tarjetas

        self.results_scroll_area.setWidget(self.results_content_widget)
        main_layout.addWidget(self.results_scroll_area)

        # Inicializamos los widgets de resultados dinámicamente
        self.status_label = QLabel(
            "Introduce una URL y haz clic en Analizar para ver las estadísticas de tu playlist."
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #b3b3b3; font-size: 11pt; padding: 20px;"
        )
        self.results_layout.addWidget(self.status_label)

        # Botón para mostrar todos los artistas (debajo de los resultados, fuera del scrollarea)
        self.show_all_artists_button = QPushButton("Mostrar Todos los Artistas")
        self.show_all_artists_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.show_all_artists_button.setFixedHeight(45)
        self.show_all_artists_button.setCursor(Qt.PointingHandCursor)
        self.show_all_artists_button.setStyleSheet(
            """
            QPushButton {
                background-color: #535353; /* Gris más oscuro */
                color: white;
                border-radius: 22px;
                padding: 10px 25px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #303030;
                color: #606060;
            }
        """
        )
        self.show_all_artists_button.clicked.connect(self.show_all_artists_dialog)
        self.show_all_artists_button.setEnabled(
            False
        )  # Deshabilitado hasta que haya datos
        main_layout.addWidget(self.show_all_artists_button)

        self.setLayout(main_layout)

    def _create_card_frame(self, title: str) -> QFrame:
        # Helper para crear frames tipo "tarjeta" con título y estilo consistente
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #282828; /* Fondo más claro para las tarjetas */
                border: none; /* Quitamos los bordes */
                border-radius: 12px; /* Bordes más redondeados */
                padding: 20px; /* Más padding interno */
            }
        """
        )

        section_layout = QVBoxLayout()
        section_title = QLabel(title)
        section_title.setObjectName(
            "sectionTitle"
        )  # Para aplicar estilo CSS específico
        section_title.setAlignment(Qt.AlignLeft)  # Alineado a la izquierda
        section_layout.addWidget(section_title)
        section_layout.addSpacing(10)  # Espacio entre título y contenido

        frame.setLayout(section_layout)
        return frame

    def _create_stat_pair(
        self, name: str, value_text: str, is_title: bool = False
    ) -> QHBoxLayout:
        # Helper para crear un par "Nombre de la estadística: Valor"
        h_layout = QHBoxLayout()
        h_layout.setSpacing(5)  # Espacio entre nombre y valor

        name_label = QLabel(name)
        name_label.setObjectName("stat_name")  # Clase CSS
        name_label.setFont(QFont("Arial", 10))

        value_label = QLabel(value_text)
        if is_title:
            value_label.setObjectName(
                "title_value"
            )  # Clase CSS para títulos de canciones/álbumes
        else:
            value_label.setObjectName("stat_value")  # Clase CSS para valores numéricos

        h_layout.addWidget(name_label)
        h_layout.addWidget(value_label)
        h_layout.addStretch(1)  # Empuja los elementos a la izquierda

        return h_layout

    def extract_playlist_id(self, url: str) -> str:
        """
        Extrae el ID de la playlist de una URL de Spotify.
        """
        match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
        if match:
            return match.group(1)
        else:
            raise ValueError(
                "URL inválida. Asegúrate de pegar un enlace de playlist de Spotify válido."
            )

    def analyze_playlist(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "Advertencia", "Por favor, introduce una URL de playlist."
            )
            return

        # Limpiar resultados anteriores y mostrar mensaje de carga
        self.clear_results_display()
        self.status_label.setText(
            "<p style='color:#b3b3b3; text-align:center;'>Analizando playlist, por favor espera...</p>"
        )
        self.status_label.setVisible(True)
        self.show_all_artists_button.setEnabled(False)
        QApplication.processEvents()  # Actualiza la interfaz para mostrar el mensaje

        try:
            playlist_id = self.extract_playlist_id(url)

            if not sp_user:
                QMessageBox.critical(
                    self,
                    "Error de Conexión",
                    "No se pudo conectar con Spotify. "
                    "Revisa tu conexión a internet o credenciales de API.",
                )
                self.status_label.setText(
                    "<p style='color:red; text-align:center;'>Error: No se pudo conectar con Spotify.</p>"
                )
                return

            playlist: Playlist = get_playlist_data(sp_user, playlist_id)
            self.current_playlist = playlist  # Almacenar la playlist

            if not playlist.songs:
                self.status_label.setText(
                    "<p style='color:#b3b3b3; text-align:center;'>No se encontraron pistas en la playlist o la playlist está vacía.</p>"
                )
                return

            # Ocultar el mensaje de estado y construir los resultados
            self.status_label.setVisible(False)

            # --- Título de la Playlist Analizada ---
            playlist_title_label = QLabel(f"'{playlist.name}'")
            playlist_title_label.setFont(QFont("Arial", 20, QFont.Bold))
            playlist_title_label.setAlignment(Qt.AlignCenter)
            playlist_title_label.setStyleSheet("color: #1DB954; margin-bottom: 10px;")
            self.results_layout.addWidget(playlist_title_label)

            # --- Tarjeta de Estadísticas Principales ---
            main_stats_card = self._create_card_frame("Resumen de la Playlist")
            main_stats_grid = QGridLayout()
            main_stats_grid.setSpacing(15)  # Espacio entre elementos en la rejilla

            main_stats_grid.addLayout(
                self._create_stat_pair("Pistas:", str(playlist.num_songs)), 0, 0
            )
            main_stats_grid.addLayout(
                self._create_stat_pair("Artistas Únicos:", str(playlist.num_artists)),
                0,
                1,
            )
            main_stats_grid.addLayout(
                self._create_stat_pair(
                    "Duración Total:", format_duration_ms(playlist.total_duration_ms)
                ),
                1,
                0,
            )
            main_stats_grid.addLayout(
                self._create_stat_pair(
                    "Álbumes Únicos:", str(playlist.num_unique_albums)
                ),
                1,
                1,
            )
            main_stats_grid.addLayout(
                self._create_stat_pair("Explícitas:", str(playlist.num_explicit_songs)),
                2,
                0,
            )
            main_stats_grid.addLayout(
                self._create_stat_pair(
                    "Colaborativas:", str(playlist.num_collaborative_songs)
                ),
                2,
                1,
            )

            main_stats_card.layout().addLayout(
                main_stats_grid
            )  # Añadir el grid al layout de la tarjeta
            self.results_layout.addWidget(main_stats_card)

            # --- Tarjeta de Duración de Canciones ---
            duration_card = self._create_card_frame("Canciones por Duración")
            duration_layout = QVBoxLayout()
            duration_layout.setSpacing(8)
            duration_layout.addLayout(
                self._create_stat_pair(
                    "Más Corta:",
                    f"'{playlist.shortest_song['title']}' ({format_duration_ms(playlist.shortest_song['duration_ms'])})",
                    is_title=True,
                )
            )
            duration_layout.addLayout(
                self._create_stat_pair(
                    "Más Larga:",
                    f"'{playlist.longest_song['title']}' ({format_duration_ms(playlist.longest_song['duration_ms'])})",
                    is_title=True,
                )
            )
            duration_card.layout().addLayout(duration_layout)
            self.results_layout.addWidget(duration_card)

            # --- Tarjeta de Álbum Más Representado ---
            album_card = self._create_card_frame("Álbum Más Representado")
            album_layout = QVBoxLayout()
            album_layout.setSpacing(8)
            album_layout.addLayout(
                self._create_stat_pair(
                    "Álbum:",
                    f"'{playlist.most_represented_album[0]}' ({playlist.most_represented_album[1]} canciones)",
                    is_title=True,
                )
            )
            album_card.layout().addLayout(album_layout)
            self.results_layout.addWidget(album_card)

            # --- Tarjeta de Top Artistas y Colaboraciones ---
            artist_card = self._create_card_frame("Estadísticas de Artistas")
            artist_content_layout = QVBoxLayout()
            artist_content_layout.setSpacing(10)

            # Top 5 artistas
            top_artists_text = (
                "<span class='stat_name'>Top 5 Artistas con más apariciones:</span>"
            )
            if playlist.artist_frequencies:
                top_artists_list_html = "<ul style='margin-top:5px; margin-bottom: 5px; padding-left: 20px;'>"
                for artist, count in playlist.artist_frequencies.most_common(5):
                    top_artists_list_html += f"<li style='color:#b3b3b3;'>{artist}: <span class='stat_value'>{count} canción{'es' if count > 1 else ''}</span></li>"
                top_artists_list_html += "</ul>"
                top_artists_label_content = QLabel(
                    top_artists_text + top_artists_list_html
                )
            else:
                top_artists_label_content = QLabel(
                    top_artists_text
                    + "<br><span style='color:#b3b3b3;'>No se encontraron artistas.</span>"
                )
            top_artists_label_content.setFont(QFont("Arial", 10))
            artist_content_layout.addWidget(top_artists_label_content)

            # Top 5 colaboraciones
            top_collaborators_text = (
                "<span class='stat_name'>Top 5 Artistas con más Colaboraciones:</span>"
            )
            top_collaborators = [
                (artist, count)
                for artist, count in playlist.artist_collaboration_counts.most_common(5)
                if count > 0
            ]
            if top_collaborators:
                top_collaborators_list_html = "<ul style='margin-top:5px; margin-bottom: 5px; padding-left: 20px;'>"
                for artist, count in top_collaborators:
                    top_collaborators_list_html += f"<li style='color:#b3b3b3;'>{artist}: <span class='stat_value'>{count} colaboracion{'es' if count > 1 else ''}</span></li>"
                top_collaborators_list_html += "</ul>"
                top_collaborators_label_content = QLabel(
                    top_collaborators_text + top_collaborators_list_html
                )
            else:
                top_collaborators_label_content = QLabel(
                    top_collaborators_text
                    + "<br><span style='color:#b3b3b3;'>No se encontraron colaboraciones.</span>"
                )
            top_collaborators_label_content.setFont(QFont("Arial", 10))
            artist_content_layout.addWidget(top_collaborators_label_content)

            artist_card.layout().addLayout(artist_content_layout)
            self.results_layout.addWidget(artist_card)

            # Habilitar el botón de "Mostrar Todos los Artistas" si hay datos
            if playlist.num_artists > 0:
                self.show_all_artists_button.setEnabled(True)

        except ValueError as e:
            QMessageBox.warning(self, "URL Inválida", str(e))
            self.status_label.setText(
                f"<p style='color:red; text-align:center;'>Error: {e}</p>"
            )
            self.status_label.setVisible(True)
            self.show_all_artists_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al Analizar",
                f"Ha ocurrido un error inesperado al analizar la playlist: {e}",
            )
            self.status_label.setText(
                f"<p style='color:red; text-align:center;'>Error inesperado: {e}</p>"
            )
            self.status_label.setVisible(True)
            self.show_all_artists_button.setEnabled(False)
            import traceback

            traceback.print_exc()

    def clear_results_display(self):
        # Elimina todos los widgets actuales del layout de resultados (excepto el status_label si está visible)
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            widget = item.widget()

            # No eliminamos el status_label si está presente y es el único widget
            if widget is self.status_label and self.status_label.isVisible():
                continue

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()  # Asegurarse de que los widgets se eliminen de la memoria
            else:
                # Si es un layout anidado, también vaciarlo recursivamente
                if item.layout() is not None:
                    self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                self._clear_layout(item.layout())  # Recursivamente para sub-layouts

    def show_all_artists_dialog(self):
        if not self.current_playlist or not self.current_playlist.artist_frequencies:
            QMessageBox.information(
                self,
                "Info",
                "No hay datos de artistas para mostrar. Analiza una playlist primero.",
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Todos los Artistas por Apariciones")
        dialog.setGeometry(
            self.x() + 100, self.y() + 100, 550, 750
        )  # Más grande para la lista
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: #191414;
                color: white;
            }
            QLabel#dialogTitle {
                color: #1DB954;
                font-weight: bold;
                font-size: 18pt; /* Título del diálogo más grande */
                margin-bottom: 15px;
            }
            QListWidget {
                background-color: #121212;
                color: #b3b3b3;
                border: 1px solid #282828;
                border-radius: 8px;
                padding: 10px;
                outline: none;
                font-size: 10pt; /* Tamaño de fuente para los items */
            }
            QListWidget::item {
                padding: 8px; /* Más padding para los items */
            }
            QListWidget::item:selected {
                background-color: #1DB954;
                color: white;
            }
            QPushButton {
                background-color: #1DB954;
                color: white;
                border-radius: 22px;
                padding: 10px 25px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QPushButton:pressed {
                background-color: #179B4B;
            }
        """
        )

        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        dialog_layout.setSpacing(15)

        dialog_title_label = QLabel("Lista Completa de Artistas")
        dialog_title_label.setObjectName("dialogTitle")
        dialog_title_label.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(dialog_title_label)

        list_widget = QListWidget()

        # Llenar la lista con todos los artistas ordenados por frecuencia
        for i, (artist, count) in enumerate(
            self.current_playlist.artist_frequencies.most_common()
        ):
            item_text = f"{i+1}. {artist}: {count} canci{'ones' if count > 1 else 'ón'}"
            list_widget.addItem(item_text)

        dialog_layout.addWidget(list_widget)

        close_button = QPushButton("Cerrar")
        close_button.setFont(QFont("Arial", 12, QFont.Bold))
        close_button.setFixedHeight(45)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(dialog.accept)
        dialog_layout.addWidget(close_button)

        dialog.setLayout(dialog_layout)
        dialog.exec_()


# Función para iniciar la aplicación
def start_gui():
    app = QApplication(sys.argv)
    window = PlayLabApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start_gui()
