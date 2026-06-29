import logging
import time
from typing import Any, Dict, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.components.anexo_preview import AnexoPreview
from view.components.midia.video_player import VideoPlayer
from view.components.sidebar import Sidebar
from view.infrastructure.layout_loader import LayoutLoader
from view.screens.anexo_gallery import AnexoGallery
from view.screens.media_viewer import MediaViewer

logger = logging.getLogger(__name__)


class TelaInspecaoCheia(QFrame):
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    minimizar_solicitado = Signal()

    IDX_INSPECAO = 0
    IDX_DIAGNOSTICO = 1
    IDX_RESULTADO = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tela_inspecao_cheia")
        self.setProperty("class", "tela_cheia")

        self.__label_titulo_relatorio: QLabel
        self.__chk_riscos: Dict[str, QCheckBox]
        self.__chk_fatores: Dict[str, QCheckBox]
        self.__radio_decisao: QButtonGroup
        self.__btn_submeter: QPushButton
        self.__label_diagnostico: QLabel
        self.__btn_continuar: QPushButton
        self.__label_resultado: QLabel
        self.__tempo_inicio_inspecao: float = 0.0
        self.__anexo_preview: AnexoPreview
        self.__anexo_gallery: AnexoGallery
        self.__media_viewer: MediaViewer
        self.__video_player_fullscreen: VideoPlayer | None = None
        self.__anexos_data: List[Dict] = []

        self.__setup_ui()

    def __setup_ui(self):
        L = LayoutLoader.instance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("header_bar")
        header.setProperty("class", "header_bar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 4, 12, 4)

        header_titulo = QLabel("Relatório de Inspeção")
        header_titulo.setObjectName("header_title")
        header_layout.addWidget(header_titulo)
        header_layout.addStretch()

        btn_minimizar = QPushButton("—")
        btn_minimizar.setObjectName("minimizar_button")
        btn_minimizar.setProperty("class", "minimizar_button")
        btn_minimizar.clicked.connect(self.minimizar_solicitado.emit)
        header_layout.addWidget(btn_minimizar)

        layout.addWidget(header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.__sidebar = Sidebar()
        body.addWidget(self.__sidebar)

        self.__stack = QStackedWidget()
        self.__stack.addWidget(self.__criar_tela_inspecao())
        self.__stack.addWidget(self.__criar_tela_diagnostico())
        self.__stack.addWidget(self.__criar_tela_resultado())
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)
        body.addWidget(self.__stack, stretch=1)

        layout.addLayout(body, stretch=1)

        self.__anexo_gallery = AnexoGallery(self)
        self.__anexo_gallery.fechar_solicitado.connect(self.__fechar_gallery)
        self.__anexo_gallery.ampliar_solicitado.connect(self.__abrir_media_viewer)
        self.__anexo_gallery.hide()

        self.__media_viewer = MediaViewer(self)
        self.__media_viewer.fechar_solicitado.connect(self.__fechar_media_viewer)
        self.__media_viewer.hide()

    def __criar_tela_inspecao(self) -> QWidget:
        pagina = QWidget()
        pagina.setProperty("class", "pagina_inspecao")
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.__label_titulo_relatorio = QLabel("Aguardando relatório...")
        self.__label_titulo_relatorio.setObjectName("label_titulo_relatorio")
        self.__label_titulo_relatorio.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__label_titulo_relatorio.setWordWrap(True)
        layout.addWidget(self.__label_titulo_relatorio)

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

        self.__anexo_preview = AnexoPreview()
        self.__anexo_preview.ver_todos_anexos.connect(self.__abrir_gallery)
        layout.addWidget(self.__anexo_preview)

        self.__btn_submeter = QPushButton("Submeter Respostas")
        self.__btn_submeter.setObjectName("btn_submeter")
        self.__btn_submeter.setProperty("class", "btn_primario")
        self.__btn_submeter.clicked.connect(self.__coletar_respostas)
        layout.addWidget(self.__btn_submeter)

        return pagina

    def __criar_tela_diagnostico(self) -> QWidget:
        pagina = QWidget()
        pagina.setProperty("class", "pagina_diagnostico")
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_diagnostico = QLabel("")
        self.__label_diagnostico.setObjectName("label_diagnostico")
        self.__label_diagnostico.setProperty("class", "label_feedback")
        self.__label_diagnostico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_diagnostico)

        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar")
        self.__btn_continuar.setProperty("class", "btn_primario")
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        layout.addWidget(self.__btn_continuar)

        return pagina

    def __criar_tela_resultado(self) -> QWidget:
        pagina = QWidget()
        pagina.setProperty("class", "pagina_resultado")
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_resultado = QLabel("")
        self.__label_resultado.setObjectName("label_resultado")
        self.__label_resultado.setProperty("class", "label_feedback")
        self.__label_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_resultado.setWordWrap(True)
        layout.addWidget(self.__label_resultado)

        return pagina

    def __coletar_respostas(self) -> None:
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
        for chk in self.__chk_riscos.values():
            chk.setChecked(False)
        for chk in self.__chk_fatores.values():
            chk.setChecked(False)
        if self.__radio_decisao.checkedButton():
            self.__radio_decisao.setExclusive(False)
            for btn in self.__radio_decisao.buttons():
                btn.setChecked(False)
            self.__radio_decisao.setExclusive(True)

    def __abrir_gallery(self) -> None:
        if not self.__anexos_data:
            return
        self.__anexo_gallery.carregar_anexos(self.__anexos_data)
        self.__anexo_gallery.setGeometry(self.rect())
        self.__anexo_gallery.show()
        self.__anexo_gallery.raise_()

    def __fechar_gallery(self) -> None:
        self.__anexo_gallery.hide()

    def __abrir_media_viewer(self, indice: int) -> None:
        if indice < 0 or indice >= len(self.__anexos_data):
            return
        anexo = self.__anexos_data[indice]
        if anexo.get("tipo_midia") == "IMAGEM":
            self.__media_viewer.exibir_imagem(anexo)
            self.__media_viewer.setGeometry(self.rect())
            self.__media_viewer.show()
            self.__media_viewer.raise_()
        elif anexo.get("tipo_midia") == "VIDEO":
            player = self.__anexo_gallery.findChild(VideoPlayer)
            if player:
                player.entrar_fullscreen(self)
                self.__video_player_fullscreen = player
                self.__anexo_gallery.hide()

    def __fechar_media_viewer(self) -> None:
        self.__media_viewer.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__anexo_gallery.isVisible():
            self.__anexo_gallery.setGeometry(self.rect())
        if self.__media_viewer.isVisible():
            self.__media_viewer.setGeometry(self.rect())
        if self.__video_player_fullscreen is not None:
            vp = self.__video_player_fullscreen
            if vp.property("class") == "video_player" and vp.isVisible():
                vp.entrar_fullscreen(self)

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico: %s", diagnostico)
        self.__label_diagnostico.setText(
            f"Pontuação: {diagnostico.pontuacao_final:.1f}\n"
            f"Riscos corretos: {diagnostico.qnt_riscos_corretos_marcados}/{diagnostico.qnt_riscos_gabarito}\n"
            f"Decisão: {diagnostico.status_decisao_jogador}\n"
            f"Tempo: {diagnostico.tempo_resposta_segundos:.0f}s"
        )
        self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        self.__label_titulo_relatorio.setText(
            f"Título: {dados_relatorio.get('titulo', '')}\n"
            f"Local: {dados_relatorio.get('local', '')}\n"
            f"Atividade: {dados_relatorio.get('atividade', '')}\n"
            f"Descrição: {dados_relatorio.get('texto_descricao', '')}"
        )
        self.__anexos_data = dados_relatorio.get("anexos", [])
        if self.__anexos_data:
            primeiro = self.__anexos_data[0]
            self.__anexo_preview._carregar_thumbnail(
                primeiro.get("caminho_arquivo", "")
            )
            self.__anexo_preview._meta_label.setText(
                f"{len(self.__anexos_data)} anexo(s)"
            )
        self.__limpar_formulario_inspecao()
        self.__tempo_inicio_inspecao = time.time()
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int) -> None:
        logger.info("Exibindo resultado: %.1f pts em %d dia(s).", pontuacao_global, dias_concluidos)
        self.__label_resultado.setText(
            f"Campanha encerrada!\n\n"
            f"Pontuação final: {pontuacao_global:.1f}\n"
            f"Dias concluídos: {dias_concluidos}"
        )
        self.__stack.setCurrentIndex(self.IDX_RESULTADO)
