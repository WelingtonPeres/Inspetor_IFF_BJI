"""
Suite de testes para o widget GameWin.

Testes de estrutura, sinais, pontuacao, parecer, efeitos visuais
e integracao com repositorio. Segue o padrão de test_game_over.py.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QFrame, QScrollArea

from view.expediente.paginas.game_win import GameWin
from view.widgets.efeitos.crt_overlay import CrtEffectsOverlay
from view.widgets.efeitos.confetti_overlay import ConfettiOverlay
from view.widgets.efeitos.background_riscos import BackgroundRiscos


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def game_win():
    """Retorna uma GameWin com pontuacao 5000.0."""
    return GameWin(pontuacao_global=5000.0)


@pytest.fixture
def game_win_com_repo():
    """Retorna uma GameWin com repositorio mockado."""
    repo = MagicMock()
    repo.obter_parecer_para_curso.return_value = MagicMock(
        numero="001/2026",
        referencia="Desempenho do Inspetor",
        texto="Texto de teste de vitoria.",
    )
    return GameWin(pontuacao_global=5000.0, repositorio=repo)


class TestEstrutura:
    """
    Testes de estrutura basica da GameWin.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, game_win):
        """A GameWin deve ter objectName 'game_win'."""
        assert game_win.objectName() == "game_win"

    def test_titulo_existe(self, game_win):
        """A GameWin deve conter um QLabel 'gamewin_titulo' com texto de vitoria."""
        titulo = game_win.findChild(QLabel, "gamewin_titulo")
        assert titulo is not None
        assert titulo.text() == "CASO ENCERRADO"

    def test_subtitulo_existe(self, game_win):
        """A GameWin deve conter um QLabel 'gamewin_subtitulo'."""
        sub = game_win.findChild(QLabel, "gamewin_subtitulo")
        assert sub is not None
        assert "Credencial de inspetor mantida" in sub.text()

    def test_header_existe(self, game_win):
        """A GameWin deve conter um QLabel 'gamewin_header'."""
        header = game_win.findChild(QLabel, "gamewin_header")
        assert header is not None
        assert "IFF-BJI" in header.text()

    def test_timestamp_existe(self, game_win):
        """A GameWin deve conter um QLabel 'gamewin_timestamp'."""
        ts = game_win.findChild(QLabel, "gamewin_timestamp")
        assert ts is not None

    def test_card_existe(self, game_win):
        """A GameWin deve conter um QFrame 'gamewin_card'."""
        card = game_win.findChild(QFrame, "gamewin_card")
        assert card is not None

    def test_card_cabecalho_existe(self, game_win):
        """O card deve conter cabecalho 'gamewin_card_cabecalho'."""
        cab = game_win.findChild(QLabel, "gamewin_card_cabecalho")
        assert cab is not None
        assert "IFF Fluminense" in cab.text()

    def test_card_subcabecalho_existe(self, game_win):
        """O card deve conter subcabecalho 'gamewin_card_subcabecalho'."""
        sub = game_win.findChild(QLabel, "gamewin_card_subcabecalho")
        assert sub is not None
        assert "CIPA" in sub.text()

    def test_card_parecer_num_existe(self, game_win):
        """O card deve conter label 'gamewin_card_parecer_num'."""
        num = game_win.findChild(QLabel, "gamewin_card_parecer_num")
        assert num is not None

    def test_card_parecer_texto_existe(self, game_win):
        """O card deve conter label 'gamewin_card_parecer_texto'."""
        txt = game_win.findChild(QLabel, "gamewin_card_parecer_texto")
        assert txt is not None

    def test_score_label_existe(self, game_win):
        """A GameWin deve conter 'gamewin_score_label'."""
        lbl = game_win.findChild(QLabel, "gamewin_score_label")
        assert lbl is not None
        assert "PONTUA" in lbl.text()

    def test_score_valor_existe(self, game_win):
        """A GameWin deve conter 'gamewin_score_valor' com a pontuacao."""
        val = game_win.findChild(QLabel, "gamewin_score_valor")
        assert val is not None
        assert "5000" in val.text()

    def test_btn_jogar_novamente_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'gamewin_btn_retry'."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_retry")
        assert btn is not None
        assert btn.text() == "Jogar novamente"

    def test_btn_voltar_menu_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'gamewin_btn_menu'."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_menu")
        assert btn is not None
        assert btn.text() == "Menu principal"

    def test_btn_sair_jogo_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'gamewin_btn_quit'."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_quit")
        assert btn is not None
        assert btn.text() == "Sair do Jogo"

class TestPontuacao:
    """
    Testes de actualizacao de pontuacao da GameWin.
    """

    def test_atualizar_pontuacao(self, game_win):
        """atualizar_pontuacao deve actualizar o label de pontuacao."""
        game_win.atualizar_pontuacao(3000.0)
        val = game_win.findChild(QLabel, "gamewin_score_valor")
        assert "3000" in val.text()

    def test_atualizar_pontuacao_inteiro(self, game_win):
        """atualizar_pontuacao deve formatar como inteiro."""
        game_win.atualizar_pontuacao(1500.5)
        val = game_win.findChild(QLabel, "gamewin_score_valor")
        assert "1500" in val.text()


class TestParecer:
    """
    Testes de definicao de parecer da GameWin.
    """

    def test_definir_parecer_preenche_card(self, game_win_com_repo):
        """definir_parecer deve preencher texto e numero do parecer."""
        gw = game_win_com_repo
        gw.definir_parecer("T_QUIMICA")
        txt = gw.findChild(QLabel, "gamewin_card_parecer_texto")
        num = gw.findChild(QLabel, "gamewin_card_parecer_num")
        assert "Texto de teste de vitoria" in txt.text()
        assert "001/2026" in num.text()

    def test_definir_parecer_fallback(self, game_win_com_repo):
        """definir_parecer com curso inexistente deve usar fallback do repo."""
        gw = game_win_com_repo
        gw.definir_parecer("CURSO_INEXISTENTE")
        txt = gw.findChild(QLabel, "gamewin_card_parecer_texto")
        assert "Texto de teste de vitoria" in txt.text()


class TestSignals:
    """
    Testes dos sinais da GameWin.
    """

    def test_voltar_menu_signal(self, game_win, qtbot):
        """Clicar em menu principal deve emitir voltar_menu_solicitado."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_menu")
        with qtbot.waitSignal(game_win.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_jogar_novamente_signal(self, game_win, qtbot):
        """Clicar em jogar novamente deve emitir jogar_novamente_solicitado."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_retry")
        with qtbot.waitSignal(game_win.jogar_novamente_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)


class TestSignalSairSolicitado:
    """
    Testes especificos para o sinal sair_solicitado.
    """

    def test_sair_solicitado_existe(self, game_win):
        """A GameWin deve ter o sinal sair_solicitado."""
        assert hasattr(game_win, "sair_solicitado")

    def test_sair_solicitado_emite_no_botao(self, game_win, qtbot):
        """Clicar em sair do jogo deve emitir sair_solicitado."""
        btn = game_win.findChild(QPushButton, "gamewin_btn_quit")
        with qtbot.waitSignal(game_win.sair_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_sair_solicitado_nao_chama_quit(self, game_win):
        """sair_solicitado NAO deve chamar QApplication.quit directamente."""
        from PySide6.QtWidgets import QApplication
        with patch.object(QApplication, "quit") as mock_quit:
            game_win.sair_solicitado.emit()
            mock_quit.assert_not_called()


class TestDimensoesCard:
    """
    Testes de dimensoes e scaling do card de parecer.
    """

    def test_card_tem_altura_minima(self, game_win):
        """O card deve ter uma altura minima definida."""
        card = game_win.findChild(QFrame, "gamewin_card")
        assert card.minimumHeight() > 0

    def test_card_tem_largura_max(self, game_win):
        """O card deve ter largura limitada."""
        card = game_win.findChild(QFrame, "gamewin_card")
        assert card.maximumWidth() > 0

    def test_scroll_area_existe(self, game_win):
        """O card deve conter uma QScrollArea para o parecer."""
        scroll = game_win.findChild(QScrollArea)
        assert scroll is not None

    def test_parecer_texto_max_height(self, game_win):
        """O label de parecer deve ter altura maxima limitada."""
        txt = game_win.findChild(QLabel, "gamewin_card_parecer_texto")
        assert txt.maximumHeight() > 0


class TestIntegracaoRepositorio:
    """
    Testes de integracao com o repositorio de pareceres.
    """

    def test_repositorio_default(self, game_win):
        """GameWin sem repo deve usar RepositorioDePareceresCIPAVitoria."""
        from infrastructure.repository.repositorio_pareceres_cipavitoria import (
            RepositorioDePareceresCIPAVitoria,
        )
        repo = game_win._GameWin__repositorio
        assert isinstance(repo, RepositorioDePareceresCIPAVitoria)

    def test_repositorio_injecao(self, game_win_com_repo):
        """GameWin com repo injectado deve usa-lo."""
        repo = game_win_com_repo._GameWin__repositorio
        assert repo is not None
        assert hasattr(repo, "obter_parecer_para_curso")

    def test_parecer_indisponivel(self):
        """Repo sem pareceres deve mostrar mensagem de fallback."""
        repo = MagicMock()
        from infrastructure.repository.repositorio_pareceres_cipa import (
            ParecerCIPAIndisponivelError,
        )
        repo.obter_parecer_para_curso.side_effect = ParecerCIPAIndisponivelError("teste")
        gw = GameWin(pontuacao_global=100.0, repositorio=repo)
        gw.definir_parecer("T_QUIMICA")
        txt = gw.findChild(QLabel, "gamewin_card_parecer_texto")
        assert "indisponivel" in txt.text().lower()


class TestIntegracaoCrtOverlay:
    """
    Testes de integracao com o CrtEffectsOverlay.
    """

    def test_crt_overlay_existe(self, game_win):
        """A GameWin deve conter um CrtEffectsOverlay."""
        crt = game_win.findChild(CrtEffectsOverlay)
        assert crt is not None

    def test_crt_overlay_geometria(self, game_win):
        """O CRT overlay deve cobrir toda a area da GameWin."""
        crt = game_win.findChild(CrtEffectsOverlay)
        from PySide6.QtCore import QEvent, QSize
        from PySide6.QtGui import QResizeEvent
        game_win.resize(800, 600)
        event = QResizeEvent(QSize(800, 600), game_win.size())
        game_win.resizeEvent(event)
        assert crt.width() == game_win.width()
        assert crt.height() == game_win.height()


class TestIntegracaoConfetti:
    """
    Testes de integracao com o ConfettiOverlay.
    """

    def test_confetti_overlay_existe(self, game_win):
        """A GameWin deve conter um ConfettiOverlay."""
        confetti = game_win.findChild(ConfettiOverlay)
        assert confetti is not None

    def test_confetti_overlay_geometria(self, game_win):
        """O confetti overlay deve cobrir toda a area da GameWin."""
        confetti = game_win.findChild(ConfettiOverlay)
        from PySide6.QtCore import QEvent, QSize
        from PySide6.QtGui import QResizeEvent
        game_win.resize(800, 600)
        event = QResizeEvent(QSize(800, 600), game_win.size())
        game_win.resizeEvent(event)
        assert confetti.width() == game_win.width()
        assert confetti.height() == game_win.height()


class TestIntegracaoBackgroundRiscos:
    """
    Testes de integracao com o BackgroundRiscos.
    """

    def test_bg_riscos_existe(self, game_win):
        """A GameWin deve conter um BackgroundRiscos."""
        bg = game_win.findChild(BackgroundRiscos)
        assert bg is not None


class TestResponsividade:
    """
    Testes de responsividade e escalabilidade.
    """

    def test_reaplicar_dimensoes(self, game_win):
        """__reaplicar_dimensoes deve actualizar fontes sem erros."""
        game_win._GameWin__reaplicar_dimensoes()
        titulo = game_win.findChild(QLabel, "gamewin_titulo")
        assert titulo.font().pointSize() > 0

    def test_resize_nao_crasha(self, game_win):
        """Resize da GameWin nao deve causar erros."""
        game_win.resize(600, 400)
        game_win.resize(1200, 900)
        game_win.resize(400, 300)


