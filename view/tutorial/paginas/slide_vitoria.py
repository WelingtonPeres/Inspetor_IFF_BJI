from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.assets_helper import (
    carregar_pixmap_escalado,
    tingir_pixmap,
)
from view.tutorial.widgets.item_numerado import ItemNumerado
from view.tutorial.widgets.nota_aviso import NotaAviso

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
        layout.setContentsMargins(*self.margens_slide())
        layout.setSpacing(12)

        layout.addLayout(
            self._montar_conteudo(self.__build_visual(), self.__build_painel_texto())
        )

    def __build_visual(self) -> QWidget:
        L = LayoutLoader.instance()
        visual = QWidget()
        visual.setObjectName("tutorial_vitoria_visual")
        visual.setFixedWidth(L.scaled("tutorial", "vitoria_visual", "largura"))

        # Modelo: as duas mini-telas lado a lado, com a mesma largura.
        linha = QHBoxLayout(visual)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(L.scaled("tutorial", "vitoria_visual", "spacing"))
        linha.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        linha.addWidget(
            self.__build_mini_tela(
                "win", "CASO ENCERRADO", "credencial mantida", "fim_jogo", "trophy.png"
            ),
            stretch=1,
        )
        linha.addWidget(
            self.__build_mini_tela("over", "GAME OVER", "credencial revogada"),
            stretch=1,
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
        coluna.setSpacing(8)
        coluna.setAlignment(Qt.AlignmentFlag.AlignCenter)

        coluna.addWidget(
            self.__build_selo_icone(estado, *icone),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

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

    def __build_selo_icone(self, estado: str, *icone: str) -> QFrame:
        """Circulo colorido com o icone branco (modelo: .mini-icone)."""
        L = LayoutLoader.instance()
        selo = QFrame()
        selo.setObjectName("tutorial_mini_tela_selo")
        selo.setProperty("estado", estado)
        lado = L.scaled("tutorial", "mini_tela", "icone_tamanho")
        selo.setFixedSize(lado, lado)

        layout = QVBoxLayout(selo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icone_label = QLabel()
        icone_label.setObjectName("tutorial_mini_tela_icone")
        icone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icone:
            interno = lado - 16
            icone_label.setPixmap(
                tingir_pixmap(
                    carregar_pixmap_escalado(interno, interno, *icone),
                    "#FFFFFF",
                )
            )
        else:
            icone_label.setText("✕")
            icone_label.setFont(
                QFont(
                    L.get("tutorial", "font_familia"),
                    L.scaled("tutorial", "mini_tela", "titulo_font_size"),
                    QFont.Weight.Bold,
                )
            )
        layout.addWidget(icone_label)

        return selo

    def __build_painel_texto(self) -> QVBoxLayout:
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

        painel.addWidget(
            NotaAviso(
                "Errar tem peso aqui, mas também faz parte do aprendizado — "
                "você pode tentar de novo quantas vezes quiser.",
                icone="⟳",
            )
        )

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return (
            "No fim do expediente, alguém vai avaliar você. Espero, pelo seu "
            "bem, que seja em bons termos."
        )
