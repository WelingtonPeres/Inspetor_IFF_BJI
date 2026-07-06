import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class PaginaEndgame(QWidget):
    """Widget de fim de expediente com resultado e opcao de voltar ao menu."""

    voltar_menu_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_endgame")
        self.setProperty("class", "pagina_endgame")

        self.__label_titulo: QLabel
        self.__label_pontuacao: QLabel
        self.__btn_voltar: QPushButton

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_titulo = QLabel("")
        self.__label_titulo.setObjectName("label_endgame_titulo")
        self.__label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titulo.setWordWrap(True)
        layout.addWidget(self.__label_titulo)

        self.__label_pontuacao = QLabel("")
        self.__label_pontuacao.setObjectName("label_endgame_pontuacao")
        self.__label_pontuacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_pontuacao)

        self.__btn_voltar = QPushButton("Voltar ao Menu")
        self.__btn_voltar.setObjectName("btn_voltar_menu")
        self.__btn_voltar.setProperty("class", "btn_primario")
        self.__btn_voltar.clicked.connect(self.voltar_menu_solicitado.emit)
        layout.addWidget(self.__btn_voltar)

    def exibir_resultado(self, pontuacao_global: float, dias_concluidos: int, venceu: bool) -> None:
        """Preenche os labels com o resultado do expediente."""
        logger.info("Endgame: %.1f pts, venceu=%s", pontuacao_global, venceu)

        if venceu:
            self.__label_titulo.setText("EXPEDIENTE CONCLUÍDO")
            self.__label_titulo.setProperty("status", "vitoria")
        else:
            self.__label_titulo.setText("EXPEDIENTE INTERROMPIDO")
            self.__label_titulo.setProperty("status", "derrota")
        self.__label_titulo.style().unpolish(self.__label_titulo)
        self.__label_titulo.style().polish(self.__label_titulo)

        self.__label_pontuacao.setText(
            f"Pontuação final: {pontuacao_global:.1f}\n"
            f"Dias concluídos: {dias_concluidos}"
        )
