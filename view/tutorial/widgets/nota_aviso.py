from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from view.infrastructure.layout_loader import LayoutLoader


class NotaAviso(QFrame):
    """Caixa de aviso dos slides (modelo: .aviso com icone e borda).

    O icone e um glifo unicode pintado pela cor do QSS: verde por
    padrao, vermelho quando ``erro=True`` (property ``cor="erro"``).
    """

    def __init__(
        self,
        texto: str,
        icone: str = "◷",
        erro: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("tutorial_aviso")
        self.setProperty("class", "tutorial_aviso")
        self.__setup_ui(texto, icone, erro)

    def __setup_ui(self, texto: str, icone: str, erro: bool) -> None:
        L = LayoutLoader.instance()
        familia = L.get("tutorial", "font_familia")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("tutorial", "aviso", "margens"))
        layout.setSpacing(L.scaled("tutorial", "aviso", "spacing"))

        # U+FE0E forca a apresentacao em texto (monocromatica) dos
        # glifos com variante emoji, para a cor vir do QSS.
        label_icone = QLabel(icone + "︎")
        label_icone.setObjectName("tutorial_aviso_icone")
        if erro:
            label_icone.setProperty("cor", "erro")
        label_icone.setFont(
            QFont(familia, L.scaled("tutorial", "aviso", "icone_font_size"))
        )
        layout.addWidget(label_icone, 0, Qt.AlignmentFlag.AlignVCenter)

        label_texto = QLabel(texto)
        label_texto.setObjectName("tutorial_aviso_texto")
        label_texto.setWordWrap(True)
        label_texto.setFont(
            QFont(familia, L.scaled("tutorial", "aviso", "texto_font_size"))
        )
        layout.addWidget(label_texto, 1)
