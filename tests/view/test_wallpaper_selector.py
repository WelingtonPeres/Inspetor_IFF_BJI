"""
Suite completa de testes para o componente WallpaperSelector.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton

from view.components.wallpaper_selector import WallpaperSelector


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def mock_qsettings():
    """Mock global do QSettings para evitar persistencia real."""
    with patch("view.components.wallpaper_selector.QSettings") as mock:
        instance = MagicMock()
        instance.value.return_value = ""
        mock.return_value = instance
        yield instance


@pytest.fixture
def wallpaper_selector(qtbot, mock_qsettings):
    """Retorna um WallpaperSelector com mock de QSettings."""
    dialog = WallpaperSelector()
    qtbot.addWidget(dialog)
    return dialog


class TestWallpaperSelector:
    """
    Testes para o componente WallpaperSelector.

    Verifica scan de imagens, thumbnails, preview, botoes,
    signals, persistencia em QSettings e comportamento ao redimensionar.
    """

    def test_object_name(self, wallpaper_selector):
        """O WallpaperSelector deve ter objectName 'wallpaper_selector'."""
        assert wallpaper_selector.objectName() == "wallpaper_selector"

    def test_imagens_carregadas(self, wallpaper_selector):
        """O scan dinamico deve encontrar pelo menos 5 imagens (ha 6 no diretorio)."""
        assert len(wallpaper_selector._WallpaperSelector__imagens) >= 5

    def test_imagens_sao_paths_validos(self, wallpaper_selector):
        """Todos os paths carregados devem existir em disco."""
        for img_path in wallpaper_selector._WallpaperSelector__imagens:
            assert img_path.exists(), f"Ficheiro nao encontrado: {img_path}"

    def test_thumbnail_widgets_criados(self, wallpaper_selector):
        """Deve existir um QFrame por imagem com objectName 'wallpaper_thumb_N'."""
        imagens = wallpaper_selector._WallpaperSelector__imagens
        for i in range(len(imagens)):
            frame = wallpaper_selector.findChild(QFrame, f"wallpaper_thumb_{i}")
            assert frame is not None, f"Thumbnail {i} nao encontrada"

    def test_btn_aplicar_desabilitado_inicialmente(self, wallpaper_selector):
        """O botao 'Aplicar' deve comecar desabilitado sem nenhuma selecao."""
        btn = wallpaper_selector.findChild(QPushButton, "btn_wallpaper_aplicar")
        assert btn is not None
        assert btn.isEnabled() is False

    def test_btn_aplicar_habilitado_ao_selecionar(self, wallpaper_selector):
        """Apos selecionar uma thumbnail, o botao 'Aplicar' deve ser habilitado."""
        btn = wallpaper_selector.findChild(QPushButton, "btn_wallpaper_aplicar")
        wallpaper_selector._WallpaperSelector__selecionar_thumbnail(0)
        assert btn.isEnabled() is True

    def test_btn_cancelar_fecha_dialogo(self, wallpaper_selector, qtbot):
        """Clicar em 'Cancelar' deve rejeitar (fechar) o dialogo."""
        btn = wallpaper_selector.findChild(QPushButton, "btn_wallpaper_cancelar")
        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert wallpaper_selector.result() == WallpaperSelector.DialogCode.Rejected

    def test_preview_atualizado_ao_selecionar(self, wallpaper_selector):
        """A QLabel de preview deve conter um pixmap apos selecionar uma imagem."""
        preview = wallpaper_selector.findChild(QLabel, "wallpaper_preview_label")
        assert preview is not None
        wallpaper_selector._WallpaperSelector__selecionar_thumbnail(0)
        assert preview.pixmap() is not None
        assert preview.pixmap().isNull() is False

    def test_wallpaper_selecionado_signal_emitido(self, wallpaper_selector, qtbot):
        """O signal wallpaper_selecionado deve ser emitido com caminho valido ao aplicar."""
        wallpaper_selector._WallpaperSelector__selecionar_thumbnail(0)
        with qtbot.waitSignal(
            wallpaper_selector.wallpaper_selecionado, timeout=1000
        ) as blocker:
            wallpaper_selector._WallpaperSelector__on_aplicar()
        caminho = Path(blocker.args[0])
        assert caminho.exists()

    def test_persistencia_qsettings(
        self, wallpaper_selector, mock_qsettings
    ):
        """O caminho selecionado deve ser salvo em QSettings ao aplicar."""
        wallpaper_selector._WallpaperSelector__selecionar_thumbnail(0)
        caminho_esperado = wallpaper_selector._WallpaperSelector__selected_path
        wallpaper_selector._WallpaperSelector__on_aplicar()
        mock_qsettings.setValue.assert_called_once_with(
            "wallpaper/caminho_atual", caminho_esperado
        )

    def test_explorar_botao_existe(self, wallpaper_selector):
        """O botao 'Procurar...' deve existir com objectName 'btn_wallpaper_explorar'."""
        btn = wallpaper_selector.findChild(QPushButton, "btn_wallpaper_explorar")
        assert btn is not None
        assert btn.text() == "Procurar..."

    def test_grid_refresh_ao_redimensionar(self, wallpaper_selector):
        """Redimensionar o dialogo nao deve quebrar a grid (mesmo numero de itens)."""
        grid = wallpaper_selector._WallpaperSelector__grid
        count_antes = grid.count()
        wallpaper_selector.resize(800, 600)
        count_depois = grid.count()
        assert count_depois == count_antes
