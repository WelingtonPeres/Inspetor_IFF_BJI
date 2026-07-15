import logging
import time
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from view.expediente.widgets.anexo_preview import AnexoPreview
from view.widgets.midia.video_player import VideoPlayer
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer

logger = logging.getLogger(__name__)


class PaginaInspecao(QWidget):
    """Widget de inspecao com splitter 60/40, formulario e temporizador."""

    submeter_respostas = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_inspecao")
        self.setProperty("class", "pagina_inspecao")

        self.__label_titulo_relatorio: QLabel
        self.__anexo_preview: AnexoPreview
        self.__chk_riscos: Dict[str, QCheckBox]
        self.__chk_fatores: Dict[str, QCheckBox]
        self.__radio_decisao: QButtonGroup
        self.__btn_submeter: QPushButton
        self.__tempo_inicio_inspecao: float = 0.0
        self.__gallery: Optional[AnexoGallery] = None
        self.__media_viewer: Optional[MediaViewer] = None
        self.__anexos_data: List[Dict[str, Any]] = []
        self.__video_player_fullscreen: Optional[VideoPlayer] = None

        self.__setup_ui()

    def __setup_ui(self) -> None:
        splitter = self.__build_splitter()

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

    def __build_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        deck = self.__build_deck()
        prancheta = self.__build_prancheta()

        splitter.addWidget(deck)
        splitter.addWidget(prancheta)
        splitter.setStretchFactor(0, 60)
        splitter.setStretchFactor(1, 40)
        splitter.setHandleWidth(2)
        return splitter

    def __build_deck(self) -> QWidget:
        deck = QWidget(objectName="deck_observacao")
        deck_layout = QVBoxLayout(deck)

        self.__label_titulo_relatorio = QLabel("Aguardando relatório...")
        self.__label_titulo_relatorio.setObjectName("label_titulo_relatorio")
        self.__label_titulo_relatorio.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__label_titulo_relatorio.setWordWrap(True)
        deck_layout.addWidget(self.__label_titulo_relatorio)

        self.__anexo_preview = AnexoPreview()
        deck_layout.addWidget(self.__anexo_preview)

        deck_layout.addStretch()
        return deck

    def __build_prancheta(self) -> QWidget:
        prancheta = QWidget(objectName="prancheta")
        prancheta_layout = QVBoxLayout(prancheta)

        self.__chk_riscos = {}
        self.__chk_fatores = {}

        prancheta_layout.addWidget(self.__build_grupo_riscos())
        prancheta_layout.addWidget(self.__build_grupo_fatores())
        prancheta_layout.addWidget(self.__build_grupo_decisao())

        self.__btn_submeter = QPushButton("Submeter Respostas")
        self.__btn_submeter.setObjectName("btn_submeter")
        self.__btn_submeter.setProperty("class", "btn_primario")
        self.__btn_submeter.clicked.connect(self.__coletar_respostas)
        prancheta_layout.addWidget(self.__btn_submeter)

        prancheta_layout.addStretch()
        return prancheta

    def __build_grupo_riscos(self) -> QGroupBox:
        grupo = QGroupBox("Riscos Identificados")
        grupo.setObjectName("group_riscos")
        grupo.setProperty("class", "group_box")
        layout = QVBoxLayout(grupo)
        for risco in ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]:
            chk = QCheckBox(risco)
            chk.setObjectName(f"chk_risco_{risco}")
            chk.setProperty("class", "chk_risco")
            self.__chk_riscos[risco] = chk
            layout.addWidget(chk)
        return grupo

    def __build_grupo_fatores(self) -> QGroupBox:
        grupo = QGroupBox("Fatores de Insegurança")
        grupo.setObjectName("group_fatores")
        grupo.setProperty("class", "group_box")
        layout = QVBoxLayout(grupo)
        for fator in ["ATO_INSEGURO", "CONDICAO_INSEGURA"]:
            chk = QCheckBox(fator)
            chk.setObjectName(f"chk_fator_{fator}")
            chk.setProperty("class", "chk_fator")
            self.__chk_fatores[fator] = chk
            layout.addWidget(chk)
        return grupo

    def __build_grupo_decisao(self) -> QGroupBox:
        grupo = QGroupBox("Decisão Administrativa")
        grupo.setObjectName("group_decisao")
        grupo.setProperty("class", "group_box")
        layout = QHBoxLayout(grupo)
        self.__radio_decisao = QButtonGroup(grupo)
        for decisao in ["ADVERTIR", "INTERDITAR", "IGNORAR"]:
            radio = QRadioButton(decisao)
            radio.setObjectName(f"radio_decisao_{decisao}")
            radio.setProperty("class", "radio_decisao")
            self.__radio_decisao.addButton(radio)
            layout.addWidget(radio)
        return grupo

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        """Preenche o label do deck com titulo, local, atividade, envolvidos e descricao.

        Carrega o preview do primeiro anexo e reinicia o temporizador de inspecao.
        """
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        envolvidos = dados_relatorio.get("envolvidos") or []
        texto_envolvidos = ", ".join(envolvidos) if envolvidos else "Não informado"
        self.__label_titulo_relatorio.setText(
            f"Título: {dados_relatorio.get('titulo', '')}\n"
            f"Local: {dados_relatorio.get('local', '')}\n"
            f"Atividade: {dados_relatorio.get('atividade', '')}\n"
            f"Envolvidos: {texto_envolvidos}\n"
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
        self.limpar_formulario()
        self.__tempo_inicio_inspecao = time.time()

    def limpar_formulario(self) -> None:
        """Desmarca todos os checkboxes e radios."""
        for chk in self.__chk_riscos.values():
            chk.setChecked(False)
        for chk in self.__chk_fatores.values():
            chk.setChecked(False)
        if self.__radio_decisao.checkedButton():
            self.__radio_decisao.setExclusive(False)
            for btn in self.__radio_decisao.buttons():
                btn.setChecked(False)
            self.__radio_decisao.setExclusive(True)

    def __coletar_respostas(self) -> Dict[str, Any]:
        """Coleta os valores do formulario, emite signal e retorna o dict."""
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

    def configurar_midia(self, gallery: AnexoGallery, media_viewer: MediaViewer) -> None:
        """Recebe os overlays de midia e conecta os sinais."""
        self.__gallery = gallery
        self.__media_viewer = media_viewer
        self.__anexo_preview.ver_todos_anexos.connect(self.__abrir_gallery)
        self.__gallery.fechar_solicitado.connect(self.__fechar_gallery)
        self.__gallery.ampliar_solicitado.connect(self.__abrir_media_viewer)
        self.__media_viewer.fechar_solicitado.connect(self.__fechar_media_viewer)

    @Slot()
    def __abrir_gallery(self) -> None:
        if not self.__anexos_data:
            return
        self.__gallery.carregar_anexos(self.__anexos_data)
        self.__ancorar_overlay(self.__gallery)
        self.__gallery.show()
        self.__gallery.raise_()

    @Slot()
    def __fechar_gallery(self) -> None:
        self.__gallery.hide()

    @Slot(int)
    def __abrir_media_viewer(self, indice: int) -> None:
        if indice < 0 or indice >= len(self.__anexos_data):
            return
        anexo = self.__anexos_data[indice]
        if anexo.get("tipo_midia") == "IMAGEM":
            self.__media_viewer.exibir_imagem(anexo)
            self.__ancorar_overlay(self.__media_viewer)
            self.__media_viewer.show()
            self.__media_viewer.raise_()
            return
        if anexo.get("tipo_midia") == "VIDEO":
            player = self.__gallery.obter_player_atual()
            if isinstance(player, VideoPlayer):
                player.sair_fullscreen_solicitado.connect(self.__fechar_video_fullscreen, type=Qt.ConnectionType.UniqueConnection)
                player.entrar_fullscreen(self.__obter_anchor_ou_window())
                self.__video_player_fullscreen = player
                self.__gallery.hide()

    @Slot()
    def __fechar_media_viewer(self) -> None:
        self.__media_viewer.hide()

    @Slot()
    def __fechar_video_fullscreen(self) -> None:
        self.__video_player_fullscreen = None
        if self.__gallery:
            self.__ancorar_overlay(self.__gallery)
            self.__gallery.show()

    def __obter_anchor_ou_window(self) -> QWidget:
        """Retorna o _OverlayArea se existir; senao a top-level window.

        O fallback mantem o comportamento historico em cenarios standalone
        (testes), onde a galeria fica como janela top-level.
        """
        anchor = self.__obter_anchor_widget()
        if anchor is not None:
            return anchor
        return self.window()

    def __obter_anchor_widget(self) -> Optional[QWidget]:
        """Sobe na arvore de pais ate achar o _OverlayArea; None se nao houver."""
        parent: Optional[QWidget] = self.parentWidget()
        while parent is not None:
            if parent.objectName() == "overlay_area":
                return parent
            parent = parent.parentWidget()
        return None

    def __ancorar_overlay(self, overlay: QWidget) -> None:
        """Aplica o rect util ao overlay, reparentando so quando ha _OverlayArea.

        Com _OverlayArea real: reparenta para la e usa o rect acima da taskbar.
        Sem ele (standalone/testes): so aplica o rect da window, sem reparentar,
        preservando a galeria como top-level visivel.
        """
        anchor = self.__obter_anchor_widget()
        if anchor is None:
            overlay.setGeometry(self.window().rect())
            return
        if overlay.parent() is not anchor:
            overlay.setParent(anchor)
        overlay.setGeometry(anchor.rect())
