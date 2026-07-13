import logging
from typing import Optional

from PySide6.QtCore import QEvent, Qt, Signal, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QPushButton, QWidget

from view.widgets.midia.media_player_base import MediaPlayerBase

logger = logging.getLogger(__name__)


class VideoPlayer(MediaPlayerBase):
    fullscreen_solicitado = Signal()
    sair_fullscreen_solicitado = Signal()

    def __init__(self, caminho: str = "", parent=None):
        self.__video_widget = QVideoWidget()
        self.__video_widget.setObjectName("video_widget")

        super().__init__(self.__video_widget, caminho, parent)

        self.setObjectName("video_player")
        self.setProperty("class", "video_player")

        self._player.setVideoOutput(self.__video_widget)

        self._controls.setObjectName("video_controls")
        self._btn_play.setObjectName("video_play_button")
        self._slider.setObjectName("video_progress")
        self._label_tempo.setObjectName("video_tempo")

        self.__fullscreen_container: Optional[QWidget] = None
        self.__em_fullscreen: bool = False
        self.__btn_fullscreen = QPushButton("⛶")
        self.__btn_fullscreen.setObjectName("video_fullscreen_button")
        self.__btn_fullscreen.clicked.connect(self.__toggle_fullscreen)
        self._controls.layout().addWidget(self.__btn_fullscreen)

    @Slot()
    def _reaplicar_dimensoes(self) -> None:
        """Video nao precisa de ajustes extras alem da base."""
        super()._reaplicar_dimensoes()

    def __toggle_fullscreen(self) -> None:
        if self.__em_fullscreen:
            self.__btn_fullscreen.setText("⛶")
            self._controls.show()
            self.sair_fullscreen_solicitado.emit()
            self.__em_fullscreen = False
            return
        self.__btn_fullscreen.setText("─")
        self._controls.hide()
        self.fullscreen_solicitado.emit()
        self.__em_fullscreen = True

    def entrar_fullscreen(self, container: QWidget) -> None:
        self.__fullscreen_container = container
        container.installEventFilter(self)
        self.__video_widget.setParent(container)
        self.__video_widget.setGeometry(container.rect())
        self.__video_widget.show()
        self.__video_widget.raise_()

    def sair_fullscreen(self) -> None:
        if self.__fullscreen_container:
            self.__fullscreen_container.removeEventFilter(self)
            self.__fullscreen_container = None
        self.__video_widget.setParent(self)
        self.__video_widget.show()
        self._controls.show()
        self.__btn_fullscreen.setText("⛶")
        self.__em_fullscreen = False

    def eventFilter(self, obj, event):
        if obj is self.__fullscreen_container and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape and self.__em_fullscreen:
                self.__toggle_fullscreen()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.__em_fullscreen:
            self.__toggle_fullscreen()
        super().keyPressEvent(event)
