import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.dtos.parecer_cipa import ParecerCIPA

logger = logging.getLogger(__name__)


class ParecerCIPAIndisponivelError(Exception):
    """Levantada quando nao ha pareceres disponiveis (nem mesmo DEFAULT)."""
    pass


class RepositorioDePareceresCIPA:
    """
    Carrega pareceres da CIPA a partir de JSON e fornece pareceres
    aleatorios por curso, com fallback automatico para DEFAULT.

    Carrega o ficheiro uma unica vez por instancia (cache lazy em memoria).
    Suporta injecao de path para testes deterministicos.
    """

    _REFERENCIA_PADRAO = "Conduta do Inspetor"
    _CURSO_FALLBACK = "DEFAULT"

    def __init__(self, caminho_ficheiro: Optional[Path] = None) -> None:
        if caminho_ficheiro is None:
            caminho_ficheiro = self.__caminho_padrao()
        self.__caminho = Path(caminho_ficheiro)
        self.__pareceres_por_curso: Optional[Dict[str, List[str]]] = None

    def obter_parecer_para_curso(self, curso: str) -> ParecerCIPA:
        """
        Devolve um parecer aleatorio para o curso, com fallback para DEFAULT.

        Args:
            curso: identificador do curso (ex: "T_QUIMICA", "T_INFORMATICA").
                   Se nao existir ou estiver vazio, usa "DEFAULT".

        Returns:
            ParecerCIPA com numero gerado, referencia fixa e texto aleatorio.

        Raises:
            ParecerCIPAIndisponivelError: se DEFAULT tambem nao tiver pareceres.
        """
        cursos = self.__carregar_pareceres()

        curso_resolvido = curso if curso in cursos else self._CURSO_FALLBACK
        if curso_resolvido not in cursos:
            raise ParecerCIPAIndisponivelError(
                f"[Erro - RepositorioDePareceresCIPA] Curso '{curso}' e fallback "
                f"'{self._CURSO_FALLBACK}' indisponiveis."
            )

        if curso_resolvido != curso:
            logger.debug(
                "Curso '%s' sem pareceres; usando fallback '%s'.",
                curso, curso_resolvido,
            )

        texto = random.choice(cursos[curso_resolvido])
        numero = self.__gerar_numero()
        return ParecerCIPA(
            numero=numero,
            referencia=self._REFERENCIA_PADRAO,
            texto=texto,
        )

    def cursos_disponiveis(self) -> List[str]:
        """Lista os cursos que possuem pelo menos um parecer."""
        return list(self.__carregar_pareceres().keys())

    def __carregar_pareceres(self) -> Dict[str, List[str]]:
        """Carrega o JSON uma unica vez (cache lazy)."""
        if self.__pareceres_por_curso is not None:
            return self.__pareceres_por_curso

        try:
            with open(self.__caminho, "r", encoding="utf-8") as fh:
                dados = json.load(fh)
        except FileNotFoundError:
            logger.warning(
                "[Erro - RepositorioDePareceresCIPA] Ficheiro '%s' nao encontrado; "
                "repositorio vazio.", self.__caminho,
            )
            self.__pareceres_por_curso = {}
            return self.__pareceres_por_curso
        except json.JSONDecodeError as exc:
            logger.warning(
                "[Erro - RepositorioDePareceresCIPA] JSON invalido em '%s': %s; "
                "repositorio vazio.", self.__caminho, exc,
            )
            self.__pareceres_por_curso = {}
            return self.__pareceres_por_curso

        if not isinstance(dados, dict):
            logger.warning(
                "[Erro - RepositorioDePareceresCIPA] Estrutura de '%s' invalida "
                "(esperado dict na raiz); repositorio vazio.", self.__caminho,
            )
            self.__pareceres_por_curso = {}
            return self.__pareceres_por_curso

        self.__pareceres_por_curso = dados
        logger.debug(
            "Pareceres CIPA carregados: %d cursos.", len(dados),
        )
        return self.__pareceres_por_curso

    def __gerar_numero(self) -> str:
        """Gera numero de parecer no formato NNN/AAAA."""
        return f"{random.randint(100, 999)}/{datetime.now().year}"

    @staticmethod
    def __caminho_padrao() -> Path:
        """Devolve o caminho default do JSON no projecto."""
        return (
            Path(__file__).resolve().parent.parent.parent
            / "view" / "assets" / "textos" / "pareceres_gameover.json"
        )
