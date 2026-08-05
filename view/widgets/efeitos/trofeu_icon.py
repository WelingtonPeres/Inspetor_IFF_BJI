import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from view.utils.tint_icon import tint_pixmap

logger = logging.getLogger(__name__)

_ICON_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "icons" / "fim_jogo" / "trophy.png"


class TrofeuIcon(QWidget):
    """Widget que exibe o icone de trofeu tintado na cor desejada."""

    def __init__(
        self,
        cor: str = "#37a547",
        tamanho: int = 46,
        parent=None,
    ):
        super().__init__(parent)
        self.__tamanho = tamanho
        self.__cor = cor
        self.__pixmap_original = QPixmap(str(_ICON_PATH))
        if self.__pixmap_original.isNull():
            logger.warning("TrofeuIcon: nao foi possivel carregar %s", _ICON_PATH)
        self.setFixedSize(tamanho, tamanho)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, _event) -> None:
        if self.__pixmap_original.isNull():
            return
        scaled = self.__pixmap_original.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        tinted = tint_pixmap(scaled, self.__cor)
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            x = (self.width() - tinted.width()) // 2
            y = (self.height() - tinted.height()) // 2
            painter.drawPixmap(x, y, tinted)
