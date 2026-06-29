import logging
from PySide6.QtCore import Qt, QEvent, QPoint, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)


class WindowTitleBar(QFrame):
    close_requested = Signal()

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("window_title_bar")
        self.setProperty("class", "window_title_bar")
        self.__layout_loader = LayoutLoader.instance()
        self.__dragging = False
        self.__drag_offset = QPoint()
        self.__setup_ui(titulo)

    def __setup_ui(self, titulo: str):
        L = self.__layout_loader
        self.setFixedHeight(L.scaled("janela_sistema", "title_bar", "altura"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*L.scaled_margins("janela_sistema", "title_bar", "margens"))

        font = L.scaled("fontes", "ocorrencias", "modal_titulo_janela", "size")
        title_label = QLabel(titulo)
        title_label.setObjectName("window_title_text")
        title_label.setFont(QFont("Open Sans", font))
        layout.addWidget(title_label)

        layout.addStretch()

        self.__close_btn = QPushButton("✕")
        self.__close_btn.setObjectName("window_close_button")
        self.__close_btn.setProperty("class", "window_close_button")
        self.__close_btn.setFixedSize(L.scaled("janela_sistema", "title_bar", "altura"), L.scaled("janela_sistema", "title_bar", "altura"))
        self.__close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.__close_btn)

        self.installEventFilter(self)
        for child in self.findChildren(QWidget):
            if child is not self.__close_btn:
                child.installEventFilter(self)

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
