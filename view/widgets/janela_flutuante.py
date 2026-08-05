import logging
from typing import Optional, Tuple

from PySide6.QtCore import QRect, Qt, Slot
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader

logger = logging.getLogger(__name__)

LIMIAR_LARGURA_MINIMA = 1280


class JanelaFlutuante(QFrame):
    """Chrome comum das "janelas" do sistema (padrao TelaDeExpediente).

    Como num sistema operacional, a moldura, a title bar e o comportamento
    de janela — geometria proporcional centrada com fallback de ecra
    pequeno, maximizar/restaurar, minimizar e fechar — sao identicos em
    todas as janelas; cada subclasse fornece apenas o conteudo. As regras
    de sobreposicao (z-order) ficam com quem regista a janela no overlay.

    O visual e partilhado via property ``janela_flutuante``: o QSS pinta
    fundo, moldura e radius com ``QFrame[janela_flutuante="true"]``.

    Uso: a subclasse chama ``_montar_chrome(titulo)`` no seu setup e
    adiciona o corpo ao layout devolvido. Hooks de comportamento
    (``_ao_fechar``, ``_ao_minimizar``) tem default neutro e podem ser
    sobrepostos para acrescentar sinais proprios.
    """

    def __init__(
        self,
        proporcao_keys: Tuple[str, ...],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setProperty("janela_flutuante", True)
        # Sem WA_TranslucentBackground: a "janela" e sempre widget filho do
        # overlay (nunca top-level real) e o atributo impedia o QSS de
        # pintar o fundo/moldura do proprio frame.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.__proporcao_keys = proporcao_keys
        self.__maximizado: bool = False
        self.__tamanho_normal: Optional[QRect] = None
        self.__rect_referencia: Optional[QRect] = None
        self._title_bar: Optional[WindowTitleBar] = None

    @property
    def _maximizado(self) -> bool:
        """Estado de maximizacao (leitura para subclasses)."""
        return self.__maximizado

    # ------------------------------------------------------------ chrome

    def _montar_chrome(self, titulo: str) -> QVBoxLayout:
        """Cria o layout raiz com a title bar padrao; o corpo vai abaixo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._title_bar = self.__build_title_bar(titulo)
        layout.addWidget(self._title_bar)
        return layout

    def __build_title_bar(self, titulo: str) -> WindowTitleBar:
        L = LayoutLoader.instance()
        title_bar = WindowTitleBar(
            titulo=titulo,
            altura=L.scaled("tela_de_expediente", "title_bar", "altura"),
            altura_keys=("tela_de_expediente", "title_bar", "altura"),
            parent=self,
        )
        title_bar.close_requested.connect(self._ao_fechar)
        title_bar.minimized_solicitado.connect(self._ao_minimizar)
        title_bar.maximized_solicitado.connect(self._alternar_maximizar)
        return title_bar

    # ----------------------------------------- comportamento de janela

    @Slot()
    def _ao_fechar(self) -> None:
        """Hook do X da title bar; subclasses acrescentam efeitos."""
        self._fechar()

    @Slot()
    def _ao_minimizar(self) -> None:
        """Hook do minimizar; subclasses acrescentam efeitos."""
        self.hide()

    def _fechar(self) -> None:
        """Esconde a janela e reseta o estado de maximizacao."""
        self.hide()
        self.__maximizado = False
        if self._title_bar is not None:
            self._title_bar.set_maximizado(False)

    @Slot()
    def _alternar_maximizar(self) -> None:
        if self.__maximizado:
            self.__restaurar_tamanho()
            self.__maximizado = False
            self._title_bar.set_maximizado(False)
            return
        self.__maximizar()
        self.__maximizado = True
        self._title_bar.set_maximizado(True)

    def __maximizar(self) -> None:
        rect = self.__rect_maximizado()
        if rect is not None:
            self.__tamanho_normal = self.geometry()
            self.setGeometry(rect)

    def __restaurar_tamanho(self) -> None:
        if self.__tamanho_normal is not None:
            self.setGeometry(self.__tamanho_normal)

    def __rect_maximizado(self) -> Optional[QRect]:
        if self.__rect_referencia is not None:
            return self.__rect_referencia
        parent = self.parentWidget()
        return parent.rect() if parent else None

    # ------------------------------------------------------- geometria

    def exibir_com_tamanho_inicial(self, parent_rect: QRect) -> None:
        """Posiciona (proporcao do rect de referencia) e mostra.

        Recalcula a cada chamada: reabrir apos fechar+redimensionar nao
        pode manter geometria velha congelada (B4).
        """
        self._reposicionar(parent_rect)
        self.show()

    @Slot(QRect)
    def redimensionar_com_overlay(self, rect: QRect) -> None:
        """Reage ao resize do overlay; so reposiciona se visivel (B5)."""
        if self.isVisible():
            self._reposicionar(rect)

    def _reposicionar(self, parent_rect: QRect) -> None:
        self.__rect_referencia = QRect(parent_rect)
        self.__tamanho_normal = self.__calcular_rect(parent_rect)
        if self.__maximizado:
            self.setGeometry(parent_rect)
            return
        self.setGeometry(self.__tamanho_normal)

    def __calcular_rect(self, parent_rect: QRect) -> QRect:
        L = LayoutLoader.instance()
        proporcao = L.get(*self.__proporcao_keys)
        w_prop = int(parent_rect.width() * proporcao)
        if w_prop < LIMIAR_LARGURA_MINIMA:
            return QRect(0, 0, parent_rect.width(), parent_rect.height())
        w = w_prop
        h = int(parent_rect.height() * proporcao)
        x = (parent_rect.width() - w) // 2
        y = (parent_rect.height() - h) // 2
        return QRect(x, y, w, h)
