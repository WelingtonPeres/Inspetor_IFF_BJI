import logging
from typing import Optional, Tuple
from PySide6.QtCore import Qt, QEvent, QPoint, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class WindowTitleBar(QFrame):
    close_requested = Signal()
    minimized_solicitado = Signal()
    maximized_solicitado = Signal()

    def __init__(
        self,
        titulo: str = "Expediente",
        altura: int = 32,
        altura_keys: Optional[Tuple[str, ...]] = None,
        mostrar_min_max: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("window_title_bar")
        self.setProperty("class", "window_title_bar")
        self.__dragging = False
        self.__drag_offset = QPoint()
        self.__altura_keys = altura_keys
        self.__mostrar_min_max = mostrar_min_max
        self.__main_layout: Optional[QHBoxLayout] = None
        self.__title_label: Optional[QLabel] = None
        self.__btn_minimize: Optional[QPushButton] = None
        self.__btn_maximize: Optional[QPushButton] = None
        self.__close_btn: Optional[QPushButton] = None
        self.__setup_ui(titulo, altura)
        # Recalcula altura/margens/fonte quando o fator de escala muda.
        LayoutLoader.instance().escala_atualizada.connect(self.__on_escala_atualizada)

    def __setup_ui(self, titulo: str, altura: int):
        L = LayoutLoader.instance()
        self.setFixedHeight(altura)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("tela_de_expediente", "title_bar", "margens"))
        self.__main_layout = layout

        font = L.scaled("fontes", "ocorrencias", "modal_titulo_janela", "size")
        title_label = QLabel(titulo)
        title_label.setObjectName("window_title_text")
        title_label.setFont(QFont("Courier New", font))
        self.__title_label = title_label
        layout.addWidget(title_label)

        layout.addStretch()

        btn_w = L.scaled("window_title_bar", "btn_tamanho")
        btn_h = L.scaled("window_title_bar", "btn_altura")

        if self.__mostrar_min_max:
            self.__btn_minimize = QPushButton("\u2014")
            self.__btn_minimize.setObjectName("window_minimize_button")
            self.__btn_minimize.setProperty("class", "window_minimize_button")
            self.__btn_minimize.setFixedSize(btn_w, btn_h)
            self.__btn_minimize.clicked.connect(self.minimized_solicitado.emit)
            layout.addWidget(self.__btn_minimize)

            self.__btn_maximize = QPushButton("\u25a1")
            self.__btn_maximize.setObjectName("window_maximize_button")
            self.__btn_maximize.setProperty("class", "window_maximize_button")
            self.__btn_maximize.setFixedSize(btn_w, btn_h)
            self.__btn_maximize.clicked.connect(self.maximized_solicitado.emit)
            layout.addWidget(self.__btn_maximize)

        self.__close_btn = QPushButton("\u2715")
        self.__close_btn.setObjectName("window_close_button")
        self.__close_btn.setProperty("class", "window_close_button")
        self.__close_btn.setFixedSize(btn_w, btn_h)
        self.__close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.__close_btn)

        self.installEventFilter(self)
        for child in self.findChildren(QWidget):
            if (
                child is not self.__close_btn
                and child is not self.__btn_minimize
                and child is not self.__btn_maximize
            ):
                child.installEventFilter(self)

    @Slot()
    def __on_escala_atualizada(self) -> None:
        if self.__altura_keys is not None:
            L = LayoutLoader.instance()
            self.reaplicar_dimensoes(L.scaled(*self.__altura_keys))
        else:
            self.reaplicar_dimensoes(self.height())

    def reaplicar_dimensoes(self, altura: int) -> None:
        """Re-aplica altura, margens e fonte do titulo (chamado em resize)."""
        L = LayoutLoader.instance()
        self.setFixedHeight(altura)
        if self.__main_layout is not None:
            self.__main_layout.setContentsMargins(
                *L.scaled_margins("tela_de_expediente", "title_bar", "margens")
            )
        if self.__title_label is not None:
            font = L.scaled("fontes", "ocorrencias", "modal_titulo_janela", "size")
            self.__title_label.setFont(QFont("Courier New", font))

        # Atualizar tamanho dos botoes
        btn_w = L.scaled("window_title_bar", "btn_tamanho")
        btn_h = L.scaled("window_title_bar", "btn_altura")
        for btn in (self.__btn_minimize, self.__btn_maximize, self.__close_btn):
            if btn is not None:
                btn.setFixedSize(btn_w, btn_h)

    def definir_titulo(self, titulo: str) -> None:
        label = self.findChild(QLabel, "window_title_text")
        if label:
            label.setText(titulo)

    def set_maximizado(self, maximizado: bool) -> None:
        if self.__btn_maximize is not None:
            self.__btn_maximize.setText("\u2750" if maximizado else "\u25a1")

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        parent = self.parentWidget()
        if not parent:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self.__dragging = True
            self.__drag_offset = (
                event.globalPosition().toPoint()
                - parent.mapToGlobal(parent.rect().topLeft())
            )
            parent.setCursor(Qt.CursorShape.ClosedHandCursor)
            return True

        elif event.type() == QEvent.Type.MouseMove and self.__dragging:
            parent.move(event.globalPosition().toPoint() - self.__drag_offset)
            return True

        elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if self.__dragging:
                self.__dragging = False
                parent.setCursor(Qt.CursorShape.ArrowCursor)
                return True

        return super().eventFilter(obj, event)
