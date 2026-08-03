import logging
from typing import Callable, List, Optional, Tuple, Type

from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.interfaces.i_game_view import MotivoTutorial
from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader
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

LIMIAR_LARGURA_MINIMA = 1280


class TelaTutorial(QFrame):
    """Janela flutuante do tutorial, irma da TelaDeExpediente.

    Emite ``finalizado_solicitado(MotivoTutorial)`` com o motivo que abriu o
    tutorial quando o utilizador finaliza (Pular, X ou CTA).
    """

    finalizado_solicitado = Signal(MotivoTutorial)
    geometria_alterada = Signal()
    visibilidade_alterada = Signal(bool)

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

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("tela_tutorial")
        self.setProperty("class", "tela_tutorial")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__layout = LayoutLoader.instance()

        self.__motivo: MotivoTutorial = MotivoTutorial.NOVO_JOGO
        self.__index_atual: int = 0
        self.__maximizado: bool = False
        self.__tamanho_normal: Optional[QRect] = None
        self.__rect_referencia: Optional[QRect] = None

        self.__title_bar: WindowTitleBar
        self.__label_contador: QLabel
        self.__btn_pular: QPushButton
        self.__label_briefing: QLabel
        self.__stack: QStackedWidget
        self.__btn_prev: QPushButton
        self.__btn_next: QPushButton
        self.__dots_container: QWidget

        self.__setup_ui()
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__title_bar = self.__build_title_bar()
        layout.addWidget(self.__title_bar)

        body = self.__build_body()
        layout.addLayout(body, stretch=1)

        self.__aplicar_dimensoes()
        # Estado inicial do chrome (briefing, setas, dots) sem navegar.
        self.__on_page_changed(0)

    def __build_title_bar(self) -> WindowTitleBar:
        L = self.__layout
        title_bar = WindowTitleBar(
            titulo=self.TITULO,
            altura=L.scaled("tela_de_expediente", "title_bar", "altura"),
            altura_keys=("tela_de_expediente", "title_bar", "altura"),
            mostrar_min_max=True,
            parent=self,
        )
        title_bar.close_requested.connect(self.__on_finalizar)
        title_bar.minimized_solicitado.connect(self.__on_minimizar)
        title_bar.maximized_solicitado.connect(self.__on_maximizar_restaurar)
        return title_bar

    def __build_body(self) -> QVBoxLayout:
        L = self.__layout
        body = QVBoxLayout()
        body.setContentsMargins(*L.scaled_margins("tutorial", "chrome", "margens"))
        body.setSpacing(L.scaled("tutorial", "chrome", "header_spacing"))

        body.addLayout(self.__build_cabecalho())
        self.__stack = self.__build_stack()
        body.addWidget(self.__stack, stretch=1)
        body.addLayout(self.__build_footer())
        return body

    def __build_cabecalho(self) -> QVBoxLayout:
        cabecalho = QVBoxLayout()
        cabecalho.setSpacing(0)

        self.__label_contador = QLabel(self.__texto_contador())
        self.__label_contador.setObjectName("tutorial_contador")
        self.__label_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cabecalho.addWidget(self.__label_contador)

        self.__btn_pular = QPushButton(self.TEXTO_PULAR)
        self.__btn_pular.setObjectName("tutorial_pular")
        self.__btn_pular.setProperty("class", "tutorial_pular")
        self.__btn_pular.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_pular.clicked.connect(self.__on_finalizar)
        cabecalho.addWidget(self.__btn_pular, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__label_briefing = QLabel()
        self.__label_briefing.setObjectName("tutorial_briefing")
        self.__label_briefing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cabecalho.addWidget(self.__label_briefing)

        return cabecalho

    def __build_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        for slide_cls in self.SLIDES:
            self.__validar_slide(slide_cls)
            slide = slide_cls(self)
            stack.addWidget(slide)
            slide.cta_clicked.connect(self.__on_finalizar)
        stack.currentChanged.connect(self.__on_page_changed)
        return stack

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
        footer.setSpacing(L.scaled("tutorial", "dot", "gap"))

        self.__btn_prev = self.__criar_botao_seta(
            "\u2039", "tutorial_nav_prev", self.__ir_para_slide_anterior
        )
        footer.addWidget(self.__btn_prev, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__dots_container = QWidget()
        self.__dots_container.setObjectName("tutorial_dots")
        self.__dots_layout = QHBoxLayout(self.__dots_container)
        self.__dots_layout.setContentsMargins(0, 0, 0, 0)
        self.__dots_layout.setSpacing(L.scaled("tutorial", "dot", "gap"))
        self.__dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__build_dots()
        footer.addWidget(self.__dots_container, stretch=1)

        self.__btn_next = self.__criar_botao_seta(
            "\u203a", "tutorial_nav_next", self.__ir_para_slide_seguinte
        )
        footer.addWidget(self.__btn_next, alignment=Qt.AlignmentFlag.AlignCenter)

        return footer

    def __criar_botao_seta(
        self, texto: str, object_name: str, slot: Callable[[], None]
    ) -> QPushButton:
        btn = QPushButton(texto)
        btn.setObjectName(object_name)
        btn.setProperty("class", "tutorial_nav_arrow")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def __build_dots(self) -> None:
        self.__dots: List[QPushButton] = []
        for indice in range(len(self.SLIDES)):
            dot = QPushButton()
            dot.setObjectName("tutorial_dot")
            dot.setProperty("class", "tutorial_dot")
            dot.setCheckable(False)
            dot.setCursor(Qt.CursorShape.PointingHandCursor)
            dot.clicked.connect(lambda _checked, i=indice: self.__ir_para_slide(i))
            self.__dots_layout.addWidget(dot)
            self.__dots.append(dot)

    def __texto_contador(self) -> str:
        return "Como jogar · %d de %d" % (self.__index_atual + 1, len(self.SLIDES))

    def __atualizar_dots(self) -> None:
        L = self.__layout
        largura_inativo = L.scaled("tutorial", "dot", "largura")
        largura_ativo = L.scaled("tutorial", "dot", "largura_ativo")
        altura = L.scaled("tutorial", "dot", "altura")
        for indice, dot in enumerate(self.__dots):
            ativo = indice == self.__index_atual
            dot.setProperty("active", "true" if ativo else "false")
            dot.setFixedSize(largura_ativo if ativo else largura_inativo, altura)
            self.__repolish(dot)

    @staticmethod
    def __repolish(widget: QWidget) -> None:
        estilo = widget.style()
        estilo.unpolish(widget)
        estilo.polish(widget)

    def __on_page_changed(self, index: int) -> None:
        self.__index_atual = index
        self.__label_contador.setText(self.__texto_contador())
        self.__atualizar_dots()
        slide = self.__slide_do_indice(index)
        self.__label_briefing.setText(slide.texto_briefing())
        ultimo = index == self.__stack.count() - 1
        self.__btn_prev.setEnabled(index > 0)
        self.__btn_next.setVisible(not ultimo)
        self.__dots_container.setVisible(not ultimo)

    def __slide_do_indice(self, indice: int) -> SlideTutorial:
        slide = self.__stack.widget(indice)
        if not isinstance(slide, SlideTutorial):
            raise TypeError(
                "[Erro - TelaTutorial] Widget do stack nao e SlideTutorial."
            )
        return slide

    @Slot()
    def __ir_para_slide_anterior(self) -> None:
        if self.__index_atual > 0:
            self.__stack.setCurrentIndex(self.__index_atual - 1)

    @Slot()
    def __ir_para_slide_seguinte(self) -> None:
        if self.__index_atual < self.__stack.count() - 1:
            self.__stack.setCurrentIndex(self.__index_atual + 1)

    @Slot(int)
    def __ir_para_slide(self, indice: int) -> None:
        if 0 <= indice < self.__stack.count():
            self.__stack.setCurrentIndex(indice)

    @Slot()
    def __on_minimizar(self) -> None:
        self.hide()

    @Slot()
    def __on_maximizar_restaurar(self) -> None:
        if self.__maximizado:
            self.__restaurar_tamanho()
            self.__maximizado = False
            self.__title_bar.set_maximizado(False)
            return
        self.__maximizar()
        self.__maximizado = True
        self.__title_bar.set_maximizado(True)

    def __maximizar(self) -> None:
        if self.__rect_referencia is not None:
            self.__tamanho_normal = self.geometry()
            self.setGeometry(self.__rect_referencia)

    def __restaurar_tamanho(self) -> None:
        if self.__tamanho_normal is not None:
            self.setGeometry(self.__tamanho_normal)

    @Slot()
    def __on_finalizar(self) -> None:
        self.hide()
        self.__maximizado = False
        self.__title_bar.set_maximizado(False)
        self.finalizado_solicitado.emit(self.__motivo)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        self.__aplicar_dimensoes()

    def __aplicar_dimensoes(self) -> None:
        L = self.__layout
        self.__label_contador.setFont(self.__font_do_chrome("contador_font_size"))
        self.__btn_pular.setFont(self.__font_do_chrome("pular_font_size"))
        self.__label_briefing.setFixedHeight(
            L.scaled("tutorial", "chrome", "briefing_altura")
        )
        tamanho_seta = L.scaled("tutorial", "nav_arrow", "tamanho")
        self.__btn_prev.setFixedSize(tamanho_seta, tamanho_seta)
        self.__btn_next.setFixedSize(tamanho_seta, tamanho_seta)
        self.__dots_layout.setSpacing(L.scaled("tutorial", "dot", "gap"))
        self.__atualizar_dots()

    def __font_do_chrome(self, chave: str) -> QFont:
        L = self.__layout
        return QFont(
            L.get("tutorial", "font_familia"),
            L.scaled("tutorial", "chrome", chave),
        )

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.geometria_alterada.emit()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.geometria_alterada.emit()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.visibilidade_alterada.emit(True)

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self.visibilidade_alterada.emit(False)

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
        """Posiciona a janela (80% do rect de referencia) e mostra."""
        self.__reposicionar(parent_rect)
        self.show()
        self.raise_()

    @Slot(QRect)
    def redimensionar_com_overlay(self, rect: QRect) -> None:
        """Reaciona ao resize do overlay; so reposiciona se visivel."""
        if self.isVisible():
            self.__reposicionar(rect)

    def __reposicionar(self, parent_rect: QRect) -> None:
        self.__rect_referencia = QRect(parent_rect)
        self.__tamanho_normal = self.__calcular_rect(parent_rect)
        if self.__maximizado:
            self.setGeometry(parent_rect)
            return
        self.setGeometry(self.__tamanho_normal)

    def __calcular_rect(self, parent_rect: QRect) -> QRect:
        L = self.__layout
        proporcao = L.get("tutorial", "proporcao_tela")
        w_80 = int(parent_rect.width() * proporcao)
        if w_80 < LIMIAR_LARGURA_MINIMA:
            return QRect(0, 0, parent_rect.width(), parent_rect.height())
        w = w_80
        h = int(parent_rect.height() * proporcao)
        x = (parent_rect.width() - w) // 2
        y = (parent_rect.height() - h) // 2
        return QRect(x, y, w, h)