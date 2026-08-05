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
        self.__label_titulo: QLabel

        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 16)
        layout.setSpacing(12)

        self.__build_titulo(layout)
        self.__build_carousel(layout)
        self.__build_contador(layout)
        self.__build_botao_confirmar(layout)
        self.__build_combo_oculto()

        self.__carousel.index_changed.connect(self.__on_index_changed)

    def __build_titulo(self, layout: QVBoxLayout) -> None:
        """Constroi o titulo superior da pagina."""
        self.__label_titulo = QLabel("Selecione o perfil:")
        self.__label_titulo.setObjectName("label_selecao_perfil")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_titulo)

    def __build_carousel(self, layout: QVBoxLayout) -> None:
        """Constroi o carousel de perfis."""
        self.__carousel = CharacterCarousel(self.__perfis)
        layout.addWidget(self.__carousel, stretch=1)

    def __build_contador(self, layout: QVBoxLayout) -> None:
        """Constroi o contador de posicao do carousel."""
        self.__label_contador = QLabel(self.__texto_contador())
        self.__label_contador.setObjectName("label_contador_perfil")
        self.__label_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_contador)

    def __build_botao_confirmar(self, layout: QVBoxLayout) -> None:
        """Constroi o botao de confirmacao de perfil."""
        self.__btn_confirmar = QPushButton("Confirmar")
        self.__btn_confirmar.setObjectName("btn_confirmar_perfil")
        self.__btn_confirmar.setProperty("class", "btn_primario")
        self.__btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__btn_confirmar.clicked.connect(self.__on_confirmar)
        self.__btn_confirmar.setEnabled(len(self.__perfis) > 0)
        layout.addWidget(
            self.__btn_confirmar, alignment=Qt.AlignmentFlag.AlignCenter
        )

    def __build_combo_oculto(self) -> None:
        """Constroi o combo oculto de sincronizacao de indice."""
        self.__combo_perfil = QComboBox(self)
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.addItems([p.char_id for p in self.__perfis])
        self.__combo_perfil.hide()

    def __texto_contador(self) -> str:
        total = len(self.__perfis)
        if total == 0:
            return "0 / 0"
        return f"{self.__carousel.current_index + 1} / {total}"

    def __on_index_changed(self, index: int) -> None:
        self.__label_contador.setText(self.__texto_contador())
        self.__combo_perfil.setCurrentIndex(index)

    def __on_confirmar(self) -> None:
        if not self.__perfis:
            return
        perfil = self.__perfis[self.__carousel.current_index].char_id
        self.perfil_confirmado.emit(perfil)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.__carousel.slide_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.__carousel.slide_next()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.__on_confirmar()
            return
        super().keyPressEvent(event)
