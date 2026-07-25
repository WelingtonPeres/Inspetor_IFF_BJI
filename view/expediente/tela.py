import logging
from typing import Any, Dict
from PySide6.QtCore import Qt, QRect, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
)

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from infrastructure.repository.repositorio_pareceres_cipa import RepositorioDePareceresCIPA
from view.expediente.widgets.sidebar import Sidebar
from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer
from view.expediente.paginas.diagnostico import PaginaDiagnostico
from view.expediente.paginas.game_win import GameWin
from view.expediente.paginas.game_over import GameOver
from view.expediente.paginas.inspecao import PaginaInspecao
from view.expediente.paginas.loading import PaginaLoading
from view.expediente.paginas.selecao_perfil import PaginaSelecaoPerfil

logger = logging.getLogger(__name__)


class TelaDeExpediente(QFrame):
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()
    sair_solicitado = Signal()
    minimized_solicitado = Signal()

    IDX_SELECAO_PERFIL = 0
    IDX_LOADING = 1
    IDX_INSPECAO = 2
    IDX_DIAGNOSTICO = 3
    IDX_GAME_WIN = 4
    IDX_GAME_OVER = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tela_de_expediente")
        self.setProperty("class", "tela_expediente")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__maximizado: bool = False
        self.__tamanho_normal: Any = None
        self.__perfil_selecionado: str = ""

        self.__repositorio_pareceres: RepositorioDePareceresCIPA = RepositorioDePareceresCIPA()

        self.__anexo_gallery: AnexoGallery
        self.__media_viewer: MediaViewer
        self.__sidebar: Sidebar

        # Paginas Filhas
        self.__pagina_perfil: PaginaSelecaoPerfil
        self.__pagina_loading: PaginaLoading
        self.__pagina_diagnostico: PaginaDiagnostico
        self.__pagina_game_win: GameWin
        self.__pagina_game_over: GameOver
        self.__pagina_inspecao: PaginaInspecao

        self.__setup_ui()

    def __setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__title_bar = self.__build_title_bar()
        layout.addWidget(self.__title_bar)

        body = self.__build_body()
        layout.addLayout(body, stretch=1)

        self.__build_overlays()

    def __build_title_bar(self) -> WindowTitleBar:
        L = LayoutLoader.instance()
        altura_bar = L.scaled("tela_de_expediente", "title_bar", "altura")
        title_bar = WindowTitleBar(
            titulo="Expediente",
            altura=altura_bar,
            altura_keys=("tela_de_expediente", "title_bar", "altura"),
            parent=self,
        )
        title_bar.close_requested.connect(self.__on_fechar)
        title_bar.minimized_solicitado.connect(self.__on_minimizar)
        title_bar.maximized_solicitado.connect(self.__on_maximizar_restaurar)
        # Reage a mudancas de escala global (resize da janela pai).
        L.escala_atualizada.connect(self.__reaplicar_dimensoes)
        return title_bar

    def __build_body(self) -> QHBoxLayout:
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.__sidebar = self.__build_sidebar()
        body.addWidget(self.__sidebar)

        self.__stack = self.__build_pages()
        self.__stack.currentChanged.connect(self.__on_page_changed)
        body.addWidget(self.__stack, stretch=1)

        return body

    def __build_sidebar(self) -> Sidebar:
        sidebar = Sidebar()
        sidebar.setVisible(False)
        return sidebar

    def __build_pages(self) -> QStackedWidget:
        self.__pagina_perfil = PaginaSelecaoPerfil()
        self.__pagina_perfil.perfil_confirmado.connect(self.__on_perfil_confirmado)

        self.__pagina_loading = PaginaLoading()

        self.__pagina_diagnostico = PaginaDiagnostico()
        self.__pagina_diagnostico.continuar_solicitado.connect(self.continuar_solicitado.emit)

        self.__pagina_inspecao = PaginaInspecao()
        self.__pagina_inspecao.submeter_respostas.connect(self.submeter_respostas.emit)

        self.__pagina_game_win = GameWin(pontuacao_global=0.0)
        self.__pagina_game_win.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        self.__pagina_game_win.jogar_novamente_solicitado.connect(self.jogar_novamente_solicitado.emit)
        self.__pagina_game_win.sair_solicitado.connect(self.sair_solicitado.emit)

        self.__pagina_game_over = GameOver(
            pontuacao_global=0.0,
            repositorio=self.__repositorio_pareceres,
        )
        self.__pagina_game_over.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        self.__pagina_game_over.jogar_novamente_solicitado.connect(self.jogar_novamente_solicitado.emit)
        self.__pagina_game_over.sair_solicitado.connect(self.sair_solicitado.emit)

        stack = QStackedWidget()
        stack.addWidget(self.__pagina_perfil)
        stack.addWidget(self.__pagina_loading)
        stack.addWidget(self.__pagina_inspecao)
        stack.addWidget(self.__pagina_diagnostico)
        stack.addWidget(self.__pagina_game_win)
        stack.addWidget(self.__pagina_game_over)
        stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        return stack

    def __build_overlays(self) -> None:
        self.__anexo_gallery = AnexoGallery(self)
        self.__anexo_gallery.hide()

        self.__media_viewer = MediaViewer(self)
        self.__media_viewer.hide()

        self.__pagina_inspecao.configurar_midia(self.__anexo_gallery, self.__media_viewer)

    @Slot(str)
    def __on_perfil_confirmado(self, perfil: str) -> None:
        self.__perfil_selecionado = perfil
        self.exibir_tela_carregamento()
        self.perfil_confirmado.emit(perfil)

    @Slot(int)
    def __on_page_changed(self, index: int) -> None:
        self.__sidebar.setVisible(index in [self.IDX_INSPECAO, self.IDX_DIAGNOSTICO])

    @Slot()
    def __on_minimizar(self) -> None:
        self.hide()
        self.minimized_solicitado.emit()

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
        parent = self.parentWidget()
        if parent:
            self.__tamanho_normal = self.geometry()
            self.setGeometry(parent.rect())

    def __restaurar_tamanho(self) -> None:
        if self.__tamanho_normal:
            self.setGeometry(self.__tamanho_normal)

    @Slot()
    def __on_fechar(self) -> None:
        self.hide()
        self.__maximizado = False
        self.__title_bar.set_maximizado(False)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Re-aplica dims dependentes de escala (title bar) apos resize."""
        L = LayoutLoader.instance()
        self.__title_bar.reaplicar_dimensoes(L.scaled("tela_de_expediente", "title_bar", "altura"))

    def exibir_selecao_perfil(self) -> None:
        self.__title_bar.definir_titulo("Seleção de Perfil")
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)

    def exibir_tela_carregamento(self) -> None:
        self.__title_bar.definir_titulo("Carregando...")
        self.__stack.setCurrentIndex(self.IDX_LOADING)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        titulo = dados_relatorio.get("titulo", "Relatório")
        self.__title_bar.definir_titulo(f"Relatório: {titulo}")
        self.__pagina_inspecao.renderizar_relatorio(dados_relatorio)
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico: %s", diagnostico)
        self.__title_bar.definir_titulo("Resultado da Inspeção")
        self.__pagina_diagnostico.exibir_diagnostico(diagnostico)
        self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)

    def exibir_tela_endgame(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo endgame: %.1f pts, venceu=%s", pontuacao_global, venceu)
        self.__title_bar.definir_titulo("Fim do Expediente")
        if venceu:
            self.__pagina_game_win.atualizar_pontuacao(pontuacao_global)
            self.__stack.setCurrentIndex(self.IDX_GAME_WIN)
            return
        self.__pagina_game_over.exibir_resultado(
            pontuacao_global, self.__perfil_selecionado
        )
        self.__stack.setCurrentIndex(self.IDX_GAME_OVER)

    def exibir_com_tamanho_inicial(self, parent_rect: Any) -> None:
        # Recalcula a cada chamada: reabrir apos fechar+redimensionar nao pode
        # manter geometria velha congelada (B4).
        self.__reposicionar(parent_rect)
        self.show()

    @Slot(QRect)
    def redimensionar_com_overlay(self, rect: QRect) -> None:
        """Hook acionado pelo _OverlayArea ao crescer (B5).

        So reposiciona se o expediente ja esta visivel; nunca o exibe.
        """
        if self.isVisible():
            self.__reposicionar(rect)

    def __reposicionar(self, parent_rect: Any) -> None:
        if self.__maximizado:
            self.setGeometry(parent_rect)
            return
        w = int(parent_rect.width() * 0.8)
        h = int(parent_rect.height() * 0.8)
        x = (parent_rect.width() - w) // 2
        y = (parent_rect.height() - h) // 2
        self.setGeometry(x, y, w, h)
        self.__tamanho_normal = self.geometry()

    def reiniciar(self) -> None:
        self.__pagina_inspecao.limpar_formulario()
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        self.__title_bar.definir_titulo("Expediente")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__maximizado and self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        # Overlays de midia ancoram no _OverlayArea (acima da taskbar), nao no
        # rect do expediente nem da janela inteira (B7).
        anchor_rect = self.__rect_do_overlay()
        if self.__anexo_gallery.isVisible():
            self.__anexo_gallery.setGeometry(anchor_rect)
        if self.__media_viewer.isVisible():
            self.__media_viewer.setGeometry(anchor_rect)

    def __rect_do_overlay(self) -> QRect:
        parent = self.parentWidget()
        if parent is not None:
            return parent.rect()
        return self.rect()
