import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class PaginaSelecaoPerfil(QWidget):
    """Widget de selecao de perfil com combo e botao confirmar.

    Emite perfil_confirmado(str) quando o utilizador confirma a escolha.
    """

    perfil_confirmado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_selecao_perfil")
        self.setProperty("class", "pagina_selecao_perfil")

        self.__combo_perfil: QComboBox
        self.__btn_confirmar: QPushButton

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Selecione o perfil:")
        label.setObjectName("label_selecao_perfil")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.__combo_perfil = QComboBox()
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.setProperty("class", "combo_padrao")
        self.__combo_perfil.addItems([
            "DEFAULT", "T_QUIMICA", "T_INFORMATICA", "T_AGROPECUARIA",
            "T_ALIMENTOS", "T_MEIO_AMBIENTE", "T_ZOOTECNIA",
            "CT_ALIMENTOS", "E_COMPUTACAO",
        ])
        layout.addWidget(self.__combo_perfil)

        self.__btn_confirmar = QPushButton("Confirmar")
        self.__btn_confirmar.setObjectName("btn_confirmar_perfil")
        self.__btn_confirmar.setProperty("class", "btn_primario")
        self.__btn_confirmar.clicked.connect(self._on_confirmar)
        layout.addWidget(self.__btn_confirmar)

    def _on_confirmar(self) -> None:
        perfil = self.__combo_perfil.currentText()
        if not perfil:
            logger.warning("[Aviso - PaginaSelecaoPerfil] Perfil vazio ao confirmar")
        self.perfil_confirmado.emit(perfil)
