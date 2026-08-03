from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.assets_helper import carregar_pixmap_escalado
from view.tutorial.widgets.item_numerado import ItemNumerado

ITENS = (
    (
        1,
        "Vitória",
        "Sua análise foi consistente o suficiente. A CIPA emite um parecer "
        "favorável e sua credencial é mantida.",
    ),
    (
        2,
        "Game over",
        "Os erros se acumularam — riscos mal identificados, decisões "
        "incorretas. A CIPA emite um parecer negativo e você é afastado.",
    ),
)


class SlideVitoria(SlideTutorial):
    """Slide 7 do tutorial — vitoria vs game over e a avaliacao da CIPA."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_vitoria")
        self.setProperty("class", "slide_vitoria")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(24)
        layout.addLayout(conteudo)

        conteudo.addWidget(self.__build_visual(), 0, Qt.AlignmentFlag.AlignVCenter)
        conteudo.addLayout(self.__build_painel_texto(), stretch=1)

    def __build_visual(self) -> QWidget:
        L = LayoutLoader.instance()
        visual = QWidget()
        visual.setObjectName("tutorial_vitoria_visual")
        visual.setFixedWidth(L.scaled("tutorial", "vitoria_visual", "largura"))

        coluna = QVBoxLayout(visual)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(L.scaled("tutorial", "vitoria_visual", "spacing"))
        coluna.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        coluna.addWidget(
            self.__build_mini_tela(
                "win", "CASO ENCERRADO", "credencial mantida", "fim_jogo", "trophy.png"
            )
        )
        coluna.addWidget(
            self.__build_mini_tela(
                "over",
                "GAME OVER",
                "credencial revogada",
                "fim_jogo",
                "failedCarimbo.png",
            )
        )

        return visual

    def __build_mini_tela(
        self,
        estado: str,
        titulo: str,
        subtitulo: str,
        *icone: str,
    ) -> QFrame:
        L = LayoutLoader.instance()
        tela = QFrame()
        tela.setObjectName("tutorial_mini_tela")
        tela.setProperty("estado", estado)

        coluna = QVBoxLayout(tela)
        coluna.setContentsMargins(*L.scaled_margins("tutorial", "mini_tela", "margens"))
        coluna.setSpacing(6)
        coluna.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icone_label = QLabel()
        icone_label.setObjectName("tutorial_mini_tela_icone")
        icone_label.setFixedSize(
            L.scaled("tutorial", "mini_tela", "icone_tamanho"),
            L.scaled("tutorial", "mini_tela", "icone_tamanho"),
        )
        icone_label.setPixmap(
            carregar_pixmap_escalado(
                L.scaled("tutorial", "mini_tela", "icone_tamanho"),
                L.scaled("tutorial", "mini_tela", "icone_tamanho"),
                *icone,
            )
        )
        icone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coluna.addWidget(icone_label, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("tutorial_mini_tela_titulo")
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_label.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_tela", "titulo_font_size"),
            )
        )
        coluna.addWidget(titulo_label)

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setObjectName("tutorial_mini_tela_subtitulo")
        subtitulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo_label.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_tela", "subtitulo_font_size"),
            )
        )
        coluna.addWidget(subtitulo_label)

        return tela

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("O resultado reflete seu trabalho.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        nota = QLabel(
            "Errar tem peso aqui, mas também faz parte do aprendizado — você "
            "pode tentar de novo quantas vezes quiser."
        )
        nota.setObjectName("tutorial_aviso")
        nota.setWordWrap(True)
        nota.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "nota", "font_size"),
            )
        )
        nota.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(nota)

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return (
            "No fim do expediente, alguém vai avaliar você. Espero, pelo seu "
            "bem, que seja em bons termos."
        )
