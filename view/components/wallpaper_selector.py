"""
Dialogo para selecao de wallpaper de fundo da Tela Principal.

Le as imagens disponiveis em view/assets/images/wallpapers/,
exibe pre-visualizacoes e persiste a escolha via QSettings.

Uso:
    dialog = WallpaperSelector(parent)
    dialog.wallpaper_selecionado.connect(minha_funcao)
    dialog.exec()
"""

import logging
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QSettings, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

DIRETORIO_WALLPAPERS = (
    Path(__file__).resolve().parent.parent
    / "assets" / "images" / "wallpapers"
)
EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
SETTINGS_GROUP = "wallpaper"
SETTINGS_KEY = "caminho_atual"
TAMANHO_THUMBNAIL = (160, 90)


class WallpaperSelector(QDialog):
    """
    Dialog modal que exibe uma grade com thumbnails de todos os wallpapers
    disponiveis no diretorio padrao.

    O utilizador clica numa thumbnail para pre-visualizar e confirma
    com "Aplicar". A escolha e persistida em QSettings e um signal
    e emitido com o caminho absoluto do ficheiro selecionado.
    """

    wallpaper_selecionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Papel de Parede")
        self.setObjectName("wallpaper_selector")
        self.setModal(True)
        self.setMinimumSize(640, 420)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.__imagens: List[Path] = []
        self.__selected_path: str = ""
        self.__selected_index: int = -1
        self.__btn_aplicar: QPushButton | None = None
        self.__preview_label: QLabel | None = None
        self.__grid: QGridLayout | None = None
        self.__thumb_w = TAMANHO_THUMBNAIL[0]
        self.__thumb_h = TAMANHO_THUMBNAIL[1]

        self.__setup_ui()
        self.__carregar_imagens()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label_instrucao = QLabel("Escolha um wallpaper para o ambiente de trabalho (disponível apenas no diretório fixo):")
        label_instrucao.setProperty("class", "wallpaper_selector_instrucao")
        label_instrucao.setObjectName("wallpaper_selector_instrucao")
        layout.addWidget(label_instrucao)

        scroll = QScrollArea()
        scroll.setObjectName("wallpaper_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setObjectName("wallpaper_grid_container")
        self.__grid = QGridLayout(container)
        self.__grid.setContentsMargins(0, 0, 0, 0)
        self.__grid.setSpacing(12)
        self.__grid.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(8)

        self.__preview_label = QLabel("Nenhum wallpaper selecionado")
        self.__preview_label.setObjectName("wallpaper_preview_label")
        self.__preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__preview_label.setFixedHeight(120)
        self.__preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.__preview_label.setProperty("class", "wallpaper_preview")
        preview_layout.addWidget(self.__preview_label, stretch=1)

        layout.addLayout(preview_layout)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()

        self.__btn_aplicar = QPushButton("Aplicar")
        self.__btn_aplicar.setObjectName("btn_wallpaper_aplicar")
        self.__btn_aplicar.setProperty("class", "btn_primario")
        self.__btn_aplicar.clicked.connect(self.__on_aplicar)
        self.__btn_aplicar.setEnabled(False)
        botoes_layout.addWidget(self.__btn_aplicar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_wallpaper_cancelar")
        btn_cancelar.setProperty("class", "btn_secundario")
        btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(btn_cancelar)

        layout.addLayout(botoes_layout)

    def __carregar_imagens(self) -> None:
        """Scan dinamico do diretorio de wallpapers por extensoes validas."""
        if not DIRETORIO_WALLPAPERS.exists():
            logger.warning(
                "Diretorio de wallpapers nao encontrado: %s",
                DIRETORIO_WALLPAPERS,
            )
            return

        imagens_encontradas: List[Path] = []
        for arquivo in sorted(DIRETORIO_WALLPAPERS.iterdir()):
            if arquivo.suffix.lower() in EXTENSOES_VALIDAS:
                imagens_encontradas.append(arquivo)

        if not imagens_encontradas:
            logger.info(
                "Nenhuma imagem encontrada em %s",
                DIRETORIO_WALLPAPERS,
            )
            return

        self.__imagens = imagens_encontradas
        self.__popular_grid()

        settings = QSettings()
        saved = settings.value(f"{SETTINGS_GROUP}/{SETTINGS_KEY}", "")
        if saved:
            for i, img_path in enumerate(self.__imagens):
                if str(img_path) == saved:
                    self.__selecionar_thumbnail(i)
                    break

    def __popular_grid(self) -> None:
        """Preenche a grid com thumbnails clicaveis."""
        self.__limpar_grid()

        cols = max(1, (self.width() - 32) // (self.__thumb_w + 24))

        for idx, img_path in enumerate(self.__imagens):
            thumbnail_widget = self.__criar_thumbnail(img_path, idx)
            row = idx // cols
            col = idx % cols
            self.__grid.addWidget(thumbnail_widget, row, col)

    def __limpar_grid(self) -> None:
        while self.__grid.count():
            item = self.__grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def __criar_thumbnail(self, img_path: Path, index: int) -> QFrame:
        """Cria um QFrame contendo a thumbnail e o nome do ficheiro."""
        frame = QFrame()
        frame.setObjectName(f"wallpaper_thumb_{index}")
        frame.setProperty("class", "wallpaper_thumbnail")
        frame.setFixedSize(self.__thumb_w + 16, self.__thumb_h + 40)
        frame.setFrameShape(QFrame.Shape.StyledPanel)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(4, 4, 4, 4)
        frame_layout.setSpacing(4)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        thumb_label = QLabel()
        thumb_label.setObjectName(f"thumb_img_{index}")
        thumb_label.setFixedSize(self.__thumb_w, self.__thumb_h)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setProperty("class", "wallpaper_thumb_imagem")

        pixmap = QPixmap(str(img_path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.__thumb_w,
                self.__thumb_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            thumb_label.setPixmap(scaled)
        else:
            thumb_label.setText("?")

        frame_layout.addWidget(thumb_label, alignment=Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(img_path.name)
        nome_label.setObjectName(f"thumb_nome_{index}")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nome_label.setWordWrap(True)
        nome_label.setProperty("class", "wallpaper_thumb_nome")
        frame_layout.addWidget(nome_label)

        frame.mousePressEvent = lambda _event, i=index: self.__selecionar_thumbnail(
            i
        )

        return frame

    def resizeEvent(self, event) -> None:
        """Reorganiza a grid quando a janela e redimensionada."""
        super().resizeEvent(event)
        if self.__imagens:
            self.__popular_grid()

    def __selecionar_thumbnail(self, index: int) -> None:
        """Marca a thumbnail como selecionada e atualiza o preview."""
        if index < 0 or index >= len(self.__imagens):
            return

        self.__selected_index = index
        selected_path = self.__imagens[index]
        self.__selected_path = str(selected_path)
        if self.__btn_aplicar:
            self.__btn_aplicar.setEnabled(True)

        if self.__preview_label:
            pixmap = QPixmap(self.__selected_path)
            if not pixmap.isNull():
                preview_pixmap = pixmap.scaled(
                    400,
                    120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.__preview_label.setPixmap(preview_pixmap)
                self.__preview_label.setText("")
            else:
                self.__preview_label.setText("Erro ao carregar imagem")

        for i in range(len(self.__imagens)):
            thumb_frame = self.findChild(QFrame, f"wallpaper_thumb_{i}")
            if thumb_frame:
                thumb_frame.setProperty("selected", i == index)
                thumb_frame.style().unpolish(thumb_frame)
                thumb_frame.style().polish(thumb_frame)

        logger.info("Wallpaper selecionado: %s", selected_path.name)

    @Slot()
    def __on_aplicar(self) -> None:
        """Persiste a escolha em QSettings e emite o signal."""
        if not self.__selected_path:
            return

        settings = QSettings()
        settings.setValue(
            f"{SETTINGS_GROUP}/{SETTINGS_KEY}", self.__selected_path
        )
        settings.sync()
        logger.info("Wallpaper salvo em QSettings: %s", self.__selected_path)

        self.wallpaper_selecionado.emit(self.__selected_path)
        self.accept()
