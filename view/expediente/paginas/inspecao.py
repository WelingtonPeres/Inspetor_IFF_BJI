import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from view.expediente.widgets.anexo_preview import AnexoPreview
from view.expediente.widgets.stamp_button import StampButton
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

        self.__labels_info: Dict[str, QLabel]
        self.__anexo_preview: AnexoPreview
        self.__chk_riscos: Dict[str, QToolButton]
        self.__chk_fatores: Dict[str, QToolButton]
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

        info_block = self.__build_info_block()
        deck_layout.addWidget(info_block)

        self.__anexo_preview = AnexoPreview()
        deck_layout.addWidget(self.__anexo_preview)

        deck_layout.addStretch()
        return deck

    def __build_info_block(self) -> QWidget:
        """Cria o bloco de informacoes do relatorio.

        O titulo e apresentado como texto puro (QLabel), enquanto os
        demais campos (local, atividade, envolvidos, descricao) usam
        QGroupBox com classe 'group_box'.
        """
        block = QWidget(objectName="info_block_relatorio")
        layout = QVBoxLayout(block)
        layout.setSpacing(12)

        self.__labels_info = {}

        titulo_label = self.__criar_label_info("titulo")
        titulo_label.setProperty("class", "label_info_titulo")
        layout.addWidget(titulo_label)

        campos = [
            ("local", "Local"),
            ("atividade", "Atividade"),
            ("envolvidos", "Envolvidos"),
            ("descricao", "Descrição"),
        ]
        for chave, rotulo in campos:
            label = self.__criar_label_info(chave)
            grupo = QGroupBox(rotulo)
            grupo.setObjectName(f"group_info_{chave}")
            grupo.setProperty("class", "group_box")
            grupo_layout = QVBoxLayout(grupo)
            grupo_layout.setContentsMargins(8, 12, 8, 8)
            grupo_layout.addWidget(label)
            layout.addWidget(grupo)

        return block

    def __criar_label_info(self, chave: str) -> QLabel:
        """Cria um QLabel padrao para exibicao de informacoes do relatorio."""
        label = QLabel("Aguardando relatório...")
        label.setObjectName(f"label_info_{chave}")
        label.setProperty("class", "label_info_valor")
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        label.setWordWrap(True)
        self.__labels_info[chave] = label
        return label

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

        layout = QGridLayout(grupo)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 8, 0, 0)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)

        labels = {
            "FISICO": "Fisico",
            "QUIMICO": "Quimico",
            "BIOLOGICO": "Biologico",
            "ERGONOMICO": "Ergonomico",
            "ACIDENTE": "Acidente",
        }

        linha_0 = [
            ("FISICO", 0),
            ("QUIMICO", 1),
            ("BIOLOGICO", 2),
        ]
        linha_1 = ["ERGONOMICO", "ACIDENTE"]

        for risco, col in linha_0:
            btn = self.__criar_tile_risco(risco, labels[risco])
            layout.addWidget(btn, 0, col)
            self.__chk_riscos[risco] = btn

        inner = QHBoxLayout()
        inner.setSpacing(10)
        inner.addStretch()
        for risco in linha_1:
            btn = self.__criar_tile_risco(risco, labels[risco])
            inner.addWidget(btn)
            self.__chk_riscos[risco] = btn
        inner.addStretch()
        layout.addLayout(inner, 1, 0, 1, 3)

        return grupo

    def __criar_tile_risco(self, risco: str, label: str) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName(f"tile_risco_{risco}")
        btn.setProperty("riscoTile", True)
        btn.setCheckable(True)
        btn.setText(label)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        btn.setMinimumSize(96, 96)

        icone_color = self.__resolver_icone_risco(risco, "_color")
        icone_white = self.__resolver_icone_risco(risco, "_dark")

        if icone_color is not None:
            btn.setProperty("icone_color", str(icone_color))
        if icone_white is not None:
            btn.setProperty("icone_white", str(icone_white))

        btn.setIconSize(QSize(64, 64))
        self.__aplicar_icone_risco(btn, btn.isChecked())
        btn.toggled.connect(lambda checked, b=btn: self.__aplicar_icone_risco(b, checked))

        return btn

    def __aplicar_icone_risco(self, btn: QToolButton, checked: bool) -> None:
        if checked:
            caminho = btn.property("icone_white")
        else:
            caminho = btn.property("icone_color")
        if caminho:
            btn.setIcon(QIcon(caminho))

    def __resolver_icone_risco(self, risco: str, sufixo: str) -> Optional[Path]:
        assets = Path(__file__).resolve().parent.parent.parent / "assets"
        caminho = assets / "icons" / "riscos" / f"risco_{risco.lower()}{sufixo}.png"
        return caminho if caminho.exists() else None

    def __build_grupo_fatores(self) -> QGroupBox:
        grupo = QGroupBox("Fatores de Inseguranca")
        grupo.setObjectName("group_fatores")
        grupo.setProperty("class", "group_box")

        layout = QHBoxLayout(grupo)
        layout.setSpacing(12)

        dados = {
            "ATO_INSEGURO": ("Ato Inseguro", "falha humana"),
            "CONDICAO_INSEGURA": ("Condicao Insegura", "falha do ambiente"),
        }
        icone_keys = {
            "ATO_INSEGURO": "ato",
            "CONDICAO_INSEGURA": "condicao",
        }

        for fator, (titulo, subtitulo) in dados.items():
            chave = icone_keys[fator]
            icone_color = self.__resolver_icone_fator(chave, "")
            icone_check = self.__resolver_icone_fator(chave, "_dark")

            btn = QPushButton()
            btn.setObjectName(f"tile_fator_{fator}")
            btn.setProperty("class", "fator_tile")
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            inner = QHBoxLayout(btn)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.setSpacing(10)

            icon_label = QLabel()
            icon_label.setObjectName(f"fator_icon_{fator}")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if icone_color is not None:
                icon_label.setPixmap(QPixmap(str(icone_color)).scaled(
                    48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
            inner.addWidget(icon_label, 3)

            texto_layout = QVBoxLayout()
            texto_layout.setSpacing(2)

            titulo_label = QLabel(titulo)
            titulo_label.setObjectName(f"fator_titulo_{fator}")
            titulo_label.setProperty("class", "fator_titulo")
            texto_layout.addWidget(titulo_label)

            subtitulo_label = QLabel(subtitulo)
            subtitulo_label.setObjectName(f"fator_subtitulo_{fator}")
            subtitulo_label.setProperty("class", "fator_subtitulo")
            texto_layout.addWidget(subtitulo_label)

            inner.addLayout(texto_layout, 7)

            if icone_color is not None:
                btn.setProperty("icone_color", str(icone_color))
            if icone_check is not None:
                btn.setProperty("icone_check", str(icone_check))
            btn.setProperty("icon_label", icon_label)

            self.__aplicar_icone_fator(btn, btn.isChecked())
            btn.toggled.connect(lambda checked, b=btn: self.__aplicar_icone_fator(b, checked))

            layout.addWidget(btn)
            self.__chk_fatores[fator] = btn

        return grupo

    def __aplicar_icone_fator(self, btn: QPushButton, checked: bool) -> None:
        icon_label = btn.property("icon_label")
        if icon_label is None:
            return
        if checked:
            caminho = btn.property("icone_check")
        else:
            caminho = btn.property("icone_color")
        if caminho:
            pixmap = QPixmap(caminho).scaled(
                48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)

    def __resolver_icone_fator(self, chave: str, sufixo: str) -> Optional[Path]:
        assets = Path(__file__).resolve().parent.parent.parent / "assets"
        caminho = assets / "icons" / "riscos" / f"{chave}{sufixo}.png"
        return caminho if caminho.exists() else None

    def __build_grupo_decisao(self) -> QGroupBox:
        grupo = QGroupBox("Decisão Administrativa")
        grupo.setObjectName("group_decisao")
        grupo.setProperty("class", "group_box")
        layout = QHBoxLayout(grupo)
        layout.setSpacing(12)
        layout.addStretch()
        self.__radio_decisao = QButtonGroup(grupo)
        for decisao in ["ADVERTIR", "INTERDITAR", "IGNORAR"]:
            stamp = StampButton(decisao)
            self.__radio_decisao.addButton(stamp)
            layout.addWidget(stamp)
        layout.addStretch()
        return grupo

    def renderizar_relatorio(self, dados_relatorio: Dict[str, Any]) -> None:
        """Preenche os labels do deck com titulo, local, atividade, envolvidos e descricao.

        Carrega o preview do primeiro anexo e reinicia o temporizador de inspecao.
        """
        logger.info("Renderizando relatorio: %s", dados_relatorio.get("titulo", ""))
        envolvidos = dados_relatorio.get("envolvidos") or []
        texto_envolvidos = ", ".join(envolvidos) if envolvidos else "Não informado"

        self.__labels_info["titulo"].setText(dados_relatorio.get("titulo", ""))
        self.__labels_info["local"].setText(dados_relatorio.get("local", ""))
        self.__labels_info["atividade"].setText(dados_relatorio.get("atividade", ""))
        self.__labels_info["envolvidos"].setText(texto_envolvidos)
        self.__labels_info["descricao"].setText(dados_relatorio.get("texto_descricao", ""))

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
