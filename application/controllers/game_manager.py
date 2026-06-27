import logging
from typing import Any, Dict, Optional

from application.controllers.gerenciador_de_turno import GerenciadorDeTurno
from application.interfaces.i_game_view import IGameView
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO

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
    CAMPANHA_DURACAO_DIAS = 1

    def __init__(self, view: IGameView):
        """
        Injeta a View (deve implementar IGameView) e inicializa
        o estado da campanha.
        """

        self.__view = view

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
        self.__view.inicializar()
        self.carregar_menu_principal()

    def encerrar_aplicacao(self) -> None:
        """
        Instrui a View a fechar a janela e encerrar o processo.
        """
        self.__view.fechar()

    def carregar_menu_principal(self) -> None:
        """
        Destrói campanha/turno ativos e retorna ao estado de menu.
        """
        self.__gerenciador_turno = None
        self.__perfil_selecionado = ""
        self.__dias_concluidos = 0
        self.__pontuacao_global = 0.0
        self.__estado_atual = self.ESTADO_MENU
        self.__view.exibir_menu()

    def on_iniciar_solicitado(self) -> None:
        """
        Recebe o sinal ``btn_iniciar_clicado`` da ``ViewMenuInicial``.
        Instrui a View a exibir a tela de seleção de perfil.
        """
        self.__view.exibir_selecao_perfil()

    def iniciar_expediente(self, perfil: str) -> None:
        """
        Recebe o perfil escolhido via sinal ``perfil_confirmado(str)``
        da ``ViewSelecaoPerfil``. Valida o estado e delega para
        ``__iniciar_campanha()``.
        """
        if self.__estado_atual != self.ESTADO_MENU:
            raise RuntimeError("[Erro - GameManager] Expediente so pode ser iniciado pelo menu.")

        self.__iniciar_campanha(perfil)


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
            diagnostico_dto: DiagnosticoPontuacaoDTO = self.__gerenciador_turno.avaliar_respostas_jogador(
                riscos_marcados=respostas_jogador["riscos"],
                fatores_marcados=respostas_jogador["fatores"],
                decisao=respostas_jogador["decisao"],
                tempo_segundos=respostas_jogador["tempo_segundos"],
            )

            self.__pontuacao_global += diagnostico_dto.pontuacao_final
            self.__view.exibir_tela_diagnostico(diagnostico_dto)

        except ValueError as erro_negocio:
            self.__view.exibir_popup_erro(str(erro_negocio))
        except Exception as erro_sistema:
            logger.error(f"Falha ao processar submissao: {erro_sistema}")
            self.__view.exibir_popup_erro("Ocorreu um erro interno ao processar o relatorio.")

    def avancar_fila_ou_dia(self) -> None:
        """
        Invocado pela View quando o jogador clica em "Continuar"
        na Tela de Diagnóstico.

        Se o turno finalizou (pilha vazia), avança para o
        próximo dia ou encerra a campanha. Caso contrário, puxa
        o próximo relatório da pilha e volta para a tela de inspeção.
        """
        if self.__gerenciador_turno is None:
            raise RuntimeError("[Erro - GameManager] Nenhum turno ativo.")

        if self.__gerenciador_turno.qnt_relatorios() == 0:
            self.__dias_concluidos += 1
            if self.__dias_concluidos >= self.CAMPANHA_DURACAO_DIAS:
                self.__encerrar_campanha()
            else:
                self.__iniciar_dia(self.__dias_concluidos + 1)
        else:
            self.__view.trocar_para_tela_inspecao()
            dados = self.__requisitar_dados_relatorio_atual()
            self.__view.renderizar_relatorio(dados)
            
    def __requisitar_dados_relatorio_atual(self) -> Dict[str, Any]:
        """
        Ponte MVP: obtém o próximo relatório da pilha do turno e
        retorna os dados de apresentação para a View renderizar.

        Retorna um dicionário com as chaves:
          id_cenario, titulo, atividade, local, texto_descricao,
          envolvidos, anexos.
        """
        if self.__gerenciador_turno is None:
            raise RuntimeError("[Erro - GameManager] Nenhum turno ativo.")

        relatorio = self.__gerenciador_turno.obter_relatorio_da_pilha()
        return relatorio.extrair_apresentacao_relatorio()

    def __iniciar_campanha(self, perfil: str) -> None:
        """
        Inicia uma nova campanha para o perfil escolhido.
        Reseta contadores globais e parte para o primeiro dia.
        """
        if self.__estado_atual != self.ESTADO_MENU:
            raise RuntimeError("[Erro - GameManager] Campanha so pode ser iniciada pelo menu.")

        self.__perfil_selecionado = perfil
        self.__dias_concluidos = 0
        self.__pontuacao_global = 0.0
        self.__iniciar_dia(1)

    def __encerrar_campanha(self) -> None:
        """
        Finaliza a campanha e instrui a View a exibir a tela de resultados.
        """
        self.__estado_atual = self.ESTADO_RESULTADO
        self.__view.exibir_resultado(self.__pontuacao_global, self.__dias_concluidos)

    def __iniciar_dia(self, dia: int) -> None:
        """
        Cria um novo GerenciadorDeTurno para o dia especificado
        e prepara o expediente com o primeiro relatório já renderizado.
        """
        try:
            self.__gerenciador_turno = GerenciadorDeTurno(self.__perfil_selecionado)
            self.__gerenciador_turno.iniciar_turno()

            self.__estado_atual = self.ESTADO_EXPEDIENTE
            self.__view.trocar_para_tela_inspecao()

            dados = self.__requisitar_dados_relatorio_atual()
            self.__view.renderizar_relatorio(dados)

        except Exception as erro:
            logger.error(f"Erro ao carregar o dia {dia}: {erro}")
            self.__view.exibir_popup_erro(f"Falha ao carregar os dados do expediente: {erro}")
            self.carregar_menu_principal()
