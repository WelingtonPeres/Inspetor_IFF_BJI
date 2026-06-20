import logging
from typing import List

from config.constants import DIRETORIO_BASE, QUANTIDADE_GERACAO
from core.model.relatorio import Relatorio
from core.model.folha_de_resposta import FolhaDeResposta
from core.services.motor_de_pontuacao import MotorDePontuacao
from core.services.diagnostico_de_resposta import DiagnosticoDeResposta
from infrastructure.factory.fabrica_de_relatorios import FabricaDeRelatorios
from infrastructure.repository.repositorio_json import RepositorioJSON

logger = logging.getLogger(__name__)


class GerenciadorDeTurno:
    """
    Controlador responsável por gerenciar o ciclo de vida de um Expediente (Turno).
    Mantém o estado da fila de relatórios, orquestra as validações de diagnóstico
    e acumula a pontuação através do Motor de Pontuação.
    """

    def __init__(self, perfil: str):

        self.__perfil_atual = perfil
        self.__pilha_relatorios: List[Relatorio] = []
        
        self.__pontuacao_acumulada_turno: float = 0.0
        self.__v_max_turno: float = 0.0 
        
        self.__motor_pontuacao = MotorDePontuacao()
        
    def iniciar_turno(self):
        """
        Inicia o Turno para preparar Relatorios e configuração Inicial
        """
        
        repositorio = RepositorioJSON(
            diretorio_base=DIRETORIO_BASE,
            curso_selecionado=self.__perfil_atual,
            quantidade_gerada=QUANTIDADE_GERACAO,
        )

        dados_dto = repositorio.extrair_dados()
        self.__pilha_relatorios = FabricaDeRelatorios.construir_pilha(dados_dto)

        if not self.__pilha_relatorios:
            raise RuntimeError(f"[Erro - Turno] Nenhum relatório foi construído para o curso '{self.__perfil_atual}'.")

        self.__v_max_turno = self.__motor_pontuacao.calcular_meta_turno(self.__pilha_relatorios)
        
        return True 

    def obter_dados_de_finalizacao_turno(self):
        pass

    def qnt_relatorios(self):
        return len(self.__pilha_relatorios)

    def obter_relatorio_da_pilha(self):
        return self.__pilha_relatorios.pop()

    def avaliar_respostas_jogador(self, relatorio_com_respostas: Relatorio) -> float:
        
        try:
            folha_respostas = relatorio_com_respostas.folha_resposta_jogador
        except ValueError:
            raise ValueError(
                "[Erro - Turno] O relatório não possui resposta anexada. "
                "Chame relatorio.anexar_resposta_jogador() antes de avaliar."
            )
        
        diagnostico_de_resposta = DiagnosticoDeResposta()
        
        dados_pontuacao = diagnostico_de_resposta.gerar_diagnostico_pontuacao(
            gabarito=relatorio_com_respostas.folha_gabarito,
            respostas=folha_respostas,
        )
        
        v_max = self.__motor_pontuacao.calcular_vmax_relatorio(relatorio_com_respostas)
        pontuacao_final = self.__motor_pontuacao.calcular_pontuacao_relatorio(v_max, dados_pontuacao)
        
        self.__pontuacao_acumulada_turno += pontuacao_final
        
        return pontuacao_final
    
    def verificar_vitoria_do_turno(self) -> bool:
        
        if len(self.__pilha_relatorios) != 0:
            raise ValueError("[Erro - Turno] Lista de Relatorios Ainda tem elementos")
        
        if self.__motor_pontuacao.conferir_condicao_vitoria(self.__pontuacao_acumulada_turno, self.__v_max_turno):
            return True
        
        return False