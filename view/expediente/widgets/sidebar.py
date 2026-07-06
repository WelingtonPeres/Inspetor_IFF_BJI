import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class Sidebar(QFrame):
    item_selecionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setProperty("class", "sidebar")

        L = LayoutLoader.instance()
        self.setFixedWidth(L.scaled("sidebar", "largura"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for item in L.get("sidebar", "itens"):
            btn = QPushButton(item["label"])
            btn.setObjectName(f"sidebar_{item['id']}")
            btn.setProperty("class", "sidebar_item")
            btn.setFixedHeight(64)
            if item.get("inativo", False):
                btn.setEnabled(False)
            else:
                btn.clicked.connect(lambda _, i=item["id"]: self.item_selecionado.emit(i))
            layout.addWidget(btn)

        layout.addStretch()
