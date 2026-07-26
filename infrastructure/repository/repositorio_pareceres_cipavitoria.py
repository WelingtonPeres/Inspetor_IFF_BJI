"""
Repositorio de pareceres de vitoria da CIPA.

Subclasses de ``RepositorioDePareceresCIPA`` que carrega textos de
aprovacao a partir de ``pareceres_gamewin.json``. Mantem o mesmo
contrato ``IPareceresCIPA`` e a mesma logica de fallback para DEFAULT.
"""

import logging
from pathlib import Path
from typing import Optional

from infrastructure.repository.repositorio_pareceres_cipa import (
    RepositorioDePareceresCIPA,
)

logger = logging.getLogger(__name__)


class RepositorioDePareceresCIPAVitoria(RepositorioDePareceresCIPA):
    """
    Repositorio de pareceres de vitoria da CIPA.

    Carrega textos de aprovacao a partir de ``pareceres_gamewin.json``.
    Herda toda a logica de fallback, cache e geracao de numero do pai.
    """

    _REFERENCIA_PADRAO = "Desempenho do Inspetor"

    def __init__(self, caminho_ficheiro: Optional[Path] = None) -> None:
        if caminho_ficheiro is None:
            caminho_ficheiro = self.__caminho_padrao()
        super().__init__(caminho_ficheiro)

    @staticmethod
    def __caminho_padrao() -> Path:
        """Devolve o caminho default do JSON de vitoria no projecto."""
        return (
            Path(__file__).resolve().parent.parent.parent
            / "view" / "assets" / "textos" / "pareceres_gamewin.json"
        )
