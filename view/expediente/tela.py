import logging
from typing import Any, Dict
from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QStackedWidget

from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO
from infrastructure.repository.repositorio_pareceres_cipa import RepositorioDePareceresCIPA
from infrastructure.repository.repositorio_pareceres_cipavitoria import RepositorioDePareceresCIPAVitoria
from view.expediente.widgets.sidebar import Sidebar
from view.widgets.janela_flutuante import JanelaFlutuante
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer
from view.expediente.paginas.diagnostico import PaginaDiagnostico
from view.expediente.paginas.game_win import GameWin
from view.expediente.paginas.game_over import GameOver
from view.expediente.paginas.inspecao import PaginaInspecao
from view.expediente.paginas.selecao_perfil import PaginaSelecaoPerfil

logger = logging.getLogger(__name__)


class TelaDeExpediente(JanelaFlutuante):
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()
    sair_solicitado = Signal()
    minimized_solicitado = Signal()

    IDX_SELECAO_PERFIL = 0
    IDX_INSPECAO = 1
    IDX_DIAGNOSTICO = 2
    IDX_GAME_WIN = 3
    IDX_GAME_OVER = 4

    def __init__(self, parent=None):
        super().__init__(
            proporcao_keys=("tela_de_expediente", "proporcao_tela"), parent=parent
        )
        self.setObjectName("tela_de_expediente")
        self.setProperty("class", "tela_expediente")

        self.__perfil_selecionado: str = ""

        self.__repositorio_pareceres: RepositorioDePareceresCIPA = RepositorioDePareceresCIPA()
        self.__repositorio_pareceres_vitoria: RepositorioDePareceresCIPAVitoria = RepositorioDePareceresCIPAVitoria()

        self.__anexo_gallery: AnexoGallery
        self.__media_viewer: MediaViewer
        self.__sidebar: Sidebar

        # Paginas Filhas
        self.__pagina_perfil: PaginaSelecaoPerfil
        self.__pagina_diagnostico: PaginaDiagnostico
        self.__pagina_game_win: GameWin
        self.__pagina_game_over: GameOver
        self.__pagina_inspecao: PaginaInspecao

        self.__setup_ui()

    def __setup_ui(self):
        layout = self._montar_chrome("Expediente")
        layout.addLayout(self.__build_body(), stretch=1)
        self.__build_overlays()

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

        self.__pagina_diagnostico = PaginaDiagnostico()
        self.__pagina_diagnostico.continuar_solicitado.connect(self.continuar_solicitado.emit)

        self.__pagina_inspecao = PaginaInspecao()
        self.__pagina_inspecao.submeter_respostas.connect(self.submeter_respostas.emit)

        self.__pagina_game_win = GameWin(
            pontuacao_global=0.0,
            repositorio=self.__repositorio_pareceres_vitoria,
        )
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
        self.perfil_confirmado.emit(perfil)

    @Slot(int)
    def __on_page_changed(self, index: int) -> None:
        # Guard defensivo: durante o teardown (destruicao do widget) o Qt pode
        # emitir currentChanged(-1) com o wrapper Python ja em finalizacao.
        sidebar = getattr(self, "_TelaDeExpediente__sidebar", None)
        if sidebar is not None:
            sidebar.setVisible(index in [self.IDX_INSPECAO, self.IDX_DIAGNOSTICO])

    @Slot()
    def _ao_minimizar(self) -> None:
        super()._ao_minimizar()
        self.minimized_solicitado.emit()

    @Slot()
    def _ao_fechar(self) -> None:
        self.reiniciar()
        self.voltar_menu_solicitado.emit()
        self._fechar()

    def exibir_selecao_perfil(self) -> None:
        self._title_bar.definir_titulo("Seleção de Perfil")
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        titulo = dados_relatorio.get("titulo", "Relatório")
        self._title_bar.definir_titulo(f"Relatório: {titulo}")
        self.__pagina_inspecao.renderizar_relatorio(dados_relatorio)
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)

    def exibir_tela_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        logger.info("Exibindo diagnostico: %s", resultado)
        self._title_bar.definir_titulo("Resultado da Inspecao")
        self.__pagina_diagnostico.exibir_diagnostico(resultado)
        self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)

    def exibir_tela_endgame(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo endgame: %.1f pts, venceu=%s", pontuacao_global, venceu)
        self._title_bar.definir_titulo("Fim do Expediente")
        if venceu:
            self.__pagina_game_win.exibir_resultado(
                pontuacao_global, self.__perfil_selecionado
            )
            self.__stack.setCurrentIndex(self.IDX_GAME_WIN)
            return
        self.__pagina_game_over.exibir_resultado(
            pontuacao_global, self.__perfil_selecionado
        )
        self.__stack.setCurrentIndex(self.IDX_GAME_OVER)

    def reiniciar(self) -> None:
        self.__pagina_inspecao.limpar_formulario()
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        self._title_bar.definir_titulo("Expediente")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._maximizado and self.parentWidget():
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
