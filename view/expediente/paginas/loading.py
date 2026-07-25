import logging
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class PaginaLoading(QWidget):
    """Widget de carregamento com titulo, progress bar e texto informativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_loading")
        self.setProperty("class", "pagina_loading")

        self.__layout_loader = LayoutLoader.instance()

        self.__label_titulo: QLabel
        self.__progress: QProgressBar
        self.__label_texto: QLabel

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)
        logger.info("PaginaLoading exibida")

    def __setup_ui(self) -> None:
        L = self.__layout_loader
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_titulo = QLabel("IFF SISTEMA DE INSPEÇÃO")
        self.__label_titulo.setObjectName("label_loading_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_size = L.scaled("pagina_loading", "titulo", "tamanho")
        self.__label_titulo.setFont(QFont(L.get("pagina_loading", "titulo", "fonte"), font_size))
        layout.addWidget(self.__label_titulo)

        self.__progress = QProgressBar()
        self.__progress.setObjectName("loading_progress_bar")
        self.__progress.setRange(0, 0)
        self.__progress.setValue(0)
        self.__progress.setFixedHeight(L.scaled("pagina_loading", "progress_bar", "altura"))
        layout.addWidget(self.__progress)

        self.__label_texto = QLabel("CARREGANDO EXPEDIENTE...")
        self.__label_texto.setObjectName("label_loading_texto")
        self.__label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_size = L.scaled("pagina_loading", "texto", "tamanho")
        self.__label_texto.setFont(QFont(L.get("pagina_loading", "texto", "fonte"), font_size))
        layout.addWidget(self.__label_texto)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        L = self.__layout_loader
        if self.__label_titulo is not None:
            font_size = L.scaled("pagina_loading", "titulo", "tamanho")
            self.__label_titulo.setFont(QFont(L.get("pagina_loading", "titulo", "fonte"), font_size))
        if self.__progress is not None:
            self.__progress.setFixedHeight(L.scaled("pagina_loading", "progress_bar", "altura"))
        if self.__label_texto is not None:
            font_size = L.scaled("pagina_loading", "texto", "tamanho")
            self.__label_texto.setFont(QFont(L.get("pagina_loading", "texto", "fonte"), font_size))