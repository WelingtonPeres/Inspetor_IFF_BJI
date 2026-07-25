import logging
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class PaginaDiagnostico(QWidget):
    """Widget de diagnostico com label de feedback e botao continuar."""

    continuar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_diagnostico")
        self.setProperty("class", "pagina_diagnostico")

        self.__layout_loader = LayoutLoader.instance()

        self.__label_feedback: QLabel
        self.__btn_continuar: QPushButton

        self.__setup_ui()
        self.__layout_loader.escala_atualizada.connect(self.__reaplicar_dimensoes)

    def __setup_ui(self) -> None:
        L = self.__layout_loader
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(L.scaled("pagina_diagnostico", "spacing"))

        self.__label_feedback = QLabel("")
        self.__label_feedback.setObjectName("label_diagnostico")
        self.__label_feedback.setProperty("class", "label_feedback")
        self.__label_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__label_feedback)

        self.__btn_continuar = QPushButton("Continuar")
        self.__btn_continuar.setObjectName("btn_continuar")
        self.__btn_continuar.setProperty("class", "btn_primario")
        self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
        self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))
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

    @Slot()
    def __reaplicar_dimensoes(self) -> None:
        """Reaplica dimensoes dependentes de escala apos resize."""
        L = self.__layout_loader
        if self.__btn_continuar is not None:
            self.__btn_continuar.setFixedHeight(L.scaled("pagina_diagnostico", "btn_altura"))
            self.__btn_continuar.setMinimumWidth(L.scaled("pagina_diagnostico", "btn_largura_min"))