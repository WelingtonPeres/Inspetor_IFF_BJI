from abc import ABC, abstractmethod
from typing import Any, Dict

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


class IGameView(ABC):
    """
    Contrato para a interface visual do jogo.
    Qualquer classe que quiser ser a View do MVP deve implementar
    todos os métodos abaixo.
    """

    @abstractmethod
    def inicializar(self) -> None:
        """Inicializa a janela principal da aplicação."""
        pass

    @abstractmethod
    def fechar(self) -> None:
        """Fecha a janela e encerra a aplicação."""
        pass

    @abstractmethod
    def exibir_menu(self) -> None:
        """Exibe a tela de menu principal."""
        pass

    @abstractmethod
    def exibir_selecao_perfil(self) -> None:
        """Exibe a tela de seleção de perfil (curso)."""
        pass

    @abstractmethod
    def trocar_para_tela_inspecao(self) -> None:
        """Troca para a tela de inspeção do relatório atual."""
        pass

    @abstractmethod
    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        """Exibe o diagnóstico (feedback) da resposta submetida."""
        pass

    @abstractmethod
    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        """Renderiza os dados do relatório atual na tela de inspeção."""
        pass

    @abstractmethod
    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int) -> None:
        """Exibe a tela de resultado final da campanha."""
        pass

    @abstractmethod
    def exibir_popup_erro(self, mensagem: str) -> None:
        """Exibe um popup com a mensagem de erro para o usuário."""
        pass
