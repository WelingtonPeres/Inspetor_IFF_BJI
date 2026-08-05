import logging
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap

logger = logging.getLogger(__name__)

_LIMIAR_BACKGROUND: int = 200
_LIMIAR_CROMATICO: int = 40
_PCT_MIN_HOMOGENEA: float = 0.85


def tint_pixmap(source: QPixmap, color: Union[QColor, str]) -> QPixmap:
    """Retorna copia do pixmap tintada na cor alvo.

    So aplica tintagem em imagens homogeneas (grayscale / silhueta).
    Imagens multicoloridas (ex: logos) sao devolvidas sem alteracao
    para evitar destruicao de cor.
    """
    if source.isNull():
        return QPixmap()

    if isinstance(color, str):
        color = QColor(color)

    img: QImage = source.toImage().convertToFormat(
        QImage.Format.Format_ARGB32_Premultiplied
    )

    if not _is_homogeneous(img):
        logger.info(
            "tint_pixmap: imagem rejeitada (multicolorida) — "
            "devolvendo copia original"
        )
        return QPixmap(source)

    has_alpha: bool = source.hasAlpha()
    tr, tg, tb = color.red(), color.green(), color.blue()

    for y in range(img.height()):
        for x in range(img.width()):
            pixel = img.pixelColor(x, y)
            a = pixel.alpha()

            if has_alpha:
                if a > 0:
                    img.setPixelColor(x, y, QColor(tr, tg, tb, a))
            else:
                lum = pixel.red()
                if lum < _LIMIAR_BACKGROUND:
                    img.setPixelColor(
                        x, y, QColor(tr, tg, tb, _LIMIAR_BACKGROUND - lum)
                    )
                else:
                    img.setPixelColor(x, y, QColor(0, 0, 0, 0))

    return QPixmap.fromImage(img)


def _is_homogeneous(img: QImage) -> bool:
    """Retorna True se a maioria dos pixels nao-transparentes for
    aproximadamente acromatica (R ≈ G ≈ B), indicando grayscale."""
    total = 0
    ok = 0
    for y in range(img.height()):
        for x in range(img.width()):
            pixel = img.pixelColor(x, y)
            if pixel.alpha() < 1:
                continue
            total += 1
            r, g, b = pixel.red(), pixel.green(), pixel.blue()
            if (
                abs(r - g) < _LIMIAR_CROMATICO
                and abs(g - b) < _LIMIAR_CROMATICO
                and abs(r - b) < _LIMIAR_CROMATICO
            ):
                ok += 1
    if total == 0:
        return False
    return (ok / total) >= _PCT_MIN_HOMOGENEA
