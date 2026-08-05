import logging
from typing import Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from view.widgets.midia.image_viewer import ImageViewer

logger = logging.getLogger(__name__)


class MediaViewer(QFrame):
    fechar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("media_viewer")
        self.setProperty("class", "media_viewer")

        self.__image_viewer: ImageViewer | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.__label = QLabel()
        self.__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label)

    def exibir_imagem(self, anexo: Dict) -> None:
        caminho = anexo.get("caminho_arquivo", "")
        pixmap = QPixmap(caminho)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.__label.setPixmap(scaled)
        self.show()

    def mouseDoubleClickEvent(self, event):
        self.fechar_solicitado.emit()
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__label.pixmap() and not self.__label.pixmap().isNull():
            scaled = self.__label.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.__label.setPixmap(scaled)
