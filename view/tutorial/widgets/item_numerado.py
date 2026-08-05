from typing import Optional

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader


class ItemNumerado(QFrame):
    """Item de lista com badge numerado, titulo e descricao dos slides."""

    def __init__(
        self,
        numero: int,
        titulo: str,
        descricao: str,
        parent: Optional[QWidget] = None,
        cor_badge: Optional[str] = None,
    ):
        super().__init__(parent)
        self.setObjectName("tutorial_item")
        self.setProperty("class", "tutorial_item")

        self.__layout = LayoutLoader.instance()
        self.__cor_badge = cor_badge
        self.__label_titulo: QLabel
        self.__label_descricao: QLabel
        self.__badge: QLabel

        self.__setup_ui(numero, titulo, descricao)
        # escala_atualizada so dispara quando a resolucao muda de facto;
        # a primeira aplicacao das dimensoes tem de ser explicita.
        self.__reaplicar_dimensoes()
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self, numero: int, titulo: str, descricao: str) -> None:
        L = self.__layout
        familia = L.get("tutorial", "font_familia")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(L.scaled("tutorial", "item_numerado", "spacing"))
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        badge = QLabel(str(numero))
        badge.setObjectName("tutorial_item_num")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.__cor_badge is not None:
            # Variante de cor via QSS (ex: slide da decisao usa a cor
            # do carimbo correspondente, como no modelo).
            badge.setProperty("cor_badge", self.__cor_badge)
        self.__badge = badge
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)

        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(2)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("tutorial_item_titulo")
        label_titulo.setWordWrap(True)
        self.__label_titulo = label_titulo
        textos.addWidget(label_titulo)

        label_descricao = QLabel(descricao)
        label_descricao.setObjectName("tutorial_item_descricao")
        label_descricao.setWordWrap(True)
        self.__label_descricao = label_descricao
        textos.addWidget(label_descricao)

        layout.addLayout(textos, stretch=1)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica fontes e tamanhos do item apos mudanca de escala."""
        L = self.__layout
        familia = L.get("tutorial", "font_familia")
        tamanho = L.scaled("tutorial", "item_numerado", "badge_tamanho")
        self.__badge.setFixedSize(tamanho, tamanho)
        self.__badge.setFont(
            QFont(familia, L.scaled("tutorial", "item_numerado", "badge_font_size"))
        )
        self.__label_titulo.setFont(
            QFont(familia, L.scaled("tutorial", "item_numerado", "titulo_font_size"))
        )
        self.__label_descricao.setFont(
            QFont(
                familia, L.scaled("tutorial", "item_numerado", "descricao_font_size")
            )
        )
