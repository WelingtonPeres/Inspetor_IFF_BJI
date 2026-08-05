"""
Suite de testes para a PaginaInspecao.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QSplitter, QToolButton, QWidget

from view.expediente.paginas.inspecao import PaginaInspecao
from view.expediente.widgets.anexo_preview import AnexoPreview
from view.expediente.widgets.stamp_button import StampButton
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Fornece a QApplication do pytest-qt para todos os testes da view."""
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaInspecao com LayoutLoader configurado."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return PaginaInspecao()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaInspecao.

    Verifica objectName, property class, splitter, deck, prancheta,
    checkboxes, radios e botoes.
    """

    def test_object_name(self, pagina):
        """A PaginaInspecao deve ter objectName 'pagina_inspecao'."""
        assert pagina.objectName() == "pagina_inspecao"

    def test_property_class(self, pagina):
        """A PaginaInspecao deve ter property class 'pagina_inspecao'."""
        assert pagina.property("class") == "pagina_inspecao"

    def test_splitter_60_40_existe(self, pagina):
        """A pagina deve conter um QSplitter com 2 widgets."""
        splitter = pagina.findChild(QSplitter)
        assert splitter is not None
        assert splitter.count() == 2

    def test_deck_e_prancheta_existem(self, pagina):
        """Os widgets deck_observacao e prancheta devem existir."""
        deck = pagina.findChild(QWidget, "deck_observacao")
        assert deck is not None
        prancheta = pagina.findChild(QWidget, "prancheta")
        assert prancheta is not None

    def test_chk_riscos_5_itens(self, pagina):
        """A pagina deve conter 5 tiles de riscos como QToolButton."""
        labels = {
            "FISICO": "Fisico",
            "QUIMICO": "Quimico",
            "BIOLOGICO": "Biologico",
            "ERGONOMICO": "Ergonomico",
            "ACIDENTE": "Acidente",
        }
        for risco, label in labels.items():
            btn = pagina.findChild(QToolButton, f"tile_risco_{risco}")
            assert btn is not None
            assert btn.text() == label

    def test_chk_fatores_2_itens(self, pagina):
        """A pagina deve conter 2 tiles de fatores como QPushButton com layout interno."""
        labels = {
            "ATO_INSEGURO": "Ato Inseguro",
            "CONDICAO_INSEGURA": "Condicao Insegura",
        }
        for fator, label in labels.items():
            btn = pagina.findChild(QPushButton, f"tile_fator_{fator}")
            assert btn is not None
            titulo = btn.findChild(QLabel, f"fator_titulo_{fator}")
            assert titulo is not None
            assert titulo.text() == label

    def test_radio_decisao_3_itens(self, pagina):
        """A pagina deve conter 3 stamps de decisao."""
        for decisao in ["ADVERTIR", "INTERDITAR", "IGNORAR"]:
            stamp = pagina.findChild(StampButton, f"stamp_decisao_{decisao}")
            assert stamp is not None
            assert stamp.text() == decisao

    def test_btn_submeter_existe(self, pagina):
        """A pagina deve conter um QPushButton 'btn_submeter'."""
        btn = pagina.findChild(QPushButton, "btn_submeter")
        assert btn is not None
        assert btn.text() == "Submeter Respostas"

    def test_anexo_preview_integrado(self, pagina):
        """A pagina deve conter um AnexoPreview."""
        preview = pagina.findChild(AnexoPreview)
        assert preview is not None

    def test_labels_info_e_groupboxes_do_relatorio_existem(self, pagina):
        """A pagina deve conter os QLabel e QGroupBox de informacoes do relatorio.

        O campo titulo e renderizado como QLabel isolado; os demais campos
        usam QGroupBox como container.
        """
        for chave in ["titulo", "local", "atividade", "envolvidos", "descricao"]:
            label = pagina.findChild(QLabel, f"label_info_{chave}")
            assert label is not None
            assert "Aguardando" in label.text()
            if chave != "titulo":
                grupo = pagina.findChild(QGroupBox, f"group_info_{chave}")
                assert grupo is not None

        assert pagina.findChild(QGroupBox, "group_info_titulo") is None


class TestComportamento:
    """
    Testes do formulario: marcar/desmarcar, coletar, limpar, timer, signal.
    """

    def test_marcar_desmarcar_risco(self, pagina):
        """Marcar e desmarcar um tile de risco deve funcionar."""
        btn = pagina.findChild(QToolButton, "tile_risco_FISICO")
        btn.setChecked(True)
        assert btn.isChecked()
        btn.setChecked(False)
        assert not btn.isChecked()

    def test_coletar_respostas_estrutura(self, pagina):
        """__coletar_respostas deve retornar dict com chaves esperadas."""
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert "riscos" in resultado
        assert "fatores" in resultado
        assert "decisao" in resultado
        assert "tempo_segundos" in resultado

    def test_coletar_respostas_com_valores(self, pagina):
        """Coletar respostas deve refletir selecoes."""
        pagina.findChild(QToolButton, "tile_risco_FISICO").setChecked(True)
        pagina.findChild(QToolButton, "tile_risco_QUIMICO").setChecked(True)
        pagina.findChild(QPushButton, "tile_fator_ATO_INSEGURO").setChecked(True)
        pagina.findChild(StampButton, "stamp_decisao_ADVERTIR").setChecked(True)
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert "FISICO" in resultado["riscos"]
        assert "QUIMICO" in resultado["riscos"]
        assert "ATO_INSEGURO" in resultado["fatores"]
        assert resultado["decisao"] == "ADVERTIR"
        assert isinstance(resultado["tempo_segundos"], int)

    def test_limpar_formulario_reseta_tudo(self, pagina):
        """limpar_formulario deve desmarcar todos os campos."""
        pagina.findChild(QToolButton, "tile_risco_FISICO").setChecked(True)
        pagina.findChild(QPushButton, "tile_fator_ATO_INSEGURO").setChecked(True)
        pagina.findChild(StampButton, "stamp_decisao_ADVERTIR").setChecked(True)
        pagina.limpar_formulario()
        assert not pagina.findChild(QToolButton, "tile_risco_FISICO").isChecked()
        assert not pagina.findChild(QPushButton, "tile_fator_ATO_INSEGURO").isChecked()
        checked_stamp = pagina.findChild(StampButton, "stamp_decisao_ADVERTIR")
        assert not checked_stamp.isChecked()

    def test_temporizador_reiniciado_em_renderizar(self, pagina):
        """renderizar_relatorio deve reiniciar o temporizador."""
        pagina.renderizar_relatorio({"titulo": "Teste"})
        assert pagina._PaginaInspecao__tempo_inicio_inspecao > 0

    def test_submeter_signal_emitido_com_payload(self, pagina, qtbot):
        """Clicar em submeter deve emitir submeter_respostas com dict."""
        pagina.findChild(QToolButton, "tile_risco_FISICO").setChecked(True)
        btn = pagina.findChild(QPushButton, "btn_submeter")
        with qtbot.waitSignal(pagina.submeter_respostas, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        dados = blocker.args[0]
        assert isinstance(dados, dict)
        assert "riscos" in dados

    def test_renderizar_relatorio_atualiza_labels_info(self, pagina):
        """renderizar_relatorio deve atualizar todos os labels de informacao."""
        pagina.renderizar_relatorio({
            "titulo": "Lab Quimico",
            "local": "Bloco A",
            "atividade": "teste",
            "envolvidos": ["João", "Maria"],
            "texto_descricao": "descricao",
        })
        assert pagina.findChild(QLabel, "label_info_titulo").text() == "Lab Quimico"
        assert pagina.findChild(QLabel, "label_info_local").text() == "Bloco A"
        assert pagina.findChild(QLabel, "label_info_atividade").text() == "teste"
        assert pagina.findChild(QLabel, "label_info_envolvidos").text() == "João, Maria"
        assert pagina.findChild(QLabel, "label_info_descricao").text() == "descricao"

    def test_submeter_sem_decisao_envia_string_vazia(self, pagina):
        """Se nenhum radio esta selecionado, decisao deve ser string vazia."""
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert resultado["decisao"] == ""

    def test_renderizar_relatorio_sem_envolvidos_exibe_nao_informado(self, pagina):
        """Se envolvidos estiver vazio ou ausente, o label deve exibir 'Não informado'."""
        pagina.renderizar_relatorio({
            "titulo": "Lab Quimico",
            "local": "Bloco A",
            "atividade": "teste",
            "texto_descricao": "descricao",
        })
        assert pagina.findChild(QLabel, "label_info_envolvidos").text() == "Não informado"

    def test_renderizar_relatorio_com_envolvidos_vazios_exibe_nao_informado(self, pagina):
        """Lista vazia de envolvidos tambem deve renderizar 'Não informado'."""
        pagina.renderizar_relatorio({
            "titulo": "Lab Quimico",
            "local": "Bloco A",
            "atividade": "teste",
            "envolvidos": [],
            "texto_descricao": "descricao",
        })
        assert pagina.findChild(QLabel, "label_info_envolvidos").text() == "Não informado"


@pytest.fixture
def pagina_com_midia():
    """Retorna uma PaginaInspecao com overlays de midia configurados."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    pagina = PaginaInspecao()
    gallery = AnexoGallery()
    media_viewer = MediaViewer()
    pagina.configurar_midia(gallery, media_viewer)
    return pagina


class TestMidia:
    """
    Testes dos overlays de midia (gallery, media viewer).
    """

    def test_abrir_gallery_com_anexos(self, pagina_com_midia, qtbot):
        """renderizar_relatorio com anexos deve permitir abrir gallery."""
        pagina = pagina_com_midia
        gallery = pagina._PaginaInspecao__gallery
        pagina.renderizar_relatorio({
            "titulo": "Teste",
            "anexos": [{"tipo_midia": "IMAGEM", "caminho_arquivo": ""}],
        })
        pagina._PaginaInspecao__abrir_gallery()
        assert gallery.isVisible()

    def test_abrir_gallery_sem_anexos_nao_crasha(self, pagina_com_midia):
        """__abrir_gallery sem anexos nao deve crashar."""
        pagina = pagina_com_midia
        pagina.renderizar_relatorio({"titulo": "Teste"})
        pagina._PaginaInspecao__abrir_gallery()
