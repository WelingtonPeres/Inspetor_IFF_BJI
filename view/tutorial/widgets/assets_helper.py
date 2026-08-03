import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

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
