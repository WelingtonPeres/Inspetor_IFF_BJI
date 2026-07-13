import logging
from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel

from view.widgets.midia.media_player_base import MediaPlayerBase

logger = logging.getLogger(__name__)


class AudioPlayer(MediaPlayerBase):
    def __init__(self, caminho: str = "", parent=None):
        self.__label_nome = QLabel("Áudio")
        self.__label_nome.setObjectName("audio_label")
        self.__label_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        super().__init__(self.__label_nome, caminho, parent)

        self.setObjectName("audio_player")
        self.setProperty("class", "audio_player")

        self.layout().setContentsMargins(8, 8, 8, 8)

        self._btn_play.setObjectName("audio_play_button")
        self._btn_play.setFixedSize(32, 32)
        self._slider.setObjectName("audio_progress")
        self._label_tempo.setObjectName("audio_tempo")

    @Slot()
    def _reaplicar_dimensoes(self) -> None:
        """Atualiza tambem a fonte do nome do arquivo de audio."""
        super()._reaplicar_dimensoes()
        self.__label_nome.setFont(QFont("Open Sans", self._font_sz))

    def carregar(self, caminho: str) -> None:
        """Carrega o audio e exibe o nome do arquivo no label."""
        super().carregar(caminho)
        if self._caminho_carregado:
            self.__label_nome.setText(Path(self._caminho_carregado).name)

    def _atualizar_progresso(self, pos: int) -> None:
        """Audio atualiza so o slider; o tempo total ja aparece no label."""
        dur = self._player.duration()
        if dur > 0:
            self._slider.setValue(pos)

    def _atualizar_duracao(self, dur: int) -> None:
        """Audio usa range minimo para nao deixar o slider travado."""
        self._slider.setRange(0, dur if dur > 0 else 100)
        self._label_tempo.setText(f"0:00 / {self.format_tempo(dur)}")
