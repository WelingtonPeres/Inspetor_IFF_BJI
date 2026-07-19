from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QPushButton, QSizePolicy


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

        self.setObjectName(f"stamp_decisao_{texto}")
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:
        return QSize(160, 52)

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

        fonte = QFont("Open Sans", 18)
        fonte.setWeight(QFont.Weight.ExtraBold)
        fonte.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.8)
        painter.setFont(fonte)
        painter.setPen(texto_cor)

        center = self.rect().center()
        painter.save()
        painter.translate(center)
        painter.rotate(self.__angulo)

        altura_fonte = 28
        text_rect = QRectF(
            -self.rect().width() / 2.0 + 4,
            -altura_fonte / 2.0,
            self.rect().width() - 8,
            altura_fonte,
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.restore()
