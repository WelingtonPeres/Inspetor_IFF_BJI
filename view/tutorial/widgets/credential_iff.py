import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from view.infrastructure.layout_loader import LayoutLoader
from view.tutorial.widgets.assets_helper import (
    carregar_pixmap_escalado,
    tingir_pixmap,
)

logger = logging.getLogger(__name__)


class CredencialIFF(QFrame):
    """Credencial institucional do inspetor, partilhada pelos slides 1 e 8.

    Segue a ordem do modelo HTML: selo verde com icone branco, linha,
    label institucional, logo, nome e cargo em chip; sombra dura preta.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("tutorial_credential")
        self.setProperty("class", "credential_iff")
        self.__setup_ui()

    def __setup_ui(self) -> None:
        L = LayoutLoader.instance()
        self.setFixedSize(
            L.scaled("tutorial", "credential", "largura"),
            L.scaled("tutorial", "credential", "altura"),
        )
        self.__aplicar_sombra_dura()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("tutorial", "credential", "padding"))
        layout.setSpacing(L.scaled("tutorial", "chrome", "header_spacing"))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.__build_selo(), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__build_separador())
        layout.addWidget(
            self.__build_label_instituto(), alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.__build_logo(), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(self.__build_identidade())

    def __aplicar_sombra_dura(self) -> None:
        """Sombra deslocada sem blur (modelo: box-shadow 6px 6px 0 #000)."""
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(0)
        sombra.setOffset(6, 6)
        sombra.setColor(QColor("#000000"))
        self.setGraphicsEffect(sombra)

    def __build_selo(self) -> QFrame:
        L = LayoutLoader.instance()
        selo = QFrame()
        selo.setObjectName("credential_selo")
        tamanho = L.scaled("tutorial", "credential", "selo")
        selo.setFixedSize(tamanho, tamanho)
        selo_layout = QVBoxLayout(selo)
        selo_layout.setContentsMargins(0, 0, 0, 0)
        selo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        selo_icone = QLabel()
        selo_icone.setObjectName("credential_selo_icone")
        lado = L.scaled("tutorial", "credential", "selo_icone")
        selo_icone.setFixedSize(lado, lado)
        selo_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Modelo: mask-image + background branco; aqui o alfa do PNG
        # escuro e reaproveitado como mascara e pintado de branco.
        pixmap = tingir_pixmap(
            carregar_pixmap_escalado(lado, lado, "tutorial", "pessoa.png"),
            "#FFFFFF",
        )
        selo_icone.setPixmap(pixmap)
        selo_layout.addWidget(selo_icone)
        return selo

    def __build_label_instituto(self) -> QLabel:
        L = LayoutLoader.instance()
        label = QLabel("INSTITUTO FEDERAL FLUMINENSE")
        label.setObjectName("credential_label")
        label.setFont(
            QFont(
                L.get("tutorial", "font_familia"),
                L.scaled("tutorial", "credential", "label"),
            )
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def __build_identidade(self) -> QVBoxLayout:
        L = LayoutLoader.instance()
        familia = L.get("tutorial", "font_familia")
        painel = QVBoxLayout()
        painel.setSpacing(L.scaled("tutorial", "chrome", "header_spacing"))
        painel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nome = QLabel("Você")
        nome.setObjectName("credential_nome")
        nome.setFont(QFont(familia, L.scaled("tutorial", "credential", "nome")))
        nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        painel.addWidget(nome)

        cargo = QLabel("INSPETOR DE SEGURANÇA")
        cargo.setObjectName("credential_cargo")
        cargo.setFont(QFont(familia, L.scaled("tutorial", "credential", "cargo")))
        cargo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # O padding do QSS nao entra no sizeHint do QLabel e cortava o
        # texto; a folga do chip vem do margin, que entra.
        cargo.setMargin(6)
        painel.addWidget(cargo, alignment=Qt.AlignmentFlag.AlignCenter)

        return painel

    def __build_separador(self) -> QFrame:
        separador = QFrame()
        separador.setObjectName("credential_separador")
        separador.setFixedHeight(2)
        return separador

    def __build_logo(self) -> QLabel:
        L = LayoutLoader.instance()
        logo = QLabel()
        logo.setObjectName("credential_logo")
        altura = L.scaled("tutorial", "credential", "logo")
        logo.setPixmap(
            carregar_pixmap_escalado(altura * 4, altura, "iff_Icons", "logo-iff.png")
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return logo
