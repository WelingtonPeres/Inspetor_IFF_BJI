from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.assets_helper import carregar_pixmap_escalado
from view.tutorial.widgets.item_numerado import ItemNumerado

ITENS = (
    (
        1,
        "Ver Anexos",
        "abre a galeria com todas as evidências do caso — fotos, vídeos ou "
        "áudios.",
    ),
    (
        2,
        "Reproduza áudios e vídeos",
        "ou dê duplo clique numa imagem para ampliar.",
    ),
    (3, "Feche", "quando terminar de analisar."),
)


class SlideAnexos(SlideTutorial):
    """Slide 3 do tutorial — navegacao pelos anexos das evidencias."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_anexos")
        self.setProperty("class", "slide_anexos")
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
        visual.setObjectName("tutorial_anexos_visual")
        visual.setFixedWidth(L.scaled("tutorial", "anexos_visual", "largura"))

        coluna = QVBoxLayout(visual)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setAlignment(Qt.AlignmentFlag.AlignCenter)

        imagem = QLabel()
        imagem.setObjectName("tutorial_anexos_imagem")
        imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = carregar_pixmap_escalado(
            L.scaled("tutorial", "anexos_visual", "imagem_largura"),
            L.scaled("tutorial", "anexos_visual", "imagem_altura"),
            "tutorial",
            "anexo_tela.png",
        )
        imagem.setPixmap(pixmap)
        coluna.addWidget(imagem, alignment=Qt.AlignmentFlag.AlignCenter)

        return visual

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Todo caso pode ter evidências.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        nota = QLabel("Navegar pelos anexos não pausa o tempo da inspeção.")
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
        return "Anexo não é decoração. Abre e olha — ou vai adivinhar por telepatia?"
