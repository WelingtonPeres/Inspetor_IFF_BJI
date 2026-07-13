import logging
from pathlib import Path
from PySide6.QtCore import QSize, QTimer, QTime, Qt, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class Taskbar(QFrame):
    # QFrame: usado em vez de QWidget porque aceita setProperty("class")
    # + bordas via QSS de forma mais confiavel. QWidgets puros ignoram
    # border-radius e background-color em alguns padres do PySide6,
    # enquanto QFrame respeita corretamente.

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("taskbar")
        self.setProperty("class", "taskbar")
        self.__layout = LayoutLoader.instance()
        self.__main_layout = None
        self.__start_btn = None
        self.__clock_label = None
        self.__clock_fmt: str = ""
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
        start_btn = QPushButton()
        start_btn.setObjectName("taskbar_start")
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / "iff_Icons" / L.get("taskbar", "start_botao", "icone_arquivo")
        if icon_path.exists():
            start_btn.setIcon(QIcon(str(icon_path)))
            icon_h = L.scaled("taskbar", "altura") - 16
            start_btn.setIconSize(QSize(icon_h, icon_h))
        start_btn.setToolTip(L.get("taskbar", "start_botao", "texto"))
        self.__start_btn = start_btn
        layout.addWidget(start_btn)

        layout.addStretch()

        self.__clock_label = QLabel()
        self.__clock_label.setObjectName("taskbar_clock")
        self.__clock_label.setFont(QFont("Open Sans", font_size))
        layout.addWidget(self.__clock_label)

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        L = self.__layout
        self.setFixedHeight(L.scaled("taskbar", "altura"))
        if self.__main_layout is not None:
            self.__main_layout.setContentsMargins(*L.scaled_margins("taskbar", "margens"))
        if self.__start_btn is not None and not self.__start_btn.icon().isNull():
            icon_h = L.scaled("taskbar", "altura") - 16
            self.__start_btn.setIconSize(QSize(icon_h, icon_h))
        if self.__clock_label is not None:
            font_size = L.scaled("fontes", "ocorrencias", "taskbar_texto", "size")
            self.__clock_label.setFont(QFont("Open Sans", font_size))

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
