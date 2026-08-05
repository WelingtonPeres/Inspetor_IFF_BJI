import abc
from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from application.interfaces.i_game_view import MotivoTutorial
from view.infrastructure.layout_loader import LayoutLoader

_ObjectType = type(QWidget)


class _MetaSlideTutorial(abc.ABCMeta, _ObjectType):
    """Metaclasse combinada para heranca de QWidget + ABC (padrao main_window)."""


class SlideTutorial(QWidget, metaclass=_MetaSlideTutorial):
    """Contrato comum dos slides do tutorial.

    O chrome (TelaTutorial) navega os slides via esta interface: pede a
    frase de briefing a cada um e repassa o motivo de abertura. O CTA
    nao faz parte do contrato — o slide que o tiver declara o proprio
    sinal ``cta_clicked``, e o chrome liga-o por deteccao.
    """

    @staticmethod
    def margens_slide() -> Tuple[int, int, int, int]:
        """Margens do esqueleto comum dos slides (token ``tutorial.slide.margens``)."""
        return LayoutLoader.instance().scaled_margins("tutorial", "slide", "margens")

    @staticmethod
    def _montar_conteudo(visual: QWidget, painel_texto: QVBoxLayout) -> QHBoxLayout:
        """Linha central comum: visual + texto, centrados no corpo.

        Como no modelo HTML, a coluna de texto tem largura maxima
        (``tutorial.slide.texto_max_largura``) e o conjunto e centrado
        pelos stretches das pontas em vez de o texto esticar ate a borda.
        """
        L = LayoutLoader.instance()
        conteudo = QHBoxLayout()
        conteudo.setSpacing(L.scaled("tutorial", "slide", "colunas_spacing"))

        conteudo.addStretch(1)
        conteudo.addWidget(visual, 0, Qt.AlignmentFlag.AlignVCenter)

        texto = QWidget()
        texto.setLayout(painel_texto)
        texto.setMaximumWidth(L.scaled("tutorial", "slide", "texto_max_largura"))
        # Stretch alto: o texto cresce ate o teto antes de sobrar espaco
        # para os stretches laterais (que so entao centram o conjunto).
        conteudo.addWidget(texto, 100)

        conteudo.addStretch(1)
        return conteudo

    @abc.abstractmethod
    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""

    def definir_motivo(self, motivo: MotivoTutorial) -> None:
        """Ajusta o conteudo do slide ao motivo de abertura.

        Por padrao o motivo nao altera o slide; quem usa o motivo
        (ex: o CTA do ultimo slide) faz override.
        """
