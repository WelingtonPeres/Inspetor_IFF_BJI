from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QTimer, QTime, Qt, Signal, Slot
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader


class _TaskbarShortcut(QFrame):
    clicked = Signal()

    def __init__(self, legenda: str, icone_arquivo: str, layout_loader: LayoutLoader, parent=None):
        super().__init__(parent)
        self.setObjectName("taskbar_shortcut")
        self.setProperty("class", "taskbar_shortcut")
        self.__legenda = legenda
        self.__icone_arquivo = icone_arquivo
        self.__layout = layout_loader
        self.__icon_label: Optional[QLabel] = None
        self.__setup_ui()

    def __setup_ui(self):
        L = self.__layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(0)
        m = L.get("taskbar", "atalhos", "shortcut_margens")
        layout.setContentsMargins(m["left"], m["top"], m["right"], m["bottom"])

        layout.addStretch()

        self.__icon_label = QLabel()
        self.__icon_label.setObjectName("taskbar_shortcut_icon")
        self.__icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__set_icon()
        layout.addWidget(self.__icon_label)

        layout.addStretch()

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(self.__legenda)

    def __set_icon(self):
        icon_w = self.__layout.scaled("taskbar", "atalhos", "icone", "largura")
        icon_h = self.__layout.scaled("taskbar", "atalhos", "icone", "altura")
        self.__icon_label.setFixedSize(icon_w, icon_h)

        base = Path(__file__).resolve().parent.parent / "assets" / "icons"
        for sub in [base / "desktop_Icons", base]:
            path = sub / self.__icone_arquivo
            if path.exists():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    self.__icon_label.setPixmap(pixmap.scaled(
                        icon_w, icon_h,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ))
                    return
        self.__icon_label.setText("?")

    @Slot()
    def reaplicar_dimensoes(self) -> None:
        L = self.__layout
        icon_w = L.scaled("taskbar", "atalhos", "icone", "largura")
        icon_h = L.scaled("taskbar", "atalhos", "icone", "altura")
        if self.__icon_label is not None:
            self.__icon_label.setFixedSize(icon_w, icon_h)
            self.__set_icon()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class Taskbar(QFrame):
    arquivos_solicitado = Signal()
    help_solicitado = Signal()
    wallpapers_solicitado = Signal()
    iniciar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("taskbar")
        self.setProperty("class", "taskbar")
        self.__layout = LayoutLoader.instance()
        self.__main_layout = None
        self.__start_label = None
        self.__clock_label = None
        self.__clock_fmt: str = ""
        self.__shortcuts_container: Optional[QWidget] = None
        self.__shortcuts: List[_TaskbarShortcut] = []
        self.__separator_green: Optional[QFrame] = None
        self.__separator_red: Optional[QFrame] = None
        self.__setup_ui()
        self.__start_clock()
        self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self):
        L = self.__layout
        self.setFixedHeight(L.scaled("taskbar", "altura"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("taskbar", "margens"))
        self.__main_layout = layout

        font_size = L.scaled("fontes", "ocorrencias", "taskbar_texto", "size")

        self.__build_start_widget(layout, L)
        self.__build_separator(layout, L)
        self.__build_center_panel(layout, L)
        self.__build_right_panel(layout, L, font_size)

    def __build_start_widget(self, layout: QHBoxLayout, L: LayoutLoader):
        start_widget = QWidget()
        start_widget.setObjectName("taskbar_start_widget")
        start_layout = QHBoxLayout(start_widget)
        m = L.get("taskbar", "start", "margens")
        start_layout.setContentsMargins(m["left"], m["top"], m["right"], m["bottom"])
        start_layout.setSpacing(L.scaled("taskbar", "start", "spacing"))

        self.__start_label = QLabel()
        self.__start_label.setObjectName("taskbar_start")
        self.__recarregar_icone_start()
        self.__start_label.setToolTip(L.get("taskbar", "start", "tooltip"))
        start_layout.addWidget(self.__start_label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(start_widget)

    def __recarregar_icone_start(self) -> None:
        L = self.__layout
        icon_size = L.scaled("taskbar", "start", "icone_tamanho")
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / "iff_Icons" / L.get("taskbar", "start", "icone_arquivo")
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    icon_size, icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.__start_label.setPixmap(scaled)
                self.__start_label.setFixedSize(scaled.size())

    def __build_separator(self, layout: QHBoxLayout, L: LayoutLoader):
        altura = L.scaled("taskbar", "altura")
        h = int(altura * 0.86)

        container = QWidget()
        container.setObjectName("taskbar_separator_container")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        green = QFrame()
        green.setObjectName("separator_green")
        green.setFrameShape(QFrame.Shape.VLine)
        green.setFrameShadow(QFrame.Shadow.Plain)
        green.setFixedWidth(2)
        green.setFixedHeight(h)
        row.addWidget(green)
        self.__separator_green = green

        red = QFrame()
        red.setObjectName("separator_red")
        red.setFrameShape(QFrame.Shape.VLine)
        red.setFrameShadow(QFrame.Shadow.Plain)
        red.setFixedWidth(2)
        red.setFixedHeight(h)
        row.addWidget(red)
        self.__separator_red = red

        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def __build_center_panel(self, layout: QHBoxLayout, L: LayoutLoader):
        center_panel = QWidget()
        center_panel.setObjectName("taskbar_center_panel")
        center_layout = QHBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)

        self.__build_shortcuts(center_layout, L)
        center_layout.addStretch()

        layout.addWidget(center_panel, 9)

    def __build_right_panel(self, layout: QHBoxLayout, L: LayoutLoader, font_size: int):
        right_panel = QWidget()
        right_panel.setObjectName("taskbar_right_panel")
        right_layout = QHBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addStretch()

        self.__clock_label = QLabel()
        self.__clock_label.setObjectName("taskbar_clock")
        self.__clock_label.setFont(QFont("Open Sans", font_size))
        right_layout.addWidget(self.__clock_label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(right_panel, 1)

    def __build_shortcuts(self, parent_layout: QHBoxLayout, L: LayoutLoader):
        shortcuts_widget = QWidget()
        shortcuts_widget.setObjectName("taskbar_shortcuts")
        shortcuts_layout = QHBoxLayout(shortcuts_widget)
        m = L.get("taskbar", "atalhos", "margens")
        shortcuts_layout.setContentsMargins(m["top"], m["right"], m["bottom"], m["left"])
        shortcuts_layout.setSpacing(L.scaled("taskbar", "atalhos", "spacing_entre_atalhos"))
        shortcuts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__shortcuts_container = shortcuts_widget

        signal_map = {
            "iniciar": self.iniciar_solicitado,
            "info_arquivos": self.arquivos_solicitado,
            "info_help": self.help_solicitado,
            "wallpaper": self.wallpapers_solicitado,
        }
        for item in L.get("atalhos_lista"):
            legenda = item["legenda"]
            shortcut = _TaskbarShortcut(
                legenda=legenda,
                icone_arquivo=item.get("icone_arquivo", ""),
                layout_loader=self.__layout,
            )
            signal = signal_map.get(item.get("action"))
            if signal is not None:
                shortcut.clicked.connect(signal.emit)
            self.__shortcuts.append(shortcut)
            shortcuts_layout.addWidget(shortcut, 0, Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(shortcuts_widget, 0, Qt.AlignmentFlag.AlignCenter)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        self.__reaplicar_altura_e_margens()
        if self.__start_label is not None:
            self.__recarregar_icone_start()
        self.__reaplicar_separadores()
        self.__reaplicar_shortcuts()

    def __reaplicar_altura_e_margens(self) -> None:
        L = self.__layout
        self.setFixedHeight(L.scaled("taskbar", "altura"))
        if self.__main_layout is not None:
            self.__main_layout.setContentsMargins(*L.scaled_margins("taskbar", "margens"))

    def __reaplicar_separadores(self) -> None:
        L = self.__layout
        altura = L.scaled("taskbar", "altura")
        h = int(altura * 0.86)
        if self.__separator_green is not None:
            self.__separator_green.setFixedHeight(h)
        if self.__separator_red is not None:
            self.__separator_red.setFixedHeight(h)

    def __reaplicar_shortcuts(self) -> None:
        L = self.__layout
        if self.__clock_label is not None:
            font_size = L.scaled("fontes", "ocorrencias", "taskbar_texto", "size")
            self.__clock_label.setFont(QFont("Open Sans", font_size))
        if self.__shortcuts_container is not None:
            shortcuts_layout = self.__shortcuts_container.layout()
            if shortcuts_layout is not None:
                shortcuts_layout.setSpacing(L.scaled("taskbar", "atalhos", "spacing_entre_atalhos"))
        for shortcut in self.__shortcuts:
            shortcut.reaplicar_dimensoes()

    def __start_clock(self):
        L = self.__layout
        self.__clock_fmt = L.get("taskbar", "system_tray", "relogio_formato")
        interval = int(L.get("taskbar", "system_tray", "atualizacao_segundos")) * 1000

        self.__atualizar_relogio()
        timer = QTimer(self)
        timer.timeout.connect(self.__atualizar_relogio)
        timer.start(interval)

    @Slot()
    def __atualizar_relogio(self) -> None:
        self.__clock_label.setText(QTime.currentTime().toString(self.__clock_fmt))
