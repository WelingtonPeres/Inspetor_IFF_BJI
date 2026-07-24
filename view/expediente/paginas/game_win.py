import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QVBoxLayout

logger = logging.getLogger(__name__)


class GameWin(QFrame):
    """Tela de vitoria — expediente concluido com sucesso."""

    voltar_menu_solicitado = Signal()
    jogar_novamente_solicitado = Signal()

    def __init__(self, pontuacao_global: float, parent=None):
        super().__init__(parent)
        self.setObjectName("game_win")
        self.setProperty("class", "game_win")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__label_titulo: QLabel
        self.__label_pontuacao: QLabel
        self.__btn_voltar: QPushButton
        self.__btn_sair: QPushButton
        self.__btn_jogar_novamente: QPushButton

        self.__setup_ui(pontuacao_global)

    def atualizar_pontuacao(self, pontuacao_global: float) -> None:
        self.__label_pontuacao.setText(f"Pontuação final: {pontuacao_global:.1f}")

    def __setup_ui(self, pontuacao_global: float) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_titulo = QLabel("EXPEDIENTE CONCLUÍDO")
        self.__label_titulo.setObjectName("label_endgame_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titulo.setWordWrap(True)
        layout.addWidget(self.__label_titulo)

        self.__label_pontuacao = QLabel(f"Pontuação final: {pontuacao_global:.1f}")
        self.__label_pontuacao.setObjectName("label_endgame_pontuacao")
        self.__label_pontuacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_pontuacao)

        self.__btn_jogar_novamente = QPushButton("Jogar de Novo")
        self.__btn_jogar_novamente.setObjectName("btn_jogar_novamente")
        self.__btn_jogar_novamente.setProperty("class", "btn_primario")
        self.__btn_jogar_novamente.clicked.connect(self.jogar_novamente_solicitado.emit)
        layout.addWidget(self.__btn_jogar_novamente)

        self.__btn_voltar = QPushButton("Voltar ao Menu")
        self.__btn_voltar.setObjectName("btn_voltar_menu")
        self.__btn_voltar.setProperty("class", "btn_secundario")
        self.__btn_voltar.clicked.connect(self.voltar_menu_solicitado.emit)
        layout.addWidget(self.__btn_voltar)

        self.__btn_sair = QPushButton("Sair do Jogo")
        self.__btn_sair.setObjectName("btn_sair_jogo")
        self.__btn_sair.setProperty("class", "btn_secundario")
        self.__btn_sair.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.__btn_sair)
