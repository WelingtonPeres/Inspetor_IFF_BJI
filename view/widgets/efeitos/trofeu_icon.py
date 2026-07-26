"""
Widget reutilizavel que desenha um trofeu via QPainter.
Usado na TelaGameWin como icone decorativo de vitoria.

O trofeu e composto por formas geometricas simples (silhueta flat):
  1. Copo/taca (trapezio arredondado)
  2. Duas asas laterais (arcos)
  3. Haste vertical
  4. Base rectangular

Todas as formas sao desenhadas na cor configuravel (default: #37a547).
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class TrofeuIcon(QWidget):
    """Widget que desenha um trofeu flat via QPainter."""

    _COR_DEFAULT = "#37a547"

    def __init__(
        self,
        cor: str = _COR_DEFAULT,
        tamanho: int = 46,
        parent=None,
    ):
        super().__init__(parent)
        self.__cor = QColor(cor)
        self.__tamanho = tamanho
        self.setFixedSize(tamanho, tamanho)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, _event) -> None:
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w = self.width()
            h = self.height()

            escala = w / 46.0
            painter.translate(0, 0)
            painter.scale(escala, escala)

            self.__desenhar_copo(painter)
            self.__desenhar_asas(painter)
            self.__desenhar_haste(painter)
            self.__desenhar_base(painter)

    def __desenhar_copo(self, painter: QPainter) -> None:
        """Desenha a copa/taca do trofeu (trapezio arredondado)."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.__cor))

        path = QPainterPath()
        path.moveTo(14, 8)
        path.lineTo(32, 8)
        path.lineTo(30, 26)
        path.quadTo(23, 30, 16, 26)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()

    def __desenhar_asas(self, painter: QPainter) -> None:
        """Desenha as duas asas laterais (arcos simples)."""
        painter.save()
        pen = QPen(self.__cor, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawArc(6, 10, 10, 14, 90 * 16, 180 * 16)
        painter.drawArc(30, 10, 10, 14, -90 * 16, 180 * 16)
        painter.restore()

    def __desenhar_haste(self, painter: QPainter) -> None:
        """Desenha a haste vertical entre copo e base."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.__cor))
        painter.drawRect(20, 26, 6, 6)
        painter.restore()

    def __desenhar_base(self, painter: QPainter) -> None:
        """Desenha a base rectangular do trofeu."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.__cor))

        path = QPainterPath()
        path.moveTo(12, 32)
        path.lineTo(34, 32)
        path.lineTo(34, 38)
        path.quadTo(34, 40, 32, 40)
        path.lineTo(14, 40)
        path.quadTo(12, 40, 12, 38)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()
