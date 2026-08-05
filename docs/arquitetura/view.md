# Arquitetura da Camada View (PySide6 + MVP)

**Projeto:** Inspetor IFF-BJI  
**Módulo:** Camada de Apresentação (View)  
**Tecnologia:** PySide6 (Qt for Python)

---

## 1. Introdução

Este documento estabelece as diretrizes arquiteturais para o desenvolvimento de interfaces gráficas (UI) no projeto **Inspetor IFF-BJI**. A camada view segue o padrão **Model-View-Presenter (MVP)** integrado à **Arquitetura Limpa**.

O objetivo principal é uma **View Passiva**: a interface não toma decisões de negócio, não calcula pontuações, não conhece as regras do domínio. Ela exibe dados entregues e reporta interações do utilizador (cliques, seleções, submissões) ao `GameManager` via **Signals do Qt** — nunca importando código do core ou application.

---

## 2. Hierarquia de Componentes

A UI é organizada em **três seções principais**, cada uma uma janela ou overlay independente:

```
JanelaPrincipal (QMainWindow, implementa IGameView)
├── TelaDeExpediente (QStackedWidget)
│   ├── PaginaSelecaoPerfil
│   ├── PaginaInspecao (com Sidebar, overlays de anexos/media)
│   ├── PaginaDiagnostico
│   └── PaginaGameOver / PaginaGameWin
└── [z-order overlay layer]
    ├── TelaTutorial (JanelaFlutuante, z=2)
    └── TelaGameOver/GameWin (JanelaFlutuante, z=1)
```

**Camadas de Z-order (do fundo para o topo):**
1. **Base (z=0):** `TelaDeExpediente` com as páginas do expediente.
2. **Overlay overlay (z=1):** `PaginaGameOver`/`PaginaGameWin` — overlays integradas dentro do expediente.
3. **Flutuante (z=2):** `TelaTutorial` — janela flutuante que flutua acima de tudo, irmã do expediente.

---

## 3. Estrutura de Diretórios

```
view/
├── main_window.py                # JanelaPrincipal (orquestrador, implementa IGameView)
├── infrastructure/
│   └── layout_loader.py          # LayoutLoader singleton — escala responsiva
├── desktop/                       # Componentes de desktop (fora do expediente)
│   ├── menu.py                   # Menu de sistema (deprecated/experimental)
│   ├── taskbar.py                # Barra de tarefas do SO
│   ├── desktop_shortcut.py       # Atalhos de desktop
│   └── wallpaper_selector.py     # Seletor de wallpaper
├── expediente/                    # Fluxo principal do jogo (dentro do QStackedWidget)
│   ├── tela.py                   # TelaDeExpediente (orquestrador das páginas)
│   ├── paginas/                  # Páginas do fluxo
│   │   ├── selecao_perfil.py     # Seleção de personagem (1ª página)
│   │   ├── inspecao.py           # Formulário de inspeção (2ª página)
│   │   ├── diagnostico.py        # Resultado + feedback (3ª página)
│   │   ├── game_over.py          # Game over (derrota)
│   │   └── game_win.py           # Game win (vitória)
│   ├── widgets/                  # Componentes reutilizáveis dentro expediente
│   │   ├── sidebar.py            # Barra lateral de navegação
│   │   ├── character_carousel.py # Carrossel de personagens
│   │   ├── stamp_button.py       # Botão carimbo (decisão)
│   │   ├── window_title_bar.py   # Barra de título customizada
│   │   └── anexo_preview.py      # Prévia de anexos
│   ├── overlays/                 # Overlays dentro do expediente
│   │   ├── anexo_gallery.py      # Galeria de anexos (fotos/videos)
│   │   └── media_viewer.py       # Reprodutor de mídia
│   ├── configuracoes/
│   │   └── perfis.py             # (Deprecated) configuração de perfis
│   └── modelos/
│       └── character_data.py     # Dados de personagens
├── tutorial/                      # Tutorial flutuante (JanelaFlutuante)
│   ├── tela_tutorial.py          # TelaTutorial (orquestrador dos slides)
│   ├── slide_tutorial.py         # SlideTutorial base (ABC)
│   ├── paginas/                  # 8 slides do tutorial
│   │   ├── slide_boas_vindas.py
│   │   ├── slide_anatomia.py     # (etc.)
│   │   └── ... (8 slides total)
│   └── widgets/                  # Componentes reutilizáveis do tutorial
│       ├── nota_aviso.py         # Caixa de aviso estilizada
│       ├── credential_iff.py     # Cartão de credencial
│       ├── dots_navegacao.py     # Fileira de dots (carrossel)
│       ├── item_numerado.py      # Item com badge numerado
│       └── assets_helper.py      # Helpers de carregamento de pixmaps
├── widgets/                       # Componentes genéricos reutilizáveis
│   ├── janela_flutuante.py       # JanelaFlutuante (base para overlays flutuantes)
│   ├── efeitos/                  # Efeitos visuais
│   │   ├── background_riscos.py  # Fundo decorativo com pictogramas
│   │   ├── confetti_overlay.py   # Confete (vitória)
│   │   ├── crt_overlay.py        # Efeito CRT (scanlines)
│   │   └── trofeu_icon.py        # Troféu (vitória)
│   └── midia/                    # Reprodução de mídia
│       ├── media_player_base.py  # Base para players
│       ├── video_player.py       # Reprodutor de vídeo
│       ├── audio_player.py       # Reprodutor de áudio
│       └── image_viewer.py       # Visualizador de imagens
├── utils/
│   └── tint_icon.py              # (Deprecated) utility de tinting
└── assets/                        # Ficheiros estáticos
    ├── style.qss                 # Tema escuro (QSS global)
    ├── style_light.qss           # Tema claro (QSS global)
    ├── layout.json               # Tokens de layout (dimensões, spacing)
    └── icons/, images/           # Recursos visuais
```

---

## 4. Padrão MVP: Signals e Slots

A comunicação entre View e Presenter segue um fluxo determinado:

### 4.1. Bottom-Up: Página → MainWindow → GameManager

**Exemplo:** Utilizador seleciona um risco na inspeção

```python
# PaginaInspecao (página)
class PaginaInspecao(QWidget):
    risco_marcado = Signal(str)  # Sinal limpo: só passa dados
    
    def __on_risco_clicado(self, risco_id: str):
        self.risco_marcado.emit(risco_id)  # Emite para cima

# TelaDeExpediente (orquestrador do expediente)
self.pagina_inspecao.risco_marcado.connect(self.on_risco_marcado)

# JanelaPrincipal (orquestrador global)
self.expediente.on_risco_marcado_signal.connect(self.game_manager.processar_risco)
```

### 4.2. Top-Down: GameManager → MainWindow → Página

**Exemplo:** GameManager ordena trocar de página

```python
# GameManager (presenter/aplicação)
self.view.exibir_pagina_diagnostico(resultado_dto)

# JanelaPrincipal (implementa IGameView)
def exibir_pagina_diagnostico(self, resultado):
    self.expediente.mostrar_diagnostico(resultado)
    self.expediente.stack.setCurrentIndex(PAGE_DIAGNOSTICO)
```

**Regra de ouro:** Sinais fluem de baixo para cima; métodos do contrato (`IGameView`) fluem de cima para baixo. Nunca importar `GameManager` em widgets.

---

## 5. Separação Estrita: Estrutura vs. Estilo

Inspirado em HTML + CSS, a aplicação proíbe misturar lógica e estética:

### 5.1. Estrutura (Python)

Ficheiros `.py` instanciam widgets, definem hierarquia e emitem sinais. **Proibido:** `.setStyleSheet()` para cores, fontes ou margens (exceção: manipulações dinâmicas de imagens, como recoloring).

```python
# ✅ CORRETO
self.btn_risco = QPushButton("Risco Físico")
self.btn_risco.setObjectName("btn_risco_fisico")
self.btn_risco.setProperty("class", "risco_tile")
self.layout.addWidget(self.btn_risco)
```

### 5.2. Estilo (QSS)

Toda a estética vive em `assets/style.qss` (tema escuro) e `assets/style_light.qss` (tema claro), injetados ao arranque.

```css
/* Em assets/style.qss */
.risco_tile {
    background-color: #1a1a2e;
    border: 2px solid #16213e;
    border-radius: 8px;
    padding: 16px;
}

.risco_tile:hover {
    border-color: #0f3460;
}
```

---

## 6. Escala Responsiva: LayoutLoader

Todos os tamanhos, espaçamentos e fontes vêm de um único **LayoutLoader singleton**, que carrega `layout.json` (dimensões base para 1920×1080) e escala uniformemente para a resolução atual.

```python
# Em qualquer widget
L = LayoutLoader.instance()
botao.setFixedSize(L.scaled("inspecao", "botao_tamanho"), 50)
fonte = QFont("Open Sans", L.scaled("inspecao", "fonte_size"))
self.layout.setSpacing(L.scaled_margins("inspecao", "spacing"))
```

**Vantagem:** Mudar tamanho/espaçamento em uma resolução afeta toda a app uniformemente. Nenhum número mágico em `py`.

---

## 7. Contrato de Interface: IGameView

Para garantir **Inversão de Dependência**, o presenter (`GameManager`) nunca importa `PySide6`. A comunicação é via contrato abstrato `IGameView` (em `application/interfaces/`):

```python
# application/interfaces/i_game_view.py
class IGameView(ABC):
    @abstractmethod
    def exibir_selecao_perfil(self) -> None: pass
    
    @abstractmethod
    def exibir_inspecao(self, relatorio: Relatorio) -> None: pass
    
    @abstractmethod
    def exibir_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None: pass
```

**Regra:** Toda nova navegação deve ser declarada no `IGameView` antes de ser implementada em `JanelaPrincipal`.

---

## 8. Tema Claro e Escuro

A aplicação suporta dois temas via dois ficheiros QSS separados:

- **Dark (escuro):** `assets/style.qss` — tema padrão
- **Light (claro):** `assets/style_light.qss` — variante clara

Ambos definem os mesmos seletores (mesmo ObjectName/class), apenas com cores diferentes. A mudança de tema injeta o QSS apropriado via `qApp.setStyleSheet()`.

---

## 9. Padrões Comuns

### 9.1. Widget Responsivo

```python
class MeuWidget(QWidget):
    def __init__(self):
        L = LayoutLoader.instance()
        # ...
        L.escala_atualizada.connect(self.__reaplicar_dimensoes)
    
    def __reaplicar_dimensoes(self):
        L = LayoutLoader.instance()
        self.setMinimumSize(
            L.scaled("secao", "widget_largura"),
            L.scaled("secao", "widget_altura")
        )
```

### 9.2. Sinal Sem Parâmetros Desnecessários

```python
class Pagina(QWidget):
    # ❌ Evitar: Signal(str, int, bool) — acoplamento
    # ✅ Bom: Signal() — deixa a página ler o estado
    pronto_clicado = Signal()
    
    def __on_pronto(self):
        self.pronto_clicado.emit()
        # Quem receber o sinal chamará getter()'s desta página
```

### 9.3. Overlay Flutuante

```python
class TelaTutorial(JanelaFlutuante):
    finalizado_solicitado = Signal(MotivoTutorial)
    
    def exibir_com_tamanho_inicial(self, parent_rect):
        super().exibir_com_tamanho_inicial(parent_rect)
        self.raise_()  # Garantir z-order acima do expediente
```

---

## 10. Estrutura do Layout

Tokens em `assets/layout.json` definem a hierarquia de dimensões:

```json
{
  "inspecao": {
    "margens": [16, 16, 16, 16],
    "spacing_items": 12,
    "fonte_size": 14,
    "botao_tamanho": 48
  }
}
```

Uma mudança num token rebate por toda a aplicação via `L.scaled()`.

---

## Resumo: Fluxo de uma Ação do Utilizador

1. Utilizador clica num botão em `PaginaInspecao`.
2. Página lê dados locais e emite `Signal(dado)`.
3. `TelaDeExpediente` captura, valida e reemite para `JanelaPrincipal`.
4. `JanelaPrincipal` chama `GameManager.processar_acao(dado)`.
5. `GameManager` processa regras de negócio (sem saber de Qt).
6. `GameManager` chama `view.exibir_nova_pagina()` (contrato `IGameView`).
7. `JanelaPrincipal` implementa: `stack.setCurrentIndex(...)`.
8. Ciclo fecha. A página anterior pode ter sinais conectados que desfazem/limpam.

---

*Documento atualizado para refletir a arquitetura real implementada em `view/` a partir de 2024.*
