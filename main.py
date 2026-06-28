import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

from application.controllers.game_manager import GameManager
from config.logging_config import setup_logging
from view.main_window import JanelaPrincipal


def main():
    """
    Ponto de entrada da aplicação.
    Cria a View (JanelaPrincipal), o GameManager, conecta os sinais
    e inicia o loop de eventos PySide6.
    """
    setup_logging()

    app = QApplication(sys.argv)

    # Carrega o tema QSS global
    qss_path = Path(__file__).resolve().parent / "view" / "assets" / "style.qss"
    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Tema QSS carregado de: %s", qss_path)
    else:
        logger.warning("Ficheiro QSS nao encontrado: %s", qss_path)

    janela = JanelaPrincipal()
    gm = GameManager(janela)

    # Conecta sinais da View ao GameManager
    janela.iniciar_solicitado.connect(gm.on_iniciar_solicitado)
    janela.perfil_confirmado.connect(gm.iniciar_expediente)
    janela.submeter_respostas.connect(gm.processar_submissao)
    janela.continuar_solicitado.connect(gm.avancar_fila_ou_dia)

    # Encerra o GameManager quando a janela fechar
    app.aboutToQuit.connect(gm.encerrar_aplicacao)

    gm.iniciar_aplicacao()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
 