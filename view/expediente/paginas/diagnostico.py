import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO

logger = logging.getLogger(__name__)


class PaginaDiagnostico(QWidget):
    """Widget de diagnostico com label de feedback e botao continuar."""

    continuar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_diagnostico")
        self.setProperty("class", "pagina_diagnostico")

        self.__label_feedback: QLabel
        self.__btn_continuar: QPushButton

        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__label_feedback = QLabel("")
        self.__label_feedback.setObjectName("label_diagnostico")
        self.__label_feedback.setProperty("class", "label_feedback")
        self.__label_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_feedback)

        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar")
        self.__btn_continuar.setProperty("class", "btn_primario")
        self.__btn_continuar.clicked.connect(self.continuar_solicitado.emit)
        layout.addWidget(self.__btn_continuar)

    def exibir_diagnostico(self, diagnostico: DiagnosticoPontuacaoDTO) -> None:
        """Preenche o label com os dados do diagnostico."""
        logger.info("Diagnostico exibido: %s", diagnostico)
        self.__label_feedback.setText(
            f"Pontuação: {diagnostico.pontuacao_final:.1f}\n"
            f"Riscos corretos: {diagnostico.qnt_riscos_corretos_marcados}/{diagnostico.qnt_riscos_gabarito}\n"
            f"Decisão: {diagnostico.status_decisao_jogador}\n"
            f"Tempo: {diagnostico.tempo_resposta_segundos:.0f}s"
        )
