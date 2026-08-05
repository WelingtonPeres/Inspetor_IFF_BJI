from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.item_numerado import ItemNumerado
from view.tutorial.widgets.nota_aviso import NotaAviso

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
        layout.setContentsMargins(*self.margens_slide())
        layout.setSpacing(12)

        layout.addLayout(
            self._montar_conteudo(
                self.__build_mini_relatorio(), self.__build_painel_texto()
            )
        )

    def __build_mini_relatorio(self) -> QFrame:
        L = LayoutLoader.instance()
        relatorio = QFrame()
        relatorio.setObjectName("tutorial_mini_relatorio")
        relatorio.setFixedWidth(L.scaled("tutorial", "mini_relatorio", "largura"))

        coluna = QVBoxLayout(relatorio)
        coluna.setContentsMargins(
            *L.scaled_margins("tutorial", "mini_relatorio", "padding")
        )
        coluna.setSpacing(L.scaled("tutorial", "mini_relatorio", "campo_spacing"))

        titulo = QLabel("RELATÓRIO: REAGENTE NOS OLHOS")
        titulo.setObjectName("tutorial_relatorio_titulo")
        titulo.setWordWrap(True)
        titulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "mini_relatorio", "titulo_font_size"),
            )
        )
        coluna.addWidget(titulo)

        for numero, (campo, valor) in enumerate(CAMPOS, start=1):
            coluna.addWidget(self.__build_campo(numero, campo, valor))

        return relatorio

    def __build_campo(self, numero: int, campo: str, valor: str) -> QFrame:
        L = LayoutLoader.instance()
        familia = L.get("tutorial", "font_familia")
        bloco = QFrame()
        bloco.setObjectName("tutorial_relatorio_bloco")

        coluna = QVBoxLayout(bloco)
        coluna.setContentsMargins(
            *L.scaled_margins("tutorial", "mini_relatorio", "bloco_padding")
        )
        coluna.setSpacing(2)

        # Linha do label com o badge numerado a direita (modelo poe o
        # badge sobre o canto do bloco; aqui ele ancora na mesma linha).
        linha = QHBoxLayout()
        linha.setSpacing(4)

        label_campo = QLabel(campo.upper())
        label_campo.setObjectName("tutorial_relatorio_campo")
        label_campo.setFont(
            QFont(familia, L.scaled("tutorial", "mini_relatorio", "campo_font_size"))
        )
        linha.addWidget(label_campo)
        linha.addStretch(1)

        badge = QLabel(str(numero))
        badge.setObjectName("tutorial_relatorio_badge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lado = L.scaled("tutorial", "mini_relatorio", "badge_tamanho")
        badge.setFixedSize(lado, lado)
        badge.setFont(
            QFont(familia, L.scaled("tutorial", "mini_relatorio", "badge_font_size"))
        )
        linha.addWidget(badge)

        coluna.addLayout(linha)

        label_valor = QLabel(valor)
        label_valor.setObjectName("tutorial_relatorio_valor")
        label_valor.setWordWrap(True)
        label_valor.setFont(
            QFont(familia, L.scaled("tutorial", "mini_relatorio", "valor_font_size"))
        )
        coluna.addWidget(label_valor)

        return bloco

    def __build_painel_texto(self) -> QVBoxLayout:
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

        painel.addWidget(
            NotaAviso("Não existe tempo limite para analisar o caso e decidir.")
        )

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return "Não sai carimbando nada sem ler o caso direito, cowboy."
