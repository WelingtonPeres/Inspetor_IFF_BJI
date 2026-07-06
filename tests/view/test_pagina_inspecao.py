"""
Suite de testes para a PaginaInspecao.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QRadioButton, QSplitter, QWidget

from view.screens.pagina_inspecao import PaginaInspecao
from view.components.anexo_preview import AnexoPreview


@pytest.fixture(autouse=True)
def qt_app(qapp):
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
        """A pagina deve conter 5 checkboxes de riscos."""
        for risco in ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]:
            chk = pagina.findChild(QCheckBox, f"chk_risco_{risco}")
            assert chk is not None
            assert chk.text() == risco

    def test_chk_fatores_2_itens(self, pagina):
        """A pagina deve conter 2 checkboxes de fatores."""
        for fator in ["ATO_INSEGURO", "CONDICAO_INSEGURA"]:
            chk = pagina.findChild(QCheckBox, f"chk_fator_{fator}")
            assert chk is not None
            assert chk.text() == fator

    def test_radio_decisao_3_itens(self, pagina):
        """A pagina deve conter 3 radio buttons de decisao."""
        for decisao in ["ADVERTIR", "INTERDITAR", "IGNORAR"]:
            radio = pagina.findChild(QRadioButton, f"radio_decisao_{decisao}")
            assert radio is not None
            assert radio.text() == decisao

    def test_btn_submeter_existe(self, pagina):
        """A pagina deve conter um QPushButton 'btn_submeter'."""
        btn = pagina.findChild(QPushButton, "btn_submeter")
        assert btn is not None
        assert btn.text() == "Submeter Respostas"

    def test_anexo_preview_integrado(self, pagina):
        """A pagina deve conter um AnexoPreview."""
        preview = pagina.findChild(AnexoPreview)
        assert preview is not None

    def test_label_titulo_relatorio_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_titulo_relatorio'."""
        label = pagina.findChild(QLabel, "label_titulo_relatorio")
        assert label is not None
        assert "Aguardando" in label.text()


class TestComportamento:
    """
    Testes do formulario: marcar/desmarcar, coletar, limpar, timer, signal.
    """

    def test_marcar_desmarcar_risco(self, pagina):
        """Marcar e desmarcar um checkbox de risco deve funcionar."""
        chk = pagina.findChild(QCheckBox, "chk_risco_FISICO")
        chk.setChecked(True)
        assert chk.isChecked()
        chk.setChecked(False)
        assert not chk.isChecked()

    def test_coletar_respostas_estrutura(self, pagina):
        """__coletar_respostas deve retornar dict com chaves esperadas."""
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert "riscos" in resultado
        assert "fatores" in resultado
        assert "decisao" in resultado
        assert "tempo_segundos" in resultado

    def test_coletar_respostas_com_valores(self, pagina):
        """Coletar respostas deve refletir selecoes."""
        pagina.findChild(QCheckBox, "chk_risco_FISICO").setChecked(True)
        pagina.findChild(QCheckBox, "chk_risco_QUIMICO").setChecked(True)
        pagina.findChild(QCheckBox, "chk_fator_ATO_INSEGURO").setChecked(True)
        pagina.findChild(QRadioButton, "radio_decisao_ADVERTIR").setChecked(True)
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert "FISICO" in resultado["riscos"]
        assert "QUIMICO" in resultado["riscos"]
        assert "ATO_INSEGURO" in resultado["fatores"]
        assert resultado["decisao"] == "ADVERTIR"
        assert isinstance(resultado["tempo_segundos"], int)

    def test_limpar_formulario_reseta_tudo(self, pagina):
        """limpar_formulario deve desmarcar todos os campos."""
        pagina.findChild(QCheckBox, "chk_risco_FISICO").setChecked(True)
        pagina.findChild(QCheckBox, "chk_fator_ATO_INSEGURO").setChecked(True)
        pagina.findChild(QRadioButton, "radio_decisao_ADVERTIR").setChecked(True)
        pagina.limpar_formulario()
        assert not pagina.findChild(QCheckBox, "chk_risco_FISICO").isChecked()
        assert not pagina.findChild(QCheckBox, "chk_fator_ATO_INSEGURO").isChecked()
        checked_radio = pagina.findChild(QRadioButton, "radio_decisao_ADVERTIR")
        assert not checked_radio.isChecked()

    def test_temporizador_reiniciado_em_renderizar(self, pagina):
        """renderizar_relatorio deve reiniciar o temporizador."""
        pagina.renderizar_relatorio({"titulo": "Teste"})
        assert pagina._PaginaInspecao__tempo_inicio_inspecao > 0

    def test_submeter_signal_emitido_com_payload(self, pagina, qtbot):
        """Clicar em submeter deve emitir submeter_respostas com dict."""
        pagina.findChild(QCheckBox, "chk_risco_FISICO").setChecked(True)
        btn = pagina.findChild(QPushButton, "btn_submeter")
        with qtbot.waitSignal(pagina.submeter_respostas, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        dados = blocker.args[0]
        assert isinstance(dados, dict)
        assert "riscos" in dados

    def test_renderizar_relatorio_atualiza_label(self, pagina):
        """renderizar_relatorio deve atualizar o label de titulo."""
        pagina.renderizar_relatorio({
            "titulo": "Lab Quimico",
            "local": "Bloco A",
            "atividade": "teste",
            "texto_descricao": "descricao",
        })
        label = pagina.findChild(QLabel, "label_titulo_relatorio")
        assert "Lab Quimico" in label.text()
        assert "Bloco A" in label.text()

    def test_submeter_sem_decisao_envia_string_vazia(self, pagina):
        """Se nenhum radio esta selecionado, decisao deve ser string vazia."""
        resultado = pagina._PaginaInspecao__coletar_respostas()
        assert resultado["decisao"] == ""
