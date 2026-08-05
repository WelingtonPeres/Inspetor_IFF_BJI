import logging
from typing import List, Optional

from config.constants import DIRETORIO_BASE, QUANTIDADE_GERACAO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO
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
        """Guarda o perfil do jogador e inicializa o estado do turno."""

        self.__perfil_atual = perfil
        
        self.__pilha_relatorios: List[Relatorio] = []   
        self.__motor_pontuacao = MotorDePontuacao()
        self.__diagnostico_resposta = DiagnosticoDeResposta()
        
        self.__pontuacao_acumulada_turno = 0.0
        self.__v_max_turno = 0.0
        self.__turno_iniciado = False
        self.__relatorio_atual = None

    def iniciar_turno(self):
        """
        Inicia o Turno para preparar Relatorios e configuração Inicial
        """

        if self.__turno_iniciado:
            raise Exception("[Erro - Turno] Turno não pode ser iniciado mais de uma vez")

        self.__pontuacao_acumulada_turno = 0.0
        self.__v_max_turno = 0.0
        self.__relatorio_atual = None

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
        self.__turno_iniciado = True
        return True

    def qnt_relatorios(self):
        """Retorna quantos relatorios ainda restam na pilha."""

        if not self.__turno_iniciado:
            raise Exception("[Erro - Turno] Turno ainda não iniciado")

        return len(self.__pilha_relatorios)

    def obter_relatorio_da_pilha(self):
        """Remove e retorna o proximo relatorio da pilha (LIFO)."""

        if not self.__turno_iniciado:
            raise Exception("[Erro - Turno] Turno ainda não iniciado")
        if self.__relatorio_atual is not None:
            raise RuntimeError("[Erro - Turno] Relatório anterior ainda não foi avaliado")

        self.__relatorio_atual = self.__pilha_relatorios.pop()
        return self.__relatorio_atual

    def avaliar_respostas_jogador(self,
                                  riscos_marcados: List[str],
                                  fatores_marcados: List[str],
                                  decisao: str,
                                  tempo_segundos: int) -> ResultadoDiagnosticoDTO:
        """Calcula a pontuacao do relatorio respondido e acumula no turno."""

        if not self.__turno_iniciado:
            raise Exception("[Erro - Turno] Turno ainda não iniciado")
        if self.__relatorio_atual is None:
            raise RuntimeError("[Erro - Turno] Nenhum relatório foi obtido da pilha")

        folha_respostas = self.__processar_submissao_jogador(riscos_marcados, fatores_marcados, decisao, tempo_segundos)
        self.__relatorio_atual.anexar_resposta_jogador(folha_respostas)

        dados_pontuacao = self.__diagnostico_resposta.gerar_diagnostico_pontuacao(
            gabarito=self.__relatorio_atual.folha_gabarito,
            respostas=folha_respostas,
        )
        feedback = self.__diagnostico_resposta.gerar_feedback(
            gabarito=self.__relatorio_atual.folha_gabarito,
            respostas=folha_respostas,
        )

        v_max = self.__motor_pontuacao.calcular_vmax_relatorio(self.__relatorio_atual)
        score_por_risco, score_por_fator = self.__motor_pontuacao.calcular_scores_por_item(v_max, feedback)
        feedback = DiagnosticoFeedbackDTO(
            riscos_acertados=feedback.riscos_acertados,
            riscos_esquecidos=feedback.riscos_esquecidos,
            riscos_inventados=feedback.riscos_inventados,
            fatores_acertados=feedback.fatores_acertados,
            fatores_esquecidos=feedback.fatores_esquecidos,
            fatores_inventados=feedback.fatores_inventados,
            decisao_tomada=feedback.decisao_tomada,
            decisao_esperada=feedback.decisao_esperada,
            score_por_risco=score_por_risco,
            score_por_fator=score_por_fator,
        )

        pontuacao = self.__motor_pontuacao.calcular_pontuacao_detalhada(v_max, dados_pontuacao, feedback)

        self.__pontuacao_acumulada_turno += pontuacao.pontuacao_final
        self.__relatorio_atual = None

        return ResultadoDiagnosticoDTO(pontuacao=pontuacao, feedback=feedback)

    def __processar_submissao_jogador(self,
                                      riscos_marcados: List[str],
                                      fatores_marcados: List[str],
                                      decisao: str,
                                      tempo_segundos: int) -> FolhaDeResposta:
        """Cria e retorna a FolhaDeResposta com os dados do jogador."""

        return FolhaDeResposta(
            riscos=riscos_marcados,
            fatores_inseguranca=fatores_marcados,
            decisao_tomada=decisao,
            tempo_gasto_segundos=tempo_segundos,
        )

    def verificar_vitoria_do_turno(self) -> bool:
        """Retorna True se a pontuacao acumulada atingir o limiar de vitoria."""

        if not self.__turno_iniciado:
            raise Exception("[Erro - Turno] Turno ainda não iniciado")
        if self.__relatorio_atual is not None:
            raise RuntimeError("[Erro - Turno] Relatório pendente de avaliação")
        if len(self.__pilha_relatorios) != 0:
            raise ValueError("[Erro - Turno] Lista de Relatorios ainda tem elementos")

        return self.__motor_pontuacao.conferir_condicao_vitoria(self.__pontuacao_acumulada_turno, self.__v_max_turno)