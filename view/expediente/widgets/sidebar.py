import logging
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)

_ICONE_MAP = {
    "dashboard": "dashboard",
    "reports": "Reports",
    "logs": "Logs",
    "settings": "Settings",
}


def _resolver_assets() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "assets"


class Sidebar(QFrame):
    item_selecionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setProperty("class", "sidebar")

        L = LayoutLoader.instance()
        self.setFixedWidth(L.scaled("sidebar", "largura"))

        self.__botoes: Dict[str, QPushButton] = {}
        self.__ativo: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.__build_header())

        nav_items = [i for i in L.get("sidebar", "itens") if i["id"] != "settings"]
        for item in nav_items:
            btn = self.__criar_item(item)
            layout.addWidget(btn)
            self.__botoes[item["id"]] = btn

        layout.addStretch()

        divider = QFrame(objectName="sidebar_divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        settings_item = next((i for i in L.get("sidebar", "itens") if i["id"] == "settings"), None)
        if settings_item is not None:
            btn = self.__criar_item(settings_item)
            layout.addWidget(btn)
            self.__botoes[settings_item["id"]] = btn

        L.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __build_header(self) -> QFrame:
        header = QFrame(objectName="sidebar_header")
        inner = QHBoxLayout(header)
        inner.setContentsMargins(12, 12, 12, 12)
        inner.setSpacing(8)

        assets = _resolver_assets()
        logo_path = assets / "icons" / "iff_Icons" / "logo_iff_branco.png"
        logo_label = QLabel()
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(
                24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        inner.addWidget(logo_label)

        titulo = QLabel("IFF-BJI")
        titulo.setObjectName("sidebar_titulo")
        inner.addWidget(titulo)
        inner.addStretch()

        return header

    def __criar_item(self, item: dict) -> QPushButton:
        btn = QPushButton(item["label"])
        btn.setObjectName(f"sidebar_{item['id']}")
        btn.setProperty("class", "sidebar_item")
        btn.setFixedHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        icone_nome = _ICONE_MAP.get(item["id"], item["id"])
        assets = _resolver_assets()
        icone_path = assets / "icons" / "sidebar" / f"{icone_nome}.png"
        if icone_path.exists():
            btn.setIcon(QIcon(str(icone_path)))
            btn.setIconSize(QSize(20, 20))

        if item.get("inativo", False):
            btn.setEnabled(False)
        else:
            btn.clicked.connect(lambda _, i=item["id"]: self._on_item_clicked(i))

        return btn

    def _on_item_clicked(self, item_id: str) -> None:
        self.definir_ativo(item_id)
        self.item_selecionado.emit(item_id)

    def definir_ativo(self, item_id: str) -> None:
        for key, btn in self.__botoes.items():
            btn.setProperty("active", key == item_id)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.__ativo = item_id

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = LayoutLoader.instance()
        self.setFixedWidth(L.scaled("sidebar", "largura"))
