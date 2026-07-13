"""
Suite de regressão para as brechas críticas de dimensionamento (B1-B7).

Valida que o LayoutLoader é alimentado em produção, que a janela não
bloqueia em 1920x1080, que o expediente recalcula a geometria a cada
abertura, que o overlay-pai notifica os filhos, e que os overlays de
mídia ancoram na área útil (acima da taskbar).
"""

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QWidget
from unittest.mock import MagicMock

from view.infrastructure.layout_loader import LayoutLoader
from view.main_window import JanelaPrincipal, _OverlayArea
from view.expediente.tela import TelaDeExpediente
from view.expediente.widgets.anexo_preview import AnexoPreview
from view.expediente.overlays.anexo_gallery import AnexoGallery


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Garante um QApplication para os testes de widgets."""
    return qapp


@pytest.fixture(autouse=True)
def reset_layout_loader():
    """Reset do singleton do LayoutLoader para isolar o estado entre testes."""
    LayoutLoader._instance = None
    yield
    LayoutLoader._instance = None


class TestLayoutLoaderSincronizacao:
    """
    Testes para B1 e B2: LayoutLoader deve ser alimentado em produção
    e reagir a redimensionamentos da janela principal.
    """

    def test_layout_loader_sincronizado_pelo_janela_principal(self):
        """
        Após criar e redimensionar a JanelaPrincipal, o LayoutLoader
        deve conter a resolução atual e o fator de escala correto.
        """
        # Arrange
        janela = JanelaPrincipal()

        # Act
        janela.resize(1920, 1080)
        QApplication.processEvents()

        # Assert
        loader = LayoutLoader.instance()
        assert loader._LayoutLoader__screen_w == 1920
        assert loader._LayoutLoader__screen_h == 1080
        assert loader._scale_factor() == pytest.approx(1.0)

    def test_layout_loader_reativo_a_redimensionamento(self):
        """
        Redimensionar a JanelaPrincipal para 1280x720 deve atualizar
        o fator de escala e emitir escala_atualizada.
        """
        # Arrange
        janela = JanelaPrincipal()
        janela.show()
        janela.resize(1920, 1080)
        QApplication.processEvents()

        loader = LayoutLoader.instance()
        spy = MagicMock()
        loader.escala_atualizada.connect(spy)

        # Act
        janela.resize(1280, 720)
        QApplication.processEvents()

        # Assert
        assert loader._LayoutLoader__screen_w == 1280
        assert loader._LayoutLoader__screen_h == 720
        assert loader._scale_factor() == pytest.approx(720 / 1080)
        spy.assert_called_once()


class TestJanelaPrincipalLimites:
    """
    Testes para B3: a janela não deve impor 1920x1080 como mínimo.
    """

    def test_janela_nao_bloqueia_resolucao_base(self):
        """
        O minimumSize deve ser inferior a 1920x1080 para permitir
        telas menores.
        """
        # Arrange / Act
        janela = JanelaPrincipal()
        minimo = janela.minimumSize()

        # Assert
        assert minimo.width() < 1920
        assert minimo.height() < 1080
        assert minimo.width() >= 1024
        assert minimo.height() >= 576


class TestTelaExpedienteDimensionamento:
    """
    Testes para B4: o expediente deve recalcular 80% do pai a cada
    chamada, sem ficar congelado na primeira geometria.
    """

    def test_exibir_com_tamanho_inicial_recalcula_a_cada_chamada(self):
        """
        Chamadas consecutivas com parent_rect diferentes devem produzir
        geometrias diferentes e centradas.
        """
        # Arrange
        pai = QWidget()
        pai.setGeometry(0, 0, 1200, 1000)
        expediente = TelaDeExpediente(parent=pai)
        rect_pequeno = QRect(0, 0, 1000, 800)
        rect_grande = QRect(0, 0, 1200, 1000)

        # Act
        expediente.exibir_com_tamanho_inicial(rect_pequeno)
        geo_pequena = expediente.geometry()

        expediente.exibir_com_tamanho_inicial(rect_grande)
        geo_grande = expediente.geometry()

        # Assert
        assert geo_pequena.width() == int(1000 * 0.8)
        assert geo_pequena.height() == int(800 * 0.8)
        assert geo_pequena.x() == (1000 - geo_pequena.width()) // 2
        assert geo_pequena.y() == (800 - geo_pequena.height()) // 2

        assert geo_grande.width() == int(1200 * 0.8)
        assert geo_grande.height() == int(1000 * 0.8)
        assert geo_grande.x() == (1200 - geo_grande.width()) // 2
        assert geo_grande.y() == (1000 - geo_grande.height()) // 2

        assert expediente._TelaDeExpediente__tamanho_normal == geo_grande


class TestOverlayNotificacao:
    """
    Testes para B5 e B6: o _OverlayArea notifica o expediente e o
    expediente maximizado acompanha o redimensionamento do pai.
    """

    def test_overlay_area_emite_signal_ao_redimensionar(self):
        """
        _OverlayArea.resizeEvent deve emitir overlay_resized com o novo
        rect, mesmo para overlays com auto_resize=False.
        """
        # Arrange
        overlay = _OverlayArea()
        overlay.show()
        overlay.resize(800, 600)
        filho = QWidget()
        overlay.add_overlay(filho, auto_resize=False)
        filho.show()

        spy = MagicMock()
        overlay.overlay_resized.connect(spy)

        # Act
        overlay.resize(1024, 768)
        QApplication.processEvents()

        # Assert
        spy.assert_called_once()
        rect_emitted = spy.call_args[0][0]
        assert rect_emitted.width() == 1024
        assert rect_emitted.height() == 768

    def test_expediente_reage_a_notificacao_do_overlay(self):
        """
        Ao receber redimensionar_com_overlay, o expediente visível deve
        invocar __reposicionar com o rect recebido.
        """
        # Arrange
        pai = QWidget()
        pai.setGeometry(0, 0, 1000, 800)
        pai.show()
        expediente = TelaDeExpediente(parent=pai)
        expediente.show()
        novo_rect = QRect(0, 0, 1000, 800)

        spy = MagicMock()
        expediente._TelaDeExpediente__reposicionar = spy

        # Act
        expediente.redimensionar_com_overlay(novo_rect)

        # Assert
        spy.assert_called_once_with(novo_rect)

    def test_expediente_maximizado_segue_pai(self):
        """
        Quando maximizado, __reposicionar deve fazer o expediente
        coincidir com o rect do pai.
        """
        # Arrange
        pai = QWidget()
        pai.setGeometry(0, 0, 1000, 800)
        expediente = TelaDeExpediente(parent=pai)
        expediente._TelaDeExpediente__maximizado = True
        novo_rect = QRect(0, 0, 1200, 900)

        # Act
        expediente._TelaDeExpediente__reposicionar(novo_rect)

        # Assert
        assert expediente.width() == novo_rect.width()
        assert expediente.height() == novo_rect.height()
        assert expediente.x() == novo_rect.x()
        assert expediente.y() == novo_rect.y()


class TestOverlaysNaoCobremTaskbar:
    """
    Teste para B7: AnexoGallery e MediaViewer devem ancorar no
    _OverlayArea, não na janela inteira (evitando cobrir a taskbar).
    """

    def test_galeria_ancora_no_overlay_area(self):
        """
        Abrir a galeria a partir da inspeção deve reparentar o overlay
        para o _OverlayArea e aplicar a geometria da área útil.
        """
        # Arrange
        janela = JanelaPrincipal()
        janela.resize(1920, 1080)
        janela.show()
        janela.exibir_selecao_perfil()

        dados_relatorio = {
            "titulo": "Teste",
            "local": "Lab",
            "atividade": "Teste",
            "texto_descricao": "Descricao",
            "anexos": [
                {
                    "tipo_midia": "IMAGEM",
                    "caminho_arquivo": "",
                }
            ],
        }
        janela.renderizar_relatorio(dados_relatorio)

        overlay_area = janela.findChild(QWidget, "overlay_area")
        assert overlay_area is not None

        preview = janela.findChild(AnexoPreview)
        assert preview is not None

        # Act
        preview.ver_todos_anexos.emit()
        QApplication.processEvents()

        # Assert
        galeria = janela.findChild(AnexoGallery)
        assert galeria is not None
        assert galeria.isVisible()
        assert galeria.parent() is overlay_area
        assert galeria.geometry() == overlay_area.rect()
        assert galeria.height() < janela.height()
