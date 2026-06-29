import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton, QStackedWidget, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class JanelaSistemaBody(QFrame):
    perfil_confirmado = Signal(str)

    IDX_PLACEHOLDER = 0
    IDX_SELECAO_PERFIL = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("janela_sistema_body")
        self.setProperty("class", "janela_sistema_body")

        self.__combo_perfil: QComboBox
        self.__setup_ui()

    def __setup_ui(self):
        L = LayoutLoader.instance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("janela_sistema", "body", "margens"))
        layout.setSpacing(L.scaled("janela_sistema", "body", "spacing_entre_elementos"))

        self.__stack = QStackedWidget()
        self.__stack.addWidget(self.__criar_pagina_placeholder())
        self.__stack.addWidget(self.__criar_pagina_selecao_perfil())
        self.__stack.setCurrentIndex(self.IDX_PLACEHOLDER)
        layout.addWidget(self.__stack)

    def __criar_pagina_placeholder(self) -> QFrame:
        pagina = QFrame()
        sub = QVBoxLayout(pagina)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder = QLabel("Em construção")
        placeholder.setObjectName("janela_sistema_placeholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(QFont("Open Sans", 14))
        sub.addWidget(placeholder)
        return pagina

    def __criar_pagina_selecao_perfil(self) -> QFrame:
        pagina = QFrame()
        sub = QVBoxLayout(pagina)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Selecione o perfil:")
        label.setObjectName("label_selecao_perfil")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.addWidget(label)

        self.__combo_perfil = QComboBox()
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.setProperty("class", "combo_padrao")
        self.__combo_perfil.addItems([
            "T_QUIMICA", "T_INFORMATICA", "T_AGROPECUARIA",
            "T_ALIMENTOS", "T_MEIO_AMBIENTE", "T_ZOOTECNIA",
            "CT_ALIMENTOS", "E_COMPUTACAO",
        ])
        sub.addWidget(self.__combo_perfil)

        btn = QPushButton("Confirmar")
        btn.setObjectName("btn_confirmar_perfil")
        btn.setProperty("class", "btn_primario")
        btn.clicked.connect(
            lambda: self.perfil_confirmado.emit(self.__combo_perfil.currentText())
        )
        sub.addWidget(btn)

        return pagina

    def exibir_selecao_perfil(self) -> None:
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
