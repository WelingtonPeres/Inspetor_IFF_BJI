from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.item_numerado import ItemNumerado

CAMPOS = (
    ("Local", "Laboratório de Solos - IFFBJI"),
    ("Atividade", "Identificação de Cátions com NaOH"),
    ("Envolvidos", "Tec. Pietra, Est. Bernado"),
    (
        "Descrição",
        "Foi relatado que um indivíduo sofreu respingos de NaOH nos olhos "
        "durante a identificação de cátions...",
    ),
)

ITENS = (
    (1, "Local", "onde a ocorrência aconteceu."),
    (2, "Atividade", "o que estava sendo feito no momento."),
    (3, "Envolvidos", "quem participou da ocorrência."),
    (
        4,
        "Descrição",
        "o relato completo. É aqui que estão as pistas para identificar os "
        "riscos corretamente.",
    ),
)


class SlideAnatomia(SlideTutorial):
    """Slide 2 do tutorial — anatomia do relatorio de ocorrencia."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_anatomia")
        self.setProperty("class", "slide_anatomia")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(24)
        layout.addLayout(conteudo)

        conteudo.addWidget(
            self.__build_mini_relatorio(), 0, Qt.AlignmentFlag.AlignVCenter
        )

        conteudo.addLayout(self.__build_painel_texto(), stretch=1)

    def __build_mini_relatorio(self) -> QFrame:
        L = LayoutLoader.instance()
        relatorio = QFrame()
        relatorio.setObjectName("tutorial_mini_relatorio")
        relatorio.setFixedSize(
            L.scaled("tutorial", "mini_relatorio", "largura"),
            L.scaled("tutorial", "mini_relatorio", "altura"),
        )

        coluna = QVBoxLayout(relatorio)
        coluna.setContentsMargins(
            *L.scaled_margins("tutorial", "mini_relatorio", "padding")
        )
        coluna.setSpacing(L.scaled("tutorial", "mini_relatorio", "campo_spacing"))

        titulo = QLabel("Relatório: Reagente nos Olhos")
        titulo.setObjectName("tutorial_relatorio_titulo")
        titulo.setWordWrap(True)
        titulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_relatorio", "titulo_font_size"),
            )
        )
        coluna.addWidget(titulo)

        for campo, valor in CAMPOS:
            coluna.addLayout(self.__build_campo(campo, valor))

        coluna.addStretch()
        return relatorio

    def __build_campo(self, campo: str, valor: str) -> QVBoxLayout:
        L = LayoutLoader.instance()
        bloco = QVBoxLayout()
        bloco.setSpacing(2)

        label_campo = QLabel(campo)
        label_campo.setObjectName("tutorial_relatorio_campo")
        label_campo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_relatorio", "campo_font_size"),
            )
        )
        bloco.addWidget(label_campo)

        label_valor = QLabel(valor)
        label_valor.setObjectName("tutorial_relatorio_valor")
        label_valor.setWordWrap(True)
        label_valor.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_relatorio", "valor_font_size"),
            )
        )
        bloco.addWidget(label_valor)

        return bloco

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Antes de decidir, leia o caso.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        nota = QLabel("Não existe tempo limite para analisar o caso e decidir.")
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
        return "Não sai carimbando nada sem ler o caso direito, cowboy."
