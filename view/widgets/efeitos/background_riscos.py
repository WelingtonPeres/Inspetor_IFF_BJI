"""
Widget reutilizavel que desenha pictogramas decorativos de risco
no fundo de uma tela. Usado na TelaGameOver para reforcar a
identidade visual CRT + seguranca do trabalho.

Os pictogramas vem de ``view/assets/icons/fim_jogo/pictogramas/*.png``
e sao colorizados em runtime via ``CompositionMode_DestinationIn``
para que cada icone mantenha a silhueta original mas com a cor
configurada no ``layout.json`` em
``gameover.pictogramas.items[*].cor``.

Cache:
  * ``__raw_cache``: pixmaps originais carregados uma unica vez
    no ``__init__`` (evita I/O em cada repaint).
  * ``__colored_cache``: pixmaps ja escalados e coloridos, chaveados
    por ``(filename, target_size, cor_hex)``. Re-criado apenas em
    ``__atualizar_cache``, chamado quando a escala muda.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PictogramaSpec:
    """Especificacao declarativa de um pictograma decorativo."""
    filename: str
    fx: float          # posicao horizontal em fracao (0-1)
    fy: float          # posicao vertical em fracao (0-1)
    angulo_graus: int  # rotacao em graus
    tamanho_base: int  # tamanho de referencia a 1920x1080 (px)
    cor: str           # cor hex (#rrggbb) para tintar o pictograma


# Constante com os pictogramas usados no fundo do GameOver.
# Posicoes, rotacoes e cores sao calibradas para 1920x1080.
# Sao aproximadas via fracao, para escalarem com a janela.
_RISCOS_BG: Tuple[PictogramaSpec, ...] = (
    PictogramaSpec("flame.png",       0.18, 0.18, -12, 120, "#ffb4ab"),
    PictogramaSpec("skull.png",       0.82, 0.22,  10, 100, "#e2e2e2"),
    PictogramaSpec("radioactive.png", 0.20, 0.70,   8, 130, "#71dd77"),
    PictogramaSpec("biohazard.png",   0.80, 0.75,  -6, 110, "#8dd2d8"),
    PictogramaSpec("droplet.png",     0.10, 0.45,  15,  95, "#e2e2e2"),
    PictogramaSpec("test-pipe.png",   0.90, 0.50, -15,  95, "#ffb4ab"),
)


class BackgroundRiscos(QWidget):
    """Fundo decorativo com pictogramas de risco em baixa opacidade."""

    _ICONS_DIR_NAME = "pictogramas"
    _FLOOR_SCALE = 0.55
    _CEIL_SCALE = 1.0
    _OPACITY_MAX = 0.18

    def __init__(self, layout_loader: LayoutLoader, icons_dir: Path, parent=None):
        super().__init__(parent)
        self.setObjectName("bg_riscos")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.__layout_loader = layout_loader
        self.__icons_dir = icons_dir
        self.__raw_cache: Dict[str, QPixmap] = {
            spec.filename: QPixmap(str(icons_dir / self._ICONS_DIR_NAME / spec.filename))
            for spec in _RISCOS_BG
        }
        self.__colored_cache: Dict[Tuple[str, int, str], QPixmap] = {}
        self.__atualizar_cache()

    def __atualizar_cache(self) -> None:
        """Re-calcula os pixmaps coloridos+escalados segundo o scale factor corrente."""
        self.__colored_cache.clear()
        sf = self.__escala_clampada()
        size_max = self.__layout_loader.scaled(
            "gameover", "pictogramas", "size_base_max"
        )
        size_min = self.__layout_loader.scaled(
            "gameover", "pictogramas", "size_base_min"
        )
        for spec in _RISCOS_BG:
            raw = self.__raw_cache.get(spec.filename)
            if raw is None or raw.isNull():
                continue
            target = self.__tamanho_alvo(spec.tamanho_base, sf, size_min, size_max)
            scaled = raw.scaled(
                target, target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.__colored_cache[(spec.filename, target, spec.cor)] = self.__colorir(
                scaled, QColor(spec.cor)
            )

    def invalidar_cache(self) -> None:
        """Hook para re-aplicar cache apos escala_atualizada."""
        self.__atualizar_cache()
        self.update()

    def __escala_clampada(self) -> float:
        return max(
            self._FLOOR_SCALE,
            min(self._CEIL_SCALE, self.__layout_loader.scale_factor()),
        )

    @staticmethod
    def __tamanho_alvo(base: int, sf: float, size_min: int, size_max: int) -> int:
        return max(size_min, min(size_max, int(base * sf)))

    def paintEvent(self, _event):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            w, h = self.width(), self.height()

            sf_clamped = self.__escala_clampada()
            opacidade_base = self.__layout_loader.get(
                "gameover", "pictogramas", "opacity"
            )
            opacidade = min(self._OPACITY_MAX, opacidade_base / sf_clamped)

            size_max = self.__layout_loader.scaled(
                "gameover", "pictogramas", "size_base_max"
            )
            size_min = self.__layout_loader.scaled(
                "gameover", "pictogramas", "size_base_min"
            )

            for spec in _RISCOS_BG:
                raw = self.__raw_cache.get(spec.filename)
                if raw is None or raw.isNull():
                    continue
                target = self.__tamanho_alvo(
                    spec.tamanho_base, sf_clamped, size_min, size_max
                )
                colored = self.__colored_cache.get(
                    (spec.filename, target, spec.cor)
                )
                if colored is None:
                    continue

                cx = int(w * spec.fx)
                cy = int(h * spec.fy)
                painter.save()
                painter.setOpacity(opacidade)
                painter.translate(cx, cy)
                painter.rotate(spec.angulo_graus)
                painter.drawPixmap(
                    -colored.width() // 2, -colored.height() // 2, colored
                )
                painter.restore()

    @staticmethod
    def __colorir(source: QPixmap, color: QColor) -> QPixmap:
        """Substitui os pixels nao-transparentes pela cor alvo."""
        result = QPixmap(source.size())
        result.fill(color)
        with QPainter(result) as p:
            p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            p.drawPixmap(0, 0, source)
        return result
