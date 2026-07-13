import logging
from pathlib import Path
from typing import List, Optional, Tuple

from PySide6.QtGui import QPixmap

from view.expediente.modelos.character_data import CharacterData

logger = logging.getLogger(__name__)

_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "cursos"


def _load_pixmap(filename: str) -> Optional[QPixmap]:
    path = _ASSETS_DIR / filename
    if path.is_file():
        return QPixmap(str(path))
    logger.debug("Imagem de perfil nao encontrada: %s", path)
    return None


IFF_PROFILES: Tuple[Tuple[str, str, str], ...] = (
    ("DEFAULT",         "Padr\u00E3o",            "DEFAULT.png"),
    ("T_QUIMICA",       "T. Qu\u00EDmica",        "T_QUIMICA.png"),
    ("T_INFORMATICA",   "T. Inform\u00E1tica",    "T_INFORMATICA.png"),
    ("T_AGROPECUARIA",  "T. Agropecu\u00E1ria",   "T_AGROPECUARIA.png"),
    ("T_ALIMENTOS",     "T. Alimentos",            "T_ALIMENTOS.png"),
    ("T_MEIO_AMBIENTE", "T. Meio Ambiente",        "T_MEIO_AMBIENTE.png"),
    ("T_ZOOTECNIA",     "T. Zootecnia",            "T_ZOOTECNIA.png"),
    ("CT_ALIMENTOS",    "CT. Alimentos",           "CT_ALIMENTOS.png"),
    ("E_COMPUTACAO",    "E. Computa\u00E7\u00E3o", "E_COMPUTACAO.png"),
)


def make_profile_roster() -> List[CharacterData]:
    """Constroi a lista de perfis a partir da tupla IFF_PROFILES."""
    return [
        CharacterData(cid, name, _load_pixmap(fn))
        for cid, name, fn in IFF_PROFILES
    ]
