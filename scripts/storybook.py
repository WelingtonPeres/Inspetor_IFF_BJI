"""
Storybook visual — mostra todas as telas do jogo em ordem para
verificar estilo e formatação sem precisar abrir o jogo completo.

Executar: python scripts/storybook.py
Navegar:  < >  (setas do teclado)  ou  botoes Anterior / Proximo
Sair:     Esc
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from view.desktop.menu import TelaMenuPrincipal
from view.desktop.taskbar import Taskbar
from view.expediente.paginas.selecao_perfil import PaginaSelecaoPerfil
from view.expediente.paginas.loading import PaginaLoading
from view.expediente.paginas.inspecao import PaginaInspecao
from view.expediente.paginas.diagnostico import PaginaDiagnostico
from view.expediente.paginas.game_win import GameWin
from view.expediente.paginas.game_over import GameOver
from view.expediente.widgets.sidebar import Sidebar
from view.infrastructure.layout_loader import LayoutLoader

RELATORIO_FAKE: Dict[str, Any] = {
    "titulo": "Laboratorio de Quimica — Bancada 03",
    "local": "Bloco A, Sala 104 — Campus Centro",
    "atividade": "Preparacao de solucoes com acidos concentrados",
    "envolvidos": ["Prof. Carlos Mendes", "Aux. Mariana Silva"],
    "texto_descricao": (
        "O local apresenta frascos de acido sulfurico destampados sobre a "
        "bancada. Nao ha extintor visivel no corredor. O avental da auxiliar "
        "esta rasgado na manga direita e os EPIs nao estao completos."
    ),
    "anexos": [],
}

DIAGNOSTICO_FAKE = DiagnosticoPontuacaoDTO(
    qnt_riscos_marcados=3,
    qnt_riscos_gabarito=4,
    qnt_riscos_corretos_marcados=2,
    estado_ato=True,
    estado_condicao=False,
    status_decisao_jogador="BOA",
    tempo_resposta_segundos=45.0,
    pontuacao_final=1500.0,
)


def _carregar_tema(app: QApplication) -> None:
    tema = "dark"
    nome = "style_light.qss" if tema == "light" else "style.qss"
    path = Path(__file__).resolve().parent.parent / "view" / "assets" / nome
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


class Storybook(QWidget):
    """Widget principal do storybook — QStackedWidget + navegacao."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Storybook — Inspetor IFF-BJI")
        self.setStyleSheet("background-color: #0d1117;")

        LayoutLoader.instance().set_screen(1920, 1080)

        self.__paginas: List[QWidget] = []
        self.__indice: int = 0

        self.__setup_ui()
        self.__criar_paginas()

    def __setup_ui(self) -> None:
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        nav = QHBoxLayout()
        nav.setContentsMargins(12, 8, 12, 8)

        self.__btn_anterior = QPushButton("Anterior")
        self.__btn_anterior.clicked.connect(self.__anterior)
        nav.addWidget(self.__btn_anterior)

        self.__label_pagina = QLabel("")
        self.__label_pagina.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_pagina.setStyleSheet("color: #E6EDF3; font-size: 14px;")
        nav.addWidget(self.__label_pagina, stretch=1)

        self.__btn_proximo = QPushButton("Proximo")
        self.__btn_proximo.clicked.connect(self.__proximo)
        nav.addWidget(self.__btn_proximo)

        raiz.addLayout(nav)

        self.__stack = QStackedWidget()
        raiz.addWidget(self.__stack, stretch=1)

    def __criar_paginas(self) -> None:
        fabricas = [
            ("1. Menu Principal", self.__criar_menu),
            ("2. Selecao de Perfil", self.__criar_selecao_perfil),
            ("3. Carregando", self.__criar_loading),
            ("4. Inspecao (relatorio)", self.__criar_inspecao),
            ("5. Diagnostico", self.__criar_diagnostico),
            ("6. Vitoria (GameWin)", self.__criar_game_win),
            ("7. Derrota (GameOver)", self.__criar_game_over),
            ("8. Taskbar", self.__criar_taskbar),
            ("9. Sidebar (isolada)", self.__criar_sidebar),
        ]

        for nome, fabrica in fabricas:
            pagina = self.__envolver(fabrica())
            self.__paginas.append((nome, pagina))
            self.__stack.addWidget(pagina)

        self.__ir_para(0)

    def __envolver(self, widget: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignCenter)
        return wrapper

    def __criar_menu(self) -> QWidget:
        return TelaMenuPrincipal()

    def __criar_selecao_perfil(self) -> QWidget:
        return PaginaSelecaoPerfil()

    def __criar_loading(self) -> QWidget:
        return PaginaLoading()

    def __criar_inspecao(self) -> QWidget:
        w = PaginaInspecao()
        w.renderizar_relatorio(RELATORIO_FAKE)
        return w

    def __criar_diagnostico(self) -> QWidget:
        w = PaginaDiagnostico()
        w.exibir_diagnostico(DIAGNOSTICO_FAKE)
        return w

    def __criar_game_win(self) -> QWidget:
        return GameWin(pontuacao_global=8500.0)

    def __criar_game_over(self) -> QWidget:
        return GameOver(pontuacao_global=3000.0)

    def __criar_taskbar(self) -> QWidget:
        return Taskbar()

    def __criar_sidebar(self) -> QWidget:
        return Sidebar()

    def __ir_para(self, indice: int) -> None:
        self.__indice = indice % len(self.__paginas)
        nome, _ = self.__paginas[self.__indice]
        self.__stack.setCurrentIndex(self.__indice)
        n = len(self.__paginas)
        self.__label_pagina.setText(f"{nome}   ({self.__indice + 1}/{n})")

    def __anterior(self) -> None:
        self.__ir_para(self.__indice - 1)

    def __proximo(self) -> None:
        self.__ir_para(self.__indice + 1)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.__anterior()
        elif event.key() == Qt.Key.Key_Right:
            self.__proximo()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    _carregar_tema(app)

    storybook = Storybook()
    storybook.resize(1100, 750)
    storybook.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
