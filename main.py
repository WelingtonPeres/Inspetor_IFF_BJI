import logging
import os
import re
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from application.controllers.game_manager import GameManager
from config.constants import TEMA_PADRAO
from config.logging_config import setup_logging
from view.main_window import JanelaPrincipal

logger = logging.getLogger(__name__)


def _resolver_urls_relativas(qss: str, base_dir: Path) -> str:
    """Converte urls relativas em absolutas dentro do QSS.

    URLs relativas em ``setStyleSheet()`` resolvem contra o CWD da
    aplicação, não contra a pasta do ficheiro .qss. Esta função
    substitui ``url(caminho)`` por ``url(caminho_absoluto)``.
    """
    def _absoluta(match: re.Match) -> str:
        url = match.group(1).strip("\"'")
        if url.startswith(("file://", "qrc://", "http://", "https://", "data:")):
            return match.group(0)
        resolvido = base_dir / url
        return f'url({resolvido.as_posix()})'

    return re.sub(r"url\(([^)]+)\)", _absoluta, qss)


def _carregar_tema(app: QApplication) -> None:
    """
    Carrega o ficheiro QSS correspondente ao tema ativo.
    A seleção segue por ordem: variável de ambiente APP_THEME > TEMA_PADRAO.
    """
    tema = os.getenv("APP_THEME", TEMA_PADRAO).lower()

    nome_arquivo = "style_light.qss" if tema == "light" else "style.qss"
    assets_dir = Path(__file__).resolve().parent / "view" / "assets"
    qss_path = assets_dir / nome_arquivo

    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            qss = _resolver_urls_relativas(f.read(), assets_dir)
            app.setStyleSheet(qss)
        logger.info("Tema QSS '%s' carregado de: %s", tema, qss_path)
    else:
        logger.warning("Ficheiro QSS nao encontrado: %s", qss_path)


def __conectar_sinais(app: QApplication, janela: JanelaPrincipal, gm: GameManager) -> None:
    """Conecta os sinais da View aos slots do GameManager."""
    janela.iniciar_solicitado.connect(gm.on_iniciar_solicitado)
    janela.perfil_confirmado.connect(gm.iniciar_expediente)
    janela.submeter_respostas.connect(gm.processar_submissao)
    janela.continuar_solicitado.connect(gm.avancar_fila_ou_dia)
    janela.voltar_menu_solicitado.connect(gm.carregar_menu_principal)
    janela.jogar_novamente_solicitado.connect(gm.reiniciar_expediente)
    janela.sair_solicitado.connect(gm.encerrar_aplicacao)
    janela.help_solicitado.connect(gm.on_help_solicitado)
    janela.tutorial_finalizado.connect(gm.on_tutorial_finalizado)

    # Redundancia defensiva: se o utilizador fechar a janela pela X do SO
    # em vez de usar o botao "Sair do Jogo", aboutToQuit garante que o
    # presenter ainda e notificado para libertar recursos. O GameManager
    # e idempotente, entao a dupla execucao e inofensiva.
    app.aboutToQuit.connect(gm.encerrar_aplicacao)


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

    __conectar_sinais(app, janela, gm)

    gm.iniciar_aplicacao()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
 