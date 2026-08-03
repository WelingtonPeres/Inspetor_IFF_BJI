import abc
import logging
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from application.interfaces.i_game_view import IGameView, MotivoTutorial
from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO
from view.desktop.taskbar import Taskbar
from view.expediente.tela import TelaDeExpediente
from view.desktop.menu import TelaMenuPrincipal
from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.tela_tutorial import TelaTutorial

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
    sair_solicitado = Signal()
    arquivos_solicitado = Signal()
    help_solicitado = Signal()
    wallpapers_solicitado = Signal()
    tutorial_finalizado = Signal(MotivoTutorial)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspetor IFF-BJI")
        # 1280x720 = HD (16:9). Tamanho minimo e inicial.
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)

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

        self.__tela_tutorial = self.__build_tela_tutorial()
        self.__overlay_area.add_overlay(self.__tela_tutorial, auto_resize=False)

    def __build_container(self) -> QWidget:
        container = QWidget()
        container.setObjectName("container_area")
        return container

    def __build_overlay_area(self) -> "_OverlayArea":
        overlay_area = _OverlayArea()
        return overlay_area

    def __build_taskbar(self) -> Taskbar:
        taskbar = Taskbar()
        taskbar.arquivos_solicitado.connect(self.__on_arquivos_solicitado)
        taskbar.help_solicitado.connect(self.__on_help_solicitado)
        taskbar.wallpapers_solicitado.connect(self.__on_wallpapers_solicitado)
        taskbar.iniciar_solicitado.connect(self.__encaminhar_iniciar)
        return taskbar

    def __build_tela_menu(self) -> TelaMenuPrincipal:
        tela_menu = TelaMenuPrincipal()
        tela_menu.iniciar_solicitado.connect(self.__encaminhar_iniciar)
        return tela_menu

    def __build_tela_expediente(self) -> TelaDeExpediente:
        tela_expediente = TelaDeExpediente()
        tela_expediente.perfil_confirmado.connect(self.perfil_confirmado.emit)
        tela_expediente.submeter_respostas.connect(self.submeter_respostas.emit)
        tela_expediente.continuar_solicitado.connect(self.continuar_solicitado.emit)
        tela_expediente.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        tela_expediente.jogar_novamente_solicitado.connect(self.jogar_novamente_solicitado.emit)
        tela_expediente.sair_solicitado.connect(self.sair_solicitado.emit)
        tela_expediente.minimized_solicitado.connect(self.__on_minimizar_expediente)
        # O expediente flutua a 80% e nao preenche o overlay, mas ainda precisa
        # reagir quando o overlay cresce (B5). O signal repassa o novo rect.
        self.__overlay_area.overlay_resized.connect(
            tela_expediente.redimensionar_com_overlay
        )
        return tela_expediente

    def __build_tela_tutorial(self) -> TelaTutorial:
        # Sombra 6x6 solida: QFrame irmao com z abaixo do tutorial — QSS nao
        # suporta box-shadow (padrao #expediente_sombra). Registada primeiro
        # para ficar sob a janela flutuante.
        self.__sombra_tutorial = QFrame()
        self.__sombra_tutorial.setObjectName("tutorial_sombra")
        self.__overlay_area.add_overlay(self.__sombra_tutorial, auto_resize=False)

        tela_tutorial = TelaTutorial()
        tela_tutorial.finalizado_solicitado.connect(self.tutorial_finalizado.emit)
        # auto_resize=False: a geometria 80% so recalcula via overlay_resized.
        self.__overlay_area.add_overlay(tela_tutorial, auto_resize=False)
        self.__overlay_area.overlay_resized.connect(
            tela_tutorial.redimensionar_com_overlay
        )
        tela_tutorial.geometria_alterada.connect(self.__sincronizar_geometria_sombra)
        tela_tutorial.visibilidade_alterada.connect(self.__sombra_tutorial.setVisible)
        return tela_tutorial

    @Slot()
    def __sincronizar_geometria_sombra(self) -> None:
        """Espelha a geometria da sombra na janela do tutorial (offset 6, 6)."""
        self.__sombra_tutorial.setGeometry(
            self.__tela_tutorial.geometry().translated(6, 6)
        )

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

    @Slot()
    def __encaminhar_iniciar(self, _legenda: str = "") -> None:
        self.iniciar_solicitado.emit()

    @Slot()
    def __on_arquivos_solicitado(self) -> None:
        logger.info("Arquivos solicitado via taskbar.")

    @Slot()
    def __on_help_solicitado(self) -> None:
        logger.info("Help solicitado via taskbar.")
        self.help_solicitado.emit()

    @Slot()
    def __on_wallpapers_solicitado(self) -> None:
        from view.desktop.wallpaper_selector import WallpaperSelector

        dialog = WallpaperSelector(self)
        dialog.wallpaper_selecionado.connect(self.__tela_menu._TelaMenuPrincipal__aplicar_wallpaper)
        dialog.exec()

    def inicializar(self) -> None:
        logger.info("JanelaPrincipal inicializada.")
        self.show()

    def fechar(self) -> None:
        logger.info("JanelaPrincipal fechando.")
        self.close()

    def exibir_menu(self) -> None:
        logger.info("Exibindo menu principal (desktop).")
        self.__tela_expediente.hide()
        self.__tela_tutorial.hide()

    def exibir_selecao_perfil(self) -> None:
        logger.info("Exibindo selecao de perfil no expediente.")
        self.__tela_expediente.exibir_selecao_perfil()
        self.__tela_expediente.exibir_com_tamanho_inicial(self.__overlay_area.rect())

    def exibir_tutorial(self, motivo: "MotivoTutorial") -> None:
        logger.info("Exibindo tutorial (motivo=%s).", motivo.name)
        self.__tela_tutorial.exibir_tutorial(motivo)
        # Rect de referencia geometrico: menu -> overlay; consulta sobre o
        # expediente visivel -> rect actual do expediente (nunca maior que ele).
        rect_ref = self.__overlay_area.rect()
        if motivo == MotivoTutorial.CONSULTA and self.__tela_expediente.isVisible():
            rect_ref = self.__tela_expediente.geometry()
        self.__tela_tutorial.exibir_com_tamanho_inicial(rect_ref)

    def trocar_para_tela_inspecao(self) -> None:
        logger.info("Exibindo expediente (tela de inspecao).")
        self.__tela_expediente.show()

    def exibir_tela_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        logger.info("Exibindo diagnostico no expediente.")
        self.__tela_expediente.exibir_tela_diagnostico(resultado)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio no expediente.")
        self.__tela_expediente.renderizar_relatorio(dados_relatorio)
        self.__tela_expediente.show()

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo resultado final. venceu=%s, pontuacao=%.1f", venceu, pontuacao_global)
        self.__tela_expediente.exibir_tela_endgame(pontuacao_global, dias_concluidos, venceu)

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
