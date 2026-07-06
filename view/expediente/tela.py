import logging
from typing import Any, Dict
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
)

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.expediente.widgets.sidebar import Sidebar
from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer
from view.expediente.paginas.diagnostico import PaginaDiagnostico
from view.expediente.paginas.endgame import PaginaEndgame
from view.expediente.paginas.inspecao import PaginaInspecao
from view.expediente.paginas.loading import PaginaLoading
from view.expediente.paginas.selecao_perfil import PaginaSelecaoPerfil

logger = logging.getLogger(__name__)


class TelaDeExpediente(QFrame):
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()
    minimized_solicitado = Signal()

    IDX_SELECAO_PERFIL = 0
    IDX_LOADING = 1
    IDX_INSPECAO = 2
    IDX_DIAGNOSTICO = 3
    IDX_ENDGAME = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tela_de_expediente")
        self.setProperty("class", "tela_expediente")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__maximizado: bool = False
        self.__inicializado: bool = False
        self.__tamanho_normal: Any = None

        self.__anexo_gallery: AnexoGallery
        self.__media_viewer: MediaViewer
        self.__sidebar: Sidebar
        
        # Paginas Filhas
        self.__pagina_perfil: PaginaSelecaoPerfil
        self.__pagina_loading: PaginaLoading
        self.__pagina_diagnostico: PaginaDiagnostico
        self.__pagina_endgame: PaginaEndgame
        self.__pagina_inspecao: PaginaInspecao

        self.__setup_ui()

    def __setup_ui(self):
        L = LayoutLoader.instance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        altura_bar = L.scaled("tela_de_expediente", "title_bar", "altura")
        self.__title_bar = WindowTitleBar(titulo="Expediente", altura=altura_bar, parent=self)
        self.__title_bar.close_requested.connect(self.__on_fechar)
        self.__title_bar.minimized_solicitado.connect(self.__on_minimizar)
        self.__title_bar.maximized_solicitado.connect(self.__on_maximizar_restaurar)
        layout.addWidget(self.__title_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.__sidebar = Sidebar()
        body.addWidget(self.__sidebar)

        self.__pagina_perfil = PaginaSelecaoPerfil()
        self.__pagina_perfil.perfil_confirmado.connect(self.__on_perfil_confirmado)
        
        self.__pagina_loading = PaginaLoading()
        self.__pagina_diagnostico = PaginaDiagnostico()
        
        self.__pagina_diagnostico.continuar_solicitado.connect(self.continuar_solicitado.emit)
        self.__pagina_endgame = PaginaEndgame()
        
        self.__pagina_endgame.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        self.__pagina_inspecao = PaginaInspecao()
        self.__pagina_inspecao.submeter_respostas.connect(self.submeter_respostas.emit)

        self.__stack = QStackedWidget()
        self.__stack.addWidget(self.__pagina_perfil)
        self.__stack.addWidget(self.__pagina_loading)
        self.__stack.addWidget(self.__pagina_inspecao)
        self.__stack.addWidget(self.__pagina_diagnostico)
        self.__stack.addWidget(self.__pagina_endgame)
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        body.addWidget(self.__stack, stretch=1)

        layout.addLayout(body, stretch=1)

        self.__stack.currentChanged.connect(self.__on_page_changed)
        self.__sidebar.setVisible(False)

        self.__anexo_gallery = AnexoGallery(self)
        self.__anexo_gallery.hide()

        self.__media_viewer = MediaViewer(self)
        self.__media_viewer.hide()

        self.__pagina_inspecao.configurar_midia(self.__anexo_gallery, self.__media_viewer)

    @Slot(str)
    def __on_perfil_confirmado(self, perfil: str) -> None:
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
        else:
            self.__maximizar()
        self.__maximizado = not self.__maximizado
        self.__title_bar.set_maximizado(self.__maximizado)

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
        logger.info("Exibindo endgame: %.1f pts em %d dia(s), venceu=%s", pontuacao_global, dias_concluidos, venceu)
        self.__title_bar.definir_titulo("Fim do Expediente")
        self.__pagina_endgame.exibir_resultado(pontuacao_global, dias_concluidos, venceu)
        self.__stack.setCurrentIndex(self.IDX_ENDGAME)

    def exibir_com_tamanho_inicial(self, parent_rect: Any) -> None:
        if not self.__inicializado:
            w = int(parent_rect.width() * 0.8)
            h = int(parent_rect.height() * 0.8)
            x = (parent_rect.width() - w) // 2
            y = (parent_rect.height() - h) // 2
            self.setGeometry(x, y, w, h)
            self.__tamanho_normal = self.geometry()
            self.__inicializado = True
        self.show()

    def reiniciar(self) -> None:
        self.__pagina_inspecao.limpar_formulario()
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        self.__title_bar.definir_titulo("Expediente")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__maximizado and self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        if self.__anexo_gallery.isVisible():
            self.__anexo_gallery.setGeometry(self.rect())
        if self.__media_viewer.isVisible():
            self.__media_viewer.setGeometry(self.rect())
