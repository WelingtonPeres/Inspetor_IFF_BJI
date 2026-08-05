from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from view.infrastructure.layout_loader import LayoutLoader


class DotsNavegacao(QWidget):
    """Fileira de dots do carrossel do tutorial (first-class collection).

    Dono unico da lista de dots: cria, dimensiona e re-estiliza cada um.
    O chrome so precisa de ``atualizar(indice_ativo)`` a cada mudanca de
    pagina e de ``reaplicar_dimensoes()`` quando a escala muda; cliques
    saem como ``slide_solicitado(int)``.
    """

    slide_solicitado = Signal(int)

    def __init__(
        self,
        total: int,
        layout_loader: Optional[LayoutLoader] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("tutorial_dots")

        self.__layout = layout_loader or LayoutLoader.instance()
        self.__dots: List[QPushButton] = []
        self.__indice_ativo = 0

        self.__setup_ui(total)
        self.__aplicar_dimensoes()

    def __setup_ui(self, total: int) -> None:
        linha = QHBoxLayout(self)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(self.__layout.scaled("tutorial", "dot", "gap"))
        linha.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for indice in range(total):
            dot = self.__criar_dot(indice)
            linha.addWidget(dot)
            self.__dots.append(dot)

    def __criar_dot(self, indice: int) -> QPushButton:
        dot = QPushButton()
        dot.setObjectName("tutorial_dot")
        dot.setProperty("class", "tutorial_dot")
        dot.setCheckable(False)
        dot.setCursor(Qt.CursorShape.PointingHandCursor)
        dot.clicked.connect(lambda _checked, i=indice: self.slide_solicitado.emit(i))
        return dot

    def atualizar(self, indice_ativo: int) -> None:
        """Marca o dot ativo e re-aplica tamanho/estilo de todos."""
        self.__indice_ativo = indice_ativo
        self.__aplicar_dimensoes()

    def reaplicar_dimensoes(self) -> None:
        """Re-aplica gap e tamanhos apos mudanca de escala."""
        self.__aplicar_dimensoes()

    def __aplicar_dimensoes(self) -> None:
        L = self.__layout
        self.layout().setSpacing(L.scaled("tutorial", "dot", "gap"))
        largura_inativo = L.scaled("tutorial", "dot", "largura")
        largura_ativo = L.scaled("tutorial", "dot", "largura_ativo")
        altura = L.scaled("tutorial", "dot", "altura")
        for indice, dot in enumerate(self.__dots):
            ativo = indice == self.__indice_ativo
            dot.setProperty("active", "true" if ativo else "false")
            dot.setFixedSize(largura_ativo if ativo else largura_inativo, altura)
            self.__repolish(dot)

    @staticmethod
    def __repolish(widget: QWidget) -> None:
        estilo = widget.style()
        estilo.unpolish(widget)
        estilo.polish(widget)
