# Análise Técnica de Interfaces para o Inspetor IFF BJI
## Comparativo Aprofundado e Justificação da Decisão pelo PySide6

---

**Projeto:** Inspetor IFF BJI  
**Documento:** Análise de Selecção de Framework UI  
**Data:** Junho de 2026  
**Versão:** 1.0

---

## 1. Introdução e Escopo

Este documento apresenta uma análise técnica aprofundada das principais bibliotecas de interface gráfica disponíveis para Python, com o objectivo de justificar a selecção do **PySide6** como framework de UI para o projecto *Inspetor IFF BJI*.

A análise parte do perfil concreto do projecto — não de critérios genéricos — e avalia cada alternativa em função da capacidade real de responder às exigências arquitecturais e visuais identificadas.

---

## 2. Perfil do Projecto

Antes de qualquer comparação técnica, é necessário caracterizar com precisão o tipo de software que o *Inspetor IFF BJI* representa. Esta caracterização é o filtro primário que elimina ou qualifica cada alternativa.

### 2.1 Natureza da Aplicação

O *Inspetor IFF BJI* não é um jogo de acção. É melhor descrito como um **jogo de simulação de ambiente de trabalho** — categoria que partilha mais características com ferramentas de produtividade desktop do que com motores de jogo tradicionais.

As três dimensões que definem o seu perfil são:

**Dimensão 1 — Interface pesada (UI-Heavy)**  
A interacção do utilizador ocorre quase exclusivamente através de elementos de UI: menus, formulários, caixas de diálogo, relatórios tabulares, checkboxes e painéis de controlo. Não há loop de física, não há renderização de sprites por frame, não há colisão de objectos. O "jogo" acontece na leitura e na tomada de decisão, não no reflexo ou no movimento.

**Dimensão 2 — Estética de Sistema Operativo**  
A apresentação visual do jogo simula um ambiente de trabalho fictício: ecrãs de inspeção, painéis de diagnóstico e formulários de decisão que se sucedem num fluxo linear. Esta estética é uma escolha de design central, não opcional.

**Dimensão 3 — Arquitectura MVP rigorosa no back-end**  
O `GameManager` centraliza a lógica de domínio e implementa o padrão Model-View-Presenter de forma estrita. A camada de UI deve funcionar como uma View pura — recebe dados formatados e emite eventos de utilizador, sem conter lógica de negócio. O acoplamento entre UI e back-end deve ser mínimo e bidireccional via contrato explícito.

### 2.2 Requisitos Funcionais Derivados

| Requisito | Descrição |
|---|---|
| RF-01 | Transições de estado entre telas (Menu → Perfil → Inspeção → Diagnóstico → Resultado) |
| RF-02 | Formulários com validação: campos de texto, dropdowns, checkboxes, botões |
| RF-03 | Visualização tabular de relatórios com ordenação e filtragem |
| RF-04 | Tema visual completamente customizável (paleta, fontes, bordas, ícones) |
| RF-05 | Comunicação assíncrona entre UI e GameManager sem bloqueio da interface |
| RF-06 | Integração limpa com padrão MVP — View não acede directamente ao Model |

---

## 3. Frameworks Avaliadas

Foram avaliadas seis alternativas, divididas em dois grupos: **concorrentes sérios** (que respondem parcialmente ao perfil) e **descartadas por incompatibilidade estrutural**.

### 3.1 PySide6

**Origem e manutenção:** PySide6 é o binding oficial do Qt 6 para Python, desenvolvido e mantido pela [The Qt Company](https://www.qt.io/). É a implementação de referência do projecto *Qt for Python*.

**Licença:** LGPL 3.0 — permite uso em aplicações fechadas e comerciais sem obrigação de publicar o código-fonte, desde que o PySide6 seja linkado dinamicamente (comportamento padrão).

**Fonte oficial:** [https://doc.qt.io/qtforpython-6/](https://doc.qt.io/qtforpython-6/)  
**Repositório:** [https://code.qt.io/cgit/pyside/pyside-setup.git/](https://code.qt.io/cgit/pyside/pyside-setup.git/)  
**Instalação:** `pip install PySide6`

#### 3.1.1 Capacidades Relevantes para o Projecto

**Navegação por estado com QStackedWidget**  
`QStackedWidget` implementa o padrão de "pilha de ecrãs" — cada tela (Menu, Seleção de Perfil, Inspeção, Diagnóstico, Resultado) é um `QWidget` independente. Apenas um está visível de cada vez, controlado por `setCurrentIndex(indice)`. Isto é exactamente o que o fluxo linear do MVP exige (Menu → Inspeção → Diagnóstico → Resultado), sem a complexidade de janelas flutuantes.

```python
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self._criar_menu())       # indice 0
        self.stack.addWidget(self._criar_inspecao())   # indice 1
        self.stack.addWidget(self._criar_diagnostico()) # indice 2

    def exibir_menu(self):
        self.stack.setCurrentIndex(0)

    def exibir_inspecao(self):
        self.stack.setCurrentIndex(1)
```

**Estilização com Qt Style Sheets (QSS)**  
O QSS é uma linguagem de estilos análoga ao CSS, aplicável a qualquer widget ou hierarquia de widgets. Permite definir cores, fontes, bordas, margens, estados hover/pressed/disabled, e pseudo-elementos — o suficiente para replicar a estética visual de um SO completo.

```css
/* Tema de inspetor - exemplo de QSS para o Inspetor IFF BJI */
QMainWindow {
    background-color: #0A171C;
}

QGroupBox {
    background-color: #14312B;
    border: 1px solid #1D4940;
    color: #FDE2CF;
    font-weight: bold;
}

QGroupBox::title {
    color: #2F9E41;
    padding: 4px 8px;
}

QPushButton {
    background-color: #2F9E41;
    color: #FDE2CF;
    border: 1px solid #1D4940;
    border-radius: 4px;
    padding: 6px 14px;
}

QPushButton:hover {
    background-color: #37a547;
    border-color: #2F9E41;
}
```

**Model/View para relatórios tabulares**  
O Qt implementa o padrão Model/View de forma nativa. `QAbstractTableModel` define o contrato de dados; `QTableView` exibe-os. A View recebe DTOs agnósticos do GameManager e converte-os internamente em `QAbstractTableModel` para exibição otimizada, mantendo o limite do MVP — o GameManager permanece puro e sem dependência de Qt.

```python
from PySide6.QtCore import QAbstractTableModel, Qt

class RelatorioModel(QAbstractTableModel):
    def __init__(self, dados, cabecalhos):
        super().__init__()
        self._dados = dados
        self._cabecalhos = cabecalhos

    def rowCount(self, parent=None):
        return len(self._dados)

    def columnCount(self, parent=None):
        return len(self._cabecalhos)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._dados[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._cabecalhos[section]
```

**Signals/Slots como ponte MVP**  
O mecanismo de Signals/Slots do Qt é o veículo natural para a comunicação desacoplada entre a View e o `GameManager`. A View usa Signals nativos do Qt para comunicar com os métodos puros do GameManager, garantindo que o Presenter se mantenha cego e agnóstico à biblioteca de UI. O GameManager é Python puro — não herda de `QObject`, não emite Signals.

```python
from PySide6.QtCore import Signal

class JanelaPrincipal(QMainWindow):
    iniciar_solicitado = Signal()
    submeter_respostas = Signal(dict)

    def __init__(self):
        super().__init__()
        self.btn = QPushButton("Iniciar")
        self.btn.clicked.connect(self.iniciar_solicitado.emit)

# GameManager — totalmente agnóstico a Qt:
# gm = GameManager(view)
# view.iniciar_solicitado.connect(gm.on_iniciar_solicitado)
```

**Operações assíncronas com QThread**  
Processamento pesado (leitura de ficheiros, cálculos de simulação) pode ser delegado a `QThread` ou `QRunnable`, mantendo a UI responsiva. `QTimer` serve para eventos periódicos — actualizar um relógio de jogo, fazer polling de estado.

#### 3.1.2 Avaliação por Requisito

| Requisito | Suporte | Mecanismo Qt |
|---|---|---|
| RF-01 Transições de estado | Nativo | `QStackedWidget` |
| RF-02 Formulários | Nativo | `QFormLayout`, `QLineEdit`, `QComboBox`, `QCheckBox` |
| RF-03 Relatórios tabulares | Nativo | `QTableView` + `QAbstractTableModel` |
| RF-04 Tema customizável | Completo | Qt Style Sheets (QSS) |
| RF-05 Assincronicidade | Nativo | `QThread`, `QRunnable`, `QTimer` |
| RF-06 Integração MVP | Estrutural | Signals/Slots + Model/View |

---

### 3.2 PyQt6

**Origem e manutenção:** PyQt6 é um binding alternativo do Qt 6, desenvolvido pela [Riverbank Computing](https://www.riverbankcomputing.com/). Não é afiliado à Qt Company.

**Licença:** GPL 3.0 (open-source) ou licença comercial paga.

**Fonte oficial:** [https://www.riverbankcomputing.com/software/pyqt/](https://www.riverbankcomputing.com/software/pyqt/)  
**Documentação:** [https://www.riverbankcomputing.com/static/Docs/PyQt6/](https://www.riverbankcomputing.com/static/Docs/PyQt6/)  
**Instalação:** `pip install PyQt6`

#### 3.2.1 Análise Técnica

A API do PyQt6 é, em termos práticos, idêntica à do PySide6. Os módulos têm nomes diferentes (`PyQt6.QtWidgets` vs `PySide6.QtWidgets`) mas a estrutura de classes, os métodos e os comportamentos são equivalentes. Qualquer exemplo de código de um funciona no outro com substituição de imports.

As diferenças técnicas reais são marginais:

- O PyQt6 expõe algumas APIs de baixo nível do Qt de forma ligeiramente diferente em casos de uso avançados com `sip` vs `shiboken`
- O mecanismo de Signals no PyQt6 usa `pyqtSignal` em vez de `Signal`; os Slots usam o decorador `@pyqtSlot`
- A distribuição de recursos (ficheiros `.qrc`) tem diferenças no processo de compilação

#### 3.2.2 O Factor Decisivo: Licença

A diferença operacionalmente relevante é a licença. O PyQt6 sob GPL obriga a que qualquer software que o distribua também seja publicado sob GPL. Para um projecto que possa vir a ser distribuído fechado, vendido, ou simplesmente mantido privado, esta restrição é bloqueante.

O PySide6 sob LGPL não tem esta restrição. A selecção entre os dois, dado o perfil do *Inspetor IFF BJI*, é determinada pela licença, não pela técnica.

---

### 3.3 Dear PyGui

**Origem e manutenção:** Dear PyGui é um wrapper Python para a biblioteca C++ [Dear ImGui](https://github.com/ocornut/imgui), desenvolvido e mantido pela comunidade [hoffstadt](https://github.com/hoffstadt).

**Licença:** MIT — totalmente permissiva.

**Fonte oficial:** [https://dearpygui.readthedocs.io/](https://dearpygui.readthedocs.io/)  
**Repositório:** [https://github.com/hoffstadt/DearPyGui](https://github.com/hoffstadt/DearPyGui)  
**Instalação:** `pip install dearpygui`

#### 3.3.1 Análise Técnica

O Dear PyGui destaca-se por dois atributos: renderização via GPU (DirectX 11 / Metal / Vulkan) e o paradigma *immediate mode* herdado do Dear ImGui.

A renderização GPU confere-lhe uma fluidez visual difícil de igualar com widgets tradicionais. Para HUDs em tempo real, gráficos animados, ou dashboards com dados em actualização contínua, é tecnicamente superior ao Qt.

O paradigma *immediate mode* é, contudo, uma incompatibilidade estrutural com a arquitectura MVP do projecto. Num sistema *immediate mode*, a UI é reconstruída a cada frame — não há estado persistente nos widgets, não há Model separado, não há notificações de mudança. O "estado" existe no código da aplicação, não na UI.

Isto inverte o fluxo de controlo que o MVP pressupõe:

- **MVP/retained mode (Qt):** O Model notifica a View quando o estado muda. A View actualiza-se pontualmente.
- **Immediate mode (Dear PyGui):** A aplicação reconstrói a UI inteira a cada frame, consultando o estado a cada iteração.

Integrar um `GameManager` com lógica de domínio encapsulada num sistema *immediate mode* é possível, mas exige adaptadores que essencialmente simulam o comportamento retained-mode — trabalho extra sem benefício para este perfil de projecto.

#### 3.3.2 Caso de Uso Favorável

O Dear PyGui seria uma escolha justificada se o *Inspetor IFF BJI* incluísse painéis de monitoramento de dados em tempo real com alta frequência de actualização — radar ao vivo, telemetria de voo, visualizações gráficas animadas. Nesse cenário, o seu modelo de renderização ofereceria vantagens concretas.

---

### 3.4 wxPython

**Origem e manutenção:** wxPython é um binding Python para a biblioteca C++ [wxWidgets](https://www.wxwidgets.org/), mantida pela comunidade wxPython.

**Licença:** LGPL (wxWidgets) + licença wxWindows — permissiva para uso comercial.

**Fonte oficial:** [https://wxpython.org/](https://wxpython.org/)  
**Documentação:** [https://docs.wxpython.org/](https://docs.wxpython.org/)  
**Instalação:** `pip install wxPython`

#### 3.4.1 Análise Técnica

A característica distintiva do wxPython — e o motivo do seu descarte para este projecto — é o uso de widgets *nativos do sistema operativo*. O wxPython não renderiza os seus próprios widgets: delega ao Win32 API no Windows, ao Cocoa no macOS, ao GTK no Linux. O resultado é uma UI que parece exactamente com o SO em que está a correr.

Esta propriedade, que é uma vantagem em aplicações de produtividade que querem integração visual com o SO, é uma desvantagem directa para um projecto que pretende criar a estética de um SO *fictício*. Não é possível fazer um botão wxPython parecer diferente de um botão Windows — a renderização está fora do controlo da aplicação.

Adicionalmente, o wxPython não tem um equivalente moderno do `QMdiArea`, e a sua camada de estilização (wxSystemSettings, SetBackgroundColour, SetForegroundColour) é rudimentar comparada com o QSS.

---

### 3.5 Kivy

**Fonte oficial:** [https://kivy.org/](https://kivy.org/)  
**Repositório:** [https://github.com/kivy/kivy](https://github.com/kivy/kivy)  
**Instalação:** `pip install kivy`

**Descarte:** O Kivy foi concebido para interfaces touch-first em dispositivos móveis e tablets. O seu sistema de layout e os seus widgets pressupõem interacção táctil, ecrãs de tamanho variável, e paradigmas de navegação móvel. A criação de uma interface desktop UI-heavy com janelas MDI e formulários complexos em Kivy exigiria reconstruir do zero elementos que o Qt oferece nativamente. Descartado por incompatibilidade de propósito.

---

### 3.6 Abordagem Web (Flask/FastAPI + HTML/CSS/JS)

**Frameworks de referência:**  
- Flask: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)  
- FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

**Análise:** A abordagem de servir a UI via browser (servidor Python local + frontend HTML/CSS/JS) tem capacidade técnica real para replicar a estética de SO fictício — bibliotecas como [OS.js](https://www.os-js.org/) e [jQuery UI](https://jqueryui.com/) implementam janelas flutuantes no browser com maturidade.

O problema é arquitectural. O `GameManager` e a UI passam a ser processos separados:

```
[Python: GameManager] ←→ HTTP/WebSocket ←→ [Browser: UI]
```

Isto fragmenta o padrão MVP em dois ambientes de execução com linguagens diferentes. O estado do domínio existe em Python; o estado visual existe em JavaScript. A sincronização entre ambos exige serialização e deserialização a cada interacção, introduzindo latência e pontos de falha. Distribuir a aplicação como executável desktop exigiria empacotamento adicional (Electron, Tauri, ou PyInstaller com servidor embedded).

Para um projecto com arquitectura MVP estabelecida em Python puro, esta fragmentação representa um custo de complexidade sem benefício equivalente.

---

## 4. Matriz Comparativa

| Critério | PySide6 | PyQt6 | Dear PyGui | wxPython | Kivy | Web |
|---|---|---|---|---|---|---|
| Navegação por estados (QStackedWidget) | Sim | Sim | Não | Sim | Não | Parcial |
| Formulários completos | Sim | Sim | Parcial | Sim | Não | Sim |
| Relatórios tabulares (Model/View) | Sim | Sim | Não | Parcial | Não | Sim |
| Estilização total (SO fictício) | Sim | Sim | Sim | Não | Parcial | Sim |
| Integração MVP nativa | Sim | Sim | Não | Não | Não | Não |
| Assincronicidade sem bloqueio | Sim | Sim | Sim | Parcial | Sim | Sim |
| Licença permissiva (LGPL/MIT) | Sim | Não (GPL) | Sim | Sim | Sim | N/A |
| Maturidade e documentação | Alta | Alta | Média | Alta | Média | Alta |
| Comunidade Python activa | Alta | Alta | Crescente | Média | Média | Alta |

---

## 5. Justificação da Decisão

### 5.1 PySide6 como escolha primária

O PySide6 é a única framework que responde a todos os seis requisitos funcionais identificados sem adaptadores, workarounds, ou inversão de paradigmas.

A convergência de quatro factores determina a decisão:

**Factor 1 — Alinhamento arquitectural com MVP**  
O sistema Model/View do Qt não é apenas compatível com o padrão MVP — é uma implementação concreta dele. `QAbstractTableModel` é um Model. `QTableView` é uma View. Signals/Slots são o canal de comunicação entre View e Presenter. A View usa Signals nativos; o `GameManager` é Python puro e não depende de Qt.

**Factor 2 — QStackedWidget resolve o fluxo de telas sem complexidade**  
`QStackedWidget` implementa a navegação linear entre estados do MVP (Menu → Inspeção → Diagnóstico → Resultado) com zero sobrecarga. Cada tela é um `QWidget` independente; a troca é instantânea e não exige criar/destruir widgets.

**Factor 3 — QSS fornece controlo visual completo**  
A capacidade de estilizar cada widget, estado e pseudo-elemento via QSS significa que a identidade visual do SO fictício do *Inspetor IFF BJI* pode ser implementada e iterada em CSS sem tocar no código Python.

**Factor 4 — Licença LGPL preserva flexibilidade**  
A LGPL não impõe restrições à distribuição do projecto, seja em formato aberto, fechado, ou comercial. PyQt6, o único equivalente técnico, não oferece esta flexibilidade sem custo.

### 5.2 Condição de revisão da decisão

A decisão em favor do PySide6 deve ser revista se o projecto vier a incluir um dos seguintes elementos como funcionalidade central:

- **Painéis de dados em tempo real com alta frequência de actualização (>30 actualizações/segundo):** nesse caso, Dear PyGui ofereceria vantagens de performance GPU que justificariam o custo de adaptação do MVP.
- **Distribuição exclusivamente como projecto open-source GPL:** nesse caso, PyQt6 seria equivalente ao PySide6 sem desvantagem prática.

---

## 6. Referências e Fontes

### Documentação Oficial das Frameworks

| Framework | Documentação | Repositório |
|---|---|---|
| PySide6 | [doc.qt.io/qtforpython-6](https://doc.qt.io/qtforpython-6/) | [code.qt.io/pyside](https://code.qt.io/cgit/pyside/pyside-setup.git/) |
| PyQt6 | [riverbankcomputing.com/PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/) | [PyPI: PyQt6](https://pypi.org/project/PyQt6/) |
| Dear PyGui | [dearpygui.readthedocs.io](https://dearpygui.readthedocs.io/) | [github.com/hoffstadt/DearPyGui](https://github.com/hoffstadt/DearPyGui) |
| wxPython | [docs.wxpython.org](https://docs.wxpython.org/) | [github.com/wxWidgets/wxPython](https://github.com/wxWidgets/Phoenix) |
| Kivy | [kivy.org/doc](https://kivy.org/doc/stable/) | [github.com/kivy/kivy](https://github.com/kivy/kivy) |
| Dear ImGui (base C++) | [github.com/ocornut/imgui](https://github.com/ocornut/imgui) | — |

### Referências de Padrões e Arquitectura

- Qt Model/View Programming: [doc.qt.io/qt-6/model-view-programming.html](https://doc.qt.io/qt-6/model-view-programming.html)
- Qt Style Sheets Reference: [doc.qt.io/qt-6/stylesheet-reference.html](https://doc.qt.io/qt-6/stylesheet-reference.html)
- Qt QStackedWidget: [doc.qt.io/qt-6/qstackedwidget.html](https://doc.qt.io/qt-6/qstackedwidget.html)
- Qt Signals and Slots: [doc.qt.io/qt-6/signalsandslots.html](https://doc.qt.io/qt-6/signalsandslots.html)
- Martin Fowler — GUI Architectures (MVP): [martinfowler.com/eaaDev/uiArchs.html](https://martinfowler.com/eaaDev/uiArchs.html)
- PyPI — PySide6: [pypi.org/project/PySide6](https://pypi.org/project/PySide6/)
- Licença LGPL 3.0: [gnu.org/licenses/lgpl-3.0.html](https://www.gnu.org/licenses/lgpl-3.0.html)

---

*Documento elaborado como parte da fase de análise e decisão tecnológica do projecto Inspetor IFF BJI.*
