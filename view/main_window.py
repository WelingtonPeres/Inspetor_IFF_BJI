import abc
import logging
import time
from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.interfaces.i_game_view import IGameView
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO

logger = logging.getLogger(__name__)


_ObjectType = type(QMainWindow)


class _MetaInterface(abc.ABCMeta, _ObjectType):
    """Metaclasse combinada para permitir heranca de QMainWindow + IGameView."""


class JanelaPrincipal(QMainWindow, IGameView, metaclass=_MetaInterface):
    """
    Janela principal do jogo. Implementa o contrato IGameView
    e gerencia as telas via QStackedWidget.
    """

    iniciar_solicitado = Signal()
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()

    IDX_MENU = 0
    IDX_SELECAO_PERFIL = 1
    IDX_INSPECAO = 2
    IDX_DIAGNOSTICO = 3
    IDX_RESULTADO = 4

    def __init__(self):
        """Inicializa a janela, layout e QStackedWidget com as telas."""
        super().__init__()

        self.setWindowTitle("Inspetor IFF-BJI: Análise de Risco")
        self.setMinimumSize(1280, 720)

        self.__btn_iniciar: QPushButton
        self.__combo_perfil: QComboBox
        self.__btn_confirmar_perfil: QPushButton
        self.__label_titulo_relatorio: QLabel
        self.__chk_riscos: Dict[str, QCheckBox]
        self.__chk_fatores: Dict[str, QCheckBox]
        self.__radio_decisao: QButtonGroup
        self.__btn_submeter: QPushButton
        self.__label_diagnostico: QLabel
        self.__btn_continuar: QPushButton
        self.__label_resultado: QLabel
        self.__tempo_inicio_inspecao: float = 0.0

        self.__stack = QStackedWidget()
        self.setCentralWidget(self.__stack)

        self.__stack.addWidget(self.__criar_tela_menu())
        self.__stack.addWidget(self.__criar_tela_selecao_perfil())
        self.__stack.addWidget(self.__criar_tela_inspecao())
        self.__stack.addWidget(self.__criar_tela_diagnostico())
        self.__stack.addWidget(self.__criar_tela_resultado())

        self.__stack.setCurrentIndex(self.IDX_MENU)

    def __criar_tela_menu(self) -> QWidget:
        """Cria e retorna o widget da tela de menu principal."""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignCenter)

        titulo = QLabel("Inspetor IFF-BJI: Análise de Risco")
        titulo.setObjectName("titulo_menu")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.__btn_iniciar = QPushButton("Iniciar")
        self.__btn_iniciar.setObjectName("btn_iniciar")
        self.__btn_iniciar.setProperty("class", "btn_primario")
        self.__btn_iniciar.clicked.connect(self.iniciar_solicitado.emit)
        layout.addWidget(self.__btn_iniciar)

        return pagina

    def __criar_tela_selecao_perfil(self) -> QWidget:
        """Cria e retorna o widget da tela de selecao de perfil."""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Selecione o perfil:")
        label.setObjectName("label_selecao_perfil")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.__combo_perfil = QComboBox()
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.setProperty("class", "combo_padrao")
        self.__combo_perfil.addItems([
            "T_QUIMICA", "T_INFORMATICA", "T_AGROPECUARIA",
            "T_ALIMENTOS", "T_MEIO_AMBIENTE", "T_ZOOTECNIA",
            "CT_ALIMENTOS", "E_COMPUTACAO",
        ])
        layout.addWidget(self.__combo_perfil)

        self.__btn_confirmar_perfil = QPushButton("Confirmar")
        self.__btn_confirmar_perfil.setObjectName("btn_confirmar_perfil")
        self.__btn_confirmar_perfil.setProperty("class", "btn_primario")
        self.__btn_confirmar_perfil.clicked.connect(
            lambda: self.perfil_confirmado.emit(self.__combo_perfil.currentText())
        )
        layout.addWidget(self.__btn_confirmar_perfil)

        return pagina

    def __criar_tela_inspecao(self) -> QWidget:
        """Cria e retorna o widget da tela de inspecao com o formulario de respostas."""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignTop)

        self.__label_titulo_relatorio = QLabel("Aguardando relatório...")
        self.__label_titulo_relatorio.setObjectName("label_titulo_relatorio")
        self.__label_titulo_relatorio.setAlignment(Qt.AlignTop)
        self.__label_titulo_relatorio.setWordWrap(True)
        layout.addWidget(self.__label_titulo_relatorio)

        # Riscos
        grupo_riscos = QGroupBox("Riscos Identificados")
        grupo_riscos.setObjectName("group_riscos")
        grupo_riscos.setProperty("class", "group_box")
        layout_riscos = QVBoxLayout(grupo_riscos)
        self.__chk_riscos = {}
        for risco in ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]:
            chk = QCheckBox(risco)
            chk.setObjectName(f"chk_risco_{risco}")
            chk.setProperty("class", "chk_risco")
            self.__chk_riscos[risco] = chk
            layout_riscos.addWidget(chk)
        layout.addWidget(grupo_riscos)

        # Fatores de Inseguranca
        grupo_fatores = QGroupBox("Fatores de Insegurança")
        grupo_fatores.setObjectName("group_fatores")
        grupo_fatores.setProperty("class", "group_box")
        layout_fatores = QVBoxLayout(grupo_fatores)
        self.__chk_fatores = {}
        for fator in ["ATO_INSEGURO", "CONDICAO_INSEGURA"]:
            chk = QCheckBox(fator)
            chk.setObjectName(f"chk_fator_{fator}")
            chk.setProperty("class", "chk_fator")
            self.__chk_fatores[fator] = chk
            layout_fatores.addWidget(chk)
        layout.addWidget(grupo_fatores)

        # Decisao Administrativa
        grupo_decisao = QGroupBox("Decisão Administrativa")
        grupo_decisao.setObjectName("group_decisao")
        grupo_decisao.setProperty("class", "group_box")
        layout_decisao = QHBoxLayout(grupo_decisao)
        self.__radio_decisao = QButtonGroup(grupo_decisao)
        for decisao in ["ADVERTIR", "INTERDITAR", "IGNORAR"]:
            radio = QRadioButton(decisao)
            radio.setObjectName(f"radio_decisao_{decisao}")
            radio.setProperty("class", "radio_decisao")
            self.__radio_decisao.addButton(radio)
            layout_decisao.addWidget(radio)
        layout.addWidget(grupo_decisao)

        self.__btn_submeter = QPushButton("Submeter Respostas")
        self.__btn_submeter.setObjectName("btn_submeter")
        self.__btn_submeter.setProperty("class", "btn_primario")
        self.__btn_submeter.clicked.connect(self.__coletar_respostas)
        layout.addWidget(self.__btn_submeter)

        return pagina

    def __coletar_respostas(self) -> None:
        """Coleta os campos do formulario e emite submeter_respostas."""
        riscos_marcados: List[str] = [
            nome for nome, chk in self.__chk_riscos.items() if chk.isChecked()
        ]
        fatores_marcados: List[str] = [
            nome for nome, chk in self.__chk_fatores.items() if chk.isChecked()
        ]
        radio_selecionado = self.__radio_decisao.checkedButton()
        decisao = radio_selecionado.text() if radio_selecionado else ""

        tempo_gasto = time.time() - self.__tempo_inicio_inspecao

        self.submeter_respostas.emit({
            "riscos": riscos_marcados,
            "fatores": fatores_marcados,
            "decisao": decisao,
            "tempo_segundos": int(tempo_gasto),
        })

    def __limpar_formulario_inspecao(self) -> None:
        """Reseta todos os campos do formulario de inspecao."""
        for chk in self.__chk_riscos.values():
            chk.setChecked(False)
        for chk in self.__chk_fatores.values():
            chk.setChecked(False)
        if self.__radio_decisao.checkedButton():
            self.__radio_decisao.setExclusive(False)
            for btn in self.__radio_decisao.buttons():
                btn.setChecked(False)
            self.__radio_decisao.setExclusive(True)

    def __criar_tela_diagnostico(self) -> QWidget:
        """Cria e retorna o widget da tela de diagnostico (feedback)."""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignCenter)

        self.__label_diagnostico = QLabel("")
        self.__label_diagnostico.setObjectName("label_diagnostico")
        self.__label_diagnostico.setProperty("class", "label_feedback")
        self.__label_diagnostico.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.__label_diagnostico)

        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar")
        self.__btn_continuar.setProperty("class", "btn_primario")
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        layout.addWidget(self.__btn_continuar)

        return pagina

    def __criar_tela_resultado(self) -> QWidget:
        """Cria e retorna o widget da tela de resultado final."""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignCenter)

        self.__label_resultado = QLabel("")
        self.__label_resultado.setObjectName("label_resultado")
        self.__label_resultado.setProperty("class", "label_feedback")
        self.__label_resultado.setAlignment(Qt.AlignCenter)
        self.__label_resultado.setWordWrap(True)
        layout.addWidget(self.__label_resultado)

        return pagina

    def inicializar(self) -> None:
        """Exibe a janela principal."""
        logger.info("JanelaPrincipal inicializada.")
        self.show()

    def fechar(self) -> None:
        """Fecha a janela e encerra a aplicacao."""
        logger.info("JanelaPrincipal fechando.")
        self.close()

    def exibir_menu(self) -> None:
        """Troca para a tela de menu principal."""
        logger.info("Exibindo menu principal.")
        self.__stack.setCurrentIndex(self.IDX_MENU)

    def exibir_selecao_perfil(self) -> None:
        """Troca para a tela de selecao de perfil."""
        logger.info("Exibindo selecao de perfil.")
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)

    def trocar_para_tela_inspecao(self) -> None:
        """Troca para a tela de inspecao do relatorio."""
        logger.info("Exibindo tela de inspecao.")
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        """Exibe o diagnostico da resposta submetida."""
        logger.info("Exibindo diagnostico: %s", diagnostico)
        self.__label_diagnostico.setText(
            f"Pontuação: {diagnostico.pontuacao_final:.1f}\n"
            f"Riscos corretos: {diagnostico.qnt_riscos_corretos_marcados}/{diagnostico.qnt_riscos_gabarito}\n"
            f"Decisão: {diagnostico.status_decisao_jogador}\n"
            f"Tempo: {diagnostico.tempo_resposta_segundos:.0f}s"
        )
        self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        """Renderiza os dados do relatorio na tela de inspecao e reseta o formulario."""
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        self.__label_titulo_relatorio.setText(
            f"Título: {dados_relatorio.get('titulo', '')}\n"
            f"Local: {dados_relatorio.get('local', '')}\n"
            f"Atividade: {dados_relatorio.get('atividade', '')}\n"
            f"Descrição: {dados_relatorio.get('texto_descricao', '')}"
        )
        self.__limpar_formulario_inspecao()
        self.__tempo_inicio_inspecao = time.time()

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int) -> None:
        """Exibe a tela de resultado final da campanha."""
        logger.info("Exibindo resultado: %.1f pts em %d dia(s).", pontuacao_global, dias_concluidos)
        self.__label_resultado.setText(
            f"Campanha encerrada!\n\n"
            f"Pontuação final: {pontuacao_global:.1f}\n"
            f"Dias concluídos: {dias_concluidos}"
        )
        self.__stack.setCurrentIndex(self.IDX_RESULTADO)

    def exibir_popup_erro(self, mensagem: str) -> None:
        """Exibe um popup de erro para o usuario."""
        logger.warning("Popup de erro: %s", mensagem)
        QMessageBox.critical(self, "Erro", mensagem)
