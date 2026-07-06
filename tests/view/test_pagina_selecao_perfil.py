"""
Suite completa de testes para o widget PaginaSelecaoPerfil.

Cobre estrutura basica, navegacao do carousel animado, confirmacao
via botao e teclado, e sincronizacao com o combo oculto.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton

from view.expediente.paginas.selecao_perfil import PaginaSelecaoPerfil
from view.expediente.widgets.character_carousel import CharacterCarousel
from view.expediente.configuracoes.perfis import make_profile_roster


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Garante que o QApplication existe para widgets Qt."""
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaSelecaoPerfil limpa."""
    return PaginaSelecaoPerfil()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaSelecaoPerfil.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, pagina):
        """
        A PaginaSelecaoPerfil deve ter objectName 'pagina_selecao_perfil'.

        Necessario para o seletor QSS #pagina_selecao_perfil.
        """
        # Arrange — fixture pagina ja instancia o widget

        # Act — obtem o objectName
        nome = pagina.objectName()

        # Assert
        assert nome == "pagina_selecao_perfil"

    def test_property_class(self, pagina):
        """
        A PaginaSelecaoPerfil deve ter property class 'pagina_selecao_perfil'.

        Necessario para o seletor QSS .pagina_selecao_perfil.
        """
        # Arrange — fixture pagina ja instancia o widget

        # Act — obtem a property "class"
        classe = pagina.property("class")

        # Assert
        assert classe == "pagina_selecao_perfil"

    def test_combo_perfil_tem_itens_corretos(self, pagina):
        """
        O QComboBox interno deve conter todos os itens de perfil.

        O numero de itens deve coincidir com make_profile_roster().
        """
        # Arrange — localiza o combo pelo objectName
        combo = pagina.findChild(QComboBox, "combo_perfil")
        total_perfis = len(make_profile_roster())

        # Assert — o combo existe e tem o numero correcto de itens
        assert combo is not None
        assert combo.count() == total_perfis

    def test_btn_confirmar_perfil_existe(self, pagina):
        """
        O QPushButton 'btn_confirmar_perfil' deve existir com texto 'Confirmar'.

        O botao e o unico meio de confirmar a selecao de perfil.
        """
        # Arrange — localiza o botao pelo objectName
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")

        # Assert — o botao existe e tem o texto correcto
        assert btn is not None
        assert btn.text() == "Confirmar"


class TestSignals:
    """
    Testes do signal perfil_confirmado emitido pela PaginaSelecaoPerfil.
    """

    def test_perfil_confirmado_signal(self, pagina, qtbot):
        """
        Clicar no botao de confirmar deve emitir perfil_confirmado
        com o texto do perfil actualmente selecionado no combo.

        O signal carrega uma string que corresponde ao currentText
        do QComboBox no momento do clique.
        """
        # Arrange — localiza o botao e o combo
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert btn is not None
        assert combo is not None
        perfil_esperado = combo.currentText()

        # Act & Assert — clica no botao e verifica o signal emitido
        with qtbot.waitSignal(pagina.perfil_confirmado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

        # Assert — o signal deve ter sido emitido com o texto do combo
        assert len(blocker.args) == 1
        assert blocker.args[0] == perfil_esperado


class TestCarouselNavegacao:
    """
    Testes de navegacao do CharacterCarousel integrado no PaginaSelecaoPerfil.

    Verifica existencia, indice inicial, navegacao lateral com slide_next/slide_previous,
    comportamento nos limites e actualizacao do label contador.
    """

    def test_carousel_existe(self, pagina):
        """
        O CharacterCarousel deve ser localizavel como filho do PaginaSelecaoPerfil.
        """
        # Arrange — fixture pagina ja instancia o widget

        # Act
        carousel = pagina.findChild(CharacterCarousel)

        # Assert
        assert carousel is not None

    def test_carousel_comeca_no_indice_0(self, pagina):
        """
        O carousel deve iniciar no indice 0, correspondente ao primeiro perfil.

        O indice 0 representa o perfil DEFAULT.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel

        # Act
        indice = carousel.current_index

        # Assert
        assert indice == 0

    def test_current_character_retorna_perfil_correto(self, pagina):
        """
        current_character() deve retornar o CharacterData do perfil activo.

        No indice 0, o char_id deve ser 'DEFAULT' e o name 'Padrão'.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel

        # Act
        perfil = carousel.current_character()

        # Assert
        assert perfil.char_id == "DEFAULT"
        assert perfil.name == "Padr\u00E3o"

    def test_slide_next_avanca_indice(self, pagina, qtbot):
        """
        Chamar slide_next() deve avancar o indice do carousel de 0 para 1.

        Aguarda a emissao do signal index_changed apos a animacao
        de deslize concluir.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        assert carousel.current_index == 0

        # Act — aguarda o fim da animacao de slide
        with qtbot.waitSignal(carousel.index_changed, timeout=1000):
            carousel.slide_next()

        # Assert
        assert carousel.current_index == 1

    def test_slide_previous_nao_ultrapassa_inicio(self, pagina):
        """
        slide_previous() no indice 0 nao deve alterar o indice.

        Deve executar a animacao de bump (elastica) sem modificar
        o indice do carousel.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        assert carousel.current_index == 0

        # Act — tenta recuar alem do primeiro perfil
        carousel.slide_previous()

        # Assert — o bump animation nao altera o indice
        assert carousel.current_index == 0

    def test_slide_next_nao_ultrapassa_fim(self, pagina):
        """
        slide_next() no ultimo indice nao deve ultrapassar o limite.

        Deve executar a animacao de bump (elastica) sem modificar
        o indice do carousel.
        """
        # Arrange — posiciona o carousel no ultimo perfil
        carousel = pagina._PaginaSelecaoPerfil__carousel
        ultimo = len(carousel.characters) - 1
        carousel._CharacterCarousel__index = ultimo
        carousel.update()
        assert carousel.current_index == ultimo

        # Act — tenta avancar alem do ultimo perfil
        carousel.slide_next()

        # Assert — o bump animation nao altera o indice
        assert carousel.current_index == ultimo

    def test_contador_atualiza_com_navegacao(self, pagina, qtbot):
        """
        O label_contador deve actualizar o texto apos navegacao no carousel.

        Apos slide_next() do indice 0 para 1, o texto deve mudar
        de '1 / N' para '2 / N'.
        """
        # Arrange
        total = len(make_profile_roster())
        carousel = pagina._PaginaSelecaoPerfil__carousel
        label_contador = pagina.findChild(QLabel, "label_contador_perfil")
        assert label_contador is not None
        assert label_contador.text() == f"1 / {total}"

        # Act — navega para o segundo perfil e aguarda a animacao
        with qtbot.waitSignal(carousel.index_changed, timeout=1000):
            carousel.slide_next()

        # Assert
        assert label_contador.text() == f"2 / {total}"


class TestCarouselConfirm:
    """
    Testes de confirmacao de perfil via botao e atalhos de teclado.

    Cobre o fluxo completo: navegar com o carousel e confirmar
    a escolha emitindo o signal perfil_confirmado com o char_id correcto.
    """

    def test_confirmar_emite_perfil_correto(self, pagina, qtbot):
        """
        Apos navegar para o indice 2, confirmar emite o terceiro perfil.

        Navega com slide_next duas vezes e verifica que o signal
        perfil_confirmado carrega o char_id 'T_INFORMATICA'.
        """
        # Arrange — navega do indice 0 ate ao indice 2
        carousel = pagina._PaginaSelecaoPerfil__carousel
        for _ in range(2):
            with qtbot.waitSignal(carousel.index_changed, timeout=1000):
                carousel.slide_next()
        assert carousel.current_index == 2

        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")
        assert btn is not None

        # Act & Assert — confirma via clique no botao
        with qtbot.waitSignal(pagina.perfil_confirmado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

        # Assert — o terceiro perfil (indice 2) e T_INFORMATICA
        assert len(blocker.args) == 1
        assert blocker.args[0] == "T_INFORMATICA"

    def test_key_enter_confirma(self, pagina, qtbot):
        """
        Pressionar Enter deve emitir perfil_confirmado com o perfil actual.

        Com o carousel no indice 0, o signal deve carregar 'DEFAULT'.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        assert carousel.current_index == 0
        pagina.setFocus()

        # Act & Assert — pressiona Enter e aguarda o signal
        with qtbot.waitSignal(pagina.perfil_confirmado, timeout=1000) as blocker:
            qtbot.keyClick(pagina, Qt.Key_Return)

        # Assert
        assert len(blocker.args) == 1
        assert blocker.args[0] == "DEFAULT"

    def test_key_left_navega(self, pagina, qtbot):
        """
        Pressionar Left no indice 0 nao deve lancar erro nem alterar o indice.

        O carousel executa a animacao de bump sem modificar o estado.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        assert carousel.current_index == 0
        pagina.setFocus()

        # Act — pressiona a seta esquerda
        qtbot.keyClick(pagina, Qt.Key_Left)

        # Assert — o indice permanece em 0 (apenas bump animation)
        assert carousel.current_index == 0

    def test_key_right_navega_e_confirma(self, pagina, qtbot):
        """
        Pressionar Right seguido de Enter deve navegar para o segundo
        perfil e emitir perfil_confirmado com 'T_QUIMICA'.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        assert carousel.current_index == 0
        pagina.setFocus()

        # Act — pressiona seta direita e aguarda a animacao de slide
        with qtbot.waitSignal(carousel.index_changed, timeout=1000):
            qtbot.keyClick(pagina, Qt.Key_Right)

        assert carousel.current_index == 1

        # Act & Assert — pressiona Enter e verifica o signal
        with qtbot.waitSignal(pagina.perfil_confirmado, timeout=1000) as blocker:
            qtbot.keyClick(pagina, Qt.Key_Return)

        # Assert — o segundo perfil (indice 1) e T_QUIMICA
        assert len(blocker.args) == 1
        assert blocker.args[0] == "T_QUIMICA"


class TestCarouselIntegracao:
    """
    Testes de integracao entre o carousel visivel e o combo oculto.

    O QComboBox com objectName 'combo_perfil' permanece escondido
    mas deve estar sempre sincronizado com o estado do carousel.
    """

    def test_combo_oculto_sincronizado(self, pagina, qtbot):
        """
        Apos slide_next(), o combo oculto deve reflectir o novo indice.

        O currentIndex do combo deve coincidir com o current_index do carousel.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert combo is not None
        assert combo.currentIndex() == 0

        # Act — navega para o segundo perfil
        with qtbot.waitSignal(carousel.index_changed, timeout=1000):
            carousel.slide_next()

        # Assert — combo e carousel sincronizados no mesmo indice
        assert carousel.current_index == 1
        assert combo.currentIndex() == 1

    def test_combo_oculto_conteudo_correto(self, pagina):
        """
        O combo oculto deve conter o char_id correspondente ao perfil actual.

        No indice inicial 0, o currentText do combo deve ser 'DEFAULT'.
        """
        # Arrange
        carousel = pagina._PaginaSelecaoPerfil__carousel
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert combo is not None
        assert carousel.current_index == 0

        # Act
        texto_combo = combo.currentText()
        perfil_actual = carousel.current_character().char_id

        # Assert
        assert texto_combo == perfil_actual
        assert texto_combo == "DEFAULT"
