from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget

from application.interfaces.i_game_view import MotivoTutorial
from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.credential_iff import CredencialIFF
from view.tutorial.widgets.nota_aviso import NotaAviso

TITULO = "Você está pronto, Inspetor."

PARAGRAFOS = (
    "Você já sabe ler um caso, checar as evidências, apontar os riscos, "
    "entender as causas e bater o carimbo certo.",
    "Precisar rever alguma parte? Este guia continua disponível a qualquer "
    "momento, no menu de Ajuda.",
)


class SlidePronto(SlideTutorial):
    """Slide 8 do tutorial — pronto para comecar, com CTA final.

    Unico slide com CTA, logo o unico que declara ``cta_clicked``
    (o sinal nao vive na base para os outros slides nao o carregarem).
    """

    cta_clicked = Signal()

    TEXTO_CTA_NOVO_JOGO = "Começar inspeção"
    TEXTO_CTA_CONSULTA = "Fechar guia"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_pronto")
        self.setProperty("class", "slide_pronto")

        self.__btn_cta: QPushButton
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
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

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

        painel.addWidget(
            NotaAviso(
                "Na dúvida, releia a Descrição do caso antes de decidir. É "
                "sempre dali que vem a resposta.",
                icone="💡",
            )
        )

        # Modelo: o CTA fica logo apos o aviso, com um respiro maior,
        # e nao ancorado no fundo do slide.
        painel.addSpacing(12)
        painel.addWidget(self.__build_cta(), alignment=Qt.AlignmentFlag.AlignLeft)
        return painel

    def __build_cta(self) -> QPushButton:
        L = LayoutLoader.instance()
        btn = QPushButton(self.TEXTO_CTA_NOVO_JOGO)
        btn.setObjectName("tutorial_cta")
        btn.setProperty("class", "tutorial_cta")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(L.scaled("tutorial", "cta_btn", "altura"))
        btn.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "cta_btn", "font_size"),
            )
        )
        btn.clicked.connect(self.cta_clicked.emit)
        self.__btn_cta = btn
        return btn

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return "Vai lá e não a decepciona. Ou decepciona, mas com estilo."

    def definir_motivo(self, motivo: MotivoTutorial) -> None:
        """Ajusta o texto do CTA conforme o motivo que abriu o tutorial."""
        if motivo == MotivoTutorial.CONSULTA:
            self.__btn_cta.setText(self.TEXTO_CTA_CONSULTA)
            return
        self.__btn_cta.setText(self.TEXTO_CTA_NOVO_JOGO)
