"""
Suite de testes para o widget GameOver com estetica CRT.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QFrame, QLabel, QPushButton

from core.dtos.parecer_cipa import ParecerCIPA
from infrastructure.repository.repositorio_pareceres_cipa import (
    ParecerCIPAIndisponivelError,
    RepositorioDePareceresCIPA,
)
from view.expediente.paginas.game_over import GameOver
from view.infrastructure.layout_loader import LayoutLoader
from view.widgets.efeitos.crt_overlay import CrtEffectsOverlay


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def layout_loader_1920():
    """Garante LayoutLoader em 1920x1080 para cálculos determinísticos."""
    LayoutLoader._instance = None
    loader = LayoutLoader.instance()
    loader.set_screen(1920, 1080)
    return loader


@pytest.fixture
def game_over(layout_loader_1920):
    """Retorna uma GameOver com pontuação 3000.0 e LayoutLoader configurado."""
    return GameOver(pontuacao_global=3000.0)


@pytest.fixture
def parecer_fake():
    """ParecerCIPA deterministico para injecao em testes."""
    return ParecerCIPA(
        numero="123/2026",
        referencia="Conduta do Inspetor",
        texto="Texto de teste com tamanho suficiente para nao ser vazio.",
    )


@pytest.fixture
def repositorio_mock(parecer_fake):
    """Mock do RepositorioDePareceresCIPA com MagicMock."""
    mock = MagicMock(spec=RepositorioDePareceresCIPA)
    mock.obter_parecer_para_curso.return_value = parecer_fake
    return mock


class TestEstrutura:
    """Testes de estrutura basica da GameOver CRT.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, game_over):
        """A GameOver deve ter objectName 'game_over'."""
        assert game_over.objectName() == "game_over"

    def test_property_class(self, game_over):
        """A GameOver deve ter property class 'game_over'."""
        assert game_over.property("class") == "game_over"

    def test_titulo_existe(self, game_over):
        """A GameOver deve conter um QLabel com texto 'GAME OVER'."""
        titulo = game_over.findChild(QLabel, "gameover_titulo")
        assert titulo is not None
        assert titulo.text() == "GAME OVER"

    def test_subtitulo_existe(self, game_over):
        """A GameOver deve conter o subtitulo de credencial revogada."""
        subtitulo = game_over.findChild(QLabel, "gameover_subtitulo")
        assert subtitulo is not None
        assert "revogada" in subtitulo.text()

    def test_header_existe(self, game_over):
        """A GameOver deve conter o header da sessao IFF-BJI."""
        header = game_over.findChild(QLabel, "gameover_header")
        assert header is not None
        assert "IFF-BJI" in header.text()

    def test_timestamp_existe(self, game_over):
        """A GameOver deve conter o timestamp da sessao."""
        ts = game_over.findChild(QLabel, "gameover_timestamp")
        assert ts is not None

    def test_card_existe(self, game_over):
        """A GameOver deve conter o card do parecer."""
        card = game_over.findChild(QFrame, "gameover_card")
        assert card is not None

    def test_pontuacao_existe(self, game_over):
        """O score deve exibir a pontuacao em 'pts'."""
        valor = game_over.findChild(QLabel, "gameover_score_valor")
        assert valor is not None
        assert "pts" in valor.text()

    def test_btn_retry_existe(self, game_over):
        """Deve conter QPushButton 'Tentar novamente'."""
        btn = game_over.findChild(QPushButton, "gameover_btn_retry")
        assert btn is not None
        assert btn.text() == "Tentar novamente"

    def test_btn_menu_existe(self, game_over):
        """Deve conter QPushButton 'Menu principal'."""
        btn = game_over.findChild(QPushButton, "gameover_btn_menu")
        assert btn is not None
        assert btn.text() == "Menu principal"

    def test_btn_sair_existe(self, game_over):
        """Deve conter QPushButton 'Sair do Jogo'."""
        btn = game_over.findChild(QPushButton, "gameover_btn_quit")
        assert btn is not None
        assert btn.text() == "Sair do Jogo"

    def test_footer_existe(self, game_over):
        """O footer de sessao encerrada deve existir."""
        footer = game_over.findChild(QFrame, "gameover_footer")
        assert footer is not None
        label = footer.findChild(QLabel, "gameover_footer_label")
        assert label is not None
        assert "ENCERRADA" in label.text()


class TestPontuacao:
    """Testes de atualizacao de pontuacao."""

    def test_atualizar_pontuacao(self, game_over):
        """atualizar_pontuacao deve atualizar o texto do score."""
        game_over.atualizar_pontuacao(820.0)
        valor = game_over.findChild(QLabel, "gameover_score_valor")
        assert "820" in valor.text()

    def test_atualizar_pontuacao_formato_inteiro(self, game_over):
        """atualizar_pontuacao deve formatar float como inteiro sem casas decimais."""
        game_over.atualizar_pontuacao(1234.5)
        valor = game_over.findChild(QLabel, "gameover_score_valor")
        assert "1234" in valor.text()


class TestParecer:
    """Testes do parecer da CIPA."""

    def test_definir_parecer_popula_card(self, game_over):
        """definir_parecer deve preencher o card com texto e numero."""
        game_over.definir_parecer("T_QUIMICA")
        num = game_over.findChild(QLabel, "gameover_card_parecer_num")
        assert num is not None
        assert "Parecer n" in num.text()
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        assert texto is not None
        assert len(texto.text()) > 10

    def test_definir_parecer_fallback(self, game_over):
        """definir_parecer com curso inexistente deve usar fallback."""
        game_over.definir_parecer("CURSO_INEXISTENTE")
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        assert texto is not None
        assert len(texto.text()) > 10


class TestSignals:
    """Testes dos sinais da GameOver."""

    def test_voltar_menu_signal(self, game_over, qtbot):
        """Clicar em Menu principal deve emitir voltar_menu_solicitado."""
        btn = game_over.findChild(QPushButton, "gameover_btn_menu")
        with qtbot.waitSignal(game_over.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_jogar_novamente_signal(self, game_over, qtbot):
        """Clicar em Tentar novamente deve emitir jogar_novamente_solicitado."""
        btn = game_over.findChild(QPushButton, "gameover_btn_retry")
        with qtbot.waitSignal(game_over.jogar_novamente_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)


class TestDimensoesCard:
    """Cobertura das dimensões responsivas do CARD após correção do overflow.

    Verifica que __label_parecer_texto e __card consomem o LayoutLoader
    como fonte única de verdade para maximumHeight/minimumHeight, e que
    o signal escala_atualizada provoca reaplicação correta.
    """

    def test_parecer_texto_tem_maximum_height_definido(self, game_over):
        """QLabel do parecer tem maximumHeight > 0 após setup.

        Garante que o limite vertical está aplicado, impedindo que o texto
        cresça indefinidamente e cause overflow no CARD.
        """
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        assert texto is not None
        assert texto.maximumHeight() > 0

    def test_parecer_texto_maximum_height_vem_do_layout(self, game_over, layout_loader_1920):
        """maximumHeight do parecer corresponde ao valor do layout.json.

        Verifica a integração com o LayoutLoader (fonte única de verdade).
        """
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        esperado = layout_loader_1920.scaled("gameover", "card", "parecer_max_height")
        assert texto.maximumHeight() == esperado

    def test_card_tem_minimum_height_apos_setup(self, game_over):
        """CARD tem minimumHeight > 0 após setup.

        Garante que o CARD tem um piso de altura, não sendo esmagado
        pelos addStretch() do layout externo.
        """
        card = game_over.findChild(QFrame, "gameover_card")
        assert card is not None
        assert card.minimumHeight() > 0

    def test_card_minimum_height_vem_do_layout(self, game_over, layout_loader_1920):
        """minimumHeight do CARD corresponde ao valor do layout.json."""
        card = game_over.findChild(QFrame, "gameover_card")
        esperado = layout_loader_1920.scaled("gameover", "card", "altura_minima")
        assert card.minimumHeight() == esperado

    def test_card_minimum_height_reaplicado_em_resize(self, game_over, layout_loader_1920):
        """Após mudar resolução, minimumHeight é recalculado.

        Verifica que __reaplicar_dimensoes() está conectado correctamente
        ao signal escala_atualizada do LayoutLoader.
        """
        card = game_over.findChild(QFrame, "gameover_card")
        layout_loader_1920.set_screen(1280, 720)
        esperado = layout_loader_1920.scaled("gameover", "card", "altura_minima")
        assert card.minimumHeight() == esperado

    def test_parecer_max_height_reaplicado_em_resize(self, game_over, layout_loader_1920):
        """Após mudar resolução, maximumHeight do parecer é recalculado.

        Garante que o slot conectado a escala_atualizada re-aplica o
        limite vertical do texto do parecer CIPA.
        """
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        layout_loader_1920.set_screen(1280, 720)
        esperado = layout_loader_1920.scaled("gameover", "card", "parecer_max_height")
        assert texto.maximumHeight() == esperado

    def test_card_largura_limitada_pelo_layout(self, game_over, layout_loader_1920):
        """Largura do CARD respeita os bornes largura_min/largura_max.

        Após resize + ajuste, a largura deve estar dentro do range
        calculado a partir do fator_largura clampado pelos bornes.
        """
        card = game_over.findChild(QFrame, "gameover_card")
        game_over.resize(1920, 1080)
        game_over._GameOver__ajustar_tamanho_do_card()
        largura_min = layout_loader_1920.scaled("gameover", "card", "largura_min")
        largura_max = layout_loader_1920.scaled("gameover", "card", "largura_max")
        assert largura_min <= card.width() <= largura_max

    def test_parecer_max_height_acomoda_pior_caso(self, game_over, layout_loader_1920):
        """Capacidade do CARD acomoda o parecer mais longo do JSON (252 chars).

        Derivação:
        - 252 caracteres / ~45 caracteres por linha (largura mínima 330px) = 6 linhas
        - 13pt × 1.5 line-height = 19.5px por linha
        - 6 × 19.5 = 117px mínimo necessário
        - Configuração actual: 150px (folga de ~28%)

        Se este teste falhar, algum dos valores em layout.json foi reduzido
        para um valor que não acomoda o pior parecer.
        """
        texto = game_over.findChild(QLabel, "gameover_card_parecer_texto")
        assert texto is not None
        altura_por_linha = 13 * 1.5
        linhas_necessarias_pior_caso = 6
        altura_minima_necessaria = int(linhas_necessarias_pior_caso * altura_por_linha)
        assert texto.maximumHeight() >= altura_minima_necessaria


class TestSignalSairSolicitado:
    """Cobertura do signal sair_solicitado (correccao do bug do QApplication.quit)."""

    def test_sinal_sair_solicitado_existe(self, game_over):
        """Signal sair_solicitado esta' declarado na classe."""
        # Arrange — nada a preparar, GameOver ja' existe via fixture

        # Act — nada a executar

        # Assert — o signal e' um atributo da classe, nao da instancia
        assert "sair_solicitado" in GameOver.__dict__
        # Validacao adicional: e' efectivamente um Signal PySide6
        assert isinstance(GameOver.__dict__["sair_solicitado"], Signal)

    def test_botao_sair_emite_sair_solicitado(self, repositorio_mock, qtbot):
        """Clicar no botao 'Sair do Jogo' emite o signal sair_solicitado.

        Antes da refactoracao, este botao chamava QApplication.quit()
        directamente, violando o MVP. Agora propaga via signal.
        """
        # Arrange — usar repo mock para nao ler JSON real
        widget = GameOver(pontuacao_global=3000.0, repositorio=repositorio_mock)
        botao_sair = widget.findChild(QPushButton, "gameover_btn_quit")
        assert botao_sair is not None

        # Act & Assert — clicar deve emitir o signal dentro do timeout
        with qtbot.waitSignal(widget.sair_solicitado, timeout=1000):
            botao_sair.click()

    def test_botao_sair_nao_chama_qapplication_quit(self, repositorio_mock, qtbot):
        """Clicar no botao 'Sair do Jogo' NAO chama QApplication.instance().quit."""
        # Arrange
        widget = GameOver(pontuacao_global=3000.0, repositorio=repositorio_mock)
        botao_sair = widget.findChild(QPushButton, "gameover_btn_quit")
        assert botao_sair is not None

        # Act — patch so' durante o click; nada dentro do GameOver deve chamar quit
        with patch("PySide6.QtWidgets.QApplication.instance") as mock_qapp_instance:
            mock_instance = MagicMock()
            mock_qapp_instance.return_value = mock_instance
            botao_sair.click()

        # Assert — QApplication.quit nunca foi invocado
        mock_instance.quit.assert_not_called()


class TestIntegracaoRepositorio:
    """Cobertura da injecao do RepositorioDePareceresCIPA no construtor."""

    def test_construtor_aceita_repositorio_injetado(self, repositorio_mock):
        """GameOver aceita um repositorio injetado no construtor."""
        # Arrange — repo mock preparado pela fixture

        # Act
        widget = GameOver(pontuacao_global=3000.0, repositorio=repositorio_mock)

        # Assert — widget criado com sucesso e expoe o repo injectado
        assert widget is not None
        repo_interno = widget._GameOver__repositorio
        assert repo_interno is repositorio_mock

    def test_construtor_sem_repositorio_instancia_default(self, layout_loader_1920):
        """Sem injecao, GameOver instancia um RepositorioDePareceresCIPA real."""
        # Arrange — layout_loader_1920 garante LayoutLoader pronto

        # Act
        widget = GameOver(pontuacao_global=3000.0)

        # Assert — widget criado sem erro; repo real existe como atributo privado
        assert widget is not None
        repo = widget._GameOver__repositorio
        assert isinstance(repo, RepositorioDePareceresCIPA)

    def test_definir_parecer_delega_ao_repositorio(self, repositorio_mock):
        """definir_parecer() delega ao repositorio.obter_parecer_para_curso."""
        # Arrange
        widget = GameOver(pontuacao_global=3000.0, repositorio=repositorio_mock)

        # Act
        widget.definir_parecer("T_INFORMATICA")

        # Assert — repo foi chamado exactamente uma vez com o curso recebido
        repositorio_mock.obter_parecer_para_curso.assert_called_once_with("T_INFORMATICA")

    def test_definir_parecer_popula_label_com_texto_do_repositorio(
        self, repositorio_mock, parecer_fake
    ):
        """definir_parecer() actualiza o QLabel do parecer com o texto vindo do repo."""
        # Arrange
        widget = GameOver(pontuacao_global=3000.0, repositorio=repositorio_mock)
        label_texto = widget.findChild(QLabel, "gameover_card_parecer_texto")
        label_num = widget.findChild(QLabel, "gameover_card_parecer_num")
        assert label_texto is not None
        assert label_num is not None

        # Act
        widget.definir_parecer("T_QUIMICA")

        # Assert — labels preenchidos com os campos do parecer do repo
        assert label_texto.text() == parecer_fake.texto
        assert parecer_fake.numero in label_num.text()
        assert parecer_fake.referencia in label_num.text()

    def test_definir_parecer_trata_erro_indisponivel(self, layout_loader_1920):
        """Se o repositorio levantar ParecerCIPAIndisponivelError, define mensagem fallback."""
        # Arrange
        repo_mock = MagicMock(spec=RepositorioDePareceresCIPA)
        repo_mock.obter_parecer_para_curso.side_effect = ParecerCIPAIndisponivelError(
            "[Erro - Test] Inexistente"
        )
        widget = GameOver(pontuacao_global=3000.0, repositorio=repo_mock)
        label_texto = widget.findChild(QLabel, "gameover_card_parecer_texto")
        assert label_texto is not None

        # Act
        widget.definir_parecer("CURSO_INEXISTENTE")

        # Assert — mensagem de indisponibilidade aparece no label
        assert "indispon" in label_texto.text().lower()


class TestIntegracaoCrtOverlay:
    """Cobertura da presenca do CrtEffectsOverlay como filho."""

    def test_widget_tem_crt_overlay_como_filho(self, game_over):
        """GameOver tem um CrtEffectsOverlay configurado como filho directo."""
        # Arrange — game_over pronto via fixture

        # Act — nada a executar, a fixture ja' criou o widget

        # Assert — existe exactamente 1 CrtEffectsOverlay dentro do GameOver
        overlays = game_over.findChildren(CrtEffectsOverlay)
        assert len(overlays) == 1

    def test_crt_overlay_cobre_todo_o_widget_pai(self, layout_loader_1920, qtbot):
        """Apos resize, o CrtEffectsOverlay tem a mesma geometria que o GameOver.

        O resizeEvent do GameOver chama __crt_overlay.setGeometry(self.rect()),
        portanto a geometria do overlay deve coincidir com o rect do pai
        apos o resize.
        """
        # Arrange
        widget = GameOver(pontuacao_global=3000.0)
        widget.resize(1920, 1080)
        widget.show()
        qtbot.waitExposed(widget)

        # Act — show + resize garante que o resizeEvent foi processado pelo overlay
        widget.resize(1920, 1080)

        # Assert — overlay cobre exactamente a area do GameOver
        overlay = widget.findChild(CrtEffectsOverlay)
        assert overlay is not None
        area_pai = widget.rect()
        area_overlay = overlay.geometry()
        assert (area_overlay.x(), area_overlay.y()) == (area_pai.x(), area_pai.y())
        assert (area_overlay.width(), area_overlay.height()) == (
            area_pai.width(),
            area_pai.height(),
        )

    def test_game_over_nao_tem_qtimer_proprio(self, game_over):
        """Apos a refactoracao, GameOver nao cria o seu proprio QTimer.

        A gestao do QTimer de animacao foi delegada ao CrtEffectsOverlay.
        Se existir algum QTimer dentro do GameOver, o seu parent deve ser
        o overlay, nunca o proprio GameOver.
        """
        # Arrange — game_over pronto via fixture

        # Act — nada a executar

        # Assert — nenhum QTimer tem o GameOver como parent directo
        timers = game_over.findChildren(QTimer)
        for timer in timers:
            assert timer.parent() is not game_over
