import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QLabel

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class DesktopShortcut(QFrame):
    clicked = Signal(str)

    def __init__(
        self,
        legenda: str,
        icone_arquivo: str = "",
        parent=None,
        layout_loader: LayoutLoader | None = None,
    ):
        """Inicializa atalho de desktop com ícone e legenda."""
        super().__init__(parent)
        self.setObjectName("desktop_shortcut")
        self.__legenda = legenda
        self.__layout = layout_loader or LayoutLoader.instance()
        self.__icon_label: QLabel | None = None
        self.__text_label: QLabel | None = None
        self.__setup_ui(icone_arquivo)

    def __setup_ui(self, icone_arquivo: str):
        self.__configure_size()
        layout = self.__create_main_layout()

        self.__icon_label = self.__build_icon_label(icone_arquivo)
        layout.addWidget(self.__icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__text_label = self.__build_text_label()
        self.__apply_text_shadow()
        layout.addWidget(self.__text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def __configure_size(self):
        L = self.__layout
        self.setFixedSize(
            L.scaled("desktop_shortcut", "largura"),
            L.scaled("desktop_shortcut", "altura"),
        )

    def __create_main_layout(self) -> QVBoxLayout:
        L = self.__layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(L.scaled("desktop_shortcut", "spacing", "icone_legenda"))
        return layout

    def __build_icon_label(self, icone_arquivo: str) -> QLabel:
        icon_w, icon_h = self.__icon_dimensions()
        label = self.__create_icon_label(icon_w, icon_h)
        self.__set_icon_content(label, icone_arquivo, icon_w, icon_h)
        return label

    def __icon_dimensions(self) -> tuple[int, int]:
        L = self.__layout
        return (
            L.scaled("desktop_shortcut", "icone", "largura"),
            L.scaled("desktop_shortcut", "icone", "altura"),
        )

    def __create_icon_label(self, icon_w: int, icon_h: int) -> QLabel:
        label = QLabel()
        label.setObjectName("shortcut_icon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedSize(icon_w, icon_h)
        return label

    def __set_icon_content(self, label: QLabel, icone_arquivo: str, icon_w: int, icon_h: int):
        pixmap = self.__carregar_pixmap(icone_arquivo)
        
        if pixmap is not None and not pixmap.isNull():
            label.setPixmap(pixmap.scaled(
                icon_w, icon_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            return
        
        self.__apply_icon_fallback(label)

    def __apply_icon_fallback(self, label: QLabel):
        L = self.__layout
        font_family = L.get("desktop_shortcut", "icone", "font_family")
        font_size = L.scaled("desktop_shortcut", "icone", "font_size")
        label.setFont(QFont(font_family, font_size))
        label.setText("?")

    def __build_text_label(self) -> QLabel:
        L = self.__layout
        font_family = L.get("desktop_shortcut", "legenda", "font_family")
        font_size = L.scaled("desktop_shortcut", "legenda", "font_size")
        label = QLabel(self.__legenda)
        label.setObjectName("shortcut_label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(L.get("desktop_shortcut", "legenda", "word_wrap"))
        label.setFont(QFont(font_family, font_size, QFont.Weight.DemiBold))
        return label

    def __apply_text_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setOffset(1, 1)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.__text_label.setGraphicsEffect(shadow)

    def __carregar_pixmap(self, icone_arquivo: str):
        if not icone_arquivo:
            return None
        base = Path(__file__).resolve().parent.parent / "assets" / "icons"
        for sub in [base / "desktop_Icons", base]:
            path = sub / icone_arquivo
            if path.exists():
                return QPixmap(str(path))
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Emite clicked com a legenda ao pressionar o mouse."""
        self.clicked.emit(self.__legenda)
        super().mousePressEvent(event)
