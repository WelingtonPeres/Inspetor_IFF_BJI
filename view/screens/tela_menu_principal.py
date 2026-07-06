import logging
from pathlib import Path
from PySide6.QtCore import Qt, QSettings, Signal, Slot
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
        desktop.setObjectName("desktop_area")
        desktop_layout = QHBoxLayout(desktop)
        desktop_layout.setContentsMargins(*L.scaled_margins("tela", "margens", "desktop"))

        self.__build_shortcuts(desktop_layout)
        desktop_layout.addStretch()

        main_layout.addWidget(desktop)
        self.__load_wallpaper()

    def __load_wallpaper(self) -> None:
        """Carrega o wallpaper: QSettings primeiro, fallback para layout.json."""
        settings = QSettings()
        saved_path = settings.value("wallpaper/caminho_atual", "")

        if saved_path and Path(saved_path).exists():
            caminho = saved_path
        else:
            L = self.__layout
            caminho = str(
                Path(__file__).resolve().parent.parent.parent
                / L.get("wallpaper", "arquivo")
            )

        self.__carregar_wallpaper_especifico(caminho)

    def __carregar_wallpaper_especifico(self, caminho: str) -> None:
        """Carrega um wallpaper a partir do caminho absoluto."""
        path = Path(caminho)
        if not path.exists():
            logger.warning("Wallpaper nao encontrado: %s", caminho)
            return

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            logger.warning("Falha ao carregar wallpaper: %s", caminho)
            return

        if self.__wallpaper_label is None:
            self.__wallpaper_label = QLabel(self)
            self.__wallpaper_label.setObjectName("wallpaper_label")
            self.__wallpaper_label.setScaledContents(
                self.__layout.get("wallpaper", "scaled_contents")
            )

        self.__wallpaper_label.setPixmap(pixmap)
        self.__wallpaper_label.resize(self.size())
        self.__wallpaper_label.lower()

        logger.info("Wallpaper carregado: %s", path.name)

    @Slot()
    def __abrir_seletor_wallpaper(self) -> None:
        """Abre o dialogo de selecao de wallpaper."""
        from view.components.wallpaper_selector import WallpaperSelector

        dialog = WallpaperSelector(self)
        dialog.wallpaper_selecionado.connect(self.__aplicar_wallpaper)
        dialog.exec()

    @Slot(str)
    def __aplicar_wallpaper(self, caminho: str) -> None:
        """Aplica o wallpaper selecionado (QSettings ja foi salvo pelo dialogo)."""
        self.__carregar_wallpaper_especifico(caminho)

    def __build_shortcuts(self, parent_layout: QHBoxLayout):
        L = self.__layout
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        shortcuts_layout.setSpacing(L.scaled("desktop_shortcut", "spacing", "entre_atalhos"))

        for item in L.get("atalhos_lista"):
            shortcut = DesktopShortcut(
                legenda=item["legenda"],
                icone_arquivo=item.get("icone_arquivo", ""),
            )
            action = item.get("action")
            if action == "iniciar":
                shortcut.clicked.connect(self.iniciar_solicitado.emit)
            elif action == "wallpaper":
                shortcut.clicked.connect(self.__abrir_seletor_wallpaper)
            else:
                shortcut.clicked.connect(self.__on_shortcut_info)
            self.__shortcuts.append(shortcut)
            shortcuts_layout.addWidget(shortcut)

        parent_layout.addLayout(shortcuts_layout)

    @Slot(str)
    def __on_shortcut_info(self, legenda: str) -> None:
        logger.info("Shortcut info clicado: %s", legenda)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__wallpaper_label:
            self.__wallpaper_label.resize(self.size())
