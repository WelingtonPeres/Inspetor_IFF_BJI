from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader


class ItemNumerado(QWidget):
    """Item de lista com badge numerado, titulo e descricao dos slides."""

    def __init__(
        self,
        numero: int,
        titulo: str,
        descricao: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("tutorial_item")
        self.__setup_ui(numero, titulo, descricao)

    def __setup_ui(self, numero: int, titulo: str, descricao: str) -> None:
        L = LayoutLoader.instance()
        familia = L.get("tutorial", "font_familia")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(L.scaled("tutorial", "item_numerado", "spacing"))
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        badge = QLabel(str(numero))
        badge.setObjectName("tutorial_item_num")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(
            L.scaled("tutorial", "item_numerado", "badge_tamanho"),
            L.scaled("tutorial", "item_numerado", "badge_tamanho"),
        )
        badge.setFont(
            QFont(familia, L.scaled("tutorial", "item_numerado", "badge_font_size"))
        )
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)

        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("tutorial_item_titulo")
        label_titulo.setWordWrap(True)
        label_titulo.setFont(
            QFont(familia, L.scaled("tutorial", "item_numerado", "titulo_font_size"))
        )
        textos.addWidget(label_titulo)

        label_descricao = QLabel(descricao)
        label_descricao.setObjectName("tutorial_item_descricao")
        label_descricao.setWordWrap(True)
        label_descricao.setFont(
            QFont(familia, L.scaled("tutorial", "item_numerado", "descricao_font_size"))
        )
        textos.addWidget(label_descricao)

        layout.addLayout(textos, stretch=1)
