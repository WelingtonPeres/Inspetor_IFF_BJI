from abc import ABC, abstractmethod
from typing import Any

from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO


class IGameView(ABC):
    @abstractmethod
    def inicializar(self) -> None:
        pass

    @abstractmethod
    def fechar(self) -> None:
        pass

    @abstractmethod
    def exibir_menu(self) -> None:
        pass

    @abstractmethod
    def exibir_selecao_perfil(self) -> None:
        pass

    @abstractmethod
    def trocar_para_tela_inspecao(self) -> None:
        pass

    @abstractmethod
    def renderizar_relatorio(self, dados_relatorio: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def exibir_tela_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
        pass

    @abstractmethod
    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        pass

    @abstractmethod
    def exibir_popup_erro(self, mensagem: str) -> None:
        pass
