import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class AnexoPreview(QFrame):
    ver_todos_anexos = Signal()

    def __init__(self, caminho_thumbnail: str = "", metadados: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("anexo_preview")
        self.setProperty("class", "anexo_preview")

        L = LayoutLoader.instance()
        self.setFixedHeight(L.scaled("anexo_preview", "altura"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("anexo_preview", "margens"))

        self.__thumb_label = QLabel()
        self.__thumb_label.setObjectName("anexo_thumbnail")
        thumb_w = L.scaled("anexo_preview", "thumbnail_largura")
        thumb_h = L.scaled("anexo_preview", "thumbnail_altura")
        self.__thumb_label.setFixedSize(thumb_w, thumb_h)
        self.__thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__thumb_label)

        if caminho_thumbnail:
            self._carregar_thumbnail(caminho_thumbnail)

        info_layout = QVBoxLayout()
        self._meta_label = QLabel(metadados)
        self._meta_label.setObjectName("anexo_metadados")
        info_layout.addWidget(self._meta_label)
        info_layout.addStretch()
        layout.addLayout(info_layout, stretch=1)

        self.__btn_ver = QPushButton("Ver Anexos")
        self.__btn_ver.setObjectName("btn_ver_anexos")
        self.__btn_ver.setProperty("class", "btn_primario")
        self.__btn_ver.clicked.connect(self.ver_todos_anexos.emit)
        layout.addWidget(self.__btn_ver)

    def _carregar_thumbnail(self, caminho: str) -> None:
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
