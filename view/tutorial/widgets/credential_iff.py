import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class CredencialIFF(QFrame):
    """Credencial institucional do inspetor, partilhada pelos slides 1 e 8."""

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("tutorial", "credential", "padding"))
        layout.setSpacing(L.scaled("tutorial", "chrome", "header_spacing"))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.__build_selo(), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(self.__build_identidade())
        layout.addWidget(self.__build_separador())
        layout.addWidget(self.__build_logo(), alignment=Qt.AlignmentFlag.AlignCenter)

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
        selo_icone.setFixedSize(
            L.scaled("tutorial", "credential", "selo_icone"),
            L.scaled("tutorial", "credential", "selo_icone"),
        )
        selo_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        selo_layout.addWidget(selo_icone)
        return selo

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
        painel.addWidget(cargo)

        return painel

    def __build_separador(self) -> QFrame:
        separador = QFrame()
        separador.setObjectName("credential_separador")
        separador.setFixedHeight(1)
        return separador

    def __build_logo(self) -> QLabel:
        L = LayoutLoader.instance()
        logo = QLabel()
        logo.setObjectName("credential_logo")
        logo.setFixedHeight(L.scaled("tutorial", "credential", "logo"))
        logo.setScaledContents(True)
        logo.setPixmap(self.__carregar_logo())
        return logo

    def __carregar_logo(self) -> QPixmap:
        caminho = (
            Path(__file__).resolve().parent.parent.parent
            / "assets"
            / "icons"
            / "iff_Icons"
            / "logo-iff.png"
        )
        if not caminho.exists():
            logger.warning("[Erro - CredencialIFF] Logo nao encontrado: %s", caminho)
            return QPixmap()
        return QPixmap(str(caminho))
