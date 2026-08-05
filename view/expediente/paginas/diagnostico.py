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

_TILE_STATE_CORRETO = "correto"
_TILE_STATE_ESQUECIDO = "esquecido"
_TILE_STATE_INDEVIDO = "indevido"

_SCORE_COR_POSITIVO = "#71dd77"
_SCORE_COR_NEGATIVO = "#ffb4ab"
_SCORE_COR_NEUTRO = "#889484"

_DECISAO_STATUS = {
    "OTIMA": ("decisao otima", "#71dd77"),
    "BOA": ("decisao boa", "#d9a824"),
    "INCORRETA": ("decisao incorreta", "#ffb4ab"),
}

_TILE_ICONE_SUFIXO = {
    _TILE_STATE_CORRETO: "_dark",
    _TILE_STATE_ESQUECIDO: "_color",
    _TILE_STATE_INDEVIDO: "_dark",
}
_FATOR_ICONE_SUFIXO = {
    _TILE_STATE_CORRETO: "_dark",
    _TILE_STATE_ESQUECIDO: "_white",
    _TILE_STATE_INDEVIDO: "_dark",
}
_TILE_CONTAINER_SPACING = 4
_HEADER_BODY_SPACING = 4

_TILE_STYLE = {
    _TILE_STATE_CORRETO: "background-color: {cor};",
    _TILE_STATE_ESQUECIDO: "border: 2px solid {cor};",
}

_SCORE_FORMAT = {
    _TILE_STATE_CORRETO: ("+{score:.0f} pts", _SCORE_COR_POSITIVO),
    _TILE_STATE_INDEVIDO: ("{score:+.0f} pts", _SCORE_COR_NEGATIVO),
    _TILE_STATE_ESQUECIDO: ("+0 pts", _SCORE_COR_NEUTRO),
}


def _hex_para_rgba(hex_str: str, alpha: float) -> str:
    """Converte uma cor hex (#RRGGBB) para rgba(r, g, b, alpha)."""
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def _resolver_icone(nome: str, sufixo: str) -> Path | None:
    """Resolve o caminho de um icone de risco ou factor."""
    assets = Path(__file__).resolve().parent.parent.parent / "assets"
    caminho = assets / "icons" / "riscos" / f"{nome}{sufixo}.png"
    return caminho if caminho.exists() else None


class _RiskTile(QFrame):
    """Tile quadrado que exibe o icone de um risco ou factor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__layout = LayoutLoader.instance()
        tile_size = self.__layout.scaled("pagina_diagnostico", "tile", "size")
        icon_size = self.__layout.scaled("pagina_diagnostico", "tile", "icon_size")

        self.setObjectName("diagnostico_tile")
        self.setFixedSize(tile_size, tile_size)
        self.setProperty("class", "diagnostico_tile")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__icone = QLabel()
        self.__icone.setObjectName("diagnostico_tile_icone")
        self.__icone.setProperty("class", "diagnostico_tile_icone")
        self.__icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__icone.setFixedSize(icon_size, icon_size)
        self.__icone.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.__icone, 0, Qt.AlignmentFlag.AlignCenter)

        self.__icon_size = icon_size
        self.__caminho_icone: str | None = None
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def definir_icone(self, caminho: str) -> None:
        """Carrega e exibe o icone no tile."""
        self.__caminho_icone = caminho
        pixmap = QPixmap(caminho).scaled(
            self.__icon_size, self.__icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.__icone.setPixmap(pixmap)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        tile_size = self.__layout.scaled("pagina_diagnostico", "tile", "size")
        icon_size = self.__layout.scaled("pagina_diagnostico", "tile", "icon_size")
        self.setFixedSize(tile_size, tile_size)
        self.__icone.setFixedSize(icon_size, icon_size)
        self.__icon_size = icon_size
        if self.__caminho_icone:
            pixmap = QPixmap(self.__caminho_icone).scaled(
                icon_size, icon_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.__icone.setPixmap(pixmap)


class _CardWidget(QFrame):
    """Card com header (titulo) e area de conteudo."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.__layout = LayoutLoader.instance()
        ph = self.__layout.scaled("pagina_diagnostico", "card", "padding_h")
        pv = self.__layout.scaled("pagina_diagnostico", "card", "padding_v")
        gap = self.__layout.scaled("pagina_diagnostico", "card", "gap")

        self.setObjectName("diagnostico_card")
        self.setProperty("class", "diagnostico_card")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setFrameShape(QFrame.Shape.NoFrame)
        header.setObjectName("diagnostico_card_header")
        header.setProperty("class", "diagnostico_card_header")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(ph, 6, ph, 6)

        self.__header_layout = header_layout

        self.__titulo = QLabel(titulo)
        self.__titulo.setObjectName("diagnostico_card_titulo")
        self.__titulo.setProperty("class", "diagnostico_card_titulo")
        header_layout.addWidget(self.__titulo)
        header_layout.addStretch()

        self.__pontos = QLabel("")
        self.__pontos.setObjectName("diagnostico_card_pontos")
        self.__pontos.setProperty("class", "diagnostico_card_pontos")
        header_layout.addWidget(self.__pontos)
        layout.addWidget(header)

        self.__body = QFrame()
        self.__body.setObjectName("diagnostico_card_body")
        self.__body.setProperty("class", "diagnostico_card_body")
        self.__body.setFrameShape(QFrame.Shape.NoFrame)
        self.__body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.__body_layout = QHBoxLayout(self.__body)
        self.__body_layout.setContentsMargins(ph + 2, pv, ph + 2, ph + 2)
        self.__body_layout.setSpacing(gap)
        layout.addWidget(self.__body)

        self.__ph = ph
        self.__pv = pv
        self.__gap = gap
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def definir_titulo(self, texto: str) -> None:
        """Define o texto completo do header do card."""
        self.__titulo.setText(texto)

    def definir_pontos(self, texto: str) -> None:
        """Define o texto de pontuacao alinhado a direita."""
        self.__pontos.setText(texto)

    def adicionar_widget(self, widget: QWidget) -> None:
        """Adiciona um widget ao corpo do card."""
        self.__body_layout.addWidget(widget)

    def limpar_corpo(self) -> None:
        """Remove todos os widgets do corpo do card."""
        while self.__body_layout.count():
            item = self.__body_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        ph = self.__layout.scaled("pagina_diagnostico", "card", "padding_h")
        pv = self.__layout.scaled("pagina_diagnostico", "card", "padding_v")
        gap = self.__layout.scaled("pagina_diagnostico", "card", "gap")
        self.__body_layout.setContentsMargins(ph + 2, pv, ph + 2, ph + 2)
        self.__body_layout.setSpacing(gap)
        self.__header_layout.setContentsMargins(ph, 6, ph, 6)
        self.__ph = ph
        self.__pv = pv
        self.__gap = gap


class _DecisionOption(QFrame):
    """Bloco retangular representando uma opcao de decisao administrativa."""

    def __init__(self, texto: str, cor: str, parent=None):
        super().__init__(parent)
        self.__layout = LayoutLoader.instance()
        altura = self.__layout.scaled("pagina_diagnostico", "decisao", "opcao_altura")
        largura_min = self.__layout.scaled("pagina_diagnostico", "decisao", "opcao_largura_min")

        self.setObjectName("diagnostico_decisao_opcao")
        self.setProperty("class", "diagnostico_decisao_opcao")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setFixedHeight(altura)
        self.setMinimumWidth(largura_min)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.__cor = cor

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label = QLabel(texto)
        self.__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.__label)

        self.setProperty("decisao_state", "nao_escolhida")
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def marcar_escolhida(self) -> None:
        """Marca a opcao como escolhida pelo jogador (fundo colorido)."""
        self.setProperty("decisao_state", "escolhida")
        self.setStyleSheet(
            f"background-color: {self.__cor};"
            f"border: 2px solid {self.__cor};"
            "border-radius: 4px;"
            "font-weight: 800;"
            "font-size: 13px;"
            "letter-spacing: 0.05em;"
            "color: #ffffff;"
        )

    def marcar_correta_nao_escolhida(self) -> None:
        """Marca como a opcao correcta que o jogador nao escolheu (borda dashed)."""
        self.setProperty("decisao_state", "correta_nao_escolhida")
        self.setStyleSheet(
            f"border: 2px dashed {self.__cor};"
            "background-color: transparent;"
            "border-radius: 4px;"
            "font-weight: 800;"
            "font-size: 13px;"
            "letter-spacing: 0.05em;"
            "color: #5f5e5a;"
        )

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        self.setFixedHeight(self.__layout.scaled("pagina_diagnostico", "decisao", "opcao_altura"))
        self.setMinimumWidth(self.__layout.scaled("pagina_diagnostico", "decisao", "opcao_largura_min"))


class PaginaDiagnostico(QFrame):
    """Pagina de diagnostico detalhado com cards, tiles e badges."""

    continuar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_diagnostico")
        self.setProperty("class", "pagina_diagnostico")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.__layout_loader = LayoutLoader.instance()
        self.__resultado: ResultadoDiagnosticoDTO | None = None
        self.__tile_containers: list[QWidget] = []

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
        container.setProperty("class", "diagnostico_container")
        scroll.setWidget(container)

        self.__layout = QVBoxLayout(container)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__layout.setSpacing(L.scaled("pagina_diagnostico", "spacing"))
        self.__layout.setContentsMargins(*L.scaled_margins("pagina_diagnostico", "margins"))

        self.__criar_header()
        self.__criar_cards()
        self.__criar_total()
        self.__criar_botao()
        self.__layout.addStretch()

    def __criar_scroll(self) -> QScrollArea:
        """Cria e configura a area de scroll."""
        scroll = QScrollArea()
        scroll.setObjectName("diagnostico_scroll")
        scroll.setProperty("class", "diagnostico_scroll")
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
        self.__layout.addSpacing(_HEADER_BODY_SPACING)

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
        container = QFrame()
        container.setObjectName("diagnostico_total")
        container.setProperty("class", "diagnostico_total")
        container.setFrameShape(QFrame.Shape.NoFrame)
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)

        label = QLabel("Total")
        label.setObjectName("diagnostico_total_label")
        label.setProperty("class", "diagnostico_total_label")
        layout.addWidget(label)
        layout.addStretch()

        self.__total_valor = QLabel("0 pts")
        self.__total_valor.setObjectName("diagnostico_total_valor")
        self.__total_valor.setProperty("class", "diagnostico_total_valor")
        layout.addWidget(self.__total_valor)
        self.__layout.addWidget(container)

    def __criar_botao(self) -> None:
        """Cria o botao Continuar."""
        L = self.__layout_loader
        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar_diagnostico")
        self.__btn_continuar.setProperty("class", "btn_continuar_diagnostico")
        self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
        self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        self.__layout.addWidget(self.__btn_continuar, 0, Qt.AlignmentFlag.AlignCenter)

    def exibir_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        """Preenche a pagina com os dados do resultado do diagnostico."""
        logger.info("Diagnostico exibido: pontuacao_final=%.0f", resultado.pontuacao.pontuacao_final)
        self.__resultado = resultado
        self.__tile_containers.clear()
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
            f"Riscos \u00b7 {len(f.riscos_acertados)} de {total}"
        )
        self.__card_riscos.definir_pontos(f"+{p.nota_riscos:.0f} pts")
        self.__card_riscos.limpar_corpo()

        for risco in f.riscos_acertados:
            self.__adicionar_tile_risco(self.__card_riscos, risco, "correto", f.score_por_risco.get(risco, 0.0))
        for risco in f.riscos_esquecidos:
            self.__adicionar_tile_risco(self.__card_riscos, risco, "esquecido", 0.0)
        for risco in f.riscos_inventados:
            self.__adicionar_tile_risco(self.__card_riscos, risco, "indevido", f.score_por_risco.get(risco, 0.0))

    def __popular_card_fatores(self, p, f) -> None:
        """Popula o card de fatores de inseguranca."""
        self.__card_fatores.definir_titulo("Fatores de inseguranca")
        self.__card_fatores.definir_pontos(f"+{p.nota_fatores:.0f} pts")
        self.__card_fatores.limpar_corpo()

        dados = [
            ("ATO_INSEGURO", "ato"),
            ("CONDICAO_INSEGURA", "condicao"),
        ]
        for fator_nome, chave_icone in dados:
            estado = (
                "correto" if fator_nome in f.fatores_acertados
                else "esquecido" if fator_nome in f.fatores_esquecidos
                else "indevido" if fator_nome in f.fatores_inventados
                else "esquecido"
            )
            self.__adicionar_tile_fator(
                self.__card_fatores, estado,
                f.score_por_fator.get(fator_nome, 0.0),
                chave_icone,
            )

    def __popular_card_decisao(self, p, f) -> None:
        """Popula o card de decisao administrativa com 3 opcoes."""
        self.__card_decisao.definir_titulo("Decisao administrativa")
        self.__card_decisao.definir_pontos(f"+{p.nota_decisao:.0f} pts")
        self.__card_decisao.limpar_corpo()

        acertou = f.decisao_tomada == f.decisao_esperada
        status = p.status_decisao_jogador
        qualidade = "otima" if status == "OTIMA" else "boa" if status == "BOA" else "incorreta"
        self.__card_decisao.setProperty("decisao_qualidade", qualidade)

        decisao_anulada = p.decisao_anulada

        for nome in ("ADVERTIR", "INTERDITAR", "IGNORAR"):
            cor = _DECISAO_CORES[nome]
            opcao = _DecisionOption(nome, cor)
            if nome == f.decisao_tomada:
                opcao.marcar_escolhida()
            elif nome == f.decisao_esperada and not acertou:
                opcao.marcar_correta_nao_escolhida()
            self.__card_decisao.adicionar_widget(opcao)

        texto, cor = _DECISAO_STATUS.get(status, ("decisao incorreta", _SCORE_COR_NEGATIVO))

        if decisao_anulada:
            texto = "solucao sem sentido"
            cor = _SCORE_COR_NEGATIVO

        resultado_label = QLabel(texto)
        resultado_label.setObjectName("diagnostico_decisao_resultado")
        resultado_label.setProperty("class", "diagnostico_decisao_resultado")
        resultado_label.setProperty("decisao_acerto", qualidade)
        resultado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resultado_label.setStyleSheet(f"color: {cor};")
        self.__card_decisao.adicionar_widget(resultado_label)

    def __popular_card_tempo(self, p) -> None:
        """Popula o card de bonus de tempo."""
        self.__card_tempo.definir_titulo("Bonus de tempo")
        self.__card_tempo.definir_pontos(f"{p.pontos_bonus_tempo:+.0f} pts")
        self.__card_tempo.limpar_corpo()

        label = QLabel(f"resposta em {p.tempo_resposta_segundos:.0f}s")
        label.setObjectName("diagnostico_tempo_label")
        label.setProperty("class", "diagnostico_tempo_label")
        self.__card_tempo.adicionar_widget(label)

    def __popular_total(self, p) -> None:
        """Define o valor da linha de total."""
        self.__total_valor.setText(f"{p.pontuacao_final:.0f} pts")

    def __adicionar_tile_risco(
        self, card: _CardWidget, risco: str, estado: str, score: float,
    ) -> None:
        """Adiciona um tile de risco ao card."""
        cor = _RISCO_CORES.get(risco, "#5f5e5a")
        nome_exibicao = _RISCO_NOMES.get(risco, risco)
        sufixo = _TILE_ICONE_SUFIXO.get(estado, "_dark")
        icone = _resolver_icone(f"risco_{risco.lower()}", sufixo)

        self.__construir_tile(card, cor, nome_exibicao, estado, score, icone)

    def __adicionar_tile_fator(
        self, card: _CardWidget, estado: str, score: float, chave_icone: str,
    ) -> None:
        """Adiciona um tile de factor ao card."""
        cor = _COR_FATOR

        nome_map = {"ato": "Ato inseguro", "condicao": "Condicao insegura"}
        nome_exibicao = nome_map.get(chave_icone, chave_icone)
        sufixo = _FATOR_ICONE_SUFIXO.get(estado, "_dark")
        icone = _resolver_icone(chave_icone, sufixo)

        self.__construir_tile(card, cor, nome_exibicao, estado, score, icone)

    def __construir_tile(
        self, card: _CardWidget, cor: str, nome_exibicao: str,
        estado: str, score: float, icone: Path | None,
    ) -> None:
        """Constroi o container do tile e adiciona-o ao card."""
        container = QWidget()
        container.setObjectName("diagnostico_tile_container")
        container.setProperty("class", "diagnostico_tile_container")
        container.setFixedWidth(self.__layout_loader.scaled("pagina_diagnostico", "tile", "container_width"))
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(_TILE_CONTAINER_SPACING)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tile = _RiskTile()
        tile.setProperty("tile_state", estado)
        estilo = _TILE_STYLE.get(estado)
        if estilo is not None:
            tile.setStyleSheet(estilo.format(cor=cor))
        else:
            tile.setStyleSheet(f"background-color: {_hex_para_rgba(cor, 0.45)};")

        if icone:
            tile.definir_icone(str(icone))
        vbox.addWidget(tile, 0, Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(nome_exibicao)
        nome_label.setObjectName("diagnostico_tile_nome")
        nome_label.setProperty("class", "diagnostico_tile_nome")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(nome_label)

        score_fmt, score_cor = _SCORE_FORMAT.get(estado, ("+0 pts", _SCORE_COR_NEUTRO))
        score_texto = score_fmt.format(score=score)

        score_label = QLabel(score_texto)
        score_label.setObjectName("diagnostico_tile_score")
        score_label.setProperty("class", "diagnostico_tile_score")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet(f"color: {score_cor};")
        vbox.addWidget(score_label)

        card.adicionar_widget(container)
        self.__tile_containers.append(container)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        L = self.__layout_loader
        if self.__btn_continuar is not None:
            self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
            self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
        self.__layout.setSpacing(L.scaled("pagina_diagnostico", "spacing"))
        self.__layout.setContentsMargins(*L.scaled_margins("pagina_diagnostico", "margins"))
        container_width = L.scaled("pagina_diagnostico", "tile", "container_width")
        for c in self.__tile_containers:
            if c is not None:
                c.setFixedWidth(container_width)
