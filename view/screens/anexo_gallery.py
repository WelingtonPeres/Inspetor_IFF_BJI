import logging
from typing import Dict, List
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from view.components.midia.audio_player import AudioPlayer
from view.components.midia.image_viewer import ImageViewer
from view.components.midia.video_player import VideoPlayer
logger = logging.getLogger(__name__)


class AnexoGallery(QFrame):
    fechar_solicitado = Signal()
    ampliar_solicitado = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("anexo_gallery")
        self.setProperty("class", "anexo_gallery")

        self.__anexos: List[Dict] = []
        self.__indice_atual: int = 0
        self.__players: List[QWidget] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.addStretch()
        btn_fechar = QPushButton("✕")
        btn_fechar.setObjectName("gallery_close_button")
        btn_fechar.clicked.connect(self.fechar_solicitado.emit)
        header.addWidget(btn_fechar)
        layout.addLayout(header)

        content = QHBoxLayout()
        content.setContentsMargins(48, 0, 48, 0)

        btn_ant = QPushButton("◀")
        btn_ant.setObjectName("gallery_prev_button")
        btn_ant.setFixedSize(48, 48)
        btn_ant.clicked.connect(self.__anterior)
        content.addWidget(btn_ant)

        self.__stack = QStackedWidget()
        self.__stack.setObjectName("gallery_stack")
        content.addWidget(self.__stack, stretch=1)

        btn_prox = QPushButton("▶")
        btn_prox.setObjectName("gallery_next_button")
        btn_prox.setFixedSize(48, 48)
        btn_prox.clicked.connect(self.__proximo)
        content.addWidget(btn_prox)

        layout.addLayout(content, stretch=1)

        self.__indicador = QLabel("0 / 0")
        self.__indicador.setObjectName("gallery_indicador")
        self.__indicador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__indicador)

    def carregar_anexos(self, anexos: List[Dict]) -> None:
        self.__anexos = anexos
        self.__indice_atual = 0
        self.__players.clear()

        while self.__stack.count() > 0:
            w = self.__stack.widget(0)
            self.__stack.removeWidget(w)
            w.deleteLater()

        for item in anexos:
            player = self.__criar_player(item)
            if player is not None:
                self.__players.append(player)
                self.__stack.addWidget(player)

        if self.__players:
            self.__stack.setCurrentIndex(0)
        self.__atualizar_indicador()

    def __criar_player(self, item: Dict) -> QWidget | None:
        tipo = item.get("tipo_midia", "")
        caminho = item.get("caminho_arquivo", "")
        if tipo == "IMAGEM":
            viewer = ImageViewer(caminho)
            viewer.ampliar_solicitado.connect(self.__ampliar_atual)
            return viewer
        elif tipo == "VIDEO":
            return VideoPlayer(caminho)
        elif tipo == "AUDIO":
            return AudioPlayer(caminho)
        logger.warning("Tipo de midia desconhecido: %s", tipo)
        return None

    @Slot()
    def __ampliar_atual(self) -> None:
        self.ampliar_solicitado.emit(self.__indice_atual)

    @Slot()
    def __anterior(self) -> None:
        if self.__indice_atual > 0:
            self.__indice_atual -= 1
            self.__stack.setCurrentIndex(self.__indice_atual)
            self.__atualizar_indicador()

    @Slot()
    def __proximo(self) -> None:
        if self.__indice_atual < len(self.__players) - 1:
            self.__indice_atual += 1
            self.__stack.setCurrentIndex(self.__indice_atual)
            self.__atualizar_indicador()

    def obter_player_atual(self):
        if 0 <= self.__indice_atual < len(self.__players):
            return self.__players[self.__indice_atual]
        return None

    def __atualizar_indicador(self) -> None:
        total = len(self.__players)
        if total > 0:
            self.__indicador.setText(f"{self.__indice_atual + 1} / {total}")
        else:
            self.__indicador.setText("0 / 0")
