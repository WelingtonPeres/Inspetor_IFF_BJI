import logging
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

from application.controllers.game_manager import GameManager
from config.constants import TEMA_PADRAO
from config.logging_config import setup_logging
from view.main_window import JanelaPrincipal


def _carregar_tema(app: QApplication) -> None:
    """
    Carrega o ficheiro QSS correspondente ao tema ativo.
    A seleção segue por ordem: variável de ambiente APP_THEME > TEMA_PADRAO.
    """
    tema = os.getenv("APP_THEME", TEMA_PADRAO).lower()

    nome_arquivo = "style_light.qss" if tema == "light" else "style.qss"
    qss_path = Path(__file__).resolve().parent / "view" / "assets" / nome_arquivo

    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Tema QSS '%s' carregado de: %s", tema, qss_path)
    else:
        logger.warning("Ficheiro QSS nao encontrado: %s", qss_path)


def main():
    """
    Ponto de entrada da aplicação.
    Cria a View (JanelaPrincipal), o GameManager, conecta os sinais
    e inicia o loop de eventos PySide6.
    """
    setup_logging()

    app = QApplication(sys.argv)

    _carregar_tema(app)

    janela = JanelaPrincipal()
    gm = GameManager(janela)

    janela.iniciar_solicitado.connect(gm.on_iniciar_solicitado)
    janela.perfil_confirmado.connect(gm.iniciar_expediente)
    janela.submeter_respostas.connect(gm.processar_submissao)
    janela.continuar_solicitado.connect(gm.avancar_fila_ou_dia)
    janela.voltar_menu_solicitado.connect(gm.carregar_menu_principal)
    janela.jogar_novamente_solicitado.connect(gm.reiniciar_expediente)
    janela.sair_solicitado.connect(gm.encerrar_aplicacao)

    # Redundancia defensiva: se o utilizador fechar a janela pela X do SO
    # em vez de usar o botao "Sair do Jogo", aboutToQuit garante que o
    # presenter ainda e notificado para libertar recursos.
    app.aboutToQuit.connect(gm.encerrar_aplicacao)

    gm.iniciar_aplicacao()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
 