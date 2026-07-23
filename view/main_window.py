import abc
import logging
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from application.interfaces.i_game_view import IGameView
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.desktop.taskbar import Taskbar
from view.expediente.tela import TelaDeExpediente
from view.expediente.paginas.game_win import GameWin
from view.expediente.paginas.game_over import GameOver
from view.desktop.menu import TelaMenuPrincipal
from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


_ObjectType = type(QMainWindow)


class _MetaInterface(abc.ABCMeta, _ObjectType):
    """Metaclasse combinada para permitir heranca de QMainWindow + IGameView."""


class JanelaPrincipal(QMainWindow, IGameView, metaclass=_MetaInterface):
    """
    Janela principal do jogo. Implementa o contrato IGameView
    e gerencia as telas via sobreposicao (overlay) com z-order:

      z=0: Taskbar (sempre visivel, rodape)
      z=1: Desktop (TelaMenuPrincipal, sempre visivel)
      z=2: TelaDeExpediente (flutuante 80%, oculta por padrao)
    """

    iniciar_solicitado = Signal()
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspetor IFF-BJI: Análise de Risco")
        # 1024x576 = metade da resolucao base (1920x1080). Permite encolcher
        # a janela sem a tornar unusavel, mas nao bloqueia abaixo da resolucao
        # real do monitor como o antigo 1920x1080 fazia.
        self.setMinimumSize(1024, 576)

        self.__sincronizar_escala_com_tela()

        container = self.__build_container()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__overlay_area = self.__build_overlay_area()
        layout.addWidget(self.__overlay_area, stretch=1)

        self.__taskbar = self.__build_taskbar()
        layout.addWidget(self.__taskbar)

        self.__tela_menu = self.__build_tela_menu()
        self.__overlay_area.add_desktop(self.__tela_menu)

        self.__tela_expediente = self.__build_tela_expediente()
        self.__overlay_area.add_overlay(self.__tela_expediente, auto_resize=False)

        self.__endgame_atual: Optional[QWidget] = None

    def __build_container(self) -> QWidget:
        container = QWidget()
        container.setObjectName("container_area")
        return container

    def __build_overlay_area(self) -> "_OverlayArea":
        overlay_area = _OverlayArea()
        return overlay_area

    def __build_taskbar(self) -> Taskbar:
        return Taskbar()

    def __build_tela_menu(self) -> TelaMenuPrincipal:
        tela_menu = TelaMenuPrincipal()
        tela_menu.iniciar_solicitado.connect(self.__encaminhar_iniciar)
        return tela_menu

    def __build_tela_expediente(self) -> TelaDeExpediente:
        tela_expediente = TelaDeExpediente()
        tela_expediente.perfil_confirmado.connect(self.perfil_confirmado.emit)
        tela_expediente.submeter_respostas.connect(self.submeter_respostas.emit)
        tela_expediente.continuar_solicitado.connect(self.continuar_solicitado.emit)
        tela_expediente.minimized_solicitado.connect(self.__on_minimizar_expediente)
        # O expediente flutua a 80% e nao preenche o overlay, mas ainda precisa
        # reagir quando o overlay cresce (B5). O signal repassa o novo rect.
        self.__overlay_area.overlay_resized.connect(
            tela_expediente.redimensionar_com_overlay
        )
        return tela_expediente

    def __sincronizar_escala_com_tela(self) -> None:
        """Alimenta o LayoutLoader com a resolucao real do monitor.

        Usa a geometria completa do screen (nao availableGeometry) porque a
        referencia do layout (1920x1080) e a resolucao total; a taskbar ficticia
        do proprio app e que desconta a area util, via overlay layout.
        """
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.geometry()
        if geo.width() > 0 and geo.height() > 0:
            LayoutLoader.instance().set_screen(geo.width(), geo.height())

    def resizeEvent(self, event) -> None:
        # Cada redimensionamento da janela atualiza o fator de escala global;
        # o LayoutLoader emite escala_atualizada e os widgets re-aplicam dims.
        LayoutLoader.instance().set_screen(self.width(), self.height())
        super().resizeEvent(event)

    @Slot()
    def __on_minimizar_expediente(self) -> None:
        self.__tela_expediente.hide()

    @Slot(str)
    def __encaminhar_iniciar(self, _legenda: str) -> None:
        self.iniciar_solicitado.emit()

    def inicializar(self) -> None:
        logger.info("JanelaPrincipal inicializada.")
        self.show()

    def fechar(self) -> None:
        logger.info("JanelaPrincipal fechando.")
        self.close()

    def exibir_menu(self) -> None:
        logger.info("Exibindo menu principal (desktop).")
        self.__tela_expediente.hide()
        self.__limpar_endgame_anterior()

    def exibir_selecao_perfil(self) -> None:
        logger.info("Exibindo selecao de perfil no expediente.")
        self.__tela_expediente.exibir_selecao_perfil()
        self.__tela_expediente.exibir_com_tamanho_inicial(self.__overlay_area.rect())

    def exibir_tela_carregamento(self) -> None:
        logger.info("Exibindo tela de carregamento.")
        self.__tela_expediente.exibir_tela_carregamento()

    def trocar_para_tela_inspecao(self) -> None:
        logger.info("Exibindo expediente (tela de inspecao).")
        self.__tela_expediente.show()

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico no expediente.")
        self.__tela_expediente.exibir_tela_diagnostico(diagnostico)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio no expediente.")
        self.__tela_expediente.renderizar_relatorio(dados_relatorio)
        self.__tela_expediente.show()

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo resultado final. venceu=%s, pontuacao=%.1f", venceu, pontuacao_global)
        self.__tela_expediente.hide()
        self.__limpar_endgame_anterior()
        widget = self.__criar_endgame(pontuacao_global, venceu)
        self.__endgame_atual = widget
        self.__overlay_area.add_overlay(widget, auto_resize=False)
        self.__overlay_area.overlay_resized.connect(self.__reposicionar_endgame)
        widget.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        widget.jogar_novamente_solicitado.connect(self.jogar_novamente_solicitado.emit)
        self.__reposicionar_endgame(self.__overlay_area.rect())
        widget.show()

    @Slot(QRect)
    def __reposicionar_endgame(self, parent_rect: QRect) -> None:
        if self.__endgame_atual is None:
            return
        w = int(parent_rect.width() * 0.8)
        h = int(parent_rect.height() * 0.8)
        x = (parent_rect.width() - w) // 2
        y = (parent_rect.height() - h) // 2
        self.__endgame_atual.setGeometry(x, y, w, h)

    def __criar_endgame(self, pontuacao: float, venceu: bool) -> QWidget:
        if venceu:
            return GameWin(pontuacao)
        return GameOver(pontuacao)

    def __limpar_endgame_anterior(self) -> None:
        if self.__endgame_atual is not None:
            self.__overlay_area.remove_overlay(self.__endgame_atual)
            self.__endgame_atual.deleteLater()
            self.__endgame_atual = None

    def exibir_popup_erro(self, mensagem: str) -> None:
        logger.warning("Popup de erro: %s", mensagem)
        QMessageBox.critical(self, "Erro", mensagem)


class _OverlayArea(QWidget):
    """
    Area central que empilha widgets em z-order.
    O primeiro widget adicionado via add_desktop e o fundo (z=1);
    os overlays (z=2) sao posicionados por cima.
    """

    overlay_resized = Signal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlay_area")
        self.__desktop: Optional[QWidget] = None
        self.__overlays: List[Tuple[QWidget, bool]] = []
        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

    def add_desktop(self, widget: QWidget) -> None:
        self.__desktop = widget
        self.__layout.addWidget(widget)

    def add_overlay(self, widget: QWidget, auto_resize: bool = True) -> None:
        self.__overlays.append((widget, auto_resize))
        widget.setParent(self)
        widget.hide()
        widget.raise_()

    def remove_overlay(self, widget: QWidget) -> None:
        widget.hide()
        widget.setParent(None)
        self.__overlays = [(w, ar) for w, ar in self.__overlays if w is not widget]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        for widget, auto_resize in self.__overlays:
            if not widget.isVisible():
                continue
            if auto_resize:
                widget.setGeometry(rect)
        # auto_resize=False overlays ouvem o signal e decidem sozinhos.
        self.overlay_resized.emit(rect)
