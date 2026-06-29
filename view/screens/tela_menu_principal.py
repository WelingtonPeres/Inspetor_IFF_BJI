import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from view.infrastructure.layout_loader import LayoutLoader
from view.components.desktop_shortcut import DesktopShortcut

logger = logging.getLogger(__name__)


class TelaMenuPrincipal(QWidget):
    iniciar_solicitado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tela_menu_principal")
        self.__layout = LayoutLoader.instance()
        self.__shortcuts: list[DesktopShortcut] = []
        self.__wallpaper_label: QLabel | None = None
        self.__setup_ui()

    def __setup_ui(self):
        L = self.__layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        desktop = QWidget()
        desktop.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        desktop_layout = QHBoxLayout(desktop)
        desktop_layout.setContentsMargins(*L.scaled_margins("tela", "margens", "desktop"))

        self.__build_shortcuts(desktop_layout)
        desktop_layout.addStretch()

        main_layout.addWidget(desktop)
        self.__load_wallpaper()

    def __load_wallpaper(self):
        L = self.__layout
        wallpaper_path = (
            Path(__file__).resolve().parent.parent.parent
            / L.get("wallpaper", "arquivo")
        )
        if not wallpaper_path.exists():
            return

        pixmap = QPixmap(str(wallpaper_path))
        self.__wallpaper_label = QLabel(self)
        self.__wallpaper_label.setObjectName("wallpaper_label")
        self.__wallpaper_label.setPixmap(pixmap)
        self.__wallpaper_label.setScaledContents(L.get("wallpaper", "scaled_contents"))
        self.__wallpaper_label.lower()

    def __build_shortcuts(self, parent_layout: QHBoxLayout):
        L = self.__layout
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        shortcuts_layout.setSpacing(L.scaled("tela", "spacing", "atalhos_entre"))

        for item in L.get("atalhos_lista"):
            shortcut = DesktopShortcut(
                legenda=item["legenda"],
                icone_arquivo=item.get("icone_arquivo", ""),
            )
            if item.get("action") == "iniciar":
                shortcut.clicked.connect(
                    lambda _, a=item["legenda"]: self.iniciar_solicitado.emit(a)
                )
            else:
                shortcut.clicked.connect(self.__on_shortcut_info)
            self.__shortcuts.append(shortcut)
            shortcuts_layout.addWidget(shortcut)

        parent_layout.addLayout(shortcuts_layout)

    def __on_shortcut_info(self, legenda: str):
        logger.info("Shortcut info clicado: %s", legenda)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__wallpaper_label:
            self.__wallpaper_label.resize(self.size())
