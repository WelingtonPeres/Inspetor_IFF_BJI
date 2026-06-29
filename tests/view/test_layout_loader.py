"""
Suite completa de testes para o LayoutLoader.
"""

import pytest

from view.infrastructure.layout_loader import LayoutLoader


def teardown_module():
    LayoutLoader._instance = None


@pytest.fixture(autouse=True)
def reset_singleton():
    LayoutLoader._instance = None


@pytest.fixture
def loader():
    """Retorna uma instancia limpa do LayoutLoader."""
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return l


class TestLayoutLoader:
    """
    Testes para o LayoutLoader — singleton de layout responsivo.

    Verifica carregamento do JSON, escala proporcional e margens.
    """

    def test_carregar_json_sem_erro(self, loader):
        """
        Carrega o arquivo layout.json sem levantar excecao.

        O LayoutLoader deve conseguir ler e parsear o JSON
        do blueprint geometrico sem falhas.
        """
        assert loader is not None

    def test_singleton(self, loader):
        """
        Duas chamadas a instance() retornam o mesmo objeto.

        O LayoutLoader deve ser um singleton para garantir
        estado compartilhado de screen dimensions.
        """
        l2 = LayoutLoader.instance()
        assert loader is l2

    def test_scaled_referencia(self, loader):
        """
        Na resolucao de referencia (1920x1080) o fator de escala deve ser 1.0.

        scaled(80) deve retornar 80.
        """
        loader.set_screen(1920, 1080)
        valor = loader.scaled("atalho", "largura")
        assert valor == 80

    def test_scaled_1280x720(self, loader):
        """
        Em 1280x720 (resolucao minima) o fator deve ser ~0.66.

        scaled(80) deve retornar ~53 (80 * 720/1080 ≈ 53.33).
        """
        loader.set_screen(1280, 720)
        valor = loader.scaled("atalho", "largura")
        assert valor == 53

    def test_scaled_margens(self, loader):
        """
        scaled_margins retorna tupla na ordem (left, top, right, bottom).

        Para taskbar.margens {left:12, top:0, right:12, bottom:0}
        em resolucao referencia deve retornar (12, 0, 12, 0).
        """
        loader.set_screen(1920, 1080)
        margens = loader.scaled_margins("taskbar", "margens")
        assert margens == (12, 0, 12, 0)

    def test_get_raw(self, loader):
        """
        get() retorna o valor bruto do JSON sem escala.

        taskbar.start_botao.texto deve retornar "Iniciar".
        """
        texto = loader.get("taskbar", "start_botao", "texto")
        assert texto == "Iniciar"

    def test_get_lista_atalhos(self, loader):
        """
        get() na chave atalhos_lista retorna a lista de shortcuts.

        Deve conter pelo menos 3 atalhos.
        """
        atalhos = loader.get("atalhos_lista")
        assert len(atalhos) >= 3
        assert atalhos[0]["action"] == "iniciar"
