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
    filename: str
    fx: float
    fy: float
    angulo_graus: int
    tamanho_base: int
    cor: str


_RISCOS_BG: Tuple[PictogramaSpec, ...] = (
    PictogramaSpec("flame.png",       0.18, 0.18, -12, 120, "#ffb4ab"),
    PictogramaSpec("skull.png",       0.82, 0.22,  10, 100, "#e2e2e2"),
    PictogramaSpec("radioactive.png", 0.20, 0.70,   8, 130, "#71dd77"),
    PictogramaSpec("biohazard.png",   0.80, 0.75,  -6, 110, "#8dd2d8"),
    PictogramaSpec("droplet.png",     0.10, 0.45,  15,  95, "#e2e2e2"),
    PictogramaSpec("test-pipe.png",   0.90, 0.50, -15,  95, "#ffb4ab"),
)

_RISCOS_BG_GAMEWIN: Tuple[PictogramaSpec, ...] = (
    PictogramaSpec("star.png",           0.12, 0.15, -10, 100, "#71dd77"),
    PictogramaSpec("shield-check.png",   0.85, 0.20,  12, 110, "#8dd2d8"),
    PictogramaSpec("medal-2.png",        0.18, 0.72,   6, 120, "#f3d78a"),
    PictogramaSpec("leaf.png",           0.82, 0.78,  -8, 115, "#71dd77"),
    PictogramaSpec("clipboard-check.png",0.08, 0.42,  14, 100, "#eeeae2"),
    PictogramaSpec("square-check.png",   0.92, 0.50, -12, 100, "#8dd2d8"),
)

_SPEC_MAP = {
    "gameover": _RISCOS_BG,
    "gamewin": _RISCOS_BG_GAMEWIN,
}

_ICON_SUBDIR_MAP = {
    "gameover": "pictogramas",
    "gamewin": "",
}


class BackgroundRiscos(QWidget):
    """Fundo decorativo com pictogramas de risco em baixa opacidade."""

    _FLOOR_SCALE = 0.55
    _CEIL_SCALE = 1.0
    _OPACITY_MAX = 0.18

    def __init__(self, layout_loader: LayoutLoader, icons_dir: Path, parent=None, layout_key: str = "gameover"):
        super().__init__(parent)
        self.setObjectName("bg_riscos")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.__layout_loader = layout_loader
        self.__icons_dir = icons_dir
        self.__layout_key = layout_key
        self.__spec_list = _SPEC_MAP.get(layout_key, _RISCOS_BG)
        self.__icons_subdir = _ICON_SUBDIR_MAP.get(layout_key, "pictogramas")
        self.__raw_cache: Dict[str, QPixmap] = {}
        self.__carregar_raw_cache()
        self.__colored_cache: Dict[Tuple[str, int, str], QPixmap] = {}
        self.__atualizar_cache()

    def __carregar_raw_cache(self) -> None:
        for spec in self.__spec_list:
            if self.__icons_subdir:
                path = str(self.__icons_dir / self.__icons_subdir / spec.filename)
            else:
                path = str(self.__icons_dir / spec.filename)
            self.__raw_cache[spec.filename] = QPixmap(path)

    def __atualizar_cache(self) -> None:
        self.__colored_cache.clear()
        sf = self.__escala_clampada()
        size_max = self.__layout_loader.scaled(
            self.__layout_key, "pictogramas", "size_base_max"
        )
        size_min = self.__layout_loader.scaled(
            self.__layout_key, "pictogramas", "size_base_min"
        )
        for spec in self.__spec_list:
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
                self.__layout_key, "pictogramas", "opacity"
            )
            opacidade = min(self._OPACITY_MAX, opacidade_base / sf_clamped)

            size_max = self.__layout_loader.scaled(
                self.__layout_key, "pictogramas", "size_base_max"
            )
            size_min = self.__layout_loader.scaled(
                self.__layout_key, "pictogramas", "size_base_min"
            )

            for spec in self.__spec_list:
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
        result = QPixmap(source.size())
        result.fill(color)
        with QPainter(result) as p:
            p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            p.drawPixmap(0, 0, source)
        return result
