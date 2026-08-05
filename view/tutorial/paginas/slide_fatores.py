from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.assets_helper import RAIZ_ASSETS
from view.tutorial.widgets.item_numerado import ItemNumerado

FATORES = (
    ("ATO_INSEGURO", "Ato Inseguro", "falha de comportamento humano", "ato"),
    ("CONDICAO_INSEGURA", "Condição Insegura", "falha do ambiente ou equipamento", "condicao"),
)

ITENS = (
    (
        1,
        "Ato Inseguro",
        "— a pessoa fez algo de forma errada (ex: pulou uma etapa, não usou "
        "um EPI disponível).",
    ),
    (
        2,
        "Condição Insegura",
        "— o ambiente ou equipamento não oferecia segurança (ex: EPI "
        "indisponível, equipamento danificado).",
    ),
)


class SlideFatores(SlideTutorial):
    """Slide 5 do tutorial — ato inseguro vs condicao insegura."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_fatores")
        self.setProperty("class", "slide_fatores")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(*self.margens_slide())
        layout.setSpacing(12)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(24)
        layout.addLayout(conteudo)

        conteudo.addWidget(self.__build_visual(), 0, Qt.AlignmentFlag.AlignVCenter)
        conteudo.addLayout(self.__build_painel_texto(), stretch=1)

    def __build_visual(self) -> QWidget:
        L = LayoutLoader.instance()
        visual = QWidget()
        visual.setObjectName("tutorial_fatores_visual")
        visual.setFixedWidth(L.scaled("tutorial", "fatores_visual", "largura"))

        coluna = QVBoxLayout(visual)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(L.scaled("tutorial", "fatores_visual", "spacing"))
        coluna.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        for chave, titulo, subtitulo, icone in FATORES:
            coluna.addWidget(self.__build_tile_fator(chave, titulo, subtitulo, icone))

        coluna.addWidget(self.__build_exemplo())
        return visual

    def __build_tile_fator(
        self, chave: str, titulo: str, subtitulo: str, icone_chave: str
    ) -> QFrame:
        L = LayoutLoader.instance()
        tile = QFrame()
        tile.setObjectName(f"tutorial_fator_tile_{chave}")
        tile.setProperty("class", "tutorial_fator_tile")

        linha = QHBoxLayout(tile)
        linha.setContentsMargins(
            *L.scaled_margins("tutorial", "fator_tile", "margens")
        )
        linha.setSpacing(L.scaled("tutorial", "fator_tile", "spacing"))

        icone = QLabel()
        icone.setObjectName("tutorial_fator_icone")
        icone.setFixedSize(
            L.scaled("tutorial", "fator_tile", "icone_tamanho"),
            L.scaled("tutorial", "fator_tile", "icone_tamanho"),
        )
        pixmap = self.__carregar_icone_fator(icone_chave)
        icone.setPixmap(pixmap)
        linha.addWidget(icone, 0, Qt.AlignmentFlag.AlignVCenter)

        textos = QVBoxLayout()
        textos.setSpacing(2)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("tutorial_fator_titulo")
        label_titulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "fator_tile", "titulo_font_size"),
            )
        )
        textos.addWidget(label_titulo)

        label_subtitulo = QLabel(subtitulo)
        label_subtitulo.setObjectName("tutorial_fator_subtitulo")
        label_subtitulo.setWordWrap(True)
        label_subtitulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "fator_tile", "subtitulo_font_size"),
            )
        )
        textos.addWidget(label_subtitulo)

        linha.addLayout(textos, 1)
        tile.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return tile

    def __carregar_icone_fator(self, chave: str) -> QPixmap:
        L = LayoutLoader.instance()
        caminho = RAIZ_ASSETS / "icons" / "riscos" / f"{chave}_dark.png"
        pixmap = QPixmap(str(caminho)) if caminho.exists() else QPixmap()
        return pixmap.scaled(
            L.scaled("tutorial", "fator_tile", "icone_tamanho"),
            L.scaled("tutorial", "fator_tile", "icone_tamanho"),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def __build_exemplo(self) -> QFrame:
        L = LayoutLoader.instance()
        exemplo = QFrame()
        exemplo.setObjectName("tutorial_exemplo")

        coluna = QVBoxLayout(exemplo)
        coluna.setContentsMargins(*L.scaled_margins("tutorial", "exemplo", "margens"))
        coluna.setSpacing(6)

        titulo = QLabel("Exemplo prático")
        titulo.setObjectName("tutorial_exemplo_titulo")
        titulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "exemplo", "titulo_font_size"),
            )
        )
        coluna.addWidget(titulo)

        linhas = (
            "Não usou luvas disponíveis → Ato Inseguro.",
            "Não havia luvas disponíveis → Condição Insegura.",
        )
        for linha_texto in linhas:
            linha = QLabel(linha_texto)
            linha.setObjectName("tutorial_exemplo_linha")
            linha.setWordWrap(True)
            linha.setFont(
                QFont(
                    L.get("tutorial", "font_familia"),
                    L.scaled("tutorial", "exemplo", "linha_font_size"),
                )
            )
            coluna.addWidget(linha)

        return exemplo

    def __build_painel_texto(self) -> QVBoxLayout:
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Duas causas, dois nomes.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return "Riscos marcados? Boa. Agora descobre de quem é a culpa — sem drama, só fato."
