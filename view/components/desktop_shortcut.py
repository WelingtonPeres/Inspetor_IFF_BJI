import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QMouseEvent, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class DesktopShortcut(QWidget):
    clicked = Signal(str)

    def __init__(self, legenda: str, icone_arquivo: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("desktop_shortcut")
        self.setProperty("class", "desktop_shortcut")
        self.__legenda = legenda
        self.__layout = LayoutLoader.instance()
        self.__setup_ui(icone_arquivo)

    def __setup_ui(self, icone_arquivo: str):
        L = self.__layout
        w = L.scaled("atalho", "largura")
        h = L.scaled("atalho", "altura")
        self.setFixedSize(w, h)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(L.scaled("atalho", "spacing_icone_legenda"))

        icon_w = L.scaled("atalho", "icone", "largura")
        icon_h = L.scaled("atalho", "icone", "altura")

        self.__icon_label = QLabel()
        self.__icon_label.setObjectName("shortcut_icon")
        self.__icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__icon_label.setFixedSize(icon_w, icon_h)

        pixmap = self.__carregar_pixmap(icone_arquivo)
        if pixmap is not None and not pixmap.isNull():
            scaled = pixmap.scaled(
                icon_w, icon_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.__icon_label.setPixmap(scaled)
        else:
            font_size = L.scaled("fontes", "ocorrencias", "atalho_icone", "size")
            self.__icon_label.setFont(QFont("Open Sans", font_size))
            self.__icon_label.setText("?")

        layout.addWidget(self.__icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__text_label = QLabel(self.__legenda)
        self.__text_label.setObjectName("shortcut_label")
        self.__text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__text_label.setWordWrap(L.get("atalho", "legenda", "word_wrap"))
        font_size = L.scaled("fontes", "ocorrencias", "atalho_legenda", "size")
        self.__text_label.setFont(QFont("Open Sans", font_size))
        layout.addWidget(self.__text_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def __carregar_pixmap(self, icone_arquivo: str):
        if not icone_arquivo:
            return None
        base = Path(__file__).resolve().parent.parent / "assets" / "icons"
        for sub in [base / "desktop_Icos", base]:
            path = sub / icone_arquivo
            if path.exists():
                return QPixmap(str(path))
        return None

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.__legenda)
        super().mousePressEvent(event)
