"""
Suite de validacao dos icones do tutorial (Etapa 0).

Garante que os PNGs copiados de /temp para view/assets/icons/tutorial/
existem, carregam com dimensoes validas e cumprem o minimo exigido.
O requisito de 200px (2x do render ~50px, retina) aplica-se aos icones
quadrados do selo da credencial; as imagens largas (anexo_*) sao
validadas apenas como imagens validas nao-nulas.
"""

from pathlib import Path

import pytest
from PySide6.QtGui import QPixmap

ICONES_ESPERADOS = [
    "pessoa.png",
    "boss.png",
    "anexo_tela.png",
    "anexo_botao.png",
]

ICONES_SELO_QUADRADOS = [
    "pessoa.png",
    "boss.png",
]

DIMENSAO_MINIMA_PX = 200


@pytest.fixture(autouse=True)
def _qt_app(qapp):
    """Garante QApplication disponivel para carregar QPixmap."""
    return qapp


@pytest.fixture
def dir_icones():
    """Caminho absoluto do diretorio dos icones do tutorial."""
    return (
        Path(__file__).resolve().parent.parent.parent
        / "view"
        / "assets"
        / "icons"
        / "tutorial"
    )


class TestIconesExistem:
    """Valida que a copia de /temp para assets foi feita."""

    def test_diretorio_contem_todos_os_icones_esperados(self, dir_icones):
        """O diretorio tutorial/ deve conter os 4 PNGs do pilote."""
        for nome in ICONES_ESPERADOS:
            assert (dir_icones / nome).is_file(), (
                f"Icone '{nome}' ausente em {dir_icones}"
            )


class TestIconesCarregam:
    """Valida que os PNGs sao imagens validas, nao zero-byte."""

    def test_pixmap_carrega_com_dimensoes_positivas(self, dir_icones):
        """Cada icone deve carregar como QPixmap com largura e altura > 0."""
        for nome in ICONES_ESPERADOS:
            pixmap = QPixmap(str(dir_icones / nome))
            assert not pixmap.isNull(), f"Icone '{nome}' nao carregou"
            assert pixmap.width() > 0, f"Icone '{nome}' com largura zero"
            assert pixmap.height() > 0, f"Icone '{nome}' com altura zero"


class TestIconesSeloDimensaoMinima:
    """Valida o minimo de 200px nos icones quadrados (selo da credencial)."""

    def test_icones_quadrados_atendem_ao_minimo_de_dimensao(self, dir_icones):
        """
        O selo exibe o icone a ~50px; com minimo de 200px (2x) o render
        fica nitido (retina), sem pixelacao.
        """
        for nome in ICONES_SELO_QUADRADOS:
            pixmap = QPixmap(str(dir_icones / nome))
            assert pixmap.width() >= DIMENSAO_MINIMA_PX, (
                f"Icone '{nome}' com largura {pixmap.width()}<{DIMENSAO_MINIMA_PX}px"
            )
            assert pixmap.height() >= DIMENSAO_MINIMA_PX, (
                f"Icone '{nome}' com altura {pixmap.height()}<{DIMENSAO_MINIMA_PX}px"
            )