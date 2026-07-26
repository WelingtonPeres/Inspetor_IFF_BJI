"""
Widget reutilizavel que desenha particulas de confete caindo.
Usado na TelaGameWin como efeito celebratorio de vitoria.

Cada particula e um rectangulo colorido que cai com gravidade
constante e rotacao continua. Quando sai do limite inferior,
e reposicionada no topo com parametros aleatorios.

Animacao via QTimer a ~30fps. So corre enquanto visivel.
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtWidgets import QFrame

logger = logging.getLogger(__name__)

_PALETAS = ["#71dd77", "#8dd2d8", "#f3d78a", "#eeeae2", "#37a547"]


@dataclass
class Particula:
    """Estado de uma particula de confete."""

    x: float
    y: float
    largura: float
    altura: float
    cor: str
    velocidade: float
    rotacao: float
    velocidade_rotacao: float
    opacidade: float


class ConfettiOverlay(QFrame):
    """
    Overlay que desenha particulas de confete caindo.

    E transparente ao mouse e ao fundo. A animacao so corre
    enquanto o widget esta visivel (show/hide lifecycle).
    """

    _INTERVALO_MS = 33
    _GRAVIDADE = 0.3
    _NUM_PARTICULAS = 26

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("confetti_overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__particulas: List[Particula] = []
        self.__timer: QTimer = QTimer(self)
        self.__timer.setInterval(self._INTERVALO_MS)
        self.__timer.timeout.connect(self.__animar)

        self.__inicializar_particulas()

    def __inicializar_particulas(self) -> None:
        """Cria todas as particulas com parametros aleatorios iniciais."""
        self.__particulas.clear()
        for _ in range(self._NUM_PARTICULAS):
            self.__particulas.append(self.__criar_particula(random_y=True))

    def __criar_particula(self, random_y: bool = False) -> Particula:
        """Cria uma nova particula com parametros aleatorios."""
        largura = 5.0 + random.random() * 4.0
        altura = largura * 2.0
        y = random.random() * (self.height() + 100) if random_y else -altura

        return Particula(
            x=random.random() * max(1, self.width() - largura),
            y=y,
            largura=largura,
            altura=altura,
            cor=random.choice(_PALETAS),
            velocidade=random.uniform(1.5, 3.5),
            rotacao=random.uniform(0, 360),
            velocidade_rotacao=random.uniform(-4.0, 4.0),
            opacidade=random.uniform(0.35, 0.65),
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.__timer.start()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self.__timer.stop()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

    @Slot()
    def __animar(self) -> None:
        """Avanca a animacao de todas as particulas e redesenha."""
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        for i, p in enumerate(self.__particulas):
            p.y += p.velocidade
            p.rotacao += p.velocidade_rotacao
            p.velocidade += self._GRAVIDADE

            if p.y > h + 20:
                self.__particulas[i] = self.__criar_particula(random_y=False)
                self.__particulas[i].y = -self.__particulas[i].altura
                self.__particulas[i].x = random.random() * max(1, w - self.__particulas[i].largura)

        self.update()

    def paintEvent(self, _event) -> None:
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for p in self.__particulas:
                painter.save()
                painter.setOpacity(p.opacidade)
                painter.translate(p.x + p.largura / 2, p.y + p.altura / 2)
                painter.rotate(p.rotacao)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(p.cor)))
                painter.drawRect(
                    int(-p.largura / 2),
                    int(-p.altura / 2),
                    int(p.largura),
                    int(p.altura),
                )
                painter.restore()
