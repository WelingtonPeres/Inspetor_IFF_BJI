"""
Tela de vitoria — expediente concluido com sucesso.

Espelha a estrutura do GameOver (CRT overlay, card CIPA, parecer,
pictogramas decorativos) mas com paleta verde de aprovacao.
Inclui efeito de confete.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPainter, QTransform
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.dtos.parecer_cipa import ParecerCIPA
from core.interfaces.i_pareceres_cipa import IPareceresCIPA
from infrastructure.repository.repositorio_pareceres_cipa import (
    ParecerCIPAIndisponivelError,
)
from infrastructure.repository.repositorio_pareceres_cipavitoria import (
    RepositorioDePareceresCIPAVitoria,
)
from view.infrastructure.layout_loader import LayoutLoader
from view.widgets.efeitos.background_riscos import BackgroundRiscos
from view.widgets.efeitos.confetti_overlay import ConfettiOverlay
from view.widgets.efeitos.crt_overlay import CrtEffectsOverlay
from view.widgets.efeitos.trofeu_icon import TrofeuIcon

logger = logging.getLogger(__name__)


_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
_ICONS_FIM_JOGO = _ASSETS_DIR / "icons" / "fim_jogo"

_MESES = (
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ",
)


class GameWin(QFrame):
    """Tela de vitoria com estetica terminal CRT e parecer da CIPA."""

    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()
    sair_solicitado = Signal()

    def __init__(
        self,
        pontuacao_global: float,
        repositorio: Optional[IPareceresCIPA] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("game_win")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__pontuacao_global: float = pontuacao_global
        self.__repositorio: IPareceresCIPA = (
            repositorio if repositorio is not None
            else RepositorioDePareceresCIPAVitoria()
        )

        self.__layout_loader: LayoutLoader = LayoutLoader.instance()

        self.__timer_timestamp: QTimer = None
        self.__crt_overlay: CrtEffectsOverlay = None
        self.__bg_riscos: BackgroundRiscos = None
        self.__confetti_overlay: ConfettiOverlay = None
        self.__label_header: QLabel = None
        self.__label_timestamp: QLabel = None
        self.__trofeu: TrofeuIcon = None
        self.__label_titulo: QLabel = None
        self.__label_subtitulo: QLabel = None
        self.__card: QFrame = None
        self.__label_card_cabecalho: QLabel = None
        self.__label_card_subcabecalho: QLabel = None
        self.__card_divider: QFrame = None
        self.__label_parecer_num: QLabel = None
        self.__label_parecer_texto: QLabel = None
        self.__scroll_parecer: QScrollArea = None
        self.__label_pontuacao_label: QLabel = None
        self.__label_pontuacao_valor: QLabel = None
        self.__btn_jogar_novamente: QPushButton = None
        self.__btn_menu_principal: QPushButton = None
        self.__btn_sair: QPushButton = None

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def exibir_resultado(self, pontuacao_global: float, perfil: str) -> None:
        """API agregada chamada pelo Presenter ao terminar a campanha."""
        self.atualizar_pontuacao(pontuacao_global)
        self.definir_parecer(perfil)

    def atualizar_pontuacao(self, pontuacao_global: float) -> None:
        self.__pontuacao_global = pontuacao_global
        self.__label_pontuacao_valor.setText(f"{pontuacao_global:.0f} pts")
        self.__atualizar_timestamp()

    def definir_parecer(self, curso: str) -> None:
        try:
            parecer: ParecerCIPA = self.__repositorio.obter_parecer_para_curso(curso)
        except ParecerCIPAIndisponivelError as exc:
            logger.warning("Parecer indisponivel: %s", exc)
            self.__label_parecer_texto.setText("Parecer indisponivel.")
            return
        self.__label_parecer_texto.setText(parecer.texto)
        self.__label_parecer_num.setText(
            f"Parecer n\u00BA {parecer.numero} \u00B7 Ref: {parecer.referencia}"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        r = self.rect()
        self.__crt_overlay.setGeometry(r)
        self.__bg_riscos.setGeometry(r)
        self.__confetti_overlay.setGeometry(r)
        self.__ajustar_tamanho_do_card()

    def showEvent(self, event):
        super().showEvent(event)
        if self.__timer_timestamp is not None:
            self.__timer_timestamp.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.__timer_timestamp is not None:
            self.__timer_timestamp.stop()

    def __setup_ui(self) -> None:
        L = self.__layout_loader
        margem = L.scaled("gamewin", "spacing", "margem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(margem, margem, margem, margem)
        layout.setSpacing(0)

        self.__build_efeitos_visuais()
        self.__build_header(layout)
        layout.addStretch()
        self.__build_trofeu_e_titulo(layout)
        layout.addSpacing(L.scaled("gamewin", "spacing", "entre_titulo_card"))
        self.__build_card(layout)
        layout.addSpacing(L.scaled("gamewin", "spacing", "entre_card_score"))
        self.__build_score(layout)
        layout.addSpacing(L.scaled("gamewin", "spacing", "entre_score_botoes"))
        self.__build_botoes(layout)
        layout.addStretch()

    def __build_efeitos_visuais(self) -> None:
        self.__crt_overlay = CrtEffectsOverlay(self)
        self.__crt_overlay.setGeometry(self.rect())

        self.__bg_riscos = BackgroundRiscos(
            self.__layout_loader, _ICONS_FIM_JOGO, self, layout_key="gamewin",
        )
        self.__bg_riscos.setGeometry(self.rect())

        self.__confetti_overlay = ConfettiOverlay(self)
        self.__confetti_overlay.setGeometry(self.rect())

    def __build_header(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.__label_header = QLabel("\u25CF IFF-BJI \u00B7 SESS\u00C3O DE INSPE\u00C7\u00C3O")
        self.__label_header.setObjectName("gamewin_header")
        font = QFont("Open Sans")
        font.setPointSize(L.scaled("gamewin", "fontes", "header", "size"))
        font.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gamewin", "fontes", "header", "letter_spacing"),
        )
        self.__label_header.setFont(font)

        self.__label_timestamp = QLabel()
        self.__label_timestamp.setObjectName("gamewin_timestamp")
        font_ts = QFont("Courier New")
        font_ts.setPointSize(L.scaled("gamewin", "fontes", "timestamp", "size"))
        self.__label_timestamp.setFont(font_ts)
        self.__atualizar_timestamp()

        row_layout.addWidget(self.__label_header)
        row_layout.addStretch()
        row_layout.addWidget(self.__label_timestamp)
        layout.addWidget(row)

    def __build_trofeu_e_titulo(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader

        self.__trofeu = TrofeuIcon(
            cor="#FFD700",
            tamanho=L.scaled("gamewin", "fontes", "trophy", "size"),
        )
        container_trofeu = QWidget()
        container_layout = QHBoxLayout(container_trofeu)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.__trofeu)
        layout.addWidget(container_trofeu)

        self.__label_titulo = QLabel("CASO ENCERRADO")
        self.__label_titulo.setObjectName("gamewin_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Open Sans")
        font.setPointSize(L.scaled("gamewin", "fontes", "titulo", "size"))
        font.setWeight(QFont.Weight.ExtraBold)
        font.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gamewin", "fontes", "titulo", "letter_spacing"),
        )
        self.__label_titulo.setFont(font)
        layout.addWidget(self.__label_titulo)

        self.__label_subtitulo = QLabel("Credencial de inspetor mantida")
        self.__label_subtitulo.setObjectName("gamewin_subtitulo")
        self.__label_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_sub = QFont("Open Sans")
        font_sub.setPointSize(L.scaled("gamewin", "fontes", "subtitulo", "size"))
        font_sub.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gamewin", "fontes", "subtitulo", "letter_spacing"),
        )
        self.__label_subtitulo.setFont(font_sub)
        layout.addWidget(self.__label_subtitulo)

    def __build_card(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__card = QFrame()
        self.__card.setObjectName("gamewin_card")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(L.scaled("gamewin", "shadow", "blur"))
        shadow.setOffset(
            L.scaled("gamewin", "shadow", "offset_x"),
            L.scaled("gamewin", "shadow", "offset_y"),
        )
        shadow.setColor(QColor(0, 0, 0, 180))
        self.__card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.__card)
        card_layout.setContentsMargins(
            L.scaled("gamewin", "card", "padding", "left"),
            L.scaled("gamewin", "card", "padding", "top"),
            L.scaled("gamewin", "card", "padding", "right"),
            L.scaled("gamewin", "card", "padding", "bottom"),
        )
        card_layout.setSpacing(0)

        font_cab = QFont("Open Sans")
        font_cab.setPointSize(L.scaled("gamewin", "fontes", "card_cabecalho", "size"))
        font_cab.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gamewin", "fontes", "card_cabecalho", "letter_spacing"),
        )

        self.__label_card_cabecalho = QLabel(
            "IFF Fluminense \u00B7 Campus Bom Jesus do Itabapoana"
        )
        self.__label_card_cabecalho.setObjectName("gamewin_card_cabecalho")
        self.__label_card_cabecalho.setFont(font_cab)
        card_layout.addWidget(self.__label_card_cabecalho)

        self.__label_card_subcabecalho = QLabel(
            "Comiss\u00E3o Interna de Preven\u00E7\u00E3o de Acidentes \u2014 CIPA"
        )
        self.__label_card_subcabecalho.setObjectName("gamewin_card_subcabecalho")
        font_subcab = QFont("Open Sans")
        font_subcab.setPointSize(
            L.scaled("gamewin", "fontes", "card_subcabecalho", "size")
        )
        font_subcab.setWeight(QFont.Weight.Bold)
        self.__label_card_subcabecalho.setFont(font_subcab)
        card_layout.addWidget(self.__label_card_subcabecalho)

        spacers_top = QWidget()
        spacers_top.setFixedHeight(L.scaled("gamewin", "spacing", "spacers_top"))
        card_layout.addWidget(spacers_top)

        self.__card_divider = QFrame()
        self.__card_divider.setObjectName("gamewin_card_divider")
        self.__card_divider.setFixedHeight(
            L.scaled("gamewin", "spacing", "card_divider_altura")
        )
        card_layout.addWidget(self.__card_divider)

        spacers_mid = QWidget()
        spacers_mid.setFixedHeight(L.scaled("gamewin", "spacing", "spacers_mid"))
        card_layout.addWidget(spacers_mid)

        self.__label_parecer_num = QLabel()
        self.__label_parecer_num.setObjectName("gamewin_card_parecer_num")
        font_ref = QFont("Open Sans")
        font_ref.setPointSize(
            L.scaled("gamewin", "fontes", "card_parecer_num", "size")
        )
        self.__label_parecer_num.setFont(font_ref)
        card_layout.addWidget(self.__label_parecer_num)

        spacers_ref = QWidget()
        spacers_ref.setFixedHeight(L.scaled("gamewin", "spacing", "spacers_ref"))
        card_layout.addWidget(spacers_ref)

        self.__label_parecer_texto = QLabel()
        self.__label_parecer_texto.setObjectName("gamewin_card_parecer_texto")
        self.__label_parecer_texto.setWordWrap(True)
        self.__label_parecer_texto.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.__label_parecer_texto.setMaximumHeight(
            L.scaled("gamewin", "card", "parecer_max_height")
        )
        font_texto = QFont("Open Sans")
        font_texto.setPointSize(
            L.scaled("gamewin", "fontes", "card_parecer_texto", "size")
        )
        self.__label_parecer_texto.setFont(font_texto)
        self.__scroll_parecer = QScrollArea()
        self.__scroll_parecer.setWidgetResizable(True)
        self.__scroll_parecer.setFrameShape(QFrame.Shape.NoFrame)
        self.__scroll_parecer.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.__scroll_parecer.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.__scroll_parecer.setStyleSheet("background-color: transparent;")
        self.__scroll_parecer.viewport().setStyleSheet("background-color: transparent;")
        self.__scroll_parecer.setWidget(self.__label_parecer_texto)
        card_layout.addWidget(self.__scroll_parecer)

        self.__card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.__card.setMinimumHeight(L.scaled("gamewin", "card", "altura_minima"))
        layout.addWidget(self.__card, alignment=Qt.AlignmentFlag.AlignCenter)

    def __build_score(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__label_pontuacao_label = QLabel("PONTUA\u00C7\u00C3O FINAL")
        self.__label_pontuacao_label.setObjectName("gamewin_score_label")
        self.__label_pontuacao_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_lbl = QFont("Open Sans")
        font_lbl.setPointSize(L.scaled("gamewin", "fontes", "score_label", "size"))
        font_lbl.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gamewin", "fontes", "score_label", "letter_spacing"),
        )
        self.__label_pontuacao_label.setFont(font_lbl)
        layout.addWidget(self.__label_pontuacao_label)

        self.__label_pontuacao_valor = QLabel(f"{self.__pontuacao_global:.0f} pts")
        self.__label_pontuacao_valor.setObjectName("gamewin_score_valor")
        self.__label_pontuacao_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_val = QFont("Open Sans")
        font_val.setPointSize(L.scaled("gamewin", "fontes", "score_valor", "size"))
        font_val.setWeight(QFont.Weight.ExtraBold)
        self.__label_pontuacao_valor.setFont(font_val)
        layout.addWidget(self.__label_pontuacao_valor)

    def __build_botoes(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        altura = L.scaled("gamewin", "botoes", "altura")
        largura_min = L.scaled("gamewin", "botoes", "largura_min")
        font_btn = QFont("Open Sans")
        font_btn.setPointSize(L.scaled("gamewin", "fontes", "botao", "size"))
        font_btn.setWeight(QFont.Weight.Bold)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(L.scaled("gamewin", "spacing", "entre_botoes_row"))

        self.__btn_menu_principal = self.__make_btn(
            "Menu principal", "gamewin_btn_menu",
            self.voltar_menu_solicitado.emit,
            altura, largura_min, font_btn,
        )
        self.__btn_jogar_novamente = self.__make_btn(
            "Jogar novamente", "gamewin_btn_retry",
            self.jogar_novamente_solicitado.emit,
            altura, largura_min, font_btn,
        )
        self.__btn_sair = self.__make_btn(
            "Sair do Jogo", "gamewin_btn_quit",
            self.sair_solicitado.emit,
            altura, largura_min, font_btn,
        )

        row_layout.addStretch()
        row_layout.addWidget(self.__btn_menu_principal)
        row_layout.addWidget(self.__btn_jogar_novamente)
        row_layout.addWidget(self.__btn_sair)
        row_layout.addStretch()

        layout.addWidget(row)

    def __make_btn(self, texto, object_name, callback, altura, largura_min, font):
        btn = QPushButton(texto)
        btn.setObjectName(object_name)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(altura)
        btn.setMinimumWidth(largura_min)
        btn.setFont(font)
        btn.clicked.connect(callback)
        return btn

    def __atualizar_timestamp(self) -> None:
        agora = datetime.now()
        mes = _MESES[agora.month - 1]
        texto = f"{agora:%H:%M:%S} \u00B7 {agora.day:02d} {mes} {agora.year}"
        self.__label_timestamp.setText(texto)

    def __ajustar_tamanho_do_card(self) -> None:
        L = self.__layout_loader
        disponivel = self.width() - 40
        fator = L.get("gamewin", "card", "fator_largura")
        alvo = int(disponivel * fator)
        largura_min = L.scaled("gamewin", "card", "largura_min")
        largura_max = L.scaled("gamewin", "card", "largura_max")
        largura = max(largura_min, min(alvo, largura_max))
        self.__card.setFixedWidth(largura)
        self.__card.setMinimumHeight(
            L.scaled("gamewin", "card", "altura_minima")
        )

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = self.__layout_loader

        for label, grupo in [
            (self.__label_header, "header"),
            (self.__label_timestamp, "timestamp"),
            (self.__label_titulo, "titulo"),
            (self.__label_subtitulo, "subtitulo"),
            (self.__label_card_cabecalho, "card_cabecalho"),
            (self.__label_card_subcabecalho, "card_subcabecalho"),
            (self.__label_parecer_num, "card_parecer_num"),
            (self.__label_parecer_texto, "card_parecer_texto"),
            (self.__label_pontuacao_label, "score_label"),
            (self.__label_pontuacao_valor, "score_valor"),
        ]:
            font = label.font()
            font.setPointSize(L.scaled("gamewin", "fontes", grupo, "size"))
            label.setFont(font)

        self.__label_parecer_texto.setMaximumHeight(
            L.scaled("gamewin", "card", "parecer_max_height")
        )
        self.__card.setMinimumHeight(L.scaled("gamewin", "card", "altura_minima"))
        self.__ajustar_tamanho_do_card()
        self.__bg_riscos.invalidar_cache()
