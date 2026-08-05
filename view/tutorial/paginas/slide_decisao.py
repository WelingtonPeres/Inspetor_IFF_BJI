from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.widgets.item_numerado import ItemNumerado
from view.tutorial.widgets.nota_aviso import NotaAviso

# (nome, tipo, marcado) — tipo alimenta as cores do QSS, como as vars
# --cor do modelo (amarelo, vermelho, cinza).
CARIMBOS = (
    ("Advertir", "advertir", False),
    ("Interditar", "interditar", True),
    ("Ignorar", "ignorar", False),
)

ITENS = (
    (
        1,
        "Advertir",
        "— o risco existe, mas é leve. A atividade pode continuar com uma "
        "notificação formal.",
        "advertir",
    ),
    (
        2,
        "Interditar",
        "— o risco é grave o suficiente para exigir a parada imediata da "
        "atividade.",
        "interditar",
    ),
    (
        3,
        "Ignorar",
        "— após a análise, não há risco real a ser tratado.",
        "ignorar",
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

        layout.addLayout(
            self._montar_conteudo(self.__build_visual(), self.__build_painel_texto())
        )

    def __build_visual(self) -> QWidget:
        L = LayoutLoader.instance()
        painel = QFrame()
        painel.setObjectName("tutorial_painel")
        painel.setFixedWidth(L.scaled("tutorial", "decisao_visual", "largura"))

        coluna = QVBoxLayout(painel)
        coluna.setContentsMargins(
            *L.scaled_margins("tutorial", "decisao_visual", "padding")
        )
        coluna.setSpacing(L.scaled("tutorial", "decisao_visual", "spacing"))
        coluna.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("DECISÃO ADMINISTRATIVA")
        titulo.setObjectName("tutorial_painel_titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "decisao_visual", "legenda_font_size"),
            )
        )
        coluna.addWidget(titulo)

        # Modelo: os tres carimbos lado a lado, centrados.
        linha = QHBoxLayout()
        linha.setSpacing(L.scaled("tutorial", "decisao_visual", "spacing"))
        linha.addStretch(1)
        for nome, tipo, marcado in CARIMBOS:
            linha.addWidget(self.__build_carimbo(nome, tipo, marcado))
        linha.addStretch(1)
        coluna.addLayout(linha)

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

        return painel

    def __build_carimbo(self, nome: str, tipo: str, marcado: bool) -> QFrame:
        L = LayoutLoader.instance()
        carimbo = QFrame()
        carimbo.setObjectName("tutorial_carimbo")
        carimbo.setProperty("estado", "marcado" if marcado else "vazio")
        carimbo.setProperty("tipo", tipo)
        carimbo.setFixedHeight(L.scaled("tutorial", "carimbo", "altura"))

        layout = QVBoxLayout(carimbo)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(nome.upper())
        nome_label.setObjectName("tutorial_carimbo_nome")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nome_label.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "carimbo", "font_size"),
                QFont.Weight.Bold,
            )
        )
        layout.addWidget(nome_label)

        return carimbo

    def __build_painel_texto(self) -> QVBoxLayout:
        painel = QVBoxLayout()
        painel.setSpacing(10)
        painel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        titulo = QLabel("Carimbe a consequência certa.")
        titulo.setObjectName("tutorial_titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        painel.addWidget(titulo)

        for numero, item_titulo, descricao, tipo in ITENS:
            painel.addWidget(
                ItemNumerado(numero, item_titulo, descricao, cor_badge=tipo)
            )

        painel.addWidget(
            NotaAviso(
                "A decisão só faz sentido se a análise por trás dela também "
                "fizer — carimbar certo sem entender o caso não conta.",
                icone="⚠",
                erro=True,
            )
        )

        return painel

    def texto_briefing(self) -> str:
        """Frase exibida na barra de briefing do chrome."""
        return "Riscos e fatores marcados? Beleza. Agora bate o carimbo — sem tremer a mão."
