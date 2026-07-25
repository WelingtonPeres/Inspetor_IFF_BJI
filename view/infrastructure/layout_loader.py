import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class LayoutLoader(QObject):
    """Singleton de layout responsivo.

    Herda de QObject para poder emitir ``escala_atualizada`` sempre que
    ``set_screen`` altera a resolucao corrente. Widgets que cacheiam
    ``scaled()`` no construtor subscrevem esse signal e re-aplicam as
    dimensoes, evitando geometria congelada apos um redimensionamento.
    """

    escala_atualizada = Signal()

    _instance: "LayoutLoader | None" = None

    @classmethod
    def instance(cls) -> "LayoutLoader":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        path = Path(__file__).resolve().parent.parent / "assets" / "layout.json"
        with open(path, encoding="utf-8") as f:
            self.__data: dict = json.load(f)
        ref = self.__data["meta"]["resolucao_base"].split("x")
        self.__ref_w = int(ref[0])
        self.__ref_h = int(ref[1])
        self.__screen_w = self.__ref_w
        self.__screen_h = self.__ref_h

    def set_screen(self, w: int, h: int) -> None:
        # So notifica se houve mudanca real; evita loops e trabalho inutil.
        if w == self.__screen_w and h == self.__screen_h:
            return
        self.__screen_w = w
        self.__screen_h = h
        self.escala_atualizada.emit()

    def _scale_factor(self) -> float:
        factor_w = self.__screen_w / self.__ref_w
        factor_h = self.__screen_h / self.__ref_h
        return min(factor_w, factor_h)

    def scale_factor(self) -> float:
        """API publica para o factor de escala actual.

        O factor e o minimo entre (largura/resolucao_base.w) e
        (altura/resolucao_base.h), garantindo que o layout nao
        deforma entre orientacoes.
        """
        return self._scale_factor()

    def _navigate(self, *keys: str) -> Any:
        current = self.__data
        for key in keys:
            current = current[key]
        return current

    def get(self, *keys: str) -> Any:
        return self._navigate(*keys)

    def scaled(self, *keys: str) -> int:
        value = self._navigate(*keys)
        if isinstance(value, (int, float)):
            return round(value * self._scale_factor())
        return value

    def scaled_margins(self, *keys: str) -> tuple:
        m = self._navigate(*keys)
        sf = self._scale_factor()
        return (
            round(m.get("left", 0) * sf),
            round(m.get("top", 0) * sf),
            round(m.get("right", 0) * sf),
            round(m.get("bottom", 0) * sf),
        )