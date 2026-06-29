import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout

from view.components.janela_sistema_body import JanelaSistemaBody
from view.components.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class JanelaSistema(QFrame):
    close_requested = Signal()
    perfil_confirmado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("janela_sistema")
        self.setProperty("class", "janela_sistema")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        L = LayoutLoader.instance()
        w = L.scaled("janela_sistema", "largura")
        h = L.scaled("janela_sistema", "altura")
        self.setFixedSize(w, h)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__title_bar = WindowTitleBar("Sistema")
        self.__title_bar.close_requested.connect(self.close_requested.emit)
        layout.addWidget(self.__title_bar)

        self.__body = JanelaSistemaBody()
        self.__body.perfil_confirmado.connect(self.perfil_confirmado.emit)
        layout.addWidget(self.__body)

    def exibir_selecao_perfil(self) -> None:
        self.__body.exibir_selecao_perfil()
