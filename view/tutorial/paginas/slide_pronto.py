from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget

from application.interfaces.i_game_view import MotivoTutorial
from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.credential_iff import CredencialIFF

PARAGRAFOS = (
    "Você está pronto, Inspetor.",
    "Você já sabe ler um caso, checar as evidências, apontar os riscos, "
    "entender as causas e bater o carimbo certo.",
    "Precisar rever alguma parte? Este guia continua disponível a qualquer "
    "momento, no menu de Ajuda.",
)


class SlidePronto(SlideTutorial):
    """Slide 8 do tutorial — pronto para comecar, com CTA final."""

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
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(24)
        layout.addLayout(conteudo)

        credencial = CredencialIFF(self)
        conteudo.addWidget(credencial)

        conteudo.addLayout(self.__build_painel_texto(), stretch=1)

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Pronto.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for texto in PARAGRAFOS:
            paragrafo = QLabel(texto)
            paragrafo.setObjectName("tutorial_paragrafo")
            paragrafo.setWordWrap(True)
            paragrafo.setAlignment(Qt.AlignmentFlag.AlignLeft)
            painel.addWidget(paragrafo)

        aviso = QLabel(
            "Na dúvida, releia a Descrição do caso antes de decidir. É "
            "sempre dali que vem a resposta."
        )
        aviso.setObjectName("tutorial_aviso")
        aviso.setWordWrap(True)
        aviso.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(aviso)

        painel.addStretch()
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
