import logging
import time
from typing import Any, Dict, List
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.components.anexo_preview import AnexoPreview
from view.components.midia.video_player import VideoPlayer
from view.components.sidebar import Sidebar
from view.components.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader
from view.screens.anexo_gallery import AnexoGallery
from view.screens.media_viewer import MediaViewer
from view.screens.pagina_diagnostico import PaginaDiagnostico
from view.screens.pagina_loading import PaginaLoading
from view.screens.pagina_selecao_perfil import PaginaSelecaoPerfil

logger = logging.getLogger(__name__)


class TelaDeExpediente(QFrame):
    perfil_confirmado = Signal(str)
    submeter_respostas = Signal(dict)
    continuar_solicitado = Signal()
    voltar_menu_solicitado = Signal()
    minimized_solicitado = Signal()

    IDX_SELECAO_PERFIL = 0
    IDX_LOADING = 1
    IDX_INSPECAO = 2
    IDX_DIAGNOSTICO = 3
    IDX_ENDGAME = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tela_de_expediente")
        self.setProperty("class", "tela_expediente")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__maximizado: bool = False
        self.__inicializado: bool = False
        self.__tamanho_normal: Any = None

        self.__label_titulo_relatorio: QLabel
        self.__chk_riscos: Dict[str, QCheckBox]
        self.__chk_fatores: Dict[str, QCheckBox]
        self.__radio_decisao: QButtonGroup
        self.__btn_submeter: QPushButton
        self.__label_diagnostico: QLabel
        self.__btn_continuar: QPushButton
        self.__label_endgame_titulo: QLabel
        self.__label_endgame_pontuacao: QLabel
        self.__btn_voltar_menu: QPushButton
        self.__tempo_inicio_inspecao: float = 0.0
        self.__anexo_preview: AnexoPreview
        self.__anexo_gallery: AnexoGallery
        self.__media_viewer: MediaViewer
        self.__video_player_fullscreen: VideoPlayer | None = None
        self.__anexos_data: List[Dict] = []
        self.__sidebar: Sidebar
        self.__pagina_perfil: PaginaSelecaoPerfil
        self.__pagina_loading: PaginaLoading
        self.__pagina_diagnostico: PaginaDiagnostico
        self.__combo_perfil: QComboBox
        self.__loading_progress: QProgressBar

        self.__setup_ui()

    def __setup_ui(self):
        L = LayoutLoader.instance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        altura_bar = L.scaled("tela_de_expediente", "title_bar", "altura")
        self.__title_bar = WindowTitleBar(titulo="Expediente", altura=altura_bar, parent=self)
        self.__title_bar.close_requested.connect(self.__on_fechar)
        self.__title_bar.minimized_solicitado.connect(self.__on_minimizar)
        self.__title_bar.maximized_solicitado.connect(self.__on_maximizar_restaurar)
        layout.addWidget(self.__title_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.__sidebar = Sidebar()
        body.addWidget(self.__sidebar)

        self.__pagina_perfil = PaginaSelecaoPerfil()
        self.__pagina_perfil.perfil_confirmado.connect(self.__on_perfil_confirmado)
        self.__pagina_loading = PaginaLoading()
        self.__pagina_diagnostico = PaginaDiagnostico()
        self.__pagina_diagnostico.continuar_solicitado.connect(self.continuar_solicitado.emit)

        self.__stack = QStackedWidget()
        self.__stack.addWidget(self.__pagina_perfil)
        self.__stack.addWidget(self.__pagina_loading)
        self.__stack.addWidget(self.__criar_pagina_inspecao())
        self.__stack.addWidget(self.__pagina_diagnostico)
        self.__stack.addWidget(self.__criar_pagina_endgame())
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        body.addWidget(self.__stack, stretch=1)

        layout.addLayout(body, stretch=1)

        self.__stack.currentChanged.connect(self.__on_page_changed)
        self.__sidebar.setVisible(False)

        self.__anexo_gallery = AnexoGallery(self)
        self.__anexo_gallery.fechar_solicitado.connect(self.__fechar_gallery)
        self.__anexo_gallery.ampliar_solicitado.connect(self.__abrir_media_viewer)
        self.__anexo_gallery.hide()

        self.__media_viewer = MediaViewer(self)
        self.__media_viewer.fechar_solicitado.connect(self.__fechar_media_viewer)
        self.__media_viewer.hide()

    def __criar_pagina_selecao_perfil(self) -> QWidget:
        pagina = QWidget()
        sub = QVBoxLayout(pagina)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Selecione o perfil:")
        label.setObjectName("label_selecao_perfil")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.addWidget(label)

        self.__combo_perfil = QComboBox()
        self.__combo_perfil.setObjectName("combo_perfil")
        self.__combo_perfil.setProperty("class", "combo_padrao")
        self.__combo_perfil.addItems([
            "DEFAULT", "T_QUIMICA", "T_INFORMATICA", "T_AGROPECUARIA",
            "T_ALIMENTOS", "T_MEIO_AMBIENTE", "T_ZOOTECNIA",
            "CT_ALIMENTOS", "E_COMPUTACAO",
        ])
        sub.addWidget(self.__combo_perfil)

        btn = QPushButton("Confirmar")
        btn.setObjectName("btn_confirmar_perfil")
        btn.setProperty("class", "btn_primario")
        btn.clicked.connect(self.__on_perfil_confirmado)
        sub.addWidget(btn)

        return pagina

    @Slot(str)
    def __on_perfil_confirmado(self, perfil: str) -> None:
        self.exibir_tela_carregamento()
        self.perfil_confirmado.emit(perfil)

    def __criar_pagina_loading(self) -> QWidget:
        pagina = QWidget()
        sub = QVBoxLayout(pagina)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_sistema = QLabel("IFF SISTEMA DE INSPEÇÃO")
        label_sistema.setObjectName("label_loading_titulo")
        label_sistema.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_sistema.setFont(QFont("Courier New", 16))
        sub.addWidget(label_sistema)

        self.__loading_progress = QProgressBar()
        self.__loading_progress.setObjectName("loading_progress_bar")
        self.__loading_progress.setRange(0, 0)
        self.__loading_progress.setValue(0)
        sub.addWidget(self.__loading_progress)

        texto = QLabel("CARREGANDO EXPEDIENTE...")
        texto.setObjectName("label_loading_texto")
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.addWidget(texto)

        return pagina

    def __criar_pagina_inspecao(self) -> QWidget:
        pagina = QWidget()
        pagina.setProperty("class", "pagina_inspecao")

        splitter = QSplitter(Qt.Orientation.Horizontal)

        deck = QWidget(objectName="deck_observacao")
        deck_layout = QVBoxLayout(deck)

        self.__label_titulo_relatorio = QLabel("Aguardando relatório...")
        self.__label_titulo_relatorio.setObjectName("label_titulo_relatorio")
        self.__label_titulo_relatorio.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__label_titulo_relatorio.setWordWrap(True)
        deck_layout.addWidget(self.__label_titulo_relatorio)

        self.__anexo_preview = AnexoPreview()
        self.__anexo_preview.ver_todos_anexos.connect(self.__abrir_gallery)
        deck_layout.addWidget(self.__anexo_preview)

        deck_layout.addStretch()

        prancheta = QWidget(objectName="prancheta")
        prancheta_layout = QVBoxLayout(prancheta)

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
        prancheta_layout.addWidget(grupo_riscos)

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
        prancheta_layout.addWidget(grupo_fatores)

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
        prancheta_layout.addWidget(grupo_decisao)

        self.__btn_submeter = QPushButton("Submeter Respostas")
        self.__btn_submeter.setObjectName("btn_submeter")
        self.__btn_submeter.setProperty("class", "btn_primario")
        self.__btn_submeter.clicked.connect(self.__coletar_respostas)
        prancheta_layout.addWidget(self.__btn_submeter)

        prancheta_layout.addStretch()

        splitter.addWidget(deck)
        splitter.addWidget(prancheta)
        splitter.setStretchFactor(0, 60)
        splitter.setStretchFactor(1, 40)
        splitter.setHandleWidth(2)

        layout = QVBoxLayout(pagina)
        layout.addWidget(splitter)
        return pagina

    def __criar_pagina_diagnostico(self) -> QWidget:
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

    def __criar_pagina_endgame(self) -> QWidget:
        pagina = QWidget()
        pagina.setProperty("class", "pagina_endgame")
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_endgame_titulo = QLabel("")
        self.__label_endgame_titulo.setObjectName("label_endgame_titulo")
        self.__label_endgame_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_endgame_titulo.setWordWrap(True)
        layout.addWidget(self.__label_endgame_titulo)

        self.__label_endgame_pontuacao = QLabel("")
        self.__label_endgame_pontuacao.setObjectName("label_endgame_pontuacao")
        self.__label_endgame_pontuacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_endgame_pontuacao)

        self.__btn_voltar_menu = QPushButton("Voltar ao Menu")
        self.__btn_voltar_menu.setObjectName("btn_voltar_menu")
        self.__btn_voltar_menu.setProperty("class", "btn_primario")
        self.__btn_voltar_menu.clicked.connect(self.voltar_menu_solicitado.emit)
        layout.addWidget(self.__btn_voltar_menu)

        return pagina

    @Slot(int)
    def __on_page_changed(self, index: int) -> None:
        self.__sidebar.setVisible(index in [self.IDX_INSPECAO, self.IDX_DIAGNOSTICO])

    @Slot()
    def __coletar_respostas(self) -> Dict[str, Any]:
        riscos_marcados: List[str] = [
            nome for nome, chk in self.__chk_riscos.items() if chk.isChecked()
        ]
        fatores_marcados: List[str] = [
            nome for nome, chk in self.__chk_fatores.items() if chk.isChecked()
        ]
        radio_selecionado = self.__radio_decisao.checkedButton()
        decisao = radio_selecionado.text() if radio_selecionado else ""

        tempo_gasto = time.time() - self.__tempo_inicio_inspecao

        respostas = {
            "riscos": riscos_marcados,
            "fatores": fatores_marcados,
            "decisao": decisao,
            "tempo_segundos": int(tempo_gasto),
        }
        self.submeter_respostas.emit(respostas)
        return respostas

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

    @Slot()
    def __abrir_gallery(self) -> None:
        if not self.__anexos_data:
            return
        self.__anexo_gallery.carregar_anexos(self.__anexos_data)
        self.__anexo_gallery.setGeometry(self.rect())
        self.__anexo_gallery.show()
        self.__anexo_gallery.raise_()

    @Slot()
    def __fechar_gallery(self) -> None:
        self.__anexo_gallery.hide()

    @Slot(int)
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
            player = self.__anexo_gallery.obter_player_atual()
            if isinstance(player, VideoPlayer):
                player.sair_fullscreen_solicitado.connect(self.__fechar_video_fullscreen, type=Qt.ConnectionType.UniqueConnection)
                player.entrar_fullscreen(self)
                self.__video_player_fullscreen = player
                self.__anexo_gallery.hide()

    @Slot()
    def __fechar_media_viewer(self) -> None:
        self.__media_viewer.hide()

    @Slot()
    def __fechar_video_fullscreen(self) -> None:
        self.__video_player_fullscreen = None
        if self.__anexo_gallery:
            self.__anexo_gallery.setGeometry(self.rect())
            self.__anexo_gallery.show()

    @Slot()
    def __on_minimizar(self) -> None:
        self.hide()
        self.minimized_solicitado.emit()

    @Slot()
    def __on_maximizar_restaurar(self) -> None:
        if self.__maximizado:
            self.__restaurar_tamanho()
        else:
            self.__maximizar()
        self.__maximizado = not self.__maximizado
        self.__title_bar.set_maximizado(self.__maximizado)

    def __maximizar(self) -> None:
        parent = self.parentWidget()
        if parent:
            self.__tamanho_normal = self.geometry()
            self.setGeometry(parent.rect())

    def __restaurar_tamanho(self) -> None:
        if self.__tamanho_normal:
            self.setGeometry(self.__tamanho_normal)

    @Slot()
    def __on_fechar(self) -> None:
        self.hide()
        self.__maximizado = False
        self.__title_bar.set_maximizado(False)

    def exibir_selecao_perfil(self) -> None:
        self.__title_bar.definir_titulo("Seleção de Perfil")
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)

    def exibir_tela_carregamento(self) -> None:
        self.__title_bar.definir_titulo("Carregando...")
        self.__stack.setCurrentIndex(self.IDX_LOADING)

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        titulo = dados_relatorio.get("titulo", "Relatório")
        self.__title_bar.definir_titulo(f"Relatório: {titulo}")
        self.__label_titulo_relatorio.setText(
            f"Título: {dados_relatorio.get('titulo', '')}\n"
            f"Local: {dados_relatorio.get('local', '')}\n"
            f"Atividade: {dados_relatorio.get('atividade', '')}\n"
            f"Descrição: {dados_relatorio.get('texto_descricao', '')}"
        )
        self.__anexos_data = dados_relatorio.get("anexos", [])
        if self.__anexos_data:
            primeiro = self.__anexos_data[0]
            self.__anexo_preview.carregar_thumbnail(
                primeiro.get("caminho_arquivo", "")
            )
            self.__anexo_preview.definir_metadados(
                f"{len(self.__anexos_data)} anexo(s)"
            )
        self.__limpar_formulario_inspecao()
        self.__tempo_inicio_inspecao = time.time()
        self.__stack.setCurrentIndex(self.IDX_INSPECAO)

    def exibir_tela_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        logger.info("Exibindo diagnostico: %s", diagnostico)
        self.__title_bar.definir_titulo("Resultado da Inspeção")
        self.__pagina_diagnostico.exibir_diagnostico(diagnostico)
        self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)

    def exibir_tela_endgame(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        logger.info("Exibindo endgame: %.1f pts em %d dia(s), venceu=%s", pontuacao_global, dias_concluidos, venceu)
        self.__title_bar.definir_titulo("Fim do Expediente")

        if venceu:
            self.__label_endgame_titulo.setText("EXPEDIENTE CONCLUÍDO")
            self.__label_endgame_titulo.setProperty("status", "vitoria")
        else:
            self.__label_endgame_titulo.setText("EXPEDIENTE INTERROMPIDO")
            self.__label_endgame_titulo.setProperty("status", "derrota")
        self.__label_endgame_titulo.style().unpolish(self.__label_endgame_titulo)
        self.__label_endgame_titulo.style().polish(self.__label_endgame_titulo)

        self.__label_endgame_pontuacao.setText(
            f"Pontuação final: {pontuacao_global:.1f}\n"
            f"Dias concluídos: {dias_concluidos}"
        )
        self.__stack.setCurrentIndex(self.IDX_ENDGAME)

    def exibir_com_tamanho_inicial(self, parent_rect: Any) -> None:
        if not self.__inicializado:
            w = int(parent_rect.width() * 0.8)
            h = int(parent_rect.height() * 0.8)
            x = (parent_rect.width() - w) // 2
            y = (parent_rect.height() - h) // 2
            self.setGeometry(x, y, w, h)
            self.__tamanho_normal = self.geometry()
            self.__inicializado = True
        self.show()

    def reiniciar(self) -> None:
        self.__limpar_formulario_inspecao()
        self.__stack.setCurrentIndex(self.IDX_SELECAO_PERFIL)
        self.__title_bar.definir_titulo("Expediente")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.__maximizado and self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        if self.__anexo_gallery.isVisible():
            self.__anexo_gallery.setGeometry(self.rect())
        if self.__media_viewer.isVisible():
            self.__media_viewer.setGeometry(self.rect())
        if self.__video_player_fullscreen is not None:
            self.__video_player_fullscreen.entrar_fullscreen(self)
