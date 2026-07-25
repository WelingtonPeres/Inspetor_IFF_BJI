import logging
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
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

        self.__layout_loader = LayoutLoader.instance()
        self.setFixedWidth(self.__layout_loader.scaled("sidebar", "largura"))

        self.__botoes: Dict[str, QPushButton] = {}
        self.__ativo: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.__build_header())

        nav_items = [i for i in self.__layout_loader.get("sidebar", "itens") if i["id"] != "settings"]
        for item in nav_items:
            btn = self.__criar_item(item)
            layout.addWidget(btn)
            self.__botoes[item["id"]] = btn

        layout.addStretch()

        divider = QFrame(objectName="sidebar_divider")
        divider.setFixedHeight(self.__layout_loader.scaled("sidebar", "divider_altura"))
        layout.addWidget(divider)

        settings_item = next((i for i in self.__layout_loader.get("sidebar", "itens") if i["id"] == "settings"), None)
        if settings_item is not None:
            btn = self.__criar_item(settings_item)
            layout.addWidget(btn)
            self.__botoes[settings_item["id"]] = btn

        self.definir_ativo("reports")

        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __build_header(self) -> QFrame:
        L = self.__layout_loader
        header = QFrame(objectName="sidebar_header")
        inner = QVBoxLayout(header)
        inner.setContentsMargins(*L.scaled_margins("sidebar", "header_margens"))
        inner.setSpacing(L.scaled("sidebar", "item_altura") // 6)
        inner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        assets = _resolver_assets()
        logo_path = assets / "icons" / "iff_Icons" / "logo_iff_branco.png"
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_path.exists():
            logo_size = L.scaled("sidebar", "logo_tamanho")
            pixmap = QPixmap(str(logo_path)).scaled(
                logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        inner.addWidget(logo_label)

        titulo = QLabel("IFF-BJI · Inspetor")
        titulo.setObjectName("sidebar_titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__aplicar_fonte_titulo(titulo)
        inner.addWidget(titulo)

        return header

    def __criar_item(self, item: dict) -> QPushButton:
        L = self.__layout_loader
        btn = QPushButton(item["label"])
        btn.setObjectName(f"sidebar_{item['id']}")
        btn.setProperty("class", "sidebar_item")
        btn.setFixedHeight(L.scaled("sidebar", "item_altura"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.__aplicar_fonte_item(btn)
        self.__aplicar_padding_item(btn)

        icone_nome = _ICONE_MAP.get(item["id"], item["id"])
        assets = _resolver_assets()
        icone_normal = assets / "icons" / "sidebar" / f"{icone_nome}.png"
        icone_green = assets / "icons" / "sidebar" / f"{icone_nome}_green.png"

        icon_size = L.scaled("sidebar", "icone_tamanho")
        if icone_normal.exists():
            btn.setProperty("icone_normal", str(icone_normal))
            btn.setIcon(QIcon(str(icone_normal)))
            btn.setIconSize(QSize(icon_size, icon_size))
        if icone_green.exists():
            btn.setProperty("icone_green", str(icone_green))

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
            active = key == item_id
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

            icone_path = btn.property("icone_green") if active else btn.property("icone_normal")
            if icone_path:
                btn.setIcon(QIcon(icone_path))

        self.__ativo = item_id

    def __aplicar_fonte_item(self, btn: QPushButton) -> None:
        L = self.__layout_loader
        tamanho = L.scaled("sidebar", "item_font_size")
        fonte = btn.font()
        fonte.setPointSize(tamanho)
        btn.setFont(fonte)

    def __aplicar_padding_item(self, btn: QPushButton) -> None:
        L = self.__layout_loader
        pad = L.scaled_margins("sidebar", "item_padding")
        btn.setStyleSheet(
            f"padding: {pad[1]}px {pad[2]}px {pad[3]}px {pad[0]}px;"
        )

    def __aplicar_fonte_titulo(self, label: QLabel) -> None:
        L = self.__layout_loader
        tamanho = L.scaled("sidebar", "titulo_font_size")
        fonte = label.font()
        fonte.setPointSize(tamanho)
        label.setFont(fonte)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = self.__layout_loader
        self.setFixedWidth(L.scaled("sidebar", "largura"))
        item_altura = L.scaled("sidebar", "item_altura")
        icon_size = L.scaled("sidebar", "icone_tamanho")
        for btn in self.__botoes.values():
            btn.setFixedHeight(item_altura)
            btn.setIconSize(QSize(icon_size, icon_size))
            self.__aplicar_fonte_item(btn)
            self.__aplicar_padding_item(btn)
        header = self.findChild(QFrame, "sidebar_header")
        if header:
            self.__aplicar_fonte_titulo(
                header.findChild(QLabel, "sidebar_titulo")
            )
            logo_label = header.findChild(QLabel)
            if logo_label and logo_label.pixmap():
                logo_size = L.scaled("sidebar", "logo_tamanho")
                logo_path = _resolver_assets() / "icons" / "iff_Icons" / "logo_iff_branco.png"
                if logo_path.exists():
                    pixmap = QPixmap(str(logo_path)).scaled(
                        logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    logo_label.setPixmap(pixmap)
        divider = self.findChild(QFrame, "sidebar_divider")
        if divider:
            divider.setFixedHeight(L.scaled("sidebar", "divider_altura"))