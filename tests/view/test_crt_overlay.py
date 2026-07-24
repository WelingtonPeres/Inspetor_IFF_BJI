"""
Testes do widget CrtEffectsOverlay.

Cobre a identidade, atributos iniciais, ciclo de vida do QTimer interno,
constantes visuais, logica de animacao da scanline bar e pintura das
tres camadas CRT (scanlines estaticas, vinheta radial, scanline bar).
"""

import pytest
from unittest.mock import patch

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QFrame

from view.widgets.efeitos.crt_overlay import CrtEffectsOverlay


@pytest.fixture(scope="session")
def qapp():
    """Instancia QApplication partilhada por toda a suite de testes de widget."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def widget(qapp):
    """Widget CrtEffectsOverlay limpo, instanciado por teste."""
    return CrtEffectsOverlay()


class TestIdentidade:
    """Identidade do widget: objectName, property class e heranca."""

    def test_object_name_eh_crt_overlay(self, widget):
        """
        objectName do widget e 'crt_overlay'.

        Necessario para selectores QSS do tipo QFrame#crt_overlay.
        """
        assert widget.objectName() == "crt_overlay"

    def test_property_class_eh_crt_overlay(self, widget):
        """
        property('class') e 'crt_overlay'.

        Necessario para selectores QSS por classe (reutilizavel).
        """
        assert widget.property("class") == "crt_overlay"

    def test_herda_de_qframe(self, widget):
        """
        Widget herda de QFrame, nao QWidget puro.

        QFrame respeita border-radius e background-color no QSS.
        """
        assert isinstance(widget, QFrame)


class TestAtributosIniciais:
    """Estado do widget apos construcao, antes de show()."""

    def test_transparente_para_mouse(self, widget):
        """
        Widget tem WA_TransparentForMouseEvents activo.

        Nao deve interceptar cliques do utilizador que passem pelo overlay.
        """
        assert widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def test_background_translucido(self, widget):
        """Widget tem WA_TranslucentBackground activo para deixar ver o conteudo abaixo."""
        assert widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def test_scanline_pos_inicial_negativo(self, widget):
        """
        Posicao inicial da scanline bar e negativa (acima do widget).

        A barra comeca fora do ecra para entrar pelo topo no primeiro tick.
        """
        pos_inicial = widget._CrtEffectsOverlay__scanline_pos
        assert pos_inicial < 0
        assert pos_inicial == -float(CrtEffectsOverlay._SCANLINE_BAR_HEIGHT)

    def test_timer_instanciado(self, widget):
        """QTimer interno foi instanciado no construtor."""
        timer = widget._CrtEffectsOverlay__timer
        assert isinstance(timer, QTimer)

    def test_timer_inicialmente_inativo(self, widget):
        """
        QTimer nao esta activo antes de show().

        A animacao so arranca quando o widget fica visivel.
        """
        assert not widget._CrtEffectsOverlay__timer.isActive()

    def test_timer_intervalo_16ms(self, widget):
        """QTimer tem intervalo de 16ms (~60fps) aplicado no construtor."""
        assert widget._CrtEffectsOverlay__timer.interval() == CrtEffectsOverlay._SCANLINE_INTERVAL_MS


class TestCicloTimer:
    """Ciclo de vida do QTimer: start em show, stop em hide."""

    def test_timer_arranca_em_show(self, widget):
        """
        QTimer fica activo apos showEvent.
        """
        # Arrange
        widget.show()
        try:
            # Act
            esta_ativo = widget._CrtEffectsOverlay__timer.isActive()
            # Assert
            assert esta_ativo
        finally:
            widget.hide()

    def test_timer_para_em_hide(self, widget):
        """
        QTimer fica inactivo apos hideEvent.
        """
        # Arrange
        widget.show()
        widget.hide()
        # Assert
        assert not widget._CrtEffectsOverlay__timer.isActive()

    def test_show_depois_hide_re_arranca_timer(self, widget):
        """
        Apos um ciclo show/hide, um novo show reactiva o timer.
        """
        # Arrange
        widget.show()
        widget.hide()
        # Act
        widget.show()
        try:
            # Assert
            assert widget._CrtEffectsOverlay__timer.isActive()
        finally:
            widget.hide()


class TestLogicaAnimacao:
    """Logica do slot __animar: incremento, reset, update."""

    def test_animar_avanca_pos_por_velocidade(self, widget):
        """
        Um tick de __animar incrementa __scanline_pos por _SCANLINE_SPEED_PX.
        """
        # Arrange
        pos_antes = widget._CrtEffectsOverlay__scanline_pos
        # Act
        widget._CrtEffectsOverlay__animar()
        # Assert
        pos_depois = widget._CrtEffectsOverlay__scanline_pos
        assert pos_depois == pytest.approx(pos_antes + CrtEffectsOverlay._SCANLINE_SPEED_PX)

    def test_animar_regressa_quando_pos_ultrapassa_altura(self, widget):
        """
        Quando __scanline_pos ultrapassa self.height(), faz reset para -_SCANLINE_BAR_HEIGHT.
        """
        # Arrange
        widget.resize(800, 600)
        widget._CrtEffectsOverlay__scanline_pos = float(widget.height() + 100)
        # Act
        widget._CrtEffectsOverlay__animar()
        # Assert
        assert widget._CrtEffectsOverlay__scanline_pos == pytest.approx(
            -float(CrtEffectsOverlay._SCANLINE_BAR_HEIGHT)
        )

    def test_animar_nao_regressa_abaixo_da_altura(self, widget):
        """
        Quando __scanline_pos esta abaixo de self.height(), nao faz reset.
        """
        # Arrange
        widget.resize(800, 600)
        widget._CrtEffectsOverlay__scanline_pos = float(widget.height() - 10)
        pos_esperada = float(widget.height() - 10) + CrtEffectsOverlay._SCANLINE_SPEED_PX
        # Act
        widget._CrtEffectsOverlay__animar()
        # Assert
        assert widget._CrtEffectsOverlay__scanline_pos == pytest.approx(pos_esperada)

    def test_animar_regressa_no_limite_da_altura(self, widget):
        """
        Quando __scanline_pos igual a self.height(), o incremento seguinte provoca reset.
        """
        # Arrange
        widget.resize(800, 600)
        widget._CrtEffectsOverlay__scanline_pos = float(widget.height())
        # Act
        widget._CrtEffectsOverlay__animar()
        # Assert: 600.0 + 1.2 = 601.2 > 600, entao reset
        assert widget._CrtEffectsOverlay__scanline_pos == pytest.approx(
            -float(CrtEffectsOverlay._SCANLINE_BAR_HEIGHT)
        )

    def test_animar_chama_update_com_rect_da_bar(self, widget):
        """
        __animar chama self.update() com rect alinhado com a scanline bar.
        """
        # Arrange
        widget.resize(800, 600)
        with patch.object(widget, "update") as mock_update:
            # Act
            widget._CrtEffectsOverlay__animar()
            # Assert
            mock_update.assert_called_once()
            args = mock_update.call_args[0]
            assert args[0] == 0
            assert args[2] == widget.width()
            assert args[3] == CrtEffectsOverlay._SCANLINE_BAR_HEIGHT


class TestConstantesAnimacao:
    """Validacao dos valores das constantes de animacao e visuais."""

    def test_intervalo_timer_16ms(self):
        """Intervalo do timer e 16ms (~60fps)."""
        assert CrtEffectsOverlay._SCANLINE_INTERVAL_MS == 16

    def test_velocidade_scanline(self):
        """Velocidade da scanline bar e 1.2 px/frame."""
        assert CrtEffectsOverlay._SCANLINE_SPEED_PX == pytest.approx(1.2)

    def test_altura_bar_40(self):
        """Altura da scanline bar animada e 40px."""
        assert CrtEffectsOverlay._SCANLINE_BAR_HEIGHT == 40

    def test_espacamento_scanlines_3(self):
        """Espacamento vertical entre scanlines e 3px."""
        assert CrtEffectsOverlay._SCANLINE_SPACING == 3

    def test_cor_scanline_branco_quase_transparente(self):
        """Cor das scanlines e branca com alpha 9 (quase invisivel)."""
        cor = CrtEffectsOverlay._SCANLINE_COLOR
        assert cor.red() == 255
        assert cor.green() == 255
        assert cor.blue() == 255
        assert cor.alpha() == 9

    def test_cor_scanline_bar_verde_com_alpha_decrescente(self):
        """
        Cores da scanline bar sao tons de verde (113, 221, 119) com alpha top > mid > bot.
        """
        top = CrtEffectsOverlay._SCANLINE_BAR_TOP_COLOR
        mid = CrtEffectsOverlay._SCANLINE_BAR_MID_COLOR
        bot = CrtEffectsOverlay._SCANLINE_BAR_BOT_COLOR
        for cor in (top, mid, bot):
            assert cor.red() == 113
            assert cor.green() == 221
            assert cor.blue() == 119
        assert top.alpha() > mid.alpha() > bot.alpha() == 0

    def test_vinheta_raio_factor_07(self):
        """Raio da vinheta e 70% do maior lado do widget."""
        assert CrtEffectsOverlay._VIGNETTE_RADIUS_FACTOR == pytest.approx(0.7)

    def test_vinheta_inner_stop_055(self):
        """Parada interior da vinheta e 0.55 (gradiente de 55% ate 100%)."""
        assert CrtEffectsOverlay._VIGNETTE_INNER_STOP == pytest.approx(0.55)

    def test_vinheta_inner_totalmente_transparente(self):
        """Cor interior da vinheta e totalmente transparente (alpha 0)."""
        assert CrtEffectsOverlay._VIGNETTE_INNER_COLOR.alpha() == 0

    def test_vinheta_outer_preta_translucida(self):
        """Cor exterior da vinheta e preta translucida (alpha 115)."""
        cor = CrtEffectsOverlay._VIGNETTE_OUTER_COLOR
        assert cor.red() == 0
        assert cor.green() == 0
        assert cor.blue() == 0
        assert cor.alpha() == 115


class TestRenderizacao:
    """paintEvent nao deve levantar erros em varias condicoes de tamanho e posicao."""

    def test_paint_event_com_widget_pequeno_nao_falha(self, widget):
        """
        paintEvent executa sem erros com widget de 100x100.
        """
        # Arrange
        widget.resize(100, 100)
        widget.show()
        try:
            # Act
            widget.repaint()
        finally:
            widget.hide()

    def test_paint_event_com_widget_grande_nao_falha(self, widget):
        """
        paintEvent executa sem erros com widget 1920x1080.
        """
        # Arrange
        widget.resize(1920, 1080)
        widget.show()
        try:
            widget.repaint()
        finally:
            widget.hide()

    def test_paint_event_com_scanline_acima_do_ecra(self, widget):
        """
        paintEvent executa sem erros quando a scanline bar esta acima do ecra.
        """
        # Arrange
        widget.resize(800, 600)
        widget._CrtEffectsOverlay__scanline_pos = -100.0
        widget.show()
        try:
            widget.repaint()
        finally:
            widget.hide()

    def test_paint_event_com_scanline_abaixo_do_ecra(self, widget):
        """
        paintEvent executa sem erros quando a scanline bar esta abaixo do ecra.
        """
        # Arrange
        widget.resize(800, 600)
        widget._CrtEffectsOverlay__scanline_pos = 1000.0
        widget.show()
        try:
            widget.repaint()
        finally:
            widget.hide()
