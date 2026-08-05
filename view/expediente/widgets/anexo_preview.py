import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class AnexoPreview(QFrame):
    ver_todos_anexos = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("anexo_preview")
        self.setProperty("class", "anexo_preview")

        L = LayoutLoader.instance()
        self.__main_layout = QHBoxLayout(self)
        self.__main_layout.setContentsMargins(*L.scaled_margins("anexo_preview", "margens"))

        self.__thumb_label = QLabel()
        self.__thumb_label.setObjectName("anexo_thumbnail")
        self.__thumb_label.setFixedSize(
            L.scaled("anexo_preview", "thumbnail_largura"),
            L.scaled("anexo_preview", "thumbnail_altura"),
        )
        self.__thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__main_layout.addWidget(self.__thumb_label)

        info_layout = QVBoxLayout()
        self.__meta_label = QLabel("")
        self.__meta_label.setObjectName("anexo_metadados")
        info_layout.addWidget(self.__meta_label)
        info_layout.addStretch()
        self.__main_layout.addLayout(info_layout, stretch=1)

        self.__btn_ver = QPushButton("Ver Anexos")
        self.__btn_ver.setObjectName("btn_ver_anexos")
        self.__btn_ver.setProperty("class", "btn_primario")
        self.__btn_ver.clicked.connect(self.ver_todos_anexos.emit)
        self.__main_layout.addWidget(self.__btn_ver)

        self.setFixedHeight(L.scaled("anexo_preview", "altura"))
        L.escala_atualizada.connect(self.__reaplicar_dimensoes)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = LayoutLoader.instance()
        self.setFixedHeight(L.scaled("anexo_preview", "altura"))
        self.__thumb_label.setFixedSize(
            L.scaled("anexo_preview", "thumbnail_largura"),
            L.scaled("anexo_preview", "thumbnail_altura"),
        )
        self.__main_layout.setContentsMargins(*L.scaled_margins("anexo_preview", "margens"))

    def carregar_thumbnail(self, caminho: str) -> None:
        path = Path(caminho)
        if not path.exists():
            logger.warning("Thumbnail nao encontrado: %s", caminho)
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return
        thumb = pixmap.scaled(
            self.__thumb_label.width(), self.__thumb_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.__thumb_label.setPixmap(thumb)

    def definir_metadados(self, texto: str) -> None:
        self.__meta_label.setText(texto)
