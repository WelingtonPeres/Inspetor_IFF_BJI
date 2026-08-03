"""
Suite de testes da TelaTutorial (8 slides).

Cobre estrutura do chrome, navegacao (contador, setas, dots), sinais de
finalizacao (Pular, X, CTA), reentrancia, geometria 80% + fallback,
maximizar/restaurar e o conteudo de cada um dos 8 slides.
"""

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QLabel, QPushButton, QStackedWidget, QToolButton, QWidget

from application.interfaces.i_game_view import MotivoTutorial
from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.tutorial.paginas.slide_anatomia import SlideAnatomia
from view.tutorial.paginas.slide_anexos import SlideAnexos
from view.tutorial.paginas.slide_boas_vindas import SlideBoasVindas
from view.tutorial.paginas.slide_decisao import SlideDecisao
from view.tutorial.paginas.slide_fatores import SlideFatores
from view.tutorial.paginas.slide_pronto import SlidePronto
from view.tutorial.paginas.slide_riscos import SlideRiscos
from view.tutorial.paginas.slide_vitoria import SlideVitoria
from view.tutorial.slide_tutorial import SlideTutorial
from view.tutorial.tela_tutorial import TelaTutorial
from view.tutorial.widgets.item_numerado import ItemNumerado

TOTAL_SLIDES = 8
ULTIMO_SLIDE = TOTAL_SLIDES - 1

OBJET_NAMES_ESPERADOS = (
    "slide_boas_vindas",
    "slide_anatomia",
    "slide_anexos",
    "slide_riscos",
    "slide_fatores",
    "slide_decisao",
    "slide_vitoria",
    "slide_pronto",
)


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Garante QApplication partilhada para os widgets criados."""
    return qapp


@pytest.fixture
def tutorial():
    """Retorna uma TelaTutorial com LayoutLoader em resolucao base."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return TelaTutorial()


@pytest.fixture
def stack(tutorial):
    """QStackedWidget interno com os slides registados."""
    return tutorial.findChild(QStackedWidget)


class TestEstrutura:
    """Identidade e composicao basica da TelaTutorial."""

    def test_object_name(self, tutorial):
        """A TelaTutorial deve ter objectName 'tela_tutorial'."""
        assert tutorial.objectName() == "tela_tutorial"

    def test_property_class(self, tutorial):
        """A TelaTutorial deve ter property class 'tela_tutorial'."""
        assert tutorial.property("class") == "tela_tutorial"

    def test_window_title_bar_integrada(self, tutorial):
        """TelaTutorial deve conter um WindowTitleBar com min/max (maximizar sempre)."""
        bar = tutorial.findChild(WindowTitleBar)
        assert bar is not None
        assert bar.findChild(QPushButton, "window_maximize_button") is not None

    def test_stacked_com_oito_slides(self, stack):
        """O QStackedWidget deve ter 8 slides registados."""
        assert stack.count() == TOTAL_SLIDES

    def test_slides_com_objectname_esperado(self, stack):
        """Os slides devem seguir a ordem do storyboard (1 a 8)."""
        nomes = [stack.widget(i).objectName() for i in range(stack.count())]
        assert tuple(nomes) == OBJET_NAMES_ESPERADOS

    def test_credencial_apenas_slides_extremos(self, stack):
        """Credencial IFF deve existir so nos slides 1 e 8."""
        for indice in (0, ULTIMO_SLIDE):
            credencial = stack.widget(indice).findChild(QWidget, "tutorial_credential")
            assert credencial is not None
            selo = credencial.findChild(QWidget, "credential_selo")
            assert selo is not None
            assert credencial.findChild(QWidget, "credential_selo_icone") is not None
        for indice in range(1, ULTIMO_SLIDE):
            assert stack.widget(indice).findChild(QWidget, "tutorial_credential") is None


class TestContratoSlides:
    """Contrato SlideTutorial: ABC partilhada, no-op de motivo e CTA ligado."""

    def test_todos_os_slides_implementam_slide_tutorial(self, stack):
        """Todos os 8 slides devem herdar de SlideTutorial."""
        for indice in range(stack.count()):
            assert isinstance(stack.widget(indice), SlideTutorial)

    def test_briefing_nao_vazio_em_todos_os_slides(self, stack):
        """Todo slide deve expor uma frase de briefing nao vazia."""
        for indice in range(stack.count()):
            assert stack.widget(indice).texto_briefing().strip() != ""

    def test_definir_motivo_noop_no_slide_1(self, stack):
        """Slide 1 aceita definir_motivo sem erro (no-op herdado da ABC)."""
        stack.widget(0).definir_motivo(MotivoTutorial.CONSULTA)

    def test_cta_de_todos_os_slides_ligado_ao_chrome(self, stack, qtbot):
        """Emitir cta_clicked de qualquer slide deve finalizar o tutorial."""
        for indice in range(stack.count()):
            slide = stack.widget(indice)
            assert isinstance(slide, SlideTutorial)
            with qtbot.waitSignal(
                stack.parent().finalizado_solicitado, timeout=1000
            ):
                slide.cta_clicked.emit()

    def test_validacao_rejeita_slide_sem_contrato(self, tutorial):
        """O registry deve rejeitar slides que nao implementem o contrato."""
        class SlideIncompleto(SlideTutorial):
            pass

        with pytest.raises(TypeError):
            tutorial._TelaTutorial__validar_slide(SlideIncompleto)


class TestChrome:
    """Contador, briefing, setas e dots do chrome."""

    def test_contador_inicial(self, tutorial):
        """O contador deve iniciar em 'Como jogar · 1 de 8'."""
        label = tutorial.findChild(QLabel, "tutorial_contador")
        assert label.text() == "Como jogar · 1 de %d" % TOTAL_SLIDES

    def test_briefing_do_primeiro_slide(self, tutorial):
        """O briefing deve exibir a frase do slide actual."""
        label = tutorial.findChild(QLabel, "tutorial_briefing")
        assert "manual" in label.text()

    def test_seta_anterior_desabilitada_no_primeiro_slide(self, tutorial):
        """A seta anterior deve estar desabilitada no primeiro slide."""
        btn = tutorial.findChild(QPushButton, "tutorial_nav_prev")
        assert not btn.isEnabled()

    def test_oito_dots_registados(self, tutorial):
        """Devem existir 8 dots, com o primeiro activo."""
        dots = tutorial.findChildren(QPushButton, "tutorial_dot")
        assert len(dots) == TOTAL_SLIDES
        assert dots[0].property("active") == "true"
        assert dots[1].property("active") == "false"

    def test_navegar_ate_o_ultimo_slide_atualiza_estado(self, tutorial):
        """Ultimo slide: contador '8 de 8', seta anterior habilitada, seta
        seguinte e dots escondidos, briefing do SlidePronto."""
        for _ in range(ULTIMO_SLIDE):
            tutorial._TelaTutorial__ir_para_slide_seguinte()
        contador = tutorial.findChild(QLabel, "tutorial_contador")
        assert contador.text() == "Como jogar · %d de %d" % (
            TOTAL_SLIDES,
            TOTAL_SLIDES,
        )
        btn_prev = tutorial.findChild(QPushButton, "tutorial_nav_prev")
        assert btn_prev.isEnabled()
        btn_next = tutorial.findChild(QPushButton, "tutorial_nav_next")
        assert not btn_next.isVisible()
        dots = tutorial.findChild(QWidget, "tutorial_dots")
        assert not dots.isVisible()
        briefing = tutorial.findChild(QLabel, "tutorial_briefing")
        assert "estilo" in briefing.text()

    def test_dots_atualizados_no_terceiro_slide(self, tutorial):
        """No terceiro slide o terceiro dot deve ficar activo."""
        tutorial._TelaTutorial__ir_para_slide_seguinte()
        tutorial._TelaTutorial__ir_para_slide_seguinte()
        dots = tutorial.findChildren(QPushButton, "tutorial_dot")
        assert dots[0].property("active") == "false"
        assert dots[1].property("active") == "false"
        assert dots[2].property("active") == "true"


class TestConteudoSlides:
    """Conteudo especifico de cada um dos 8 slides."""

    def test_slide_boas_vindas_tem_quatro_paragrafos(self, stack):
        """Slide 1 deve ter 4 paragrafos de boas-vindas."""
        labels = stack.widget(0).findChildren(QLabel, "tutorial_paragrafo")
        assert len(labels) == 4

    def test_slide_anatomia_tem_quatro_itens(self, stack):
        """Slide 2 deve ter 4 ItemNumerado (Local a Descricao)."""
        itens = stack.widget(1).findChildren(ItemNumerado)
        assert len(itens) == 4
        assert stack.widget(1).findChild(QWidget, "tutorial_mini_relatorio") is not None

    def test_slide_anexos_tem_tres_itens(self, stack):
        """Slide 3 deve ter 3 ItemNumerado e a imagem da galeria."""
        itens = stack.widget(2).findChildren(ItemNumerado)
        assert len(itens) == 3
        assert stack.widget(2).findChild(QLabel, "tutorial_anexos_imagem") is not None

    def test_slide_riscos_tem_cinco_tiles(self, stack):
        """Slide 4 deve ter 5 tiles de risco NR-26, com o QUIMICO marcado."""
        slide = stack.widget(3)
        tiles = slide.findChildren(QToolButton)
        assert len(tiles) == 5
        object_names = [tile.objectName() for tile in tiles]
        assert "tile_risco_QUIMICO" in object_names
        marcados = [tile for tile in tiles if tile.isChecked()]
        assert len(marcados) == 1
        assert marcados[0].objectName() == "tile_risco_QUIMICO"

    def test_slide_fatores_tem_dois_tiles_e_exemplo(self, stack):
        """Slide 5 deve ter tiles de Ato/Condicao e o bloco exemplo."""
        slide = stack.widget(4)
        assert slide.findChild(QWidget, "tutorial_fator_tile_ATO_INSEGURO") is not None
        assert slide.findChild(QWidget, "tutorial_fator_tile_CONDICAO_INSEGURA") is not None
        assert slide.findChild(QWidget, "tutorial_exemplo") is not None

    def test_slide_decisao_tem_tres_carimbos(self, stack):
        """Slide 6 deve ter 3 carimbos com apenas o Interditar marcado."""
        slide = stack.widget(5)
        carimbos = slide.findChildren(QWidget, "tutorial_carimbo")
        assert len(carimbos) == 3
        marcados = [c for c in carimbos if c.property("estado") == "marcado"]
        assert len(marcados) == 1

    def test_slide_vitoria_tem_duas_mini_telas(self, stack):
        """Slide 7 deve ter mini-telas win e over."""
        slide = stack.widget(6)
        telas = slide.findChildren(QWidget, "tutorial_mini_tela")
        assert len(telas) == 2
        estados = sorted(tela.property("estado") for tela in telas)
        assert estados == ["over", "win"]

    def test_slide_pronto_tem_cta(self, stack):
        """Slide 8 deve manter o CTA de finalizacao."""
        assert stack.widget(7).findChild(QPushButton, "tutorial_cta") is not None


class TestFinalizacao:
    """Pular, X e CTA devem emitir finalizado_solicitado com o motivo."""

    def test_pular_emite_motivo_novo_jogo(self, tutorial, qtbot):
        """Clicar em 'Pular tutorial' deve emitir finalizado_solicitado('novo_jogo')."""
        btn = tutorial.findChild(QPushButton, "tutorial_pular")
        with qtbot.waitSignal(tutorial.finalizado_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.NOVO_JOGO

    def test_voltar_slide_1_e_pular_mantem_motivo(self, tutorial, qtbot):
        """Pular apos navegar deve devolver o mesmo motivo recebido."""
        tutorial._TelaTutorial__ir_para_slide_seguinte()
        btn = tutorial.findChild(QPushButton, "tutorial_pular")
        with qtbot.waitSignal(tutorial.finalizado_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.NOVO_JOGO

    def test_x_emite_motivo_consulta(self, tutorial, qtbot):
        """X da title bar deve emitir finalizado_solicitado(CONSULTA)."""
        tutorial.exibir_tutorial(MotivoTutorial.CONSULTA)
        bar = tutorial.findChild(WindowTitleBar)
        btn = bar.findChild(QPushButton, "window_close_button")
        with qtbot.waitSignal(tutorial.finalizado_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.CONSULTA

    def test_cta_emite_motivo(self, tutorial, qtbot):
        """O CTA do ultimo slide deve emitir finalizado_solicitado com o motivo."""
        tutorial.exibir_tutorial(MotivoTutorial.CONSULTA)
        stack = tutorial.findChild(QStackedWidget)
        stack.setCurrentIndex(ULTIMO_SLIDE)
        btn = stack.widget(ULTIMO_SLIDE).findChild(QPushButton, "tutorial_cta")
        assert btn.text() == SlidePronto.TEXTO_CTA_CONSULTA
        with qtbot.waitSignal(tutorial.finalizado_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.CONSULTA

    def test_cta_texto_novo_jogo(self, tutorial):
        """Com motivo novo_jogo o CTA deve ser 'Começar inspeção'."""
        stack = tutorial.findChild(QStackedWidget)
        stack.setCurrentIndex(ULTIMO_SLIDE)
        btn = stack.widget(ULTIMO_SLIDE).findChild(QPushButton, "tutorial_cta")
        assert btn.text() == SlidePronto.TEXTO_CTA_NOVO_JOGO


class TestReentrancia:
    """Guard de reentrancia no exibir_tutorial."""

    def test_exibir_tutorial_visivel_ignora_novo_motivo(self, tutorial, qtbot):
        """Tutorial visivel deve ignorar nova chamada e manter o motivo original."""
        tutorial.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        parent_rect = QRect(0, 0, 1920, 1080)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        assert tutorial.isVisible()
        tutorial.exibir_tutorial(MotivoTutorial.CONSULTA)
        btn = tutorial.findChild(QPushButton, "tutorial_pular")
        with qtbot.waitSignal(tutorial.finalizado_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.NOVO_JOGO
        tutorial.hide()

    def test_exibir_tutorial_reseta_para_primeiro_slide(self, tutorial):
        """Abrir de novo deve voltar o stacked para o primeiro slide."""
        stack = tutorial.findChild(QStackedWidget)
        stack.setCurrentIndex(ULTIMO_SLIDE)
        tutorial.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        assert stack.currentIndex() == 0


class TestGeometria:
    """Tamanho 80% centrado, fallback ecra pequeno, maximizar/restaurar."""

    def test_exibir_com_tamanho_inicial_80_porcento_centrado(self, tutorial):
        """Com parent 1920x1080 a janela deve ter 80% do rect."""
        parent_rect = QRect(0, 0, 1920, 1080)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        assert tutorial.isVisible()
        assert tutorial.width() == int(1920 * 0.8)
        assert tutorial.height() == int(1080 * 0.8)
        tutorial.hide()

    def test_fallback_ecra_pequeno_preenche_rect(self, tutorial):
        """Parent com largura 80% < 1280 deve preencher o rect por inteiro."""
        parent_rect = QRect(0, 0, 1000, 900)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        assert tutorial.width() == 1000
        assert tutorial.height() == 900
        tutorial.hide()

    def test_maximizar_usa_rect_referencia_completo(self, tutorial):
        """Maximizar deve usar o rect de referencia completo e restaurar depois."""
        parent_rect = QRect(0, 0, 1920, 1080)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        tamanho_normal = tutorial.geometry()
        tutorial._TelaTutorial__on_maximizar_restaurar()
        assert tutorial._TelaTutorial__maximizado
        assert tutorial.geometry() == parent_rect
        tutorial._TelaTutorial__on_maximizar_restaurar()
        assert not tutorial._TelaTutorial__maximizado
        assert tutorial.geometry() == tamanho_normal
        tutorial.hide()

    def test_redimensionar_com_overlay_so_quando_visivel(self, tutorial):
        """Oculta, redimensionar_com_overlay nao muda geometria; visivel, muda."""
        parent_rect = QRect(0, 0, 1920, 1080)
        tutorial.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        tutorial.hide()
        geometria_oculta = tutorial.geometry()
        tutorial.redimensionar_com_overlay(QRect(0, 0, 1600, 1200))
        assert tutorial.geometry() == geometria_oculta
        tutorial.show()
        tutorial.redimensionar_com_overlay(QRect(0, 0, 1600, 1200))
        assert tutorial.width() == int(1600 * 0.8)
        assert tutorial.height() == int(1200 * 0.8)
        tutorial.hide()

    def test_maximizado_redimensionar_mantem_rect_completo(self, tutorial):
        """Maximizado, redimensionar_com_overlay deve manter o rect completo."""
        parent_rect = QRect(0, 0, 1920, 1080)
        tutorial.exibir_com_tamanho_inicial(parent_rect)
        tutorial._TelaTutorial__on_maximizar_restaurar()
        tutorial.redimensionar_com_overlay(QRect(0, 0, 1600, 900))
        assert tutorial.geometry() == QRect(0, 0, 1600, 900)
        tutorial.hide()
