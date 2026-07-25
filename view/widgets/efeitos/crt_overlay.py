"""
Widget reutilizavel que combina efeitos visuais CRT: scanlines estaticas,
vinheta radial e scanline bar animada. Usado em telas com estetica retro
(terminal/monitor antigo).
"""

import logging

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QRadialGradient,
)
from PySide6.QtWidgets import QFrame

logger = logging.getLogger(__name__)


class CrtEffectsOverlay(QFrame):
    """
    Overlay decorativo que desenha efeitos CRT sobre qualquer widget pai.

    Combina tres camadas visuais:
    1. Scanlines horizontais finas (3px de espacamento).
    2. Vinheta radial que escurece os cantos.
    3. Scanline bar verde translucida animada de cima para baixo (60fps).

    O overlay e transparente para o mouse (nao intercepta cliques).
    O QTimer de animacao so corre enquanto o widget esta visivel.
    """

    _SCANLINE_INTERVAL_MS = 16
    _SCANLINE_SPEED_PX = 1.2
    _SCANLINE_BAR_HEIGHT = 40
    _SCANLINE_SPACING = 3
    _SCANLINE_COLOR = QColor(255, 255, 255, 9)
    _SCANLINE_BAR_TOP_COLOR = QColor(113, 221, 119, 15)
    _SCANLINE_BAR_MID_COLOR = QColor(113, 221, 119, 6)
    _SCANLINE_BAR_BOT_COLOR = QColor(113, 221, 119, 0)
    _VIGNETTE_RADIUS_FACTOR = 0.7
    _VIGNETTE_INNER_COLOR = QColor(0, 0, 0, 0)
    _VIGNETTE_OUTER_COLOR = QColor(0, 0, 0, 115)
    _VIGNETTE_INNER_STOP = 0.55

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("crt_overlay")
        self.setProperty("class", "crt_overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__scanline_pos: float
        self.__timer: QTimer

        self.__scanline_pos = -float(self._SCANLINE_BAR_HEIGHT)
        self.__timer = QTimer(self)
        self.__timer.setInterval(self._SCANLINE_INTERVAL_MS)
        self.__timer.timeout.connect(self.__animar)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.__timer.start()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self.__timer.stop()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

    def paintEvent(self, _event) -> None:
        with QPainter(self) as painter:
            w, h = self.width(), self.height()
            self.__desenhar_scanlines(painter, w, h)
            self.__desenhar_vinheta(painter, w, h)
            self.__desenhar_scanline_bar(painter, w, h)

    @Slot()
    def __animar(self) -> None:
        self.__scanline_pos += self._SCANLINE_SPEED_PX
        if self.__scanline_pos > self.height():
            self.__scanline_pos = -float(self._SCANLINE_BAR_HEIGHT)
        bar_rect_y = int(self.__scanline_pos)
        self.update(0, bar_rect_y, self.width(), self._SCANLINE_BAR_HEIGHT)

    def __desenhar_scanlines(self, painter: QPainter, w: int, h: int) -> None:
        painter.setPen(self._SCANLINE_COLOR)
        y = 0
        while y < h:
            painter.drawLine(0, y, w, y)
            y += self._SCANLINE_SPACING

    def __desenhar_vinheta(self, painter: QPainter, w: int, h: int) -> None:
        raio = max(w, h) * self._VIGNETTE_RADIUS_FACTOR
        grad = QRadialGradient(w / 2, h / 2, raio)
        grad.setColorAt(self._VIGNETTE_INNER_STOP, self._VIGNETTE_INNER_COLOR)
        grad.setColorAt(1.0, self._VIGNETTE_OUTER_COLOR)
        painter.fillRect(self.rect(), QBrush(grad))

    def __desenhar_scanline_bar(self, painter: QPainter, w: int, h: int) -> None:
        bar_h = self._SCANLINE_BAR_HEIGHT
        y = int(self.__scanline_pos)
        if y + bar_h < 0 or y > h:
            return
        grad = QLinearGradient(0, y, 0, y + bar_h)
        grad.setColorAt(0.0, self._SCANLINE_BAR_TOP_COLOR)
        grad.setColorAt(0.5, self._SCANLINE_BAR_MID_COLOR)
        grad.setColorAt(1.0, self._SCANLINE_BAR_BOT_COLOR)
        painter.fillRect(0, y, w, bar_h, QBrush(grad))
