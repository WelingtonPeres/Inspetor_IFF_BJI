"""
Contrato de porta para repositorios de pareceres da CIPA.

Define a abstracao que o dominio espera de qualquer implementacao
capaz de fornecer pareceres tecnicos da CIPA. Isola o dominio
(consumidores em ``view/`` e ``application/``) de detalhes de
infraestrutura (JSON, base de dados, API remota, etc.).

Este ficheiro segue o Principio de Inversao de Dependencia (DIP):
o dominio define o contrato; ``infrastructure/`` fornece a
implementacao concreta. Consumidores de camadas exteriores
devem depender apenas desta interface, nunca da classe
concreta ``RepositorioDePareceresCIPA``.
"""

from abc import ABC, abstractmethod

from core.dtos.parecer_cipa import ParecerCIPA


class IPareceresCIPA(ABC):
    """
    Porta de saida do dominio para obtencao de pareceres da CIPA.

    Qualquer implementacao concreta (e.g.
    ``infrastructure.repository.repositorio_pareceres_cipa.RepositorioDePareceresCIPA``)
    deve satisfazer este contrato. A implementacao e responsavel
    pela politica de fallback de curso (tipicamente ``"DEFAULT"``)
    e por sinalizar a indisponibilidade de pareceres via uma
    excecao especifica da camada de infraestrutura.
    """

    @abstractmethod
    def obter_parecer_para_curso(self, curso: str) -> ParecerCIPA:
        """
        Devolve um parecer da CIPA para o curso indicado.

        Contrato:
          * ``curso`` e o identificador do curso (ex: ``"T_QUIMICA"``,
            ``"T_INFORMATICA"``, ``"DEFAULT"``). Pode ser uma string
            vazia; nesse caso, a implementacao deve aplicar a sua
            politica de fallback.
          * A implementacao deve devolver um ``ParecerCIPA`` valido
            (campos ``numero``, ``referencia`` e ``texto`` preenchidos
            conforme o DTO). A logica de fallback (e.g. redirecionar
            para ``"DEFAULT"``) e responsabilidade da implementacao.

        Returns:
            ``ParecerCIPA`` com numero, referencia e texto do parecer.

        Raises:
            Exception: a implementacao concreta pode lancar uma
            excecao especifica quando nao existirem pareceres
            disponiveis (nem mesmo via fallback). Exemplo:
            ``ParecerCIPAIndisponivelError`` lancado por
            ``RepositorioDePareceresCIPA``. Consumidores que
            pretendam type-safety devem importar a excecao
            especifica da implementacao concreta.
        """
        pass
