import abc
import logging
from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from application.interfaces.i_game_view import IGameView
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.components.taskbar import Taskbar
from view.screens.tela_de_expediente import TelaDeExpediente
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
      z=2: TelaDeExpediente (flutuante 80%, oculta por padrao)
    """

    iniciar_solicitado = Signal()
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspetor IFF-BJI: Análise de Risco")
        self.setMinimumSize(1920, 1080)

        container = QWidget()
        container.setObjectName("container_area")
        self.setCentralWidget(container)

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

        self.__tela_expediente = TelaDeExpediente()
        self.__tela_expediente.perfil_confirmado.connect(self.perfil_confirmado.emit)
        self.__tela_expediente.submeter_respostas.connect(self.submeter_respostas.emit)
        self.__tela_expediente.continuar_solicitado.connect(self.continuar_solicitado.emit)
        self.__tela_expediente.voltar_menu_solicitado.connect(self.voltar_menu_solicitado.emit)
        self.__tela_expediente.minimized_solicitado.connect(self.__on_minimizar_expediente)
        self.__overlay_area.add_overlay(self.__tela_expediente, auto_resize=False)

    def __on_minimizar_expediente(self) -> None:
        self.__tela_expediente.hide()

    def inicializar(self) -> None:
        logger.info("JanelaPrincipal inicializada.")
        self.show()

    def fechar(self) -> None:
        logger.info("JanelaPrincipal fechando.")
        self.close()

    def exibir_menu(self) -> None:
        logger.info("Exibindo menu principal (desktop).")
        self.__tela_expediente.hide()

    def exibir_selecao_perfil(self) -> None:
        logger.info("Exibindo selecao de perfil no expediente.")
        self.__tela_expediente.exibir_selecao_perfil()
        self.__tela_expediente.exibir_com_tamanho_inicial(self.__overlay_area.rect())

    def exibir_tela_carregamento(self) -> None:
        logger.info("Exibindo tela de carregamento.")
        self.__tela_expediente.exibir_tela_carregamento()

    def trocar_para_tela_inspecao(self) -> None:
        logger.info("Garantindo visibilidade do expediente (compatibilidade).")
        self.__tela_expediente.show()

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico no expediente.")
        self.__tela_expediente.exibir_tela_diagnostico(diagnostico)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio no expediente.")
        self.__tela_expediente.renderizar_relatorio(dados_relatorio)
        if not self.__tela_expediente.isVisible():
            self.__tela_expediente.show()

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int) -> None:
        logger.info("Exibindo resultado final (compatibilidade).")
        venceu = pontuacao_global > 0
        self.__tela_expediente.exibir_tela_endgame(pontuacao_global, dias_concluidos, venceu)

    def exibir_tela_endgame(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo endgame.")
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlay_area")
        self.__desktop: QWidget | None = None
        self.__overlays: list[tuple[QWidget, bool]] = []
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        for widget, auto_resize in self.__overlays:
            if widget.isVisible() and auto_resize:
                widget.setGeometry(rect)
