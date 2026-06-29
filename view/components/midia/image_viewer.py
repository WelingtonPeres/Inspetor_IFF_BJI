import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class ImageViewer(QFrame):
    ampliar_solicitado = Signal()

    def __init__(self, caminho: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("image_viewer")
        self.setProperty("class", "image_viewer")

        self.__pixmap_original: QPixmap | None = None
        self.__label = QLabel()
        self.__label.setObjectName("image_viewer_label")
        self.__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__label)

        if caminho:
            self.carregar(caminho)

    def carregar(self, caminho: str) -> None:
        path = Path(caminho)
        if not path.exists():
            logger.warning("Imagem nao encontrada: %s", caminho)
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            logger.warning("QPixmap invalido: %s", caminho)
            return
        self.__pixmap_original = pixmap
        self.__ajustar_ao_container()

    def __ajustar_ao_container(self) -> None:
        if self.__pixmap_original is None:
            return
        scaled = self.__pixmap_original.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.__label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.__ajustar_ao_container()

    def obter_pixmap_original(self) -> QPixmap | None:
        return self.__pixmap_original

    def mouseDoubleClickEvent(self, event):
        self.ampliar_solicitado.emit()
        super().mouseDoubleClickEvent(event)
