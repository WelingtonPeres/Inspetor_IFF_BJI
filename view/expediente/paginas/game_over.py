import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.dtos.parecer_cipa import ParecerCIPA
from infrastructure.repository.repositorio_pareceres_cipa import (
    ParecerCIPAIndisponivelError,
    RepositorioDePareceresCIPA,
)
from view.infrastructure.layout_loader import LayoutLoader
from view.widgets.efeitos.crt_overlay import CrtEffectsOverlay

logger = logging.getLogger(__name__)


_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
_ICONS_FIM_JOGO = _ASSETS_DIR / "icons" / "fim_jogo"

_MESES = (
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ",
)


class GameOver(QFrame):
    """Tela de derrota com estetica terminal CRT e parecer da CIPA."""

    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()
    sair_solicitado = Signal()

    def __init__(
        self,
        pontuacao_global: float,
        repositorio: Optional[RepositorioDePareceresCIPA] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("game_over")
        self.setProperty("class", "game_over")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__pontuacao_global: float = pontuacao_global
        self.__repositorio: RepositorioDePareceresCIPA = (
            repositorio if repositorio is not None else RepositorioDePareceresCIPA()
        )

        self.__layout_loader: LayoutLoader = LayoutLoader.instance()

        self.__crt_overlay: CrtEffectsOverlay

        self.__label_header: QLabel
        self.__label_timestamp: QLabel
        self.__label_titulo: QLabel
        self.__label_subtitulo: QLabel
        self.__card: QFrame
        self.__label_card_cabecalho: QLabel
        self.__label_card_subcabecalho: QLabel
        self.__card_divider: QFrame
        self.__label_parecer_num: QLabel
        self.__label_parecer_texto: QLabel
        self.__label_pontuacao_label: QLabel
        self.__label_pontuacao_valor: QLabel
        self.__btn_jogar_novamente: QPushButton
        self.__btn_menu_principal: QPushButton
        self.__btn_sair: QPushButton
        self.__footer_bar: QFrame
        self.__footer_labels: List[QLabel]

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

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
        self.__crt_overlay.setGeometry(self.rect())
        self.__ajustar_tamanho_do_card()

    # —————————————————————————————————————————————
    # Setup
    # —————————————————————————————————————————————

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        self.__build_efeitos_visuais()
        self.__build_header(layout)
        layout.addStretch()
        self.__build_titulo(layout)
        layout.addSpacing(16)
        self.__build_card(layout)
        layout.addSpacing(18)
        self.__build_score(layout)
        layout.addSpacing(18)
        self.__build_botoes(layout)
        layout.addStretch()
        self.__build_footer(layout)

    def __build_efeitos_visuais(self) -> None:
        self.__crt_overlay = CrtEffectsOverlay(self)
        self.__crt_overlay.setGeometry(self.rect())

    def __build_header(self, layout: QVBoxLayout) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.__label_header = QLabel("\u25CF IFF-BJI \u00B7 SESS\u00C3O DE INSPE\u00C7\u00C3O")
        self.__label_header.setObjectName("gameover_header")
        font = QFont("Open Sans")
        font.setPointSize(11)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 0.5)
        self.__label_header.setFont(font)

        self.__label_timestamp = QLabel()
        self.__label_timestamp.setObjectName("gameover_timestamp")
        font_ts = QFont("Courier New")
        font_ts.setPointSize(9)
        self.__label_timestamp.setFont(font_ts)
        self.__atualizar_timestamp()

        row_layout.addWidget(self.__label_header)
        row_layout.addStretch()
        row_layout.addWidget(self.__label_timestamp)
        layout.addWidget(row)

    def __build_titulo(self, layout: QVBoxLayout) -> None:
        self.__label_titulo = QLabel("GAME OVER")
        self.__label_titulo.setObjectName("gameover_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Open Sans")
        font.setPointSize(40)
        font.setWeight(QFont.Weight.ExtraBold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.4)
        self.__label_titulo.setFont(font)
        layout.addWidget(self.__label_titulo)

        self.__label_subtitulo = QLabel("Credencial de inspetor revogada")
        self.__label_subtitulo.setObjectName("gameover_subtitulo")
        self.__label_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_sub = QFont("Open Sans")
        font_sub.setPointSize(11)
        font_sub.setLetterSpacing(QFont.AbsoluteSpacing, 0.9)
        self.__label_subtitulo.setFont(font_sub)
        layout.addWidget(self.__label_subtitulo)

    def __build_card(self, layout: QVBoxLayout) -> None:
        self.__card = QFrame()
        self.__card.setObjectName("gameover_card")

        bg_path = str(_ICONS_FIM_JOGO / "oldpaper.png").replace("\\", "/")
        self.__card.setStyleSheet(
            f"QFrame#gameover_card {{"
            f"background-image: url({bg_path});"
            f"background-color: #eeeae2;"
            f"border-radius: 2px;"
            f"}}"
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(4)
        shadow.setOffset(5, 5)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.__card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.__card)
        card_layout.setContentsMargins(20, 22, 20, 22)
        card_layout.setSpacing(0)

        font_cab = QFont("Open Sans")
        font_cab.setPointSize(8)
        font_cab.setLetterSpacing(QFont.AbsoluteSpacing, 0.6)

        self.__label_card_cabecalho = QLabel(
            "IFF Fluminense \u00B7 Campus Bom Jesus do Itabapoana"
        )
        self.__label_card_cabecalho.setObjectName("gameover_card_cabecalho")
        self.__label_card_cabecalho.setFont(font_cab)
        card_layout.addWidget(self.__label_card_cabecalho)

        self.__label_card_subcabecalho = QLabel(
            "Comiss\u00E3o Interna de Preven\u00E7\u00E3o de Acidentes \u2014 CIPA"
        )
        self.__label_card_subcabecalho.setObjectName("gameover_card_subcabecalho")
        font_subcab = QFont("Open Sans")
        font_subcab.setPointSize(12)
        font_subcab.setWeight(QFont.Weight.Bold)
        self.__label_card_subcabecalho.setFont(font_subcab)
        card_layout.addWidget(self.__label_card_subcabecalho)

        spacers_top = QWidget()
        spacers_top.setFixedHeight(8)
        card_layout.addWidget(spacers_top)

        self.__card_divider = QFrame()
        self.__card_divider.setObjectName("gameover_card_divider")
        self.__card_divider.setFixedHeight(2)
        card_layout.addWidget(self.__card_divider)

        spacers_mid = QWidget()
        spacers_mid.setFixedHeight(12)
        card_layout.addWidget(spacers_mid)

        self.__label_parecer_num = QLabel()
        self.__label_parecer_num.setObjectName("gameover_card_parecer_num")
        font_ref = QFont("Open Sans")
        font_ref.setPointSize(9)
        self.__label_parecer_num.setFont(font_ref)
        card_layout.addWidget(self.__label_parecer_num)

        spacers_ref = QWidget()
        spacers_ref.setFixedHeight(10)
        card_layout.addWidget(spacers_ref)

        self.__label_parecer_texto = QLabel()
        self.__label_parecer_texto.setObjectName("gameover_card_parecer_texto")
        self.__label_parecer_texto.setWordWrap(True)
        self.__label_parecer_texto.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.__label_parecer_texto.setMaximumHeight(
            self.__layout_loader.scaled("gameover", "card", "parecer_max_height")
        )
        font_texto = QFont("Open Sans")
        font_texto.setPointSize(13)
        self.__label_parecer_texto.setFont(font_texto)
        card_layout.addWidget(self.__label_parecer_texto)

        self.__card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.__card.setMinimumHeight(
            self.__layout_loader.scaled("gameover", "card", "altura_minima")
        )
        layout.addWidget(self.__card, alignment=Qt.AlignmentFlag.AlignCenter)

    def __build_score(self, layout: QVBoxLayout) -> None:
        self.__label_pontuacao_label = QLabel("PONTUA\u00C7\u00C3O FINAL")
        self.__label_pontuacao_label.setObjectName("gameover_score_label")
        self.__label_pontuacao_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_lbl = QFont("Open Sans")
        font_lbl.setPointSize(11)
        font_lbl.setLetterSpacing(QFont.AbsoluteSpacing, 0.5)
        self.__label_pontuacao_label.setFont(font_lbl)
        layout.addWidget(self.__label_pontuacao_label)

        self.__label_pontuacao_valor = QLabel(f"{self.__pontuacao_global:.0f} pts")
        self.__label_pontuacao_valor.setObjectName("gameover_score_valor")
        self.__label_pontuacao_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_val = QFont("Open Sans")
        font_val.setPointSize(30)
        font_val.setWeight(QFont.Weight.ExtraBold)
        self.__label_pontuacao_valor.setFont(font_val)
        layout.addWidget(self.__label_pontuacao_valor)

    def __build_botoes(self, layout: QVBoxLayout) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__btn_jogar_novamente = QPushButton("Tentar novamente")
        self.__btn_jogar_novamente.setObjectName("gameover_btn_retry")
        self.__btn_jogar_novamente.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_jogar_novamente.clicked.connect(self.jogar_novamente_solicitado.emit)
        row_layout.addWidget(self.__btn_jogar_novamente)

        self.__btn_menu_principal = QPushButton("Menu principal")
        self.__btn_menu_principal.setObjectName("gameover_btn_menu")
        self.__btn_menu_principal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_menu_principal.clicked.connect(self.voltar_menu_solicitado.emit)
        row_layout.addWidget(self.__btn_menu_principal)

        self.__btn_sair = QPushButton("Sair do Jogo")
        self.__btn_sair.setObjectName("gameover_btn_quit")
        self.__btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_sair.clicked.connect(self.sair_solicitado.emit)
        row_layout.addWidget(self.__btn_sair)

        layout.addWidget(row)

    def __build_footer(self, layout: QVBoxLayout) -> None:
        self.__footer_bar = QFrame()
        self.__footer_bar.setObjectName("gameover_footer")
        footer_layout = QHBoxLayout(self.__footer_bar)
        footer_layout.setContentsMargins(14, 8, 14, 8)
        footer_layout.setSpacing(10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__footer_labels = []
        for i in range(4):
            indicator = QLabel()
            indicator.setObjectName("gameover_footer_indicator")
            indicator.setFixedSize(8, 8)
            self.__footer_labels.append(indicator)
            footer_layout.addWidget(indicator)

        footer_text = QLabel("SESS\u00C3O ENCERRADA \u2014 ACESSO REVOGADO")
        footer_text.setObjectName("gameover_footer_label")
        font_ft = QFont("Open Sans")
        font_ft.setPointSize(10)
        font_ft.setWeight(QFont.Weight.Bold)
        font_ft.setLetterSpacing(QFont.AbsoluteSpacing, 1.4)
        footer_text.setFont(font_ft)
        footer_layout.addWidget(footer_text)

        for i in range(4, 8):
            indicator = QLabel()
            indicator.setObjectName("gameover_footer_indicator")
            indicator.setFixedSize(8, 8)
            self.__footer_labels.append(indicator)
            footer_layout.addWidget(indicator)

        layout.addWidget(self.__footer_bar)

    # —————————————————————————————————————————————
    # Comportamento
    # —————————————————————————————————————————————

    def __atualizar_timestamp(self) -> None:
        agora = datetime.now()
        mes = _MESES[agora.month - 1]
        texto = f"{agora:%H:%M:%S} \u00B7 {agora.day:02d} {mes} {agora.year}"
        self.__label_timestamp.setText(texto)

    def __ajustar_tamanho_do_card(self) -> None:
        L = self.__layout_loader
        disponivel = self.width() - 40
        fator = L.get("gameover", "card", "fator_largura")
        alvo = int(disponivel * fator)
        largura_min = L.scaled("gameover", "card", "largura_min")
        largura_max = L.scaled("gameover", "card", "largura_max")
        largura = max(largura_min, min(alvo, largura_max))
        self.__card.setFixedWidth(largura)
        self.__card.setMinimumHeight(
            L.scaled("gameover", "card", "altura_minima")
        )

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = self.__layout_loader
        self.__label_parecer_texto.setMaximumHeight(
            L.scaled("gameover", "card", "parecer_max_height")
        )
        self.__card.setMinimumHeight(
            L.scaled("gameover", "card", "altura_minima")
        )
        self.__ajustar_tamanho_do_card()
