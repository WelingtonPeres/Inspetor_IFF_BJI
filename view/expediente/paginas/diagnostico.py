"""
Pagina de diagnostico detalhado com cards, tiles e badges.

Exibe o resultado da inspecao apos cada relatorio submetido,
com breakdown visual por categoria de pontuacao.
"""

import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
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
_COR_FATOR = "#8dd2d8"


def _resolver_icone_risco(risco: str, sufixo: str) -> Path | None:
    assets = Path(__file__).resolve().parent.parent.parent / "assets"
    caminho = assets / "icons" / "riscos" / f"risco_{risco.lower()}{sufixo}.png"
    return caminho if caminho.exists() else None


def _resolver_icone_fator(chave: str, sufixo: str) -> Path | None:
    assets = Path(__file__).resolve().parent.parent.parent / "assets"
    caminho = assets / "icons" / "riscos" / f"{chave}{sufixo}.png"
    return caminho if caminho.exists() else None


class _RiskTile(QFrame):
    """Tile quadrado 56x56px que exibe o icone de um risco ou factor."""

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

        self.__icone = QLabel()
        self.__icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__icone.setFixedSize(22, 22)
        layout.addWidget(self.__icone, 0, Qt.AlignmentFlag.AlignCenter)

    def definir_icone(self, caminho: str) -> None:
        """Carrega e exibe o icone no tile."""
        pixmap = QPixmap(caminho).scaled(
            22, 22, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.__icone.setPixmap(pixmap)


class _CardWidget(QFrame):
    """Card com header (titulo) e area de conteudo."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("diagnostico_card")
        self.setProperty("class", "diagnostico_card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("diagnostico_card_header")
        header.setProperty("class", "diagnostico_card_header")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)

        self.__titulo = QLabel(titulo)
        self.__titulo.setObjectName("diagnostico_card_titulo")
        header_layout.addWidget(self.__titulo)
        header_layout.addStretch()
        layout.addWidget(header)

        self.__body = QWidget()
        self.__body_layout = QHBoxLayout(self.__body)
        self.__body_layout.setContentsMargins(14, 10, 14, 14)
        self.__body_layout.setSpacing(10)
        layout.addWidget(self.__body)

    def definir_titulo(self, texto: str) -> None:
        """Define o texto completo do header do card."""
        self.__titulo.setText(texto)

    def adicionar_widget(self, widget: QWidget) -> None:
        """Adiciona um widget ao corpo do card."""
        self.__body_layout.addWidget(widget)

    def limpar_corpo(self) -> None:
        """Remove todos os widgets do corpo do card."""
        while self.__body_layout.count():
            item = self.__body_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)


class _DecisionOption(QLabel):
    """Bloco retangular representando uma opcao de decisao administrativa."""

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

    def marcar_escolhida(self) -> None:
        """Marca a opcao como escolhida pelo jogador (fundo colorido)."""
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
        """Marca como a opcao correcta que o jogador nao escolheu (borda dashed)."""
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

        self.__header_valor: QLabel
        self.__card_riscos: _CardWidget
        self.__card_fatores: _CardWidget
        self.__card_decisao: _CardWidget
        self.__card_tempo: _CardWidget
        self.__total_valor: QLabel
        self.__btn_continuar: QPushButton

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self) -> None:
        """Constroi toda a interface da pagina."""
        L = self.__layout_loader
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = self.__criar_scroll()
        outer.addWidget(scroll)

        container = QWidget()
        container.setObjectName("diagnostico_container")
        scroll.setWidget(container)

        self.__layout = QVBoxLayout(container)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__layout.setSpacing(L.scaled("pagina_diagnostico", "spacing"))
        self.__layout.setContentsMargins(20, 20, 20, 12)

        self.__criar_header()
        self.__criar_cards()
        self.__criar_total()
        self.__criar_botao()
        self.__layout.addStretch()

    def __criar_scroll(self) -> QScrollArea:
        """Cria e configura a area de scroll."""
        scroll = QScrollArea()
        scroll.setObjectName("diagnostico_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    def __criar_header(self) -> None:
        """Cria o cabecalho com pontuacao final."""
        label = QLabel("Pontuacao final")
        label.setObjectName("diagnostico_header_label")
        label.setProperty("class", "diagnostico_header_label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(label)

        self.__header_valor = QLabel("0 pts")
        self.__header_valor.setObjectName("diagnostico_header_valor")
        self.__header_valor.setProperty("class", "diagnostico_header_valor")
        self.__header_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(self.__header_valor)
        self.__layout.addSpacing(4)

    def __criar_cards(self) -> None:
        """Cria os quatro cards de detalhamento."""
        self.__card_riscos = _CardWidget("Riscos")
        self.__card_fatores = _CardWidget("Fatores de inseguranca")
        self.__card_decisao = _CardWidget("Decisao administrativa")
        self.__card_tempo = _CardWidget("Bonus de tempo")
        self.__layout.addWidget(self.__card_riscos)
        self.__layout.addWidget(self.__card_fatores)
        self.__layout.addWidget(self.__card_decisao)
        self.__layout.addWidget(self.__card_tempo)

    def __criar_total(self) -> None:
        """Cria a linha de total."""
        container = QWidget()
        container.setObjectName("diagnostico_total")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)

        label = QLabel("Total")
        label.setObjectName("diagnostico_total_label")
        layout.addWidget(label)
        layout.addStretch()

        self.__total_valor = QLabel("0 pts")
        self.__total_valor.setObjectName("diagnostico_total_valor")
        layout.addWidget(self.__total_valor)
        self.__layout.addWidget(container)

    def __criar_botao(self) -> None:
        """Cria o botao Continuar."""
        L = self.__layout_loader
        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar_diagnostico")
        self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
        self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        self.__layout.addWidget(self.__btn_continuar, 0, Qt.AlignmentFlag.AlignCenter)

    def exibir_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        """Preenche a pagina com os dados do resultado do diagnostico."""
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
        """Popula o card de riscos com tiles por estado."""
        total = len(f.riscos_acertados) + len(f.riscos_esquecidos) + len(f.riscos_inventados)
        self.__card_riscos.definir_titulo(
            f"Riscos \u00b7 {len(f.riscos_acertados)} de {total}    +{p.nota_riscos:.0f} pts"
        )
        self.__card_riscos.limpar_corpo()

        for risco in f.riscos_acertados:
            self.__adicionar_tile(self.__card_riscos, risco, "correto", f.score_por_risco.get(risco, 0.0))
        for risco in f.riscos_esquecidos:
            self.__adicionar_tile(self.__card_riscos, risco, "esquecido", 0.0)
        for risco in f.riscos_inventados:
            self.__adicionar_tile(self.__card_riscos, risco, "indevido", f.score_por_risco.get(risco, 0.0))

    def __popular_card_fatores(self, p, f) -> None:
        """Popula o card de fatores de inseguranca."""
        self.__card_fatores.definir_titulo(
            f"Fatores de inseguranca    +{p.nota_fatores:.0f} pts"
        )
        self.__card_fatores.limpar_corpo()

        dados = [
            ("ATO_INSEGURO", "Ato inseguro", "ato"),
            ("CONDICAO_INSEGURA", "Condicao insegura", "condicao"),
        ]
        for fator_nome, label, chave_icone in dados:
            estado = (
                "correto" if fator_nome in f.fatores_acertados
                else "esquecido" if fator_nome in f.fatores_esquecidos
                else "indevido" if fator_nome in f.fatores_inventados
                else "esquecido"
            )
            self.__adicionar_tile(
                self.__card_fatores, label, estado,
                f.score_por_fator.get(fator_nome, 0.0),
                eh_fator=True, chave_icone=chave_icone,
            )

    def __popular_card_decisao(self, p, f) -> None:
        """Popula o card de decisao administrativa com 3 opcoes."""
        self.__card_decisao.definir_titulo(
            f"Decisao administrativa    +{p.nota_decisao:.0f} pts"
        )
        self.__card_decisao.limpar_corpo()

        acertou = f.decisao_tomada == f.decisao_esperada

        for nome in ("ADVERTIR", "INTERDITAR", "IGNORAR"):
            cor = _DECISAO_CORES[nome]
            opcao = _DecisionOption(nome, cor)
            if nome == f.decisao_tomada:
                opcao.marcar_escolhida()
            elif nome == f.decisao_esperada and not acertou:
                opcao.marcar_correta_nao_escolhida()
            self.__card_decisao.adicionar_widget(opcao)

        resultado_label = QLabel("decisao correta" if acertou else "decisao incorreta")
        resultado_label.setObjectName("diagnostico_decisao_resultado")
        resultado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resultado_label.setStyleSheet(
            f"font-size: 10px; color: {'#71dd77' if acertou else '#ffb4ab'};"
            "padding: 6px 0 10px;"
        )
        self.__card_decisao.adicionar_widget(resultado_label)

    def __popular_card_tempo(self, p) -> None:
        """Popula o card de bonus de tempo."""
        self.__card_tempo.definir_titulo(
            f"Bonus de tempo    {p.pontos_bonus_tempo:+.0f} pts"
        )
        self.__card_tempo.limpar_corpo()

        label = QLabel(f"resposta em {p.tempo_resposta_segundos:.0f}s")
        label.setObjectName("diagnostico_tempo_label")
        label.setStyleSheet("font-size: 11px; color: #889484; padding: 10px 14px;")
        self.__card_tempo.adicionar_widget(label)

    def __popular_total(self, p) -> None:
        """Define o valor da linha de total."""
        self.__total_valor.setText(f"{p.pontuacao_final:.0f} pts")

    def __adicionar_tile(
        self, card: _CardWidget, nome: str, estado: str, score: float,
        eh_fator: bool = False, chave_icone: str = "",
    ) -> None:
        """Adiciona um tile ao card com o estado visual correcto."""
        cor = _COR_FATOR if eh_fator else _RISCO_CORES.get(nome, "#5f5e5a")
        nome_exibicao = nome if eh_fator else _RISCO_NOMES.get(nome, nome)

        container = QWidget()
        container.setFixedWidth(80)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tile = _RiskTile()
        if estado == "correto":
            tile.setStyleSheet(f"background-color: {cor}; border-radius: 8px;")
            if eh_fator:
                icone = _resolver_icone_fator(chave_icone, "_dark")
            else:
                icone = _resolver_icone_risco(nome, "_dark")
        elif estado == "esquecido":
            tile.setStyleSheet(f"background-color: transparent; border: 2px solid {cor}; border-radius: 8px;")
            if eh_fator:
                icone = _resolver_icone_fator(chave_icone, "_white")
            else:
                icone = _resolver_icone_risco(nome, "_color")
        else:
            tile.setStyleSheet(f"background-color: {cor}; border-radius: 8px; opacity: 0.55;")
            if eh_fator:
                icone = _resolver_icone_fator(chave_icone, "_dark")
            else:
                icone = _resolver_icone_risco(nome, "_dark")

        if icone:
            tile.definir_icone(str(icone))
        vbox.addWidget(tile, 0, Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(nome_exibicao)
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
        if hasattr(self, '_PaginaDiagnostico__layout'):
            self.__layout.setSpacing(L.scaled("pagina_diagnostico", "spacing"))
            self.__layout.setContentsMargins(20, 20, 20, 12)
