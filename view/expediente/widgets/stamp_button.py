from PySide6.QtCore import Qt, QRectF, QSize, Slot
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QPushButton, QSizePolicy

from view.infrastructure.layout_loader import LayoutLoader


STAMP_COLORS = {
    "ADVERTIR": QColor("#E6A800"),
    "INTERDITAR": QColor("#CD191E"),
    "IGNORAR": QColor("#889484"),
}

STAMP_ROTATIONS = {
    "ADVERTIR": -4.0,
    "INTERDITAR": 3.0,
    "IGNORAR": -2.0,
}


class StampButton(QPushButton):

    def __init__(self, texto: str, parent=None):
        super().__init__(texto, parent)
        self.__cor = STAMP_COLORS.get(texto, QColor("#889484"))
        self.__angulo = STAMP_ROTATIONS.get(texto, 0.0)
        self.__layout = LayoutLoader.instance()

        self.setObjectName(f"stamp_decisao_{texto}")
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.__layout.escala_atualizada.connect(self.__reaplicar_escala)

    def sizeHint(self) -> QSize:
        return QSize(
            self.__layout.scaled("stamp_button", "largura"),
            self.__layout.scaled("stamp_button", "altura"),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        border_rect = self.rect().adjusted(1, 1, -2, -2)
        pen = QPen(self.__cor, 3)

        if self.isChecked():
            painter.fillRect(self.rect(), self.__cor)
            texto_cor = Qt.GlobalColor.white
            pen = QPen(self.__cor, 3)
        else:
            texto_cor = self.__cor

        painter.setPen(pen)
        painter.drawRect(border_rect)

        fonte, altura_fonte = self.__criar_fonte_adaptado()
        painter.setFont(fonte)
        painter.setPen(texto_cor)

        center = self.rect().center()
        painter.save()
        painter.translate(center)
        painter.rotate(self.__angulo)

        text_rect = QRectF(
            -self.rect().width() / 2.0 + 4,
            -altura_fonte / 2.0,
            self.rect().width() - 8,
            altura_fonte,
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.restore()

    def __criar_fonte_adaptado(self):
        tamanho_base = self.__layout.scaled("stamp_button", "font_size")
        margem = self.__layout.scaled("stamp_button", "margem_horizontal")
        disponivel = self.rect().width() - margem

        fonte = QFont("Open Sans", tamanho_base)
        fonte.setWeight(QFont.Weight.ExtraBold)
        fonte.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, tamanho_base * 0.1)

        fm = QFontMetrics(fonte)
        largura_texto = fm.horizontalAdvance(self.text())

        if largura_texto > disponivel:
            proporcao = disponivel / largura_texto
            tamanho = max(10, int(tamanho_base * proporcao))
        else:
            tamanho = tamanho_base

        fonte.setPointSize(tamanho)
        fonte.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, tamanho * 0.1)

        altura_fonte = int(tamanho * 1.55)
        return fonte, altura_fonte

    @Slot()
    def __reaplicar_escala(self) -> None:
        self.updateGeometry()
