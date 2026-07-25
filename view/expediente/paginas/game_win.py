import logging
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class GameWin(QFrame):
    """Tela de vitoria — expediente concluido com sucesso."""

    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()
    sair_solicitado = Signal()

    def __init__(self, pontuacao_global: float, parent=None):
        super().__init__(parent)
        self.setObjectName("game_win")
        self.setProperty("class", "game_win")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__layout_loader = LayoutLoader.instance()

        self.__label_titulo: QLabel
        self.__label_pontuacao: QLabel
        self.__btn_voltar: QPushButton
        self.__btn_sair: QPushButton
        self.__btn_jogar_novamente: QPushButton

        self.__setup_ui(pontuacao_global)
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def atualizar_pontuacao(self, pontuacao_global: float) -> None:
        self.__label_pontuacao.setText(f"Pontuação final: {pontuacao_global:.1f}")

    def __setup_ui(self, pontuacao_global: float) -> None:
        L = self.__layout_loader
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(L.scaled("game_win", "spacing"))

        self.__label_titulo = QLabel("EXPEDIENTE CONCLUÍDO")
        self.__label_titulo.setObjectName("label_endgame_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titulo.setWordWrap(True)
        font = QFont()
        font.setPointSize(L.scaled("game_win", "titulo_size"))
        self.__label_titulo.setFont(font)
        layout.addWidget(self.__label_titulo)

        self.__label_pontuacao = QLabel(f"Pontuação final: {pontuacao_global:.1f}")
        self.__label_pontuacao.setObjectName("label_endgame_pontuacao")
        self.__label_pontuacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(L.scaled("game_win", "pontuacao_size"))
        self.__label_pontuacao.setFont(font)
        layout.addWidget(self.__label_pontuacao)

        self.__btn_jogar_novamente = self.__criar_botao("Jogar de Novo", "btn_jogar_novamente", "btn_primario", self.jogar_novamente_solicitado.emit)
        layout.addWidget(self.__btn_jogar_novamente)

        self.__btn_voltar = self.__criar_botao("Voltar ao Menu", "btn_voltar_menu", "btn_secundario", self.voltar_menu_solicitado.emit)
        layout.addWidget(self.__btn_voltar)

        self.__btn_sair = self.__criar_botao("Sair do Jogo", "btn_sair_jogo", "btn_secundario", self.sair_solicitado.emit)
        layout.addWidget(self.__btn_sair)

    def __criar_botao(self, texto: str, object_name: str, class_prop: str, callback) -> QPushButton:
        L = self.__layout_loader
        btn = QPushButton(texto)
        btn.setObjectName(object_name)
        btn.setProperty("class", class_prop)
        btn.setFixedHeight(L.scaled("game_win", "btn_altura"))
        btn.setMinimumWidth(L.scaled("game_win", "btn_largura_min"))
        btn.clicked.connect(callback)
        return btn

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        L = self.__layout_loader
        if self.__label_titulo is not None:
            font = QFont()
            font.setPointSize(L.scaled("game_win", "titulo_size"))
            self.__label_titulo.setFont(font)
        if self.__label_pontuacao is not None:
            font = QFont()
            font.setPointSize(L.scaled("game_win", "pontuacao_size"))
            self.__label_pontuacao.setFont(font)
        for btn in (self.__btn_jogar_novamente, self.__btn_voltar, self.__btn_sair):
            if btn is not None:
                btn.setFixedHeight(L.scaled("game_win", "btn_altura"))
                btn.setMinimumWidth(L.scaled("game_win", "btn_largura_min"))