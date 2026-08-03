import abc

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from application.interfaces.i_game_view import MotivoTutorial

_ObjectType = type(QWidget)


class _MetaSlideTutorial(abc.ABCMeta, _ObjectType):
    """Metaclasse combinada para heranca de QWidget + ABC (padrao main_window)."""


class SlideTutorial(QWidget, metaclass=_MetaSlideTutorial):
    """Contrato comum dos slides do tutorial.

    O chrome (TelaTutorial) navega os slides via esta interface: pede a
    frase de briefing a cada um e repassa o motivo de abertura. O CTA e
    opcional — quem o tiver emite ``cta_clicked``.
    """

    cta_clicked = Signal()

    @abc.abstractmethod
    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""

    def definir_motivo(self, motivo: MotivoTutorial) -> None:
        """Ajusta o conteudo do slide ao motivo de abertura.

        Por padrao o motivo nao altera o slide; quem usa o motivo
        (ex: o CTA do ultimo slide) faz override.
        """
