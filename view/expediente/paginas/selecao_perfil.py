import logging
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox,
)
from PySide6.QtGui import QKeyEvent

from view.expediente.configuracoes.perfis import make_profile_roster
from view.expediente.modelos.character_data import CharacterData
from view.expediente.widgets.character_carousel import CharacterCarousel

logger = logging.getLogger(__name__)


class PaginaSelecaoPerfil(QWidget):
    """Widget de selecao de perfil com carousel animado de cartas.

    Emite perfil_confirmado(str) quando o utilizador confirma a escolha.
    """

    perfil_confirmado = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("pagina_selecao_perfil")
        self.setProperty("class", "pagina_selecao_perfil")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.__perfis: List[CharacterData] = make_profile_roster()

        self.__carousel: CharacterCarousel
        self.__combo_perfil: QComboBox
        self.__btn_confirmar: QPushButton
        self.__label_contador: QLabel

        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 16)
        layout.setSpacing(12)

        label = QLabel("Selecione o perfil:")
        label.setObjectName("label_selecao_perfil")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.__carousel = CharacterCarousel(self.__perfis)
        layout.addWidget(self.__carousel, stretch=1)

        self.__label_contador = QLabel(self.__texto_contador())
        self.__label_contador.setObjectName("label_contador_perfil")
        self.__label_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_contador)

        self.__btn_confirmar = QPushButton("Confirmar")
        self.__btn_confirmar.setObjectName("btn_confirmar_perfil")
        self.__btn_confirmar.setProperty("class", "btn_primario")
        self.__btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_confirmar.clicked.connect(self.__on_confirmar)
        layout.addWidget(
            self.__btn_confirmar, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.__combo_perfil = QComboBox(self)
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.addItems([p.char_id for p in self.__perfis])
        self.__combo_perfil.hide()

        self.__carousel.index_changed.connect(self.__on_index_changed)

    def __texto_contador(self) -> str:
        return (
            f"{self.__carousel.current_index + 1} / {len(self.__perfis)}"
        )

    def __on_index_changed(self, index: int) -> None:
        self.__label_contador.setText(self.__texto_contador())
        self.__combo_perfil.setCurrentIndex(index)

    def __on_confirmar(self) -> None:
        perfil = self.__perfis[self.__carousel.current_index].char_id
        self.perfil_confirmado.emit(perfil)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.__carousel.slide_previous()
        elif event.key() == Qt.Key.Key_Right:
            self.__carousel.slide_next()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.__on_confirmar()
        else:
            super().keyPressEvent(event)
