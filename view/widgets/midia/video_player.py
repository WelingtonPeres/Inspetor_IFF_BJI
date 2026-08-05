import logging

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QPushButton

from view.widgets.midia.media_player_base import MediaPlayerBase

logger = logging.getLogger(__name__)


class VideoPlayer(MediaPlayerBase):

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

        self.__btn_fullscreen = QPushButton("⛶")
        self.__btn_fullscreen.setObjectName("video_fullscreen_button")
        self.__btn_fullscreen.setEnabled(False)
        self.__btn_fullscreen.setVisible(False)
        self._controls.layout().addWidget(self.__btn_fullscreen)
