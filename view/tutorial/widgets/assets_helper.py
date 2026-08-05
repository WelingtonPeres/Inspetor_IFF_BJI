import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

logger = logging.getLogger(__name__)

RAIZ_ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"


def carregar_pixmap(*partes: str) -> QPixmap:
    """Carrega um pixmap relativo a ``view/assets/icons``, ou vazio se faltar."""
    caminho = RAIZ_ASSETS.joinpath("icons", *partes)
    if not caminho.exists():
        logger.warning("[Erro - Tutorial] Icone nao encontrado: %s", caminho)
        return QPixmap()
    return QPixmap(str(caminho))


def carregar_pixmap_escalado(
    largura: int, altura: int, *partes: str
) -> QPixmap:
    """Carrega e redimensiona um pixmap mantendo a proporcao.

    O resultado nunca excede ``largura`` x ``altura``; se a imagem for
    menor, mantem o tamanho original.
    """
    pixmap = carregar_pixmap(*partes)
    if pixmap.isNull():
        return pixmap
    return pixmap.scaled(
        largura,
        altura,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def tingir_pixmap(pixmap: QPixmap, cor: str) -> QPixmap:
    """Recolore um pixmap usando o seu alfa como mascara (padrao mask-image).

    Permite reusar os icones escuros em fundos coloridos, como o modelo
    faz com ``mask-image`` + ``background-color``.
    """
    if pixmap.isNull():
        return pixmap
    tingido = QPixmap(pixmap.size())
    tingido.fill(Qt.GlobalColor.transparent)
    painter = QPainter(tingido)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tingido.rect(), QColor(cor))
    painter.end()
    return tingido
