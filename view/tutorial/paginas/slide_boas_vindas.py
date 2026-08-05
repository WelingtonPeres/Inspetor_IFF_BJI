from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget

from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.credential_iff import CredencialIFF

TITULO = "Sua credencial acaba de ser emitida."

PARAGRAFOS = (
    "Você é o novo Inspetor de Segurança do Trabalho do IFF-BJI. Sua função "
    "é analisar relatórios de ocorrências em laboratórios e ambientes de "
    "curso.",
    "Para cada caso, você vai identificar os riscos envolvidos, entender o "
    "que causou a situação, e decidir a ação administrativa cabível.",
    "Este guia mostra, passo a passo, como cada parte do seu trabalho "
    "funciona.",
)


class SlideBoasVindas(SlideTutorial):
    """Slide 1 do tutorial — boas-vindas e apresentacao do inspetor.

    O motivo de abertura nao altera este slide (``definir_motivo`` e o
    no-op herdado da ABC).
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_boas_vindas")
        self.setProperty("class", "slide_boas_vindas")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(*self.margens_slide())
        layout.setSpacing(12)

        layout.addLayout(
            self._montar_conteudo(CredencialIFF(self), self.__build_painel_texto())
        )

    def __build_painel_texto(self) -> QVBoxLayout:
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        eyebrow = QLabel("BEM-VINDO, INSPETOR")
        eyebrow.setObjectName("tutorial_eyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(eyebrow)

        titulo = QLabel(TITULO)
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for texto in PARAGRAFOS:
            paragrafo = QLabel(texto)
            paragrafo.setObjectName("tutorial_paragrafo")
            paragrafo.setWordWrap(True)
            paragrafo.setAlignment(Qt.AlignmentFlag.AlignLeft)
            painel.addWidget(paragrafo)

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return "Presta atenção nesse manual — eu não repito duas vezes, nem o meu café."
