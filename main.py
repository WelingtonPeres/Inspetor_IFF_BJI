from config.logging_config import setup_logging
from application.controllers.game_manager import GameManager


def main():
    """
    Ponto de entrada da aplicação.
    Instancia o GameManager injetando a View principal (PySide6)
    e inicia o loop de eventos.
    """
    setup_logging()

    # TODO: instanciar a View principal (Janela, Wallpaper, QStackedWidget)
    #       view_principal = JanelaPrincipal()
    #       gm = GameManager(view_principal)
    #       gm.iniciar_aplicacao()
    #       view_principal.executar()
    pass


if __name__ == "__main__":
    main()
 