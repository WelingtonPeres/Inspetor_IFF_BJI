import json
from pathlib import Path
from typing import Any


class LayoutLoader:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if LayoutLoader._instance is not None:
            raise RuntimeError("Use LayoutLoader.instance()")
        path = Path(__file__).resolve().parent.parent / "assets" / "layout.json"
        with open(path, encoding="utf-8") as f:
            self.__data: dict = json.load(f)
        ref = self.__data["meta"]["resolucao_base"].split("x")
        self.__ref_w = int(ref[0])
        self.__ref_h = int(ref[1])
        self.__screen_w = self.__ref_w
        self.__screen_h = self.__ref_h

    def set_screen(self, w: int, h: int) -> None:
        self.__screen_w = w
        self.__screen_h = h

    def _scale_factor(self) -> float:
        return min(self.__screen_w / self.__ref_w, self.__screen_h / self.__ref_h)

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
