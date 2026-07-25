import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPixmap,
)
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
    RepositorioDePareceresCIPA,
)
from view.infrastructure.layout_loader import LayoutLoader
from view.widgets.efeitos.background_riscos import BackgroundRiscos
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
        repositorio: Optional[IPareceresCIPA] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("game_over")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__pontuacao_global: float = pontuacao_global
        self.__repositorio: IPareceresCIPA = (
            repositorio if repositorio is not None else RepositorioDePareceresCIPA()
        )

        self.__layout_loader: LayoutLoader = LayoutLoader.instance()

        self.__crt_overlay: CrtEffectsOverlay
        self.__bg_riscos: BackgroundRiscos
        self.__timer_timestamp: QTimer

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
        self.__scroll_parecer: QScrollArea
        self.__label_pontuacao_label: QLabel
        self.__label_pontuacao_valor: QLabel
        self.__btn_jogar_novamente: QPushButton
        self.__btn_menu_principal: QPushButton
        self.__btn_sair: QPushButton
        self.__footer_bar: QFrame
        self.__footer_labels: List[QLabel]

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def exibir_resultado(self, pontuacao_global: float, perfil: str) -> None:
        """API agregada chamada pelo Presenter ao terminar a campanha.

        Centraliza as duas accoes que o Presenter executava em separado
        (atualizar pontuacao + definir parecer) — Tell, Don't Ask.
        """
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
        self.__ajustar_tamanho_do_card()

    def showEvent(self, event):
        super().showEvent(event)
        self.__timer_timestamp.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.__timer_timestamp.stop()


    def __setup_ui(self) -> None:
        L = self.__layout_loader
        margem = L.scaled("gameover", "spacing", "margem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(margem, margem, margem, margem)
        layout.setSpacing(0)

        self.__build_efeitos_visuais()
        self.__build_header(layout)
        layout.addStretch()
        self.__build_titulo(layout)
        layout.addSpacing(L.scaled("gameover", "spacing", "entre_titulo_card"))
        self.__build_card(layout)
        layout.addSpacing(L.scaled("gameover", "spacing", "entre_card_score"))
        self.__build_score(layout)
        layout.addSpacing(L.scaled("gameover", "spacing", "entre_score_botoes"))
        self.__build_botoes(layout)
        layout.addStretch()
        self.__build_footer(layout)
        self.__setup_timer()

    def __setup_timer(self) -> None:
        """Cria QTimer que refresca o timestamp a cada 1s enquanto visivel."""
        self.__timer_timestamp = QTimer(self)
        self.__timer_timestamp.setInterval(1000)
        self.__timer_timestamp.timeout.connect(self.__atualizar_timestamp)

    def __build_efeitos_visuais(self) -> None:
        self.__crt_overlay = CrtEffectsOverlay(self)
        self.__crt_overlay.setGeometry(self.rect())

        self.__bg_riscos = BackgroundRiscos(self.__layout_loader, _ICONS_FIM_JOGO, self)
        self.__bg_riscos.setGeometry(self.rect())

    def __build_header(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.__label_header = QLabel("\u25CF IFF-BJI \u00B7 SESS\u00C3O DE INSPE\u00C7\u00C3O")
        self.__label_header.setObjectName("gameover_header")
        font = QFont("Open Sans")
        font.setPointSize(L.scaled("gameover", "fontes", "header", "size"))
        font.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "header", "letter_spacing"),
        )
        self.__label_header.setFont(font)

        self.__label_timestamp = QLabel()
        self.__label_timestamp.setObjectName("gameover_timestamp")
        font_ts = QFont("Courier New")
        font_ts.setPointSize(L.scaled("gameover", "fontes", "timestamp", "size"))
        self.__label_timestamp.setFont(font_ts)
        self.__atualizar_timestamp()

        row_layout.addWidget(self.__label_header)
        row_layout.addStretch()
        row_layout.addWidget(self.__label_timestamp)
        layout.addWidget(row)

    def __build_titulo(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__label_titulo = QLabel("GAME OVER")
        self.__label_titulo.setObjectName("gameover_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Open Sans")
        font.setPointSize(L.scaled("gameover", "fontes", "titulo", "size"))
        font.setWeight(QFont.Weight.ExtraBold)
        font.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "titulo", "letter_spacing"),
        )
        self.__label_titulo.setFont(font)
        layout.addWidget(self.__label_titulo)

        self.__label_subtitulo = QLabel("Credencial de inspetor revogada")
        self.__label_subtitulo.setObjectName("gameover_subtitulo")
        self.__label_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_sub = QFont("Open Sans")
        font_sub.setPointSize(L.scaled("gameover", "fontes", "subtitulo", "size"))
        font_sub.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "subtitulo", "letter_spacing"),
        )
        self.__label_subtitulo.setFont(font_sub)
        layout.addWidget(self.__label_subtitulo)

    def __build_card(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__card = QFrame()
        self.__card.setObjectName("gameover_card")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(L.scaled("gameover", "shadow", "blur"))
        shadow.setOffset(
            L.scaled("gameover", "shadow", "offset_x"),
            L.scaled("gameover", "shadow", "offset_y"),
        )
        shadow.setColor(QColor(0, 0, 0, 180))
        self.__card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.__card)
        card_layout.setContentsMargins(
            L.scaled("gameover", "card", "padding", "left"),
            L.scaled("gameover", "card", "padding", "top"),
            L.scaled("gameover", "card", "padding", "right"),
            L.scaled("gameover", "card", "padding", "bottom"),
        )
        card_layout.setSpacing(0)

        font_cab = QFont("Open Sans")
        font_cab.setPointSize(L.scaled("gameover", "fontes", "card_cabecalho", "size"))
        font_cab.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "card_cabecalho", "letter_spacing"),
        )

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
        font_subcab.setPointSize(
            L.scaled("gameover", "fontes", "card_subcabecalho", "size")
        )
        font_subcab.setWeight(QFont.Weight.Bold)
        self.__label_card_subcabecalho.setFont(font_subcab)
        card_layout.addWidget(self.__label_card_subcabecalho)

        spacers_top = QWidget()
        spacers_top.setFixedHeight(L.scaled("gameover", "spacing", "spacers_top"))
        card_layout.addWidget(spacers_top)

        self.__card_divider = QFrame()
        self.__card_divider.setObjectName("gameover_card_divider")
        self.__card_divider.setFixedHeight(L.scaled("gameover", "spacing", "card_divider_altura"))
        card_layout.addWidget(self.__card_divider)

        spacers_mid = QWidget()
        spacers_mid.setFixedHeight(L.scaled("gameover", "spacing", "spacers_mid"))
        card_layout.addWidget(spacers_mid)

        self.__label_parecer_num = QLabel()
        self.__label_parecer_num.setObjectName("gameover_card_parecer_num")
        font_ref = QFont("Open Sans")
        font_ref.setPointSize(
            L.scaled("gameover", "fontes", "card_parecer_num", "size")
        )
        self.__label_parecer_num.setFont(font_ref)
        card_layout.addWidget(self.__label_parecer_num)

        spacers_ref = QWidget()
        spacers_ref.setFixedHeight(L.scaled("gameover", "spacing", "spacers_ref"))
        card_layout.addWidget(spacers_ref)

        self.__label_parecer_texto = QLabel()
        self.__label_parecer_texto.setObjectName("gameover_card_parecer_texto")
        self.__label_parecer_texto.setWordWrap(True)
        self.__label_parecer_texto.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.__label_parecer_texto.setMaximumHeight(
            L.scaled("gameover", "card", "parecer_max_height")
        )
        font_texto = QFont("Open Sans")
        font_texto.setPointSize(
            L.scaled("gameover", "fontes", "card_parecer_texto", "size")
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
        self.__card.setMinimumHeight(L.scaled("gameover", "card", "altura_minima"))
        layout.addWidget(self.__card, alignment=Qt.AlignmentFlag.AlignCenter)

    def __build_score(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__label_pontuacao_label = QLabel("PONTUA\u00C7\u00C3O FINAL")
        self.__label_pontuacao_label.setObjectName("gameover_score_label")
        self.__label_pontuacao_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_lbl = QFont("Open Sans")
        font_lbl.setPointSize(L.scaled("gameover", "fontes", "score_label", "size"))
        font_lbl.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "score_label", "letter_spacing"),
        )
        self.__label_pontuacao_label.setFont(font_lbl)
        layout.addWidget(self.__label_pontuacao_label)

        self.__label_pontuacao_valor = QLabel(f"{self.__pontuacao_global:.0f} pts")
        self.__label_pontuacao_valor.setObjectName("gameover_score_valor")
        self.__label_pontuacao_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_val = QFont("Open Sans")
        font_val.setPointSize(L.scaled("gameover", "fontes", "score_valor", "size"))
        font_val.setWeight(QFont.Weight.ExtraBold)
        self.__label_pontuacao_valor.setFont(font_val)
        layout.addWidget(self.__label_pontuacao_valor)

    def __build_botoes(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        altura = L.scaled("gameover", "botoes", "altura")
        largura_min = L.scaled("gameover", "botoes", "largura_min")
        font_btn = QFont("Open Sans")
        font_btn.setPointSize(L.scaled("gameover", "fontes", "botao", "size"))
        font_btn.setWeight(QFont.Weight.Bold)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(L.scaled("gameover", "spacing", "entre_botoes_row"))

        self.__btn_menu_principal = self.__make_btn(
            "Menu principal", "gameover_btn_menu",
            self.voltar_menu_solicitado.emit,
            altura, largura_min, font_btn,
        )
        self.__btn_jogar_novamente = self.__make_btn(
            "Tentar novamente", "gameover_btn_retry",
            self.jogar_novamente_solicitado.emit,
            altura, largura_min, font_btn,
        )
        self.__btn_sair = self.__make_btn(
            "Sair do Jogo", "gameover_btn_quit",
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

    def __build_footer(self, layout: QVBoxLayout) -> None:
        L = self.__layout_loader
        self.__footer_bar = QFrame()
        self.__footer_bar.setObjectName("gameover_footer")
        footer_layout = QHBoxLayout(self.__footer_bar)
        footer_layout.setContentsMargins(
            L.scaled("gameover", "footer", "padding_x"),
            L.scaled("gameover", "footer", "padding_y"),
            L.scaled("gameover", "footer", "padding_x"),
            L.scaled("gameover", "footer", "padding_y"),
        )
        footer_layout.setSpacing(L.scaled("gameover", "spacing", "entre_footer"))
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ind_size = L.scaled("gameover", "footer", "indicator_size")
        self.__footer_labels = []
        for i in range(4):
            indicator = QLabel()
            indicator.setObjectName("gameover_footer_indicator")
            indicator.setFixedSize(ind_size, ind_size)
            self.__footer_labels.append(indicator)
            footer_layout.addWidget(indicator)

        footer_text = QLabel("SESS\u00C3O ENCERRADA \u2014 ACESSO REVOGADO")
        footer_text.setObjectName("gameover_footer_label")
        font_ft = QFont("Open Sans")
        font_ft.setPointSize(L.scaled("gameover", "fontes", "footer_label", "size"))
        font_ft.setWeight(QFont.Weight.Bold)
        font_ft.setLetterSpacing(
            QFont.AbsoluteSpacing,
            L.get("gameover", "fontes", "footer_label", "letter_spacing"),
        )
        footer_text.setFont(font_ft)
        footer_layout.addWidget(footer_text)

        for i in range(4, 8):
            indicator = QLabel()
            indicator.setObjectName("gameover_footer_indicator")
            indicator.setFixedSize(ind_size, ind_size)
            self.__footer_labels.append(indicator)
            footer_layout.addWidget(indicator)

        layout.addWidget(self.__footer_bar)


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

        # Recalcular fontes
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
            font.setPointSize(L.scaled("gameover", "fontes", grupo, "size"))
            label.setFont(font)

        # Card e label
        self.__label_parecer_texto.setMaximumHeight(
            L.scaled("gameover", "card", "parecer_max_height")
        )
        self.__card.setMinimumHeight(L.scaled("gameover", "card", "altura_minima"))
        self.__ajustar_tamanho_do_card()
        self.__bg_riscos.invalidar_cache()
