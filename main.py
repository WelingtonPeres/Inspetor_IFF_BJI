import sys

from PySide6.QtWidgets import QApplication

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
 