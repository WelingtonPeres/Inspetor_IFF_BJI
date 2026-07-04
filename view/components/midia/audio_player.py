import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class AudioPlayer(QFrame):
    def __init__(self, caminho: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("audio_player")
        self.setProperty("class", "audio_player")

        self.__player = QMediaPlayer(self)
        self.__audio_output = QAudioOutput(self)
        self.__player.setAudioOutput(self.__audio_output)

        L = LayoutLoader.instance()
        font_sz = L.scaled("video_player", "font_size")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.__label_nome = QLabel("Áudio")
        self.__label_nome.setObjectName("audio_label")
        self.__label_nome.setFont(QFont("Open Sans", font_sz))
        self.__label_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_nome)

        controls = QHBoxLayout()

        self.__btn_play = QPushButton("▶")
        self.__btn_play.setObjectName("audio_play_button")
        self.__btn_play.setFixedSize(32, 32)
        self.__btn_play.clicked.connect(self.__toggle_play)
        controls.addWidget(self.__btn_play)

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.setObjectName("audio_progress")
        self.__slider.sliderMoved.connect(self.__player.setPosition)
        controls.addWidget(self.__slider)

        self.__label_tempo = QLabel("0:00 / 0:00")
        self.__label_tempo.setObjectName("audio_tempo")
        self.__label_tempo.setFont(QFont("Open Sans", font_sz))
        controls.addWidget(self.__label_tempo)

        layout.addLayout(controls)

        self.__player.positionChanged.connect(self.__atualizar_progresso)
        self.__player.durationChanged.connect(self.__atualizar_duracao)
        self.__player.mediaStatusChanged.connect(self.__on_media_status)

        if caminho:
            self.carregar(caminho)

    def carregar(self, caminho: str) -> None:
        path = Path(caminho)
        if not path.exists():
            logger.warning("Audio nao encontrado: %s", caminho)
            return
        self.__player.stop()
        self.__player.setSource(QUrl.fromLocalFile(str(path.absolute())))
        self.__label_nome.setText(path.name)

    def __toggle_play(self) -> None:
        if self.__player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.__player.pause()
            self.__btn_play.setText("▶")
        else:
            self.__player.play()
            self.__btn_play.setText("⏸")

    def __atualizar_progresso(self, pos: int) -> None:
        dur = self.__player.duration()
        if dur > 0:
            self.__slider.setValue(pos)

    def __atualizar_duracao(self, dur: int) -> None:
        self.__slider.setRange(0, dur if dur > 0 else 100)
        self.__label_tempo.setText(f"0:00 / {self.__format_tempo(dur)}")

    def __on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.__btn_play.setText("▶")
            self.__slider.setValue(0)

    def format_tempo(self, ms: int) -> str:
        seg = ms // 1000
        m, s = divmod(seg, 60)
        return f"{m}:{s:02d}"
