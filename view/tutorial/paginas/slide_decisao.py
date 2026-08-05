from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.item_numerado import ItemNumerado

CARIMBOS = ("Advertir", "Interditar", "Ignorar")

ITENS = (
    (
        1,
        "Advertir",
        "— o risco existe, mas é leve. A atividade pode continuar com uma "
        "notificação formal.",
    ),
    (
        2,
        "Interditar",
        "— o risco é grave o suficiente para exigir a parada imediata da "
        "atividade.",
    ),
    (
        3,
        "Ignorar",
        "— após a análise, não há risco real a ser tratado.",
    ),
)


class SlideDecisao(SlideTutorial):
    """Slide 6 do tutorial — a decisao administrativa por carimbo."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("slide_decisao")
        self.setProperty("class", "slide_decisao")
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
        visual.setObjectName("tutorial_decisao_visual")
        visual.setFixedWidth(L.scaled("tutorial", "decisao_visual", "largura"))

        coluna = QVBoxLayout(visual)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(L.scaled("tutorial", "decisao_visual", "spacing"))
        coluna.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        for indice, nome in enumerate(CARIMBOS):
            coluna.addWidget(self.__build_carimbo(nome, indice == 1))

        legenda = QLabel("carimbo preenchido = decisão escolhida")
        legenda.setObjectName("tutorial_decisao_legenda")
        legenda.setWordWrap(True)
        legenda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legenda.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "decisao_visual", "legenda_font_size"),
            )
        )
        coluna.addWidget(legenda)

        return visual

    def __build_carimbo(self, nome: str, marcado: bool) -> QFrame:
        L = LayoutLoader.instance()
        carimbo = QFrame()
        carimbo.setObjectName("tutorial_carimbo")
        carimbo.setProperty("estado", "marcado" if marcado else "vazio")
        tamanho = L.scaled("tutorial", "carimbo", "tamanho")
        carimbo.setFixedSize(tamanho, tamanho)

        layout = QVBoxLayout(carimbo)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(nome)
        nome_label.setObjectName("tutorial_carimbo_nome")
        nome_label.setWordWrap(True)
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nome_label.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "carimbo", "font_size"),
            )
        )
        layout.addWidget(nome_label)

        return carimbo

    def __build_painel_texto(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Carimbe a consequência certa.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao in ITENS:
            painel.addWidget(ItemNumerado(numero, item_titulo, descricao))

        nota = QLabel(
            "A decisão só faz sentido se a análise por trás dela também fizer — "
            "carimbar certo sem entender o caso não conta."
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
        return "Riscos e fatores marcados? Beleza. Agora bate o carimbo — sem tremer a mão."
