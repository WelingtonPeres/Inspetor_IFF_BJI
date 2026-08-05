import logging
from typing import Callable, Optional, Tuple, Type

from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.interfaces.i_game_view import MotivoTutorial
from view.infrastructure.layout_loader import LayoutLoader
from view.widgets.janela_flutuante import JanelaFlutuante
from view.tutorial.widgets.assets_helper import (
    carregar_pixmap_escalado,
    tingir_pixmap,
)
from view.tutorial.widgets.dots_navegacao import DotsNavegacao
from view.tutorial.paginas.slide_anatomia import SlideAnatomia
from view.tutorial.paginas.slide_anexos import SlideAnexos
from view.tutorial.paginas.slide_boas_vindas import SlideBoasVindas
from view.tutorial.paginas.slide_decisao import SlideDecisao
from view.tutorial.paginas.slide_fatores import SlideFatores
from view.tutorial.paginas.slide_pronto import SlidePronto
from view.tutorial.paginas.slide_riscos import SlideRiscos
from view.tutorial.paginas.slide_vitoria import SlideVitoria
from view.tutorial.slide_tutorial import SlideTutorial

logger = logging.getLogger(__name__)


class TelaTutorial(JanelaFlutuante):
    """Janela flutuante do tutorial, irma da TelaDeExpediente.

    Emite ``finalizado_solicitado(MotivoTutorial)`` com o motivo que abriu o
    tutorial quando o utilizador finaliza (Pular, X ou CTA).
    """

    finalizado_solicitado = Signal(MotivoTutorial)

    SLIDES: Tuple[Type[SlideTutorial], ...] = (
        SlideBoasVindas,
        SlideAnatomia,
        SlideAnexos,
        SlideRiscos,
        SlideFatores,
        SlideDecisao,
        SlideVitoria,
        SlidePronto,
    )

    TITULO = "Como Jogar"
    TEXTO_PULAR = "Pular tutorial"
    # Verde IFF: legivel sobre os fundos dos dois temas (QSS nao tinge pixmap).
    COR_ICONE_BRIEFING = "#2F9E41"

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout_loader: Optional[LayoutLoader] = None,
    ):
        super().__init__(proporcao_keys=("tutorial", "proporcao_tela"), parent=parent)
        self.setObjectName("tela_tutorial")
        self.setProperty("class", "tela_tutorial")

        # Injetavel para teste; o singleton e so o default de producao.
        self.__layout = layout_loader or LayoutLoader.instance()

        self.__motivo: MotivoTutorial = MotivoTutorial.NOVO_JOGO

        self.__label_contador: QLabel
        self.__btn_pular: QPushButton
        self.__briefing_bar: QWidget
        self.__icone_briefing: QLabel
        self.__label_briefing: QLabel
        self.__stack: QStackedWidget
        self.__btn_prev: QPushButton
        self.__btn_next: QPushButton
        self.__dots: DotsNavegacao

        self.__setup_ui()
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self) -> None:
        layout = self._montar_chrome(self.TITULO)
        layout.addLayout(self.__build_body(), stretch=1)

        self.__aplicar_dimensoes()
        # Estado inicial do chrome (briefing, setas, dots) sem navegar.
        self.__on_page_changed(0)

    def __build_body(self) -> QVBoxLayout:
        L = self.__layout
        margens_chrome = L.scaled_margins("tutorial", "chrome", "margens")
        body = QVBoxLayout()
        # Recuo completo do chrome aqui (lateral e vertical): o body e o
        # unico bloco recuado, como no padrao full-bleed da irma.
        body.setContentsMargins(*margens_chrome)
        body.setSpacing(L.scaled("tutorial", "chrome", "header_spacing"))

        body.addLayout(self.__build_cabecalho())
        self.__stack = self.__build_stack()
        body.addWidget(self.__stack, stretch=1)
        body.addLayout(self.__build_footer())
        return body

    def __build_cabecalho(self) -> QVBoxLayout:
        cabecalho = QVBoxLayout()
        cabecalho.setSpacing(0)

        # Modelo: contador a esquerda e "Pular tutorial" a direita, na
        # mesma linha; o briefing centrado logo abaixo.
        linha_topo = QHBoxLayout()
        linha_topo.setSpacing(0)

        # Texto preenchido pelo __on_page_changed(0) no fim do setup —
        # aqui o stack (fonte do indice) ainda nao existe.
        self.__label_contador = QLabel()
        self.__label_contador.setObjectName("tutorial_contador")
        self.__label_contador.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        linha_topo.addWidget(self.__label_contador)
        linha_topo.addStretch(1)

        self.__btn_pular = QPushButton(self.TEXTO_PULAR)
        self.__btn_pular.setObjectName("tutorial_pular")
        self.__btn_pular.setProperty("class", "tutorial_pular")
        self.__btn_pular.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_pular.clicked.connect(self.__on_finalizar)
        linha_topo.addWidget(self.__btn_pular)

        cabecalho.addLayout(linha_topo)
        cabecalho.addWidget(self.__build_briefing_bar())

        return cabecalho

    def __build_briefing_bar(self) -> QWidget:
        """Barra do briefing: icone do chefe + frase, centrados (modelo)."""
        L = self.__layout
        barra = QWidget()
        barra.setObjectName("tutorial_briefing_bar")

        linha = QHBoxLayout(barra)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(L.scaled("tutorial", "chrome", "briefing_spacing"))

        linha.addStretch(1)

        self.__icone_briefing = QLabel()
        self.__icone_briefing.setObjectName("tutorial_briefing_icone")
        self.__icone_briefing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        linha.addWidget(self.__icone_briefing, 0, Qt.AlignmentFlag.AlignVCenter)

        self.__label_briefing = QLabel()
        self.__label_briefing.setObjectName("tutorial_briefing")
        self.__label_briefing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        linha.addWidget(self.__label_briefing, 0, Qt.AlignmentFlag.AlignVCenter)

        linha.addStretch(1)

        self.__briefing_bar = barra
        return barra

    def __build_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        for slide_cls in self.SLIDES:
            self.__validar_slide(slide_cls)
            slide = slide_cls(self)
            stack.addWidget(slide)
            self.__conectar_cta(slide)
        stack.currentChanged.connect(self.__on_page_changed)
        return stack

    def __conectar_cta(self, slide: SlideTutorial) -> None:
        """Liga o CTA por deteccao — o sinal e opcional e nao vive na base."""
        sinal_cta = getattr(slide, "cta_clicked", None)
        if sinal_cta is not None:
            sinal_cta.connect(self.__on_finalizar)

    @staticmethod
    def __validar_slide(slide_cls: Type[SlideTutorial]) -> None:
        """Garante o contrato SlideTutorial no registry.

        A metaclasse combinada do PySide6 nao bloqueia a instanciacao de
        ABCs (o Shiboken contorna o __call__ do ABCMeta), entao o contrato
        e verificado aqui, na entrada do registry.
        """
        if not issubclass(slide_cls, SlideTutorial):
            raise TypeError(
                "[Erro - TelaTutorial] Slide deve herdar de SlideTutorial: %s"
                % slide_cls.__name__
            )
        if slide_cls.__abstractmethods__:
            raise TypeError(
                "[Erro - TelaTutorial] Slide %s sem implementacao: %s"
                % (
                    slide_cls.__name__,
                    ", ".join(sorted(slide_cls.__abstractmethods__)),
                )
            )

    def __build_footer(self) -> QHBoxLayout:
        L = self.__layout
        footer = QHBoxLayout()
        # Modelo: grupo "\u2039 dots \u203a" centrado, nao setas nas extremidades.
        footer.setSpacing(L.scaled("tutorial", "chrome", "footer_gap"))

        footer.addStretch(1)

        self.__btn_prev = self.__criar_botao_seta(
            "\u2039", "tutorial_nav_prev", self.__ir_para_slide_anterior
        )
        footer.addWidget(self.__btn_prev, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__dots = DotsNavegacao(len(self.SLIDES), self.__layout)
        self.__dots.slide_solicitado.connect(self.__ir_para_slide)
        footer.addWidget(self.__dots, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__btn_next = self.__criar_botao_seta(
            "\u203a", "tutorial_nav_next", self.__ir_para_slide_seguinte
        )
        # No ultimo slide a seta some mas mantem o lugar, para o grupo
        # nao se deslocar (modelo usa um spacer da mesma largura).
        politica = self.__btn_next.sizePolicy()
        politica.setRetainSizeWhenHidden(True)
        self.__btn_next.setSizePolicy(politica)
        footer.addWidget(self.__btn_next, alignment=Qt.AlignmentFlag.AlignCenter)

        footer.addStretch(1)

        return footer

    def __criar_botao_seta(
        self, texto: str, object_name: str, slot: Callable[[], None]
    ) -> QPushButton:
        btn = QPushButton(texto)
        btn.setObjectName(object_name)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def __texto_contador(self, indice: int) -> str:
        return "Como jogar · %d de %d" % (indice + 1, len(self.SLIDES))

    def __on_page_changed(self, index: int) -> None:
        self.__label_contador.setText(self.__texto_contador(index))
        self.__dots.atualizar(index)
        slide = self.__slide_do_indice(index)
        self.__label_briefing.setText('"%s"' % slide.texto_briefing())
        ultimo = index == self.__stack.count() - 1
        self.__btn_prev.setEnabled(index > 0)
        self.__btn_next.setVisible(not ultimo)

    def __slide_do_indice(self, indice: int) -> SlideTutorial:
        slide = self.__stack.widget(indice)
        if not isinstance(slide, SlideTutorial):
            raise TypeError(
                "[Erro - TelaTutorial] Widget do stack nao e SlideTutorial."
            )
        return slide

    @Slot()
    def __ir_para_slide_anterior(self) -> None:
        # O stack e a unica fonte do indice atual (sem copia local).
        self.__ir_para_slide(self.__stack.currentIndex() - 1)

    @Slot()
    def __ir_para_slide_seguinte(self) -> None:
        self.__ir_para_slide(self.__stack.currentIndex() + 1)

    @Slot(int)
    def __ir_para_slide(self, indice: int) -> None:
        if 0 <= indice < self.__stack.count():
            self.__stack.setCurrentIndex(indice)

    @Slot()
    def _ao_fechar(self) -> None:
        self.__on_finalizar()

    @Slot()
    def __on_finalizar(self) -> None:
        self._fechar()
        self.finalizado_solicitado.emit(self.__motivo)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        self.__aplicar_dimensoes()

    def __aplicar_dimensoes(self) -> None:
        L = self.__layout
        self.__label_contador.setFont(self.__font_do_chrome("contador_font_size"))
        self.__btn_pular.setFont(self.__font_do_chrome("pular_font_size"))
        self.__briefing_bar.setFixedHeight(
            L.scaled("tutorial", "chrome", "briefing_altura")
        )
        lado_icone = L.scaled("tutorial", "chrome", "briefing_icone_tamanho")
        self.__icone_briefing.setFixedSize(lado_icone, lado_icone)
        self.__icone_briefing.setPixmap(
            tingir_pixmap(
                carregar_pixmap_escalado(lado_icone, lado_icone, "tutorial", "boss.png"),
                self.COR_ICONE_BRIEFING,
            )
        )
        tamanho_seta = L.scaled("tutorial", "nav_arrow", "tamanho")
        self.__btn_prev.setFixedSize(tamanho_seta, tamanho_seta)
        self.__btn_next.setFixedSize(tamanho_seta, tamanho_seta)
        self.__dots.reaplicar_dimensoes()

    def __font_do_chrome(self, chave: str) -> QFont:
        L = self.__layout
        return QFont(
            L.get("tutorial", "font_familia"),
            L.scaled("tutorial", "chrome", chave),
        )

    def exibir_tutorial(self, motivo: MotivoTutorial) -> None:
        """Abre o tutorial com o motivo dado (guard de reentrancia).

        Se ja estiver visivel, ignora — mantem o motivo original para
        nao corromper o fluxo novo_jogo iniciado antes.
        """
        if self.isVisible():
            logger.info("Tutorial ja visivel; reentrancia ignorada.")
            return
        self.__motivo = motivo
        self.__stack.setCurrentIndex(0)
        self.__aplicar_motivo_aos_slides(motivo)
        self.__on_page_changed(0)

    def __aplicar_motivo_aos_slides(self, motivo: MotivoTutorial) -> None:
        for indice in range(self.__stack.count()):
            self.__slide_do_indice(indice).definir_motivo(motivo)

    def exibir_com_tamanho_inicial(self, parent_rect: QRect) -> None:
        """Posiciona e mostra acima da irma (regra de sobreposicao local)."""
        super().exibir_com_tamanho_inicial(parent_rect)
        self.raise_()