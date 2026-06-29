import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class VideoPlayer(QFrame):
    fullscreen_solicitado = Signal()
    sair_fullscreen_solicitado = Signal()

    def __init__(self, caminho: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("video_player")
        self.setProperty("class", "video_player")

        L = LayoutLoader.instance()
        self.__font_sz = L.scaled("video_player", "font_size")
        self.__controls_h = L.scaled("video_player", "controls_altura")

        self.__player = QMediaPlayer(self)
        self.__audio_output = QAudioOutput()
        self.__player.setAudioOutput(self.__audio_output)
        self.__video_widget = QVideoWidget()
        self.__video_widget.setObjectName("video_widget")
        self.__player.setVideoOutput(self.__video_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.__video_widget, stretch=1)

        self.__controls = QFrame()
        self.__controls.setObjectName("video_controls")
        self.__controls.setFixedHeight(self.__controls_h)
        controls_layout = QHBoxLayout(self.__controls)
        controls_layout.setContentsMargins(8, 0, 8, 0)

        self.__btn_play = QPushButton("▶")
        self.__btn_play.setObjectName("video_play_button")
        self.__btn_play.clicked.connect(self.__toggle_play)
        controls_layout.addWidget(self.__btn_play)

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.setObjectName("video_progress")
        self.__slider.sliderMoved.connect(self.__player.setPosition)
        controls_layout.addWidget(self.__slider, stretch=1)

        self.__label_tempo = QLabel("0:00 / 0:00")
        self.__label_tempo.setObjectName("video_tempo")
        self.__label_tempo.setFont(QFont("Open Sans", self.__font_sz))
        controls_layout.addWidget(self.__label_tempo)

        self.__btn_fullscreen = QPushButton("⛶")
        self.__btn_fullscreen.setObjectName("video_fullscreen_button")
        self.__btn_fullscreen.clicked.connect(self.__toggle_fullscreen)
        controls_layout.addWidget(self.__btn_fullscreen)

        layout.addWidget(self.__controls)

        self.__player.positionChanged.connect(self.__atualizar_progresso)
        self.__player.durationChanged.connect(self.__atualizar_duracao)
        self.__player.mediaStatusChanged.connect(self.__on_media_status)

        if caminho:
            self.carregar(caminho)

    def carregar(self, caminho: str) -> None:
        path = Path(caminho)
        if not path.exists():
            logger.warning("Video nao encontrado: %s", caminho)
            return
        self.__player.stop()
        self.__player.setSource(QUrl.fromLocalFile(str(path.absolute())))

    def __toggle_play(self) -> None:
        if self.__player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.__player.pause()
            self.__btn_play.setText("▶")
        else:
            self.__player.play()
            self.__btn_play.setText("⏸")

    def __toggle_fullscreen(self) -> None:
        if self.__btn_fullscreen.text() == "⛶":
            self.__btn_fullscreen.setText("─")
            self.__controls.hide()
            self.fullscreen_solicitado.emit()
        else:
            self.__btn_fullscreen.setText("⛶")
            self.__controls.show()
            self.sair_fullscreen_solicitado.emit()

    def entrar_fullscreen(self, container: QWidget) -> None:
        self.__video_widget.setParent(container)
        self.__video_widget.setGeometry(container.rect())
        self.__video_widget.show()
        self.__video_widget.raise_()

    def sair_fullscreen(self) -> None:
        self.__video_widget.setParent(self)
        self.__video_widget.show()
        self.__controls.show()
        self.__btn_fullscreen.setText("⛶")

    def __atualizar_progresso(self, pos: int) -> None:
        dur = self.__player.duration()
        if dur > 0:
            self.__slider.setValue(int(pos * 100 / dur))
            self.__label_tempo.setText(
                f"{self.__format_tempo(pos)} / {self.__format_tempo(dur)}"
            )

    def __atualizar_duracao(self, dur: int) -> None:
        self.__slider.setRange(0, dur)
        self.__label_tempo.setText(f"0:00 / {self.__format_tempo(dur)}")

    def __on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.__btn_play.setText("▶")
            self.__slider.setValue(0)

    def __format_tempo(self, ms: int) -> str:
        seg = ms // 1000
        m, s = divmod(seg, 60)
        return f"{m}:{s:02d}"

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.__btn_fullscreen.text() == "─":
            self.__toggle_fullscreen()
        super().keyPressEvent(event)
