import abc
import logging
from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from application.interfaces.i_game_view import IGameView
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.components.janela_sistema import JanelaSistema
from view.components.taskbar import Taskbar
from view.screens.tela_inspecao_cheia import TelaInspecaoCheia
from view.screens.tela_menu_principal import TelaMenuPrincipal

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
      z=2: JanelaSistema (flutuante, oculta por padrao)
      z=2: TelaInspecaoCheia (tela cheia, oculta por padrao)
    """

    iniciar_solicitado = Signal()
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspetor IFF-BJI: Análise de Risco") # Titulo da Janela
        self.setMinimumSize(1920, 1080) # Tamanho da Janela (Virar Configuração no Futuro)

        container = QWidget() 
        container.setObjectName("container_area")
        self.setCentralWidget(container) # Torna o Widget central
        
        # Pilagem de Widget
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__overlay_area = _OverlayArea()
        layout.addWidget(self.__overlay_area, stretch=1)

        self.__taskbar = Taskbar()
        layout.addWidget(self.__taskbar)

        self.__tela_menu = TelaMenuPrincipal()
        self.__tela_menu.iniciar_solicitado.connect(lambda _: self.iniciar_solicitado.emit())
        self.__overlay_area.add_desktop(self.__tela_menu)

        self.__janela_sistema = JanelaSistema()
        self.__janela_sistema.close_requested.connect(self.__on_fechar_janela_sistema)
        self.__janela_sistema.perfil_confirmado.connect(self.perfil_confirmado.emit)
        self.__overlay_area.add_overlay(self.__janela_sistema)

        self.__tela_inspecao = TelaInspecaoCheia()
        self.__tela_inspecao.submeter_respostas.connect(self.submeter_respostas.emit)
        self.__tela_inspecao.continuar_solicitado.connect(self.continuar_solicitado.emit)
        self.__tela_inspecao.minimizar_solicitado.connect(self.__on_minimizar_inspecao)
        self.__tela_inspecao.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        self.__overlay_area.add_overlay(self.__tela_inspecao)

    def __on_fechar_janela_sistema(self) -> None:
        self.__janela_sistema.hide()

    def __on_minimizar_inspecao(self) -> None:
        self.__tela_inspecao.hide()

    def inicializar(self) -> None:
        logger.info("JanelaPrincipal inicializada.")
        self.show()

    def fechar(self) -> None:
        logger.info("JanelaPrincipal fechando.")
        self.close()

    def exibir_menu(self) -> None:
        logger.info("Exibindo menu principal (desktop).")
        self.__tela_inspecao.hide()
        self.__janela_sistema.hide()

    def exibir_selecao_perfil(self) -> None:
        logger.info("Exibindo selecao de perfil na JanelaSistema.")
        self.__tela_inspecao.hide()
        self.__janela_sistema.exibir_selecao_perfil()
        self.__janela_sistema.show()
        self.__centralizar_janela_sistema()

    def trocar_para_tela_inspecao(self) -> None:
        logger.info("Exibindo tela de inspecao (cheia).")
        self.__janela_sistema.hide()
        self.__tela_inspecao.setGeometry(self.__overlay_area.rect())
        self.__tela_inspecao.show()

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico na tela cheia.")
        self.__tela_inspecao.exibir_tela_diagnostico(diagnostico)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio na tela cheia.")
        self.__tela_inspecao.renderizar_relatorio(dados_relatorio)

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int) -> None:
        logger.info("Exibindo resultado final.")
        self.__tela_inspecao.exibir_resultado(pontuacao_global, dias_concluidos)

    def exibir_popup_erro(self, mensagem: str) -> None:
        logger.warning("Popup de erro: %s", mensagem)
        QMessageBox.critical(self, "Erro", mensagem)

    def __centralizar_janela_sistema(self) -> None:
        area = self.__overlay_area.rect()
        geo = self.__janela_sistema.geometry()
        x = (area.width() - geo.width()) // 2
        y = (area.height() - geo.height()) // 2
        self.__janela_sistema.move(x, y)


class _OverlayArea(QWidget):
    """
    Area central que empilha widgets em z-order.
    O primeiro widget adicionado via add_desktop e o fundo (z=1);
    os overlays (z=2) sao posicionados por cima.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlay_area")
        self.__desktop: QWidget | None = None
        self.__overlays: list[QWidget] = []
        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

    def add_desktop(self, widget: QWidget) -> None:
        self.__desktop = widget
        self.__layout.addWidget(widget)

    def add_overlay(self, widget: QWidget) -> None:
        self.__overlays.append(widget)
        widget.setParent(self)
        widget.hide()
        widget.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        for overlay in self.__overlays:
            if overlay.isVisible():
                overlay.setGeometry(rect)
