from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.assets_helper import RAIZ_ASSETS
from view.tutorial.widgets.item_numerado import ItemNumerado

RISCO_ORDEM = ("FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE")
RISCO_LABELS = {
    "FISICO": "Físico",
    "QUIMICO": "Químico",
    "BIOLOGICO": "Biológico",
    "ERGONOMICO": "Ergonômico",
    "ACIDENTE": "Acidente",
}

ITENS = (
    (
        1,
        "Cada risco tem uma cor própria",
        "— a mesma paleta usada nas placas de sinalização de segurança do "
        "trabalho (NR-26). Toque no tile pra marcar; pode marcar quantos "
        "forem necessários.",
    ),
    (2, "Preenchido = selecionado", "Contorno = não marcado."),
)


class SlideRiscos(SlideTutorial):
    """Slide 4 do tutorial — como marcar os riscos do caso."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_riscos")
        self.setProperty("class", "slide_riscos")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(*self.margens_slide())
        layout.setSpacing(12)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(24)
        layout.addLayout(conteudo)

        conteudo.addWidget(self.__build_grupo_riscos(), 0, Qt.AlignmentFlag.AlignVCenter)
        conteudo.addLayout(self.__build_painel_texto(), stretch=1)

    def __build_grupo_riscos(self) -> QWidget:
        L = LayoutLoader.instance()
        grupo = QWidget()
        grupo.setObjectName("tutorial_riscos_grupo")
        grupo.setFixedWidth(L.scaled("tutorial", "riscos_grupo", "largura"))

        coluna = QVBoxLayout(grupo)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(L.scaled("tutorial", "riscos_grupo", "spacing"))
        coluna.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        linha_atual = QHBoxLayout()
        linha_atual.setSpacing(L.scaled("tutorial", "riscos_grupo", "spacing"))

        for indice, risco in enumerate(RISCO_ORDEM):
            tile = self.__criar_tile_risco(risco)
            linha_atual.addWidget(tile)
            if indice == 2:
                coluna.addLayout(linha_atual)
                linha_atual = QHBoxLayout()
                linha_atual.setSpacing(L.scaled("tutorial", "riscos_grupo", "spacing"))

        coluna.addLayout(linha_atual)
        return grupo

    def __criar_tile_risco(self, risco: str) -> QToolButton:
        L = LayoutLoader.instance()
        tile = QToolButton()
        tile.setObjectName(f"tile_risco_{risco}")
        tile.setProperty("riscoTile", True)
        tile.setCheckable(True)
        tile.setText(RISCO_LABELS[risco])
        tile.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tamanho = L.scaled("tutorial", "risco_tile", "tamanho_minimo")
        tile.setFixedSize(tamanho, tamanho)
        tile.setIconSize(
            QSize(
                L.scaled("tutorial", "risco_tile", "icone_tamanho"),
                L.scaled("tutorial", "risco_tile", "icone_tamanho"),
            )
        )
        tile.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "risco_tile", "font_size"),
            )
        )

        icone_color = self.__resolver_icone_risco(risco, "_color")
        icone_dark = self.__resolver_icone_risco(risco, "_dark")
        if icone_color is not None:
            tile.setProperty("icone_color", str(icone_color))
        if icone_dark is not None:
            tile.setProperty("icone_dark", str(icone_dark))

        tile.setChecked(risco == "QUIMICO")
        self.__aplicar_icone_risco(tile, tile.isChecked())
        tile.toggled.connect(
            lambda checked, t=tile: self.__aplicar_icone_risco(t, checked)
        )
        return tile

    def __aplicar_icone_risco(self, tile: QToolButton, checked: bool) -> None:
        if checked:
            caminho = tile.property("icone_dark")
        else:
            caminho = tile.property("icone_color")
        if caminho:
            tile.setIcon(QIcon(caminho))

    def __resolver_icone_risco(self, risco: str, sufixo: str) -> Optional[Path]:
        caminho = RAIZ_ASSETS / "icons" / "riscos" / f"risco_{risco.lower()}{sufixo}.png"
        return caminho if caminho.exists() else None

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Marque cada risco encontrado.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        nota = QLabel(
            'Marcar um risco que não existe no caso também conta como erro — '
            'não marque "só por garantia".'
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
        return "Agora aponta os riscos. E não, 'vibe ruim' não é uma categoria."
