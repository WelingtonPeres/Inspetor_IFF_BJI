import logging
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class PaginaLoading(QWidget):
    """Widget de carregamento com titulo, progress bar e texto informativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_loading")
        self.setProperty("class", "pagina_loading")

        self.__label_titulo: QLabel
        self.__progress: QProgressBar
        self.__label_texto: QLabel

        self.__setup_ui()
        logger.info("PaginaLoading exibida")

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_titulo = QLabel("IFF SISTEMA DE INSPEÇÃO")
        self.__label_titulo.setObjectName("label_loading_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titulo.setFont(QFont("Courier New", 16))
        layout.addWidget(self.__label_titulo)

        self.__progress = QProgressBar()
        self.__progress.setObjectName("loading_progress_bar")
        self.__progress.setRange(0, 0)
        self.__progress.setValue(0)
        layout.addWidget(self.__progress)

        self.__label_texto = QLabel("CARREGANDO EXPEDIENTE...")
        self.__label_texto.setObjectName("label_loading_texto")
        self.__label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_texto)
