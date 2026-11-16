# Arquitetura da Camada View (PySide6 + MVP)

**Projeto:** Inspetor IFF-BJI  
**Módulo:** Camada de Apresentação (View)  
**Tecnologia:** PySide6 (Qt for Python)

---

## 1. Introdução

Este documento estabelece as diretrizes arquiteturais da interface gráfica do **Inspetor IFF-BJI**. A camada view segue o padrão **Model-View-Presenter (MVP)** integrado à **Arquitetura Limpa**.

O objetivo é uma **View Passiva**: a interface não toma decisões de negócio, não calcula pontuações e não conhece as regras do domínio. Ela exibe os dados que recebe e reporta as interações do usuário (cliques, seleções, submissões) ao `GameManager` por meio de **Signals do Qt**. A view nunca importa o `GameManager`; quem conecta os dois é o `main.py`.

---

## 2. Hierarquia de Componentes

A interface simula um sistema operacional: um desktop com barra de tarefas, sobre o qual abrem "janelas" flutuantes.

```
JanelaPrincipal (QMainWindow, implementa IGameView)
├── _OverlayArea
│   ├── TelaMenuPrincipal            (desktop: wallpaper e atalhos)
│   ├── TelaDeExpediente             (JanelaFlutuante)
│   │   ├── WindowTitleBar
│   │   ├── Sidebar                  (visível na inspeção e no diagnóstico)
│   │   ├── QStackedWidget
│   │   │   ├── 0 · PaginaSelecaoPerfil
│   │   │   ├── 1 · PaginaInspecao
│   │   │   ├── 2 · PaginaDiagnostico
│   │   │   ├── 3 · GameWin
│   │   │   └── 4 · GameOver
│   │   └── AnexoGallery, MediaViewer (overlays de mídia)
│   └── TelaTutorial                 (JanelaFlutuante, 8 slides)
└── Taskbar                          (rodapé, sempre visível)
```

**Ordem de empilhamento (do fundo para o topo):**

1. **Desktop:** `TelaMenuPrincipal`, sempre visível, ocupa toda a `_OverlayArea`.
2. **Expediente:** `TelaDeExpediente`, janela flutuante que ocupa 80% da área (token `tela_de_expediente.proporcao_tela`) e pode ser maximizada, minimizada ou fechada.
3. **Tutorial:** `TelaTutorial`, registrada por último na `_OverlayArea` e por isso desenhada acima do expediente.

A `Taskbar` fica fora da `_OverlayArea`, no rodapé da janela. `AnexoGallery` e `MediaViewer` são filhos da `TelaDeExpediente` e cobrem a área do overlay enquanto estão abertos.

---

## 3. Estrutura de Diretórios

```
view/
├── main_window.py                # JanelaPrincipal e _OverlayArea
├── infrastructure/
│   └── layout_loader.py          # LayoutLoader singleton — escala responsiva
├── desktop/                      # Desktop e barra de tarefas
│   ├── menu.py                   # TelaMenuPrincipal (wallpaper e atalhos)
│   ├── taskbar.py                # Taskbar (botão iniciar, atalhos, relógio)
│   ├── desktop_shortcut.py       # DesktopShortcut (atalho do desktop)
│   └── wallpaper_selector.py     # WallpaperSelector
├── expediente/                   # Fluxo principal do jogo
│   ├── tela.py                   # TelaDeExpediente (orquestra as páginas)
│   ├── paginas/
│   │   ├── selecao_perfil.py     # PaginaSelecaoPerfil
│   │   ├── inspecao.py           # PaginaInspecao (relatório e formulário)
│   │   ├── diagnostico.py        # PaginaDiagnostico (resultado e feedback)
│   │   ├── game_win.py           # GameWin (vitória)
│   │   └── game_over.py          # GameOver (derrota)
│   ├── widgets/
│   │   ├── sidebar.py            # Sidebar
│   │   ├── character_carousel.py # CharacterCarousel (carrossel de perfis)
│   │   ├── stamp_button.py       # StampButton (carimbo de decisão)
│   │   ├── window_title_bar.py   # WindowTitleBar
│   │   └── anexo_preview.py      # AnexoPreview
│   ├── overlays/
│   │   ├── anexo_gallery.py      # AnexoGallery (galeria de anexos)
│   │   └── media_viewer.py       # MediaViewer (mídia ampliada)
│   ├── configuracoes/
│   │   └── perfis.py             # IFF_PROFILES e make_profile_roster()
│   └── modelos/
│       └── character_data.py     # CharacterData
├── tutorial/
│   ├── tela_tutorial.py          # TelaTutorial (registro e navegação dos slides)
│   ├── slide_tutorial.py         # SlideTutorial (classe base)
│   ├── paginas/                  # Slides, na ordem de exibição
│   │   ├── slide_boas_vindas.py
│   │   ├── slide_anatomia.py
│   │   ├── slide_anexos.py
│   │   ├── slide_riscos.py
│   │   ├── slide_fatores.py
│   │   ├── slide_decisao.py
│   │   ├── slide_vitoria.py
│   │   └── slide_pronto.py
│   └── widgets/
│       ├── nota_aviso.py         # NotaAviso
│       ├── credential_iff.py     # CredencialIFF
│       ├── dots_navegacao.py     # DotsNavegacao
│       ├── item_numerado.py      # ItemNumerado
│       └── assets_helper.py      # Carregamento de pixmaps
├── widgets/                      # Componentes genéricos
│   ├── janela_flutuante.py       # JanelaFlutuante (base das janelas)
│   ├── efeitos/
│   │   ├── background_riscos.py  # BackgroundRiscos (fundo com pictogramas)
│   │   ├── confetti_overlay.py   # ConfettiOverlay (vitória)
│   │   ├── crt_overlay.py        # CrtEffectsOverlay (scanlines)
│   │   └── trofeu_icon.py        # TrofeuIcon
│   └── midia/
│       ├── media_player_base.py  # MediaPlayerBase
│       ├── video_player.py       # VideoPlayer
│       ├── audio_player.py       # AudioPlayer
│       └── image_viewer.py       # ImageViewer
├── utils/
│   └── tint_icon.py              # tint_pixmap() — recoloração de ícones
└── assets/
    ├── style.qss                 # Tema escuro
    ├── style_light.qss           # Tema claro
    ├── layout.json               # Tokens de layout (dimensões, espaçamentos, fontes)
    ├── textos/                   # pareceres_gameover.json, pareceres_gamewin.json
    ├── cursos/                   # Imagem de cada perfil (DEFAULT.png, T_QUIMICA.png, ...)
    ├── icons/                    # Ícones (desktop, riscos, sidebar, tutorial, fim de jogo)
    └── images/                   # Logo e wallpapers
```

---

## 4. Padrão MVP: Signals e Contrato

### 4.1. De baixo para cima: Página → Tela → JanelaPrincipal → GameManager

As páginas emitem sinais; cada nível acima apenas reemite, até a `JanelaPrincipal`. A ligação com o `GameManager` é feita em `main.py`.

**Exemplo:** o jogador submete a inspeção.

```python
# view/expediente/paginas/inspecao.py
class PaginaInspecao(QWidget):
    submeter_respostas = Signal(dict)

    # ao clicar em "Submeter", a página coleta as marcações e emite:
    # {"riscos": [...], "fatores": [...], "decisao": "...", "tempo_segundos": int}

# view/expediente/tela.py
self.__pagina_inspecao.submeter_respostas.connect(self.submeter_respostas.emit)

# view/main_window.py
tela_expediente.submeter_respostas.connect(self.submeter_respostas.emit)

# main.py
janela.submeter_respostas.connect(gm.processar_submissao)
```

Sinais expostos pela `JanelaPrincipal`:

| Sinal | Origem |
|-------|--------|
| `iniciar_solicitado()` | Taskbar ou atalho do desktop |
| `tutorial_finalizado(MotivoTutorial)` | `TelaTutorial` |
| `perfil_confirmado(str)` | `PaginaSelecaoPerfil` |
| `submeter_respostas(dict)` | `PaginaInspecao` |
| `continuar_solicitado()` | `PaginaDiagnostico` |
| `voltar_menu_solicitado()`, `jogar_novamente_solicitado()`, `sair_solicitado()` | `GameWin`, `GameOver` (e o fechar da janela do expediente) |
| `help_solicitado()` | Taskbar |

Os atalhos de arquivos e de wallpapers da Taskbar são tratados dentro da própria view (o segundo abre o `WallpaperSelector`) e não chegam ao `GameManager`.

### 4.2. De cima para baixo: GameManager → JanelaPrincipal → Tela

O `GameManager` comanda a view apenas pelos métodos do contrato `IGameView`.

```python
# application/controllers/game_manager.py
self.__view.exibir_tela_diagnostico(resultado)

# view/main_window.py
def exibir_tela_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
    self.__tela_expediente.exibir_tela_diagnostico(resultado)

# view/expediente/tela.py
def exibir_tela_diagnostico(self, resultado: ResultadoDiagnosticoDTO) -> None:
    self.__pagina_diagnostico.exibir_diagnostico(resultado)
    self.__stack.setCurrentIndex(self.IDX_DIAGNOSTICO)
```

**Regra de ouro:** sinais sobem; métodos do contrato descem. Nenhum widget importa o `GameManager`.

---

## 5. Separação entre Estrutura e Estilo

### 5.1. Estrutura (Python)

Os arquivos `.py` instanciam widgets, definem a hierarquia e emitem sinais. A identificação para o estilo é feita com `objectName` e com a property `class`:

```python
# view/expediente/widgets/sidebar.py
self.setObjectName("sidebar")
self.setProperty("class", "sidebar")
```

### 5.2. Estilo (QSS)

A estética estática vive em `assets/style.qss` (tema escuro) e `assets/style_light.qss` (tema claro). Os seletores usam o `objectName` e as properties definidas no Python:

```css
/* assets/style.qss */
QToolButton[objectName="tile_risco_FISICO"] {
    border: 2px solid #37a547;
    color: #71dd77;
}
QToolButton[objectName="tile_risco_FISICO"]:checked {
    background-color: #37a547;
    color: #ffffff;
}
```

### 5.3. Quando `setStyleSheet()` é aceito no Python

O padrão é não usar `setStyleSheet()` nos arquivos `.py`. As exceções existentes são estilos que dependem de um valor conhecido apenas em tempo de execução:

- `paginas/diagnostico.py`: cor de cada tile e de cada score conforme o resultado (acerto, erro, esquecimento) e destaque da decisão escolhida.
- `paginas/inspecao.py`: cor do texto dos botões de fator conforme o estado marcado.
- `paginas/game_win.py` e `paginas/game_over.py`: fundo transparente da área de rolagem do parecer.
- `widgets/sidebar.py`: estilo dos itens de navegação.

Estilos novos que não dependam de estado calculado devem ir para os dois arquivos QSS.

---

## 6. Escala Responsiva: LayoutLoader

Tamanhos, espaçamentos e fontes vêm do **`LayoutLoader`**, um singleton que carrega `assets/layout.json` (valores de referência para 1920×1080) e os escala para a resolução atual. O fator de escala é o menor entre a razão de largura e a razão de altura.

| Método | Retorno |
|--------|---------|
| `LayoutLoader.instance()` | A instância única |
| `get(*chaves)` | Valor bruto do token |
| `scaled(*chaves)` | Valor numérico multiplicado pelo fator de escala (arredondado) |
| `scaled_margins(*chaves)` | Tupla `(left, top, right, bottom)` escalada |
| `scale_factor()` | Fator de escala atual |
| `set_screen(w, h)` | Atualiza a resolução e emite `escala_atualizada` |

```python
# view/expediente/widgets/sidebar.py
L = LayoutLoader.instance()
self.setFixedWidth(L.scaled("sidebar", "largura"))
inner.setContentsMargins(*L.scaled_margins("sidebar", "header_margens"))
```

A `JanelaPrincipal` informa a resolução do monitor ao loader na criação e o tamanho da janela a cada redimensionamento; quando o valor muda, o loader emite `escala_atualizada`.

---

## 7. Contrato de Interface: IGameView

Para garantir a **Inversão de Dependência**, o presenter (`GameManager`) nunca importa PySide6. A comunicação passa pelo contrato abstrato `IGameView`, em `application/interfaces/i_game_view.py`:

| Método | Função |
|--------|--------|
| `inicializar()` | Exibe a janela |
| `fechar()` | Fecha a janela |
| `exibir_menu()` | Oculta expediente e tutorial, deixando o desktop |
| `exibir_tutorial(motivo)` | Abre o tutorial (`MotivoTutorial.NOVO_JOGO` ou `CONSULTA`) |
| `exibir_selecao_perfil()` | Abre o expediente na seleção de perfil |
| `trocar_para_tela_inspecao()` | Mostra a janela do expediente |
| `renderizar_relatorio(dados)` | Preenche a inspeção com o `dict` do relatório |
| `exibir_tela_diagnostico(resultado)` | Mostra o diagnóstico (`ResultadoDiagnosticoDTO`) |
| `exibir_resultado(pontuacao_global, dias_concluidos, venceu)` | Mostra `GameWin` ou `GameOver` |
| `exibir_popup_erro(mensagem)` | Exibe a mensagem em um `QMessageBox` |

**Regra:** toda nova navegação é declarada no `IGameView` antes de ser implementada em `JanelaPrincipal`.

### Dependências da view sobre outras camadas

Além do contrato `IGameView` e do enum `MotivoTutorial`, a view lê DTOs de `core/dtos/` (`ResultadoDiagnosticoDTO`, `ParecerCIPA`). As telas de fim de jogo recebem um `IPareceresCIPA` no construtor, mas hoje `tela.py`, `game_win.py` e `game_over.py` importam as classes concretas de `infrastructure/repository/`. Esse desvio está registrado em [Clean Architecture, seção 10](clean-architecture.md#10-desvios-conhecidos).

---

## 8. Tema Claro e Escuro

Os dois arquivos QSS definem os mesmos seletores, com cores diferentes. O tema é escolhido **na inicialização**, em `main.py`:

1. variável de ambiente `APP_THEME` (`dark` ou `light`), se definida;
2. caso contrário, `TEMA_PADRAO` de `config/constants.py` (atualmente `"dark"`).

```bash
# Linux/macOS
APP_THEME=light python main.py
# Windows (PowerShell)
$env:APP_THEME="light"; python main.py
```

Não há troca de tema com o jogo em execução. As URLs relativas dentro do QSS são convertidas em caminhos absolutos a partir de `view/assets/` antes de o estilo ser aplicado.

---

## 9. Padrões Comuns

### 9.1. Widget Responsivo

Widgets que fixam dimensões no construtor assinam `escala_atualizada` e reaplicam os valores:

```python
# view/desktop/menu.py
self.__layout = LayoutLoader.instance()
self.__layout.escala_atualizada.connect(self.__reaplicar_dimensoes)

def __reaplicar_dimensoes(self) -> None:
    L = self.__layout
    self.__desktop_layout.setContentsMargins(*L.scaled_margins("tela", "margens", "desktop"))
```

### 9.2. Sinais Carregam Apenas Dados Simples

Os sinais transportam tipos primitivos, `dict` ou enums do contrato, nunca widgets nem entidades de domínio:

```python
perfil_confirmado = Signal(str)                    # identificador do curso
submeter_respostas = Signal(dict)                  # marcações do jogador
finalizado_solicitado = Signal(MotivoTutorial)     # enum do contrato
continuar_solicitado = Signal()                    # sem dados
```

### 9.3. Janela Flutuante

`TelaDeExpediente` e `TelaTutorial` herdam de `JanelaFlutuante`, que fornece moldura, barra de título, geometria proporcional centralizada e os comportamentos de maximizar, minimizar e fechar. A subclasse monta apenas o conteúdo:

```python
class TelaDeExpediente(JanelaFlutuante):
    def __init__(self, parent=None):
        super().__init__(proporcao_keys=("tela_de_expediente", "proporcao_tela"), parent=parent)

    def __setup_ui(self):
        layout = self._montar_chrome("Expediente")   # moldura + WindowTitleBar
        layout.addLayout(self.__build_body(), stretch=1)
```

Os ganchos `_ao_fechar()` e `_ao_minimizar()` podem ser sobrescritos para emitir sinais próprios. A janela é registrada com `_OverlayArea.add_overlay()` e exibida com `exibir_com_tamanho_inicial(rect)`.

---

## 10. Estrutura do `layout.json`

O arquivo é organizado por componente. A chave `meta` define a resolução de referência:

```json
{
  "meta": { "resolucao_base": "1920x1080", "proporcao": "16:9" },
  "sidebar": {
    "largura": 200,
    "item_altura": 48,
    "header_margens": { "top": 20, "right": 0, "bottom": 16, "left": 0 }
  },
  "tela_de_expediente": {
    "proporcao_tela": 0.8,
    "title_bar": { "altura": 32 }
  }
}
```

Alterar um token muda a dimensão em todos os pontos que o leem com `scaled()`.

---

## Resumo: Fluxo de uma Ação do Usuário

1. O jogador clica em "Submeter" na `PaginaInspecao`.
2. A página coleta riscos, fatores, decisão e tempo e emite `submeter_respostas(dict)`.
3. `TelaDeExpediente` e `JanelaPrincipal` reemitem o sinal.
4. O `GameManager` (conectado em `main.py`) executa `processar_submissao()`, sem conhecer o Qt.
5. O `GameManager` chama `view.exibir_tela_diagnostico(resultado)`.
6. `JanelaPrincipal` repassa à `TelaDeExpediente`, que preenche a `PaginaDiagnostico` e troca a página do `QStackedWidget`.
7. O clique em "Continuar" emite `continuar_solicitado()`, e o ciclo recomeça com o próximo relatório ou com a tela de fim de jogo.
