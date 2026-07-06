import logging
from dataclasses import dataclass
from typing import Optional

from PySide6.QtGui import QPixmap, QColor

logger = logging.getLogger(__name__)


@dataclass
class CharacterData:
    """Dados de um perfil selecionavel no carousel."""
    char_id: str
    name: str
    pixmap: Optional[QPixmap] = None
    color: Optional[QColor] = None

    def __post_init__(self):
        if not self.char_id or not isinstance(self.char_id, str):
            raise ValueError(
                f"[Erro - CharacterData] char_id deve ser string nao-vazia. "
                f"Recebido: {self.char_id!r}"
            )
        if not self.name or not isinstance(self.name, str):
            raise ValueError(
                f"[Erro - CharacterData] name deve ser string nao-vazia. "
                f"Recebido: {self.name!r}"
            )
