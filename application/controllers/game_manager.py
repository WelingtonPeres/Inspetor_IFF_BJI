import logging
from typing import Any, Dict, Optional

from application.controllers.gerenciador_de_turno import GerenciadorDeTurno

logger = logging.getLogger(__name__)


class GameManager:
    """
    State Machine global e Presenter principal (MVP).
    Orquestra a troca de telas, campanhas multi-dia,
    instancia/destrói GerenciadorDeTurno e faz a ponte
    entre a View e os controladores de domínio.
    """

    ESTADO_MENU = "ESTADO_MENU"
    ESTADO_EXPEDIENTE = "ESTADO_EXPEDIENTE"
    ESTADO_RESULTADO = "ESTADO_RESULTADO"

    def __init__(self, view):
        """
        Injeta a View (interface burra) e inicializa o estado da campanha.
        A View deve expor métodos como:
          - inicializar()
          - fechar()
          - exibir_menu()
          - trocar_para_tela_inspecao()
          - exibir_tela_diagnostico(resultado_dto)
          - renderizar_relatorio(dados_relatorio)
          - exibir_resultado(pontuacao_global, dias_concluidos)
          - exibir_popup_erro(mensagem)
        """

        self.__view = view # view vai vir aqui
        
        self.__estado_atual: str = self.ESTADO_MENU
        self.__gerenciador_turno = None
        
        self.__perfil_selecionado: str = ""
        self.__dias_concluidos: int = 0
        self.__pontuacao_global: float = 0.0


    def iniciar_aplicacao(self) -> None:
        """
        Ponto de entrada da aplicação.
        Instrui a View a inicializar a janela e carregar o menu principal.
        """
        # TODO: view.inicializar()
        self.carregar_menu_principal()

    def encerrar_aplicacao(self) -> None:
        """
        Instrui a View a fechar a janela e encerrar o processo.
        """
        # TODO: view.fechar()
        pass

    def carregar_menu_principal(self) -> None:
        """
        Destrói campanha/turno ativos e retorna ao estado de menu.
        """
        self.__gerenciador_turno = None
        self.__perfil_selecionado = ""
        self.__dias_concluidos = 0
        self.__pontuacao_global = 0.0
        self.__estado_atual = self.ESTADO_MENU
        # TODO: view.exibir_menu()

    def requisitar_dados_relatorio_atual(self) -> Dict[str, Any]:
        """
        Ponte MVP: retorna os dados de apresentação do relatório atual
        para a View renderizar a tela de inspeção.
        """
        if self.__gerenciador_turno is None:
            raise RuntimeError("[Erro - GameManager] Nenhum turno ativo.")

        # TODO: relatorio = self.__gerenciador_turno.obter_relatorio_da_pilha()
        #       return relatorio.extrair_apresentacao_relatorio()
        return {}

    def processar_submissao(self, respostas_jogador: Dict[str, Any]) -> None:
        """
        Ponte MVP: recebe as respostas do jogador, delega a avaliação
        e envia o diagnóstico (feedback) para a View.

        O fluxo PAUSA aqui — a View exibe a tela de diagnóstico.
        O avanço para o próximo relatório ou dia só acontece quando
        a View chamar ``avancar_fila_ou_dia()`` (botão "Continuar").

        Estrutura esperada do dict:
          - riscos: List[str]
          - fatores: List[str]
          - decisao: str
          - tempo_segundos: int
        """
        if self.__gerenciador_turno is None:
            raise RuntimeError("[Erro - GameManager] Nenhum turno ativo.")

        try:
            # TODO: resultado_dto = self.__gerenciador_turno.avaliar_respostas_jogador(
            #           riscos_marcados=respostas_jogador["riscos"],
            #           fatores_marcados=respostas_jogador["fatores"],
            #           decisao=respostas_jogador["decisao"],
            #           tempo_segundos=respostas_jogador["tempo_segundos"],
            #       )
            #       self.__pontuacao_global += resultado_dto.pontuacao_final
            #       self.__view.exibir_tela_diagnostico(resultado_dto)
            pass
        except ValueError as erro_negocio:
            self.__view.exibir_popup_erro(str(erro_negocio))
        except Exception as erro_sistema:
            logger.error(f"Falha ao processar submissao: {erro_sistema}")
            self.__view.exibir_popup_erro("Ocorreu um erro interno ao processar o relatorio.")

    def avancar_fila_ou_dia(self) -> None:
        """
        Invocado pela View quando o jogador clica em "Continuar"
        na Tela de Diagnóstico.

        Se o turno atual finalizou (pilha vazia), avança para o
        próximo dia ou encerra a campanha. Caso contrário, puxa
        o próximo relatório da pilha e volta para a tela de inspeção.
        """
        if self.__gerenciador_turno is None:
            raise RuntimeError("[Erro - GameManager] Nenhum turno ativo.")

        # TODO: if self.__gerenciador_turno.turno_finalizado():
        #           self.__dias_concluidos += 1
        #           if self.__dias_concluidos >= 3:
        #               self.__encerrar_campanha()
        #           else:
        #               self.__iniciar_dia(self.__dias_concluidos + 1)
        #       else:
        #           self.__view.trocar_para_tela_inspecao()
        #           self.__view.renderizar_relatorio(self.requisitar_dados_relatorio_atual())
        pass

    # ── Privados (orquestração interna) ────────────────────────────

    def __iniciar_campanha(self, perfil: str) -> None:
        """
        Inicia uma nova campanha para o perfil escolhido.
        Reseta contadores globais e parte para o primeiro dia.
        """
        if self.__estado_atual != self.ESTADO_MENU:
            raise RuntimeError("[Erro - GameManager] Campanha só pode ser iniciada pelo menu.")

        self.__perfil_selecionado = perfil
        self.__dias_concluidos = 0
        self.__pontuacao_global = 0.0
        self.__iniciar_dia(1)

    def __encerrar_campanha(self) -> None:
        """
        Finaliza a campanha e instrui a View a exibir a tela de resultados.
        """
        self.__estado_atual = self.ESTADO_RESULTADO
        # TODO: view.exibir_resultado(self.__pontuacao_global, self.__dias_concluidos)

    def __iniciar_dia(self, dia: int) -> None:
        """
        Cria um novo GerenciadorDeTurno para o dia especificado
        e prepara o expediente.
        """
        # TODO: self.__gerenciador_turno = GerenciadorDeTurno(self.__perfil_selecionado)
        #       self.__gerenciador_turno.iniciar_turno()
        #       self.__estado_atual = self.ESTADO_EXPEDIENTE
        #       view.trocar_para_tela_inspecao()
        pass
