import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO
from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)

_RISCO_CORES = {
    "FISICO": "#37a547",
    "QUIMICO": "#bb0213",
    "BIOLOGICO": "#6d4c41",
    "ERGONOMICO": "#d9a824",
    "ACIDENTE": "#1565c0",
}
_RISCO_NOMES = {
    "FISICO": "Fisico",
    "QUIMICO": "Quimico",
    "BIOLOGICO": "Biologico",
    "ERGONOMICO": "Ergonomico",
    "ACIDENTE": "Acidente",
}
_DECISAO_CORES = {
    "ADVERTIR": "#F3997B",
    "INTERDITAR": "#CD191E",
    "IGNORAR": "#5f5e5a",
}


def _resolver_icone_risco(risco: str, sufixo: str) -> Path | None:
    assets = Path(__file__).resolve().parent.parent.parent / "assets"
    caminho = assets / "icons" / "riscos" / f"risco_{risco.lower()}{sufixo}.png"
    return caminho if caminho.exists() else None


def _resolver_icone_fator(chave: str, sufixo: str) -> Path | None:
    assets = Path(__file__).resolve().parent.parent.parent / "assets"
    caminho = assets / "icons" / "riscos" / f"{chave}{sufixo}.png"
    return caminho if caminho.exists() else None


class _RiskTile(QFrame):
    """Tile de 56x56px que representa um risco ou factor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("diagnostico_tile")
        self.setFixedSize(56, 56)
        self.setProperty("class", "diagnostico_tile")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__icone_label = QLabel()
        self.__icone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__icone_label.setFixedSize(22, 22)
        layout.addWidget(self.__icone_label, 0, Qt.AlignmentFlag.AlignCenter)

    def definir_icone(self, caminho_icone: str) -> None:
        pixmap = QPixmap(caminho_icone).scaled(
            22, 22, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.__icone_label.setPixmap(pixmap)


class _Badge(QLabel):
    """Circulo 18x18px com simbolo (check, minus, x)."""

    def __init__(self, simbolo: str, cor_fundo: str, parent=None):
        super().__init__(simbolo, parent)
        self.setFixedSize(18, 18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"background-color: {cor_fundo};"
            f"color: #ffffff;"
            f"border-radius: 9px;"
            f"border: 2px solid #1e2020;"
            f"font-size: 11px;"
            f"font-weight: bold;"
        )


class _CardWidget(QFrame):
    """Card com header (titulo + subtotal) e area de conteudo."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("diagnostico_card")
        self.setProperty("class", "diagnostico_card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        self.__header = QFrame()
        self.__header.setObjectName("diagnostico_card_header")
        self.__header.setProperty("class", "diagnostico_card_header")
        self.__header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_layout = QHBoxLayout(self.__header)
        header_layout.setContentsMargins(12, 6, 12, 6)

        self.__titulo_label = QLabel(titulo)
        self.__titulo_label.setObjectName("diagnostico_card_titulo")
        self.__layout.addWidget(self.__header)

        self.__body = QWidget()
        self.__body.setObjectName("diagnostico_card_body")
        self.__body_layout = QHBoxLayout(self.__body)
        self.__body_layout.setContentsMargins(14, 10, 14, 14)
        self.__body_layout.setSpacing(10)
        self.__layout.addWidget(self.__body)

    def definir_subtotal(self, valor: float) -> None:
        sinal = "+" if valor >= 0 else ""
        self.__titulo_label.setText(
            f"{self.__titulo_label.text()}    {sinal}{valor:.0f} pts"
        )

    def adicionar_widget(self, widget: QWidget) -> None:
        self.__body_layout.addWidget(widget)

    def adicionar_stretch(self) -> None:
        self.__body_layout.addStretch()


class _DecisionOption(QLabel):
    """Bloco retangular representando uma decisao administrativa."""

    def __init__(self, texto: str, cor: str, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(36)
        self.setMinimumWidth(80)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.__cor = cor
        self._definir_estilo_nao_escolhida()

    def _definir_estilo_nao_escolhida(self) -> None:
        self.setStyleSheet(
            "border: 2px solid #3f4a3d;"
            "color: #5f5e5a;"
            "font-weight: 800;"
            "font-size: 12px;"
            "letter-spacing: 0.05em;"
            "border-radius: 4px;"
            "background-color: transparent;"
        )

    def marcar_escolhida_correta(self) -> None:
        self.setStyleSheet(
            f"background-color: {self.__cor};"
            f"border: 2px solid {self.__cor};"
            "color: #ffffff;"
            "font-weight: 800;"
            "font-size: 12px;"
            "letter-spacing: 0.05em;"
            "border-radius: 4px;"
        )

    def marcar_escolhida_incorreta(self) -> None:
        self.setStyleSheet(
            f"background-color: {self.__cor};"
            f"border: 2px solid {self.__cor};"
            "color: #ffffff;"
            "font-weight: 800;"
            "font-size: 12px;"
            "letter-spacing: 0.05em;"
            "border-radius: 4px;"
        )

    def marcar_correta_nao_escolhida(self) -> None:
        self.setStyleSheet(
            f"border: 2px dashed {self.__cor};"
            "color: #5f5e5a;"
            "font-weight: 800;"
            "font-size: 12px;"
            "letter-spacing: 0.05em;"
            "border-radius: 4px;"
            "background-color: transparent;"
        )


class PaginaDiagnostico(QWidget):
    """Pagina de diagnostico detalhado com cards, tiles e badges."""

    continuar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_diagnostico")
        self.setProperty("class", "pagina_diagnostico")

        self.__layout_loader = LayoutLoader.instance()
        self.__resultado: ResultadoDiagnosticoDTO | None = None

        self.__setup_ui()

    def __setup_ui(self) -> None:
        L = self.__layout_loader
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("diagnostico_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        self.__container = QWidget()
        self.__container.setObjectName("diagnostico_container")
        scroll.setWidget(self.__container)

        self.__layout = QVBoxLayout(self.__container)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        spacing = L.scaled("pagina_diagnostico", "spacing")
        self.__layout.setSpacing(spacing)
        self.__layout.setContentsMargins(20, 20, 20, 12)

        # Header
        self.__header_label = QLabel("Pontuacao final")
        self.__header_label.setObjectName("diagnostico_header_label")
        self.__header_label.setProperty("class", "diagnostico_header_label")
        self.__header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(self.__header_label)

        self.__header_valor = QLabel("0 pts")
        self.__header_valor.setObjectName("diagnostico_header_valor")
        self.__header_valor.setProperty("class", "diagnostico_header_valor")
        self.__header_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(self.__header_valor)
        self.__layout.addSpacing(4)

        # Card Riscos
        self.__card_riscos = _CardWidget("Riscos")
        self.__layout.addWidget(self.__card_riscos)

        # Card Fatores
        self.__card_fatores = _CardWidget("Fatores de inseguranca")
        self.__layout.addWidget(self.__card_fatores)

        # Card Decisao
        self.__card_decisao = _CardWidget("Decisao administrativa")
        self.__layout.addWidget(self.__card_decisao)

        # Card Tempo
        self.__card_tempo = _CardWidget("Bonus de tempo")
        self.__layout.addWidget(self.__card_tempo)

        # Total
        self.__total_container = QWidget()
        self.__total_container.setObjectName("diagnostico_total")
        total_layout = QHBoxLayout(self.__total_container)
        total_layout.setContentsMargins(0, 10, 0, 0)

        self.__total_label = QLabel("Total")
        self.__total_label.setObjectName("diagnostico_total_label")
        total_layout.addWidget(self.__total_label)
        total_layout.addStretch()

        self.__total_valor = QLabel("0 pts")
        self.__total_valor.setObjectName("diagnostico_total_valor")
        total_layout.addWidget(self.__total_valor)
        self.__layout.addWidget(self.__total_container)

        # Botao
        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar_diagnostico")
        self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
        self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        self.__layout.addWidget(self.__btn_continuar, 0, Qt.AlignmentFlag.AlignCenter)

        self.__layout.addStretch()

    def exibir_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        """Preenche a pagina com os dados do resultado."""
        logger.info("Diagnostico exibido: pontuacao_final=%.0f", resultado.pontuacao.pontuacao_final)
        self.__resultado = resultado

        p = resultado.pontuacao
        f = resultado.feedback

        self.__header_valor.setText(f"{p.pontuacao_final:.0f} pts")

        self.__popular_card_riscos(p, f)
        self.__popular_card_fatores(p, f)
        self.__popular_card_decisao(p, f)
        self.__popular_card_tempo(p)
        self.__popular_total(p)

    def __popular_card_riscos(self, p, f) -> None:
        card = self.__card_riscos
        card.definir_subtotal(p.nota_riscos)
        total_riscos = len(f.riscos_acertados) + len(f.riscos_esquecidos) + len(f.riscos_inventados)
        card._CardWidget__titulo_label.setText(
            f"Riscos \u00b7 {len(f.riscos_acertados)} de {total_riscos}"
            f"    +{p.nota_riscos:.0f} pts"
        )
        self.__limpar_corpo(card)

        for risco in f.riscos_acertados:
            self.__adicionar_tile_risco(card, risco, "correto", f.score_por_risco.get(risco, 0.0))
        for risco in f.riscos_esquecidos:
            self.__adicionar_tile_risco(card, risco, "esquecido", 0.0)
        for risco in f.riscos_inventados:
            self.__adicionar_tile_risco(card, risco, "indevido", f.score_por_risco.get(risco, 0.0))

    def __popular_card_fatores(self, p, f) -> None:
        card = self.__card_fatores
        card.definir_subtotal(p.nota_fatores)
        card._CardWidget__titulo_label.setText(
            f"Fatores de inseguranca    +{p.nota_fatores:.0f} pts"
        )
        self.__limpar_corpo(card)

        dados = {
            "ATO_INSEGURO": ("Ato inseguro", "ato"),
            "CONDICAO_INSEGURA": ("Condicao insegura", "condicao"),
        }
        for fator_nome, (label, chave_icone) in dados.items():
            estado = (
                "correto" if fator_nome in f.fatores_acertados
                else "esquecido" if fator_nome in f.fatores_esquecidos
                else "indevido" if fator_nome in f.fatores_inventados
                else "esquecido"
            )
            score = f.score_por_fator.get(fator_nome, 0.0)
            self.__adicionar_tile_fator(card, label, chave_icone, estado, score)

    def __popular_card_decisao(self, p, f) -> None:
        card = self.__card_decisao
        card.definir_subtotal(p.nota_decisao)
        card._CardWidget__titulo_label.setText(
            f"Decisao administrativa    +{p.nota_decisao:.0f} pts"
        )
        self.__limpar_corpo(card)

        opcoes = [
            ("ADVERTIR", _DECISAO_CORES["ADVERTIR"]),
            ("INTERDITAR", _DECISAO_CORES["INTERDITAR"]),
            ("IGNORAR", _DECISAO_CORES["IGNORAR"]),
        ]
        acertou = f.decisao_tomada == f.decisao_esperada

        for nome, cor in opcoes:
            opcao = _DecisionOption(nome, cor)
            if nome == f.decisao_tomada and acertou:
                opcao.marcar_escolhida_correta()
            elif nome == f.decisao_tomada and not acertou:
                opcao.marcar_escolhida_incorreta()
            elif nome == f.decisao_esperada and not acertou:
                opcao.marcar_correta_nao_escolhida()
            card.adicionar_widget(opcao)

        resultado_label = QLabel("decisao correta" if acertou else "decisao incorreta")
        resultado_label.setObjectName("diagnostico_decisao_resultado")
        resultado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resultado_label.setStyleSheet(
            f"font-size: 10px; color: {'#71dd77' if acertou else '#ffb4ab'};"
            "padding: 6px 0 10px;"
        )
        card.adicionar_widget(resultado_label)

    def __popular_card_tempo(self, p) -> None:
        card = self.__card_tempo
        card.definir_subtotal(p.pontos_bonus_tempo)
        card._CardWidget__titulo_label.setText(
            f"Bonus de tempo    {p.pontos_bonus_tempo:+.0f} pts"
        )
        self.__limpar_corpo(card)

        label = QLabel(f"resposta em {p.tempo_resposta_segundos:.0f}s")
        label.setObjectName("diagnostico_tempo_label")
        label.setStyleSheet("font-size: 11px; color: #889484; padding: 10px 14px;")
        card.adicionar_widget(label)

    def __popular_total(self, p) -> None:
        self.__total_valor.setText(f"{p.pontuacao_final:.0f} pts")

    def __limpar_corpo(self, card: _CardWidget) -> None:
        body = card._CardWidget__body
        layout = card._CardWidget__body_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def __adicionar_tile_risco(self, card: _CardWidget, nome: str, estado: str, score: float) -> None:
        cor = _RISCO_CORES.get(nome, "#5f5e5a")
        container = QWidget()
        container.setFixedWidth(80)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tile = _RiskTile()
        if estado == "correto":
            tile.setStyleSheet(f"background-color: {cor}; border-radius: 8px;")
            icone = _resolver_icone_risco(nome, "_dark")
        elif estado == "esquecido":
            tile.setStyleSheet(
                f"background-color: transparent; border: 2px solid {cor}; border-radius: 8px;"
            )
            icone = _resolver_icone_risco(nome, "_color")
        else:
            tile.setStyleSheet(f"background-color: {cor}; border-radius: 8px; opacity: 0.55;")
            icone = _resolver_icone_risco(nome, "_dark")

        if icone:
            tile.definir_icone(str(icone))

        vbox.addWidget(tile, 0, Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(_RISCO_NOMES.get(nome, nome))
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nome_label.setStyleSheet("font-size: 10px; color: #e2e2e2;")
        vbox.addWidget(nome_label)

        if estado == "correto":
            score_texto = f"+{score:.0f} pts"
            score_cor = "#71dd77"
        elif estado == "indevido":
            score_texto = f"{score:.0f} pts"
            score_cor = "#ffb4ab"
        else:
            score_texto = "+0 pts"
            score_cor = "#889484"

        score_label = QLabel(score_texto)
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet(f"font-size: 9px; color: {score_cor};")
        vbox.addWidget(score_label)

        card.adicionar_widget(container)

    def __adicionar_tile_fator(
        self, card: _CardWidget, label: str, chave_icone: str, estado: str, score: float
    ) -> None:
        cor_fator = "#8dd2d8"
        container = QWidget()
        container.setFixedWidth(80)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tile = _RiskTile()
        if estado == "correto":
            tile.setStyleSheet(f"background-color: {cor_fator}; border-radius: 8px;")
            icone = _resolver_icone_fator(chave_icone, "_dark")
        elif estado == "esquecido":
            tile.setStyleSheet(
                f"background-color: transparent; border: 2px solid {cor_fator}; border-radius: 8px;"
            )
            icone = _resolver_icone_fator(chave_icone, "_white")
        else:
            tile.setStyleSheet(f"background-color: {cor_fator}; border-radius: 8px; opacity: 0.55;")
            icone = _resolver_icone_fator(chave_icone, "_dark")

        if icone:
            tile.definir_icone(str(icone))

        vbox.addWidget(tile, 0, Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(label)
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nome_label.setStyleSheet("font-size: 10px; color: #e2e2e2;")
        vbox.addWidget(nome_label)

        if estado == "correto":
            score_texto = f"+{score:.0f} pts"
            score_cor = "#71dd77"
        elif estado == "indevido":
            score_texto = f"{score:.0f} pts"
            score_cor = "#ffb4ab"
        else:
            score_texto = "+0 pts"
            score_cor = "#889484"

        score_label = QLabel(score_texto)
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet(f"font-size: 9px; color: {score_cor};")
        vbox.addWidget(score_label)

        card.adicionar_widget(container)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        L = self.__layout_loader
        if self.__btn_continuar is not None:
            self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
            self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
