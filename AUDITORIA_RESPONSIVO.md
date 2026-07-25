# Auditoria de Design Responsivo — Inspetor_IFF_BJI

**Data:** 2026-07-24  
**Base:** Skill `design-responsivo` (LayoutLoader, layout.json, padrões de widget)  
**Total de ficheiros analisados:** 26 widgets/ficheiros em `view/`

---

## Sumário Executivo

| Status | Contagem | Widgets |
|--------|----------|---------|
| ✅ **COMPLIANT** | 9 | Taskbar, DesktopShortcut, AnexoPreview, WindowTitleBar, GameOver, BackgroundRiscos, CrtEffectsOverlay, MediaPlayerBase, ImageViewer |
| ⚠️ **PARTIAL** | 8 | TelaMenuPrincipal, Sidebar, CharacterCarousel, PaginaInspecao, AnexoGallery, MediaViewer, VideoPlayer, AudioPlayer |
| ❌ **NON_COMPLIANT** | 9 | WallpaperSelector, PaginaSelecaoPerfil, PaginaLoading, PaginaDiagnostico, GameWin, PaginaGameOver (via GameOver), StampButton, _OverlayArea, TelaDeExpediente |

> **NOTA:** `TelaDeExpediente` tem `__reaplicar_dimensoes` mas só para title bar; `CharacterCarousel` tem scale próprio; `WallpaperSelector` usa constantes hardcoded; páginas simples não usam LayoutLoader.

---

## Análise Detalhada por Widget

### 1. **JanelaPrincipal** (`view/main_window.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 13, 51, 117, 122 |
| scaled()/scaled_margins() | ✅ Via `__sincronizar_escala_com_tela` + `resizeEvent` |
| escala_atualizada connect | ✅ Propaga para LayoutLoader via `set_screen()` |
| __reaplicar_dimensoes | N/A (é o driver do sistema) |
| objectName + property("class") | ✅ `container_area`, `overlay_area` |
| QFrame | ✅ `_OverlayArea` herda QWidget (container) |
| Hardcoded pixels | ⚠️ `setMinimumSize(1024, 576)` — **aceitável** (mínimo funcional) |
| Inline stylesheet | ✅ Não |

**Observação:** É o **motor do sistema responsivo** — alimenta LayoutLoader no `resizeEvent` e no show inicial.

---

### 2. **Taskbar** (`view/desktop/taskbar.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 23 |
| scaled()/scaled_margins() | ✅ Linhas 34, 37, 40, 46-47 |
| escala_atualizada connect | ✅ Linha 30 |
| __reaplicar_dimensoes | ✅ Linha 60-70 (@Slot) |
| objectName + property | ✅ `taskbar` + `taskbar` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não (usa `L.scaled("taskbar", "altura") - 16` para ícone) |
| Inline stylesheet | ✅ Não |

---

### 3. **TelaMenuPrincipal** (`view/desktop/menu.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 19 |
| scaled()/scaled_margins() | ✅ Linhas 36, 112 |
| escala_atualizada connect | ✅ Linha 25 |
| __reaplicar_dimensoes | ✅ Linha 46-51 (@Slot) — **mas incompleto** |
| objectName + property | ✅ `tela_menu_principal` + `tela_menu_principal` |
| QFrame | ❌ Herda **QWidget** (deveria ser QFrame para QSS) |
| Hardcoded pixels | ✅ Não |
| Inline stylesheet | ✅ Não |

**Issues:**
1. **Herda QWidget** — viola regra "QFrame em vez de QWidget puro" (linha 13). QSS `border-radius`/`background-color` não funciona confiavelmente.
2. `__reaplicar_dimensoes` **não reconstrói shortcuts** — apenas atualiza margens e spacing. Se `DesktopShortcut` mudar de tamanho, eles não redimensionam automaticamente (cada um tem seu próprio signal connect, mas o layout pai não força update).
3. `wallpaper_label` usa `resize(self.size())` no `resizeEvent` — OK, mas não passa por LayoutLoader.

---

### 4. **DesktopShortcut** (`view/desktop/desktop_shortcut.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 26 (com injeção opcional para testes) |
| scaled()/scaled_margins() | ✅ Linhas 49-52, 57-60, 66-69, 71-73, 79, 91-94, 118-120 |
| escala_atualizada connect | ✅ Linha 32 |
| __reaplicar_dimensoes | ✅ Linha 55-73 (@Slot) — **completo** |
| objectName + property | ✅ `desktop_shortcut` + `desktop_shortcut` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não (tudo via `L.scaled()`) |
| Inline stylesheet | ✅ Não |

**Destaque:** Permite injeção de `LayoutLoader` no construtor para testes — **padrão exemplar**.

---

### 5. **WallpaperSelector** (`view/desktop/wallpaper_selector.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ **Não usa** |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `wallpaper_selector`, `wallpaper_selector_instrucao`, etc. |
| QFrame | ❌ Herda **QDialog** (aceitável para dialogs) |
| Hardcoded pixels | ❌ **Muitos**: `TAMANHO_THUMBNAIL = (160, 90)`, `setMinimumSize(640, 420)`, `setFixedHeight(120)`, `setFixedSize(thumb_w+16, thumb_h+40)`, `scaled(400, 120)` |
| Inline stylesheet | ✅ Não (usa property class) |

**Issues críticos:**
- **Totalmente fora do sistema responsivo** — usa constantes hardcoded
- Grid recalcula colunas no `resizeEvent` mas com thumb fixo 160×90
- Preview usa `scaled(400, 120)` hardcoded
- `setMinimumSize(640, 420)` impede uso em telas pequenas

---

### 6. **Sidebar** (`view/expediente/widgets/sidebar.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 37 |
| scaled()/scaled_margins() | ✅ Linha 38 (`setFixedWidth`) |
| escala_atualizada connect | ✅ Linha 69 |
| __reaplicar_dimensoes | ✅ Linha 141-143 — **mas só largura** |
| objectName + property | ✅ `sidebar` + `sidebar` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ **Sim**: `setFixedHeight(48)` linha 101, `QSize(20,20)` linha 112, `logo 40x40` linhas 83-86, `margins(0,20,0,16)` linha 74 |
| Inline stylesheet | ✅ Não |

**Issues:**
- Altura dos botões fixa em 48px (linha 101)
- Ícones fixos 20×20 (linha 112)
- Logo hardcoded 40×40 (linhas 83-86)
- Margens do header hardcoded (linha 74)

---

### 7. **WindowTitleBar** (`view/expediente/widgets/window_title_bar.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linhas 40, 90 |
| scaled()/scaled_margins() | ✅ Linhas 37, 41, 44, 92-97 |
| escala_atualizada connect | ✅ Linha 34 |
| __reaplicar_dimensoes | ✅ `reaplicar_dimensoes` pública (linha 87-97) + `__on_escala_atualizada` (linha 80-85) |
| objectName + property | ✅ `window_title_bar` + `window_title_bar` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ **Sim**: botões `setFixedSize(36, 28)` linhas 56, 63, 70 |
| Inline stylesheet | ✅ Não |

**Issue menor:** Botões min/max/close com tamanho fixo 36×28 — deveria vir do layout.json.

---

### 8. **CharacterCarousel** (`view/expediente/widgets/character_carousel.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ **Não usa** — escala própria (`__compute_scale` base 1000×600) |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não (usa `resizeEvent` + `__compute_scale`) |
| objectName + property | ❌ **Não define** |
| QFrame | ❌ Herda **QWidget** |
| Hardcoded pixels | ❌ **Muitos**: `CARD_WIDTH=260`, `CARD_HEIGHT=460`, `SLOT_SPACING=340`, `NAV_BTN_SIZE=52`, etc. (linhas 37-58) |
| Inline stylesheet | ✅ Não (paintEvent custom) |

**Análise:** Sistema de escala **próprio e independente** do LayoutLoader. Funciona bem visualmente (scale factor baseado em área disponível), mas:
- Não reage a `LayoutLoader.escala_atualizada`
- Não usa `layout.json` — constantes no topo do ficheiro
- Não tem `objectName`/`property("class")` — QSS não consegue estilizar
- `resizeEvent` reposiciona botões nav mas não emite signal de mudança de escala

---

### 9. **AnexoPreview** (`view/expediente/widgets/anexo_preview.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 20 |
| scaled()/scaled_margins() | ✅ Linhas 22, 26-29, 46, 53-57 |
| escala_atualizada connect | ✅ Linha 47 |
| __reaplicar_dimensoes | ✅ Linha 50-57 (@Slot) |
| objectName + property | ✅ `anexo_preview` + `anexo_preview` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não |
| Inline stylesheet | ✅ Não |

---

### 10. **StampButton** (`view/expediente/widgets/stamp_button.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `setObjectName` + `setProperty` (linhas 15-16) |
| QFrame | ✅ Herda QFrame |
| Hardcoded pixels | ❌ **Sim**: `tamanho_base = 20`, `margem = 16` (linhas 69-70), rotação fixa |
| Inline stylesheet | ⚠️ **Parcial**: usa `QFont` direto no paintEvent, não QSS |

**Análise:** Widget de desenho customizado (`paintEvent`) com rotação e fonte adaptativa interna. Não integra com LayoutLoader. Funciona para o caso de uso (botão carimbo rotacionado), mas não responsivo ao sistema global.

---

### 11. **PaginaSelecaoPerfil** (`view/expediente/paginas/selecao_perfil.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `pagina_selecao_perfil` + `pagina_selecao_perfil` |
| QFrame | ❌ Herda **QWidget** |
| Hardcoded pixels | ❌ **Sim**: `setContentsMargins(0, 8, 0, 16)`, `setSpacing(12)` (linha 44-45) |
| Inline stylesheet | ✅ Não |

**Depende do `CharacterCarousel`** que também não é responsivo pelo sistema padrão.

---

### 12. **PaginaLoading** (`view/expediente/paginas/loading.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `pagina_loading` + `pagina_loading` |
| QFrame | ❌ Herda **QWidget** |
| Hardcoded pixels | ❌ **Sim**: `QFont("Courier New", 16)` hardcoded (linha 31) |
| Inline stylesheet | ✅ Não |

---

### 13. **PaginaInspecao** (`view/expediente/paginas/inspecao.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ **Não usa diretamente** (usa `AnexoPreview` que usa) |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `pagina_inspecao` + `pagina_inspecao` |
| QFrame | ❌ Herda **QWidget** |
| Hardcoded pixels | ❌ **Muitos**: `setMinimumSize(96, 96)` (linha 221), `setIconSize(QSize(64,64))` (231), `QPixmap.scaled(48,48)` (289-291, 342-344), `QFont` inline stylesheet (302, 308, 349-351, 353-355), `spacing(10/12)`, `margins(0,8,0,0)` |
| Inline stylesheet | ❌ **Sim**: linhas 302, 308, 349-351, 353-355 (`setStyleSheet` direto em labels) |

**Issues críticos:**
- **Inline stylesheet** em múltiplos labels (títulos/subtítulos fatores de risco)
- Muitos tamanhos hardcoded (icons 64×64, 48×48, tiles 96×96)
- QWidget em vez de QFrame
- Não conecta ao LayoutLoader — depende de widgets filhos (`AnexoPreview`, `StampButton`) que têm comportamentos próprios

---

### 14. **PaginaDiagnostico** (`view/expediente/paginas/diagnostico.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `pagina_diagnostico` + `pagina_diagnostico` |
| QFrame | ❌ Herda **QWidget** |
| Hardcoded pixels | ❌ Não explícito, mas layout sem dimensões definidas |
| Inline stylesheet | ✅ Não |

---

### 15. **GameOver** (`view/expediente/paginas/game_over.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 69 |
| scaled()/scaled_margins() | ✅ **Extensivo** — linhas 141, 151, 153, 155, 183-188, 208-213, 220-227, 234-249, 253-257, 271-274, 284, 288, 294-297, 301-302, 310-317, 335, 343-348, 356, 363-370, 394-395, 409-415, 423-436 |
| escala_atualizada connect | ✅ Linha 95 |
| __reaplicar_dimensoes | ✅ Linha 469-493 (@Slot) — **muito completo** |
| objectName + property | ✅ `game_over` + classes por componente |
| QFrame | ✅ |
| Hardcoded pixels | ✅ **Quase nenhum** — usa `L.scaled("gameover", ...)` para tudo |
| Inline stylesheet | ⚠️ Linha 327-328: `setStyleSheet("background-color: transparent;")` no scroll area — **aceitável** (workaround QT) |

**Destaque:** **Widget mais completo** do projecto em responsividade. Usa layout.json exaustivamente (`gameover` section).

---

### 16. **GameWin** (`view/expediente/paginas/game_win.py`) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `game_win` + `game_win` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ Layout sem dimensões, fontes sem tamanho definido |
| Inline stylesheet | ✅ Não |

**Tela "irmã" do GameOver mas sem nenhum sistema responsivo.**

---

### 17. **AnexoGallery** (`view/expediente/overlays/anexo_gallery.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `anexo_gallery` + `anexo_gallery` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ **Sim**: `setFixedSize(48, 48)` (linhas 41, 51), `margins(48,0,48,0)` (linha 37) |
| Inline stylesheet | ✅ Não |

**Overlay de mídia** — deveria ancorar no `_OverlayArea` e reagir a resize (já faz via `setGeometry` externo), mas botões de navegação e margens são hardcoded.

---

### 18. **MediaViewer** (`view/expediente/overlays/media_viewer.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled()/scaled_margins() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não (mas tem `resizeEvent` que reescala pixmap) |
| objectName + property | ✅ `media_viewer` + `media_viewer` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ Não explícito |
| Inline stylesheet | ✅ Não |

---

### 19. **MediaPlayerBase** (`view/widgets/midia/media_player_base.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 40 |
| scaled()/scaled_margins() | ✅ Linhas 41-42, 51 |
| escala_atualizada connect | ❌ **Não conecta** — mas usa `L.scaled` no init |
| __reaplicar_dimensoes | ❌ Não tem |
| objectName + property | Subclasses definem |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não (controles via layout.json `video_player`) |
| Inline stylesheet | ✅ Não |

**Issue:** Não reconecta ao `escala_atualizada` — se janela redimensionar, controles não atualizam altura/fonte.

---

### 20. **VideoPlayer** (`view/widgets/midia/video_player.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Via base |
| scaled() | ✅ Via base |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `video_player` + `video_player` |
| QFrame | ✅ (via base) |
| Hardcoded pixels | ✅ Não |
| Inline stylesheet | ✅ Não |

---

### 21. **AudioPlayer** (`view/widgets/midia/audio_player.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Via base |
| scaled() | ✅ Via base |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `audio_player` + `audio_player` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não |
| Inline stylesheet | ✅ Não |

---

### 22. **ImageViewer** (`view/widgets/midia/image_viewer.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 17 |
| scaled()/scaled_margins() | ❌ **Não usa** — mas usa `resizeEvent` para escalar pixmap ao tamanho do widget |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não |
| objectName + property | ✅ `image_viewer` + `image_viewer` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ Não |
| Inline stylesheet | ✅ Não |

**Nota:** Funciona por `resizeEvent` (adapta pixmap ao widget pai), não pelo LayoutLoader. Como é usado dentro de overlays que já são dimensionados pelo sistema, funciona na prática.

---

### 23. **BackgroundRiscos** (`view/widgets/efeitos/background_riscos.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 66 (injetado no construtor) |
| scaled()/scaled_margins() | ✅ Linhas 84-89, 130-135 (via `L.scaled` para `size_base_max/min`) |
| escala_atualizada connect | ❌ **Não connecta direto** — mas expõe `invalidar_cache()` chamado por `GameOver.__reaplicar_dimensoes` |
| __reaplicar_dimensoes | ❌ Não (usa `invalidar_cache` + `paintEvent`) |
| objectName + property | ✅ `bg_riscos` + `bg_riscos` |
| QFrame | ❌ Herda **QWidget** (mas `WA_TranslucentBackground` + `WA_TransparentForMouseEvents` — OK para overlay decorativo) |
| Hardcoded pixels | ✅ Não (usa `L.scaled` + clamp `FLOOR_SCALE`/`CEIL_SCALE`) |
| Inline stylesheet | ✅ Não |

**Padrão interessante:** Recebe `LayoutLoader` injetado, faz cache de pixmaps coloridos/escalados, invalida cache no signal de escala. **Modelo para widgets de paintEvent customizado.**

---

### 24. **CrtEffectsOverlay** (`view/widgets/efeitos/crt_overlay.py`) — ✅ COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não — usa constantes de classe para espaçamento/speed |
| scaled() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| __reaplicar_dimensoes | ❌ Não (mas `resizeEvent` chama `paintEvent` que usa `width()`/`height()`) |
| objectName + property | ✅ `crt_overlay` + `crt_overlay` |
| QFrame | ✅ |
| Hardcoded pixels | ✅ **Sim, mas proporcionais** — constantes de classe (`_SCANLINE_SPACING=3`, `_SCANLINE_BAR_HEIGHT=40`, etc.) |
| Inline stylesheet | ✅ Não |

**Análise:** Overlay decorativo full-screen que desenha relativo ao próprio `width()`/`height()` no `paintEvent`. **Não precisa do LayoutLoader** porque é intrinsicamente responsivo (desenha em % da área). Constants são razões visuais, não pixels absolutos de layout.

---

### 25. **_OverlayArea** (`view/main_window.py` linha 176) — ❌ NON_COMPLIANT
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ❌ Não |
| scaled() | ❌ Não |
| escala_atualizada connect | ❌ Não |
| objectName | ✅ `overlay_area` |
| QFrame | ❌ Herda **QWidget** (container de layout) |
| Hardcoded pixels | ✅ Não (usa `rect()` do parent) |

**Nota:** É infraestrutura de layout (z-order), não widget visual. Não precisa escalar — apenas propaga `overlay_resized` signal.

---

### 26. **TelaDeExpediente** (`view/expediente/tela.py`) — ⚠️ PARTIAL
| Critério | Status |
|----------|--------|
| LayoutLoader.instance() | ✅ Linha 85, 97, 209 |
| scaled() | ✅ Linha 86 (`title_bar` altura), 209 |
| escala_atualizada connect | ✅ Linha 97 (title bar), 100 (overlay_resized) |
| __reaplicar_dimensoes | ✅ Linha 206-209 — **mas só title bar** |
| objectName + property | ✅ `tela_de_expediente` + `tela_expediente` |
| QFrame | ✅ |
| Hardcoded pixels | ❌ **Sim**: `proporcao_tela = 0.8` hardcoded no `__reposicionar` (linha 263) — **deveria vir do layout.json** |
| Inline stylesheet | ✅ Não |

**Issue:** `__reposicionar` usa `0.8` hardcoded (linha 263) em vez de `L.get("tela_de_expediente", "proporcao_tela")` que existe no layout.json (linha 125). `__reaplicar_dimensoes` só atualiza title bar, não reposiciona o expediente.

---

## Padrões de Não-Conformidade Recorrentes

| Padrão | Ocorrências | Exemplo |
|--------|-------------|---------|
| **Herda QWidget em vez de QFrame** | 9 | TelaMenuPrincipal, PaginaSelecaoPerfil, PaginaLoading, PaginaDiagnostico, CharacterCarousel, Sidebar (header), etc. |
| **Hardcoded pixel values** | 15+ | `setFixedHeight(48)`, `setFixedSize(36,28)`, `QSize(64,64)`, `setMinimumSize(96,96)` |
| **Inline `setStyleSheet`** | 4 | PaginaInspecao (linhas 302, 308, 349, 353), GameOver (scroll area) |
| **Não conecta `escala_atualizada`** | 12 | Widgets que usam `L.scaled()` no init mas não reconectam |
| **Sistema de escala próprio** | 2 | CharacterCarousel (`__compute_scale`), BackgroundRiscos (clamp próprio) |
| **Falta `objectName`/`property("class")`** | 3 | CharacterCarousel, StampButton (parcial), _OverlayArea |
| **Constantes no topo do ficheiro** | 3 | CharacterCarousel (linhas 37-58), WallpaperSelector (linha 41), CrtEffectsOverlay (linhas 35-47) |

---

## Ações Recomendadas (Prioridade)

### 🔴 Crítico (Quebra responsividade em telas não-1920×1080)
1. **WallpaperSelector** — Reescrever usando LayoutLoader + layout.json (adicionar seção `wallpaper_selector`)
2. **PaginaInspecao** — Eliminar `setStyleSheet` inline; mover tamanhos para layout.json; conectar LayoutLoader
3. **CharacterCarousel** — Migrar constantes para layout.json; adicionar `objectName`; conectar `escala_atualizada` (ou documentar como excepção controlada)
4. **TelaDeExpediente** — Usar `L.get("tela_de_expediente", "proporcao_tela")` em vez de `0.8` hardcoded

### 🟡 Alto (Inconsistência visual em resize)
5. **Sidebar** — Altura botões, ícones, logo, margens header via LayoutLoader
6. **WindowTitleBar** — Botões min/max/close via LayoutLoader
7. **MediaPlayerBase/VideoPlayer/AudioPlayer** — Conectar `escala_atualizada` + `__reaplicar_dimensoes`
8. **AnexoGallery/MediaViewer** — Botões nav e margens via LayoutLoader
9. **PaginaSelecaoPerfil/PaginaLoading/PaginaDiagnostico/GameWin** — Adotar LayoutLoader completo

### 🟢 Médio (Qualidade/Manutenibilidade)
10. **QWidget → QFrame** nos 9 widgets identificados
11. **StampButton** — Integrar fonte/tamanho base no layout.json (seção `stamp_button`)
12. **LayoutLoader injetável** — Padronizar injeção opcional (como `DesktopShortcut`) para testabilidade

---

## layout.json — Seções Faltantes Sugeridas

```json
{
  "wallpaper_selector": {
    "largura_min": 640,
    "altura_min": 420,
    "thumbnail": { "largura": 160, "altura": 90, "spacing": 12 },
    "preview": { "largura_max": 400, "altura": 120 },
    "margens": { "left": 16, "top": 16, "right": 16, "bottom": 16 },
    "fontes": { "instrucao": { "size": 10 }, "preview": { "size": 11 } }
  },
  "sidebar": {
    "largura": 200,
    "item_altura": 48,
    "icone_tamanho": 20,
    "logo_tamanho": 40,
    "header_margens": { "top": 20, "bottom": 16 },
    "divider_altura": 1
  },
  "window_title_bar": {
    "altura": 32,
    "btn_tamanho": 36,
    "btn_altura": 28,
    "margens": { "left": 12, "top": 0, "right": 8, "bottom": 0 }
  },
  "character_carousel": {
    "card_largura_base": 260,
    "card_altura_base": 460,
    "slot_spacing": 340,
    "nav_btn_tamanho": 52,
    "nav_btn_margem": 16,
    "scale_ref": { "width": 1000, "height": 600 },
    "scale_min": 0.45,
    "scale_max": 1.0
  },
  "pagina_inspecao": {
    "tile_risco_min": 96,
    "icone_risco": 64,
    "icone_fator": 48,
    "group_margens": { "deck": {...}, "prancheta": {...} },
    "spacing": { "grupos": 12, "tiles": 10 }
  },
  "anexo_gallery": {
    "nav_btn_tamanho": 48,
    "content_margens": { "left": 48, "right": 48 }
  },
  "stamp_button": {
    "fonte_base": 20,
    "margem_texto": 16,
    "letter_spacing_factor": 0.1
  }
}
```

---

## Testes de Regressão a Adicionar

Expandir `tests/view/test_dimensionamento_critico.py`:

```python
# B8: WallpaperSelector escala corretamente
def test_wallpaper_selector_responsivo(qapp, reset_layout_loader):
    loader = LayoutLoader.instance()
    loader.set_screen(1280, 720)
    dialog = WallpaperSelector()
    # Verificar thumbnails, preview, grid usam scaled()

# B9: CharacterCarousel reage a escala_atualizada
def test_character_carousel_escala_atualizada(qapp, reset_layout_loader):
    carousel = CharacterCarousel(personagens)
    loader = LayoutLoader.instance()
    spy = MagicMock()
    loader.escala_atualizada.connect(spy)
    # Simular resize
    loader.set_screen(1280, 720)
    QApplication.processEvents()
    spy.assert_called()

# B10: PaginaInspecao não tem inline stylesheet
def test_pagina_inspecao_sem_inline_stylesheet(qapp):
    pagina = PaginaInspecao()
    for child in pagina.findChildren(QLabel):
        assert child.styleSheet() == "", f"Inline stylesheet em {child.objectName()}"
```

---

## Conclusão

O sistema responsivo **funciona bem na base** (LayoutLoader, Taskbar, GameOver, AnexoPreview, DesktopShortcut) mas **não foi aplicado consistentemente** em ~65% dos widgets. As principais falhas são:

1. **Ausência de LayoutLoader** em páginas simples e dialogs
2. **Hardcoded pixels** em widgets complexos (Sidebar, CharacterCarousel, PaginaInspecao)
3. **Inline stylesheet** violando o Design System QSS
4. **QWidget em vez de QFrame** impedindo QSS confiável

**Próximo passo recomendado:** Criar issue/backlog para migrar os 9 widgets NON_COMPLIANT e 8 PARTIAL, priorizando WallpaperSelector, PaginaInspecao e CharacterCarousel.