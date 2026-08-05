import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class _ClickSeekSlider(QSlider):
    """Slider que salta para a posicao clicada no trilho."""

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            val = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), pos.x(), self.width()
            )
            self.setValue(val)
            self.sliderMoved.emit(val)
            event.accept()
            return
        super().mousePressEvent(event)


class MediaPlayerBase(QFrame):
    """Base comum para os players de video e audio.

    Centraliza o QMediaPlayer, o slider de progresso, o label de tempo e
    o botao play/pause. As subclasses fornecem o widget visual e ajustam
    os objectNames usados pelo QSS.
    """

    def __init__(self, visual_widget: QWidget, caminho: str = "", parent=None):
        super().__init__(parent)

        self._visual_widget = visual_widget

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        L = LayoutLoader.instance()
        self._font_sz = L.scaled("video_player", "font_size")
        self._controls_h = L.scaled("video_player", "controls_altura")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._visual_widget, stretch=1)

        self._controls = QFrame()
        self._controls.setFixedHeight(self._controls_h)
        controls_layout = QHBoxLayout(self._controls)
        controls_layout.setContentsMargins(8, 0, 8, 0)

        self._btn_play = QPushButton("▶")
        self._btn_play.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self._btn_play)

        self._slider = _ClickSeekSlider(Qt.Orientation.Horizontal)
        self._slider.sliderMoved.connect(self._player.setPosition)
        controls_layout.addWidget(self._slider, stretch=1)

        self._label_tempo = QLabel("0:00 / 0:00")
        self._label_tempo.setFont(QFont("Open Sans", self._font_sz))
        controls_layout.addWidget(self._label_tempo)

        self._layout.addWidget(self._controls)

        self._caminho_carregado: Optional[str] = None

        self._player.positionChanged.connect(self._atualizar_progresso)
        self._player.durationChanged.connect(self._atualizar_duracao)
        self._player.mediaStatusChanged.connect(self._on_media_status)

        L.escala_atualizada.connect(self._reaplicar_dimensoes)

        if caminho:
            self.carregar(caminho)

    @Slot()
    def _reaplicar_dimensoes(self) -> None:
        """Reaplica fonte e altura dos controles quando a escala muda."""
        L = LayoutLoader.instance()
        self._controls_h = L.scaled("video_player", "controls_altura")
        self._font_sz = L.scaled("video_player", "font_size")
        self._controls.setFixedHeight(self._controls_h)
        self._label_tempo.setFont(QFont("Open Sans", self._font_sz))

    def carregar(self, caminho: str) -> None:
        """Carrega o arquivo de midia no player.

        Caminhos inexistentes sao ignorados silenciosamente com um warning.
        """
        path = Path(caminho)
        if not path.exists():
            logger.warning("Media nao encontrada: %s", caminho)
            self._caminho_carregado = None
            return
        self._caminho_carregado = caminho
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(str(path.absolute())))

    def _toggle_play(self) -> None:
        """Alterna entre play e pause, atualizando o icone do botao."""
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._btn_play.setText("▶")
            return
        self._player.play()
        self._btn_play.setText("⏸")

    def _atualizar_progresso(self, pos: int) -> None:
        """Atualiza slider e label de tempo conforme a posicao atual."""
        dur = self._player.duration()
        if dur > 0:
            self._slider.setValue(pos)
            self._label_tempo.setText(
                f"{self.format_tempo(pos)} / {self.format_tempo(dur)}"
            )

    def _atualizar_duracao(self, dur: int) -> None:
        """Ajusta o range do slider e exibe a duracao total."""
        self._slider.setRange(0, dur)
        self._label_tempo.setText(f"0:00 / {self.format_tempo(dur)}")

    def _on_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        """Reseta o player quando a midia chega ao fim."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._btn_play.setText("▶")
            self._slider.setValue(0)

    def parar(self) -> None:
        """Para a reproducao e reseta o estado visual."""
        self._player.stop()
        self._btn_play.setText("▶")
        self._slider.setValue(0)

    def format_tempo(self, ms: int) -> str:
        """Formata milissegundos como m:ss."""
        seg = ms // 1000
        m, s = divmod(seg, 60)
        return f"{m}:{s:02d}"
