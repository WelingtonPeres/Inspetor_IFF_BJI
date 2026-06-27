# GameManager — Conexão View-Controller (MVP)

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] `GameManager` instanciado com View injetada
- [ ] Aplicação inicializada via `iniciar_aplicacao()`
- [ ] Estado `ESTADO_MENU` ativo, `ViewMenuInicial` visível

### Pós-condições

- [ ] Perfil selecionado armazenado em `__perfil_selecionado`
- [ ] `GerenciadorDeTurno` criado e turno iniciado
- [ ] View trocada para tela de inspeção com primeiro relatório

---

## 2. Diagrama de sequência

### Fluxo principal (Menu → Expediente)

```mermaid
sequenceDiagram
    participant J as Jogador
    participant VM as ViewMenuInicial
    participant VS as ViewSelecaoPerfil
    participant GM as GameManager

    J->>VM: Clica "Iniciar"
    VM->>GM: Signal: btn_iniciar_clicado
    GM->>GM: on_iniciar_solicitado()
    GM->>VS: exibir_selecao_perfil()

    J->>VS: Seleciona "T_MEIO_AMBIENTE" + "Confirmar"
    VS->>GM: Signal: perfil_confirmado("T_MEIO_AMBIENTE")
    Note over GM: iniciar_expediente("T_MEIO_AMBIENTE")

    GM->>GM: __iniciar_campanha("T_MEIO_AMBIENTE")
    GM->>GM: __iniciar_dia(1)
    GM->>GM: GerenciadorDeTurno("T_MEIO_AMBIENTE")
    GM->>GM: iniciar_turno()

    GM->>VM: trocar_para_tela_inspecao()
    Note over VM: ViewContainer troca<br/>stacked widget
```

### Fluxo principal (Inspeção → Diagnóstico → Avanço)

```mermaid
sequenceDiagram
    participant J as Jogador
    participant VI as ViewInspecao
    participant VD as ViewDiagnostico
    participant GM as GameManager
    participant GT as GerenciadorDeTurno

    VI->>GM: requisitar_dados_relatorio_atual()
    GM->>GT: obter_relatorio_da_pilha()
    GT-->>GM: Relatorio
    GM-->>VI: dict (id_cenario, titulo, ...)
    VI->>J: Exibe cenário

    J->>VI: Preenche riscos, fatores, decisão
    VI->>GM: processar_submissao({riscos, fatores, decisao, tempo})
    GM->>GT: avaliar_respostas_jogador(...)
    GT-->>GM: pontuacao: float
    GM->>GM: __pontuacao_global += pontuacao
    GM->>VD: exibir_tela_diagnostico(pontuacao)

    J->>VD: Clica "Continuar"
    VD->>GM: avancar_fila_ou_dia()
    GM->>GT: qnt_relatorios()

    alt Ainda há relatórios
        GT-->>GM: > 0
        GM->>VI: trocar_para_tela_inspecao()
        GM->>VI: renderizar_relatorio(dados)
    else Pilha vazia
        GT-->>GM: == 0
        GM->>GM: __dias_concluidos += 1
        alt Dias restantes na campanha
            GM->>GM: __iniciar_dia(próximo_dia)
        else Campanha concluída
            GM->>VD: exibir_resultado(pontuacao_global, dias)
        end
    end
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta na UI |
|----|---------|---------------------|----------------|
| E1 | Expediente fora do menu | `iniciar_expediente()` chamado fora de `ESTADO_MENU` | `RuntimeError` com tag `[Erro - GameManager]` |
| E2 | Submissão sem turno | `processar_submissao()` sem `__gerenciador_turno` ativo | `RuntimeError` com tag `[Erro - GameManager]` |
| E3 | Regra de negócio violada | Turno lança `ValueError` (ex: decisão inválida) | `view.exibir_popup_erro()` com a mensagem |
| E4 | Erro interno inesperado | Falha não mapeada no domínio | `logger.error()` + `view.exibir_popup_erro()` genérico |

### E1 — Expediente fora do menu

**Condição:** `iniciar_expediente()` é chamado enquanto `__estado_atual != ESTADO_MENU`.

```mermaid
sequenceDiagram
    participant VS as ViewSelecaoPerfil
    participant GM as GameManager

    VS->>GM: perfil_confirmado("T_QUIMICA")
    GM->>GM: __estado_atual = ESTADO_EXPEDIENTE
    GM-->>VS: RuntimeError("[Erro - GameManager] Expediente so pode ser iniciado pelo menu.")
```

### E3 — Regra de negócio violada

**Condição:** o turno lança `ValueError` durante `avaliar_respostas_jogador()`.

```mermaid
sequenceDiagram
    participant VI as ViewInspecao
    participant GM as GameManager
    participant GT as GerenciadorDeTurno

    VI->>GM: processar_submissao({decisao: ""})
    GM->>GT: avaliar_respostas_jogador(...)
    GT-->>GM: ValueError("[Erro - Turno] Decisão inválida.")
    GM->>GM: Captura ValueError
    GM->>VI: exibir_popup_erro("[Erro - Turno] Decisão inválida.")
```

---

## 4. Métodos públicos da View (Contrato MVP)

| Método | Chamado por | Função |
|--------|-------------|--------|
| `inicializar()` | `iniciar_aplicacao()` | Prepara a janela principal |
| `fechar()` | `encerrar_aplicacao()` | Encerra a aplicação |
| `exibir_menu()` | `carregar_menu_principal()` | Mostra `ViewMenuInicial` |
| `exibir_selecao_perfil()` | `on_iniciar_solicitado()` | Mostra `ViewSelecaoPerfil` |
| `trocar_para_tela_inspecao()` | `__iniciar_dia()` | Mostra `ViewInspecao` |
| `exibir_tela_diagnostico(pontuacao)` | `processar_submissao()` | Mostra `ViewDiagnostico` |
| `renderizar_relatorio(dados)` | `avancar_fila_ou_dia()` | Alimenta `ViewInspecao` com dados |
| `exibir_resultado(pont_global, dias)` | `__encerrar_campanha()` | Mostra tela de resultados |
| `exibir_popup_erro(mensagem)` | Todos os catchs | Exibe pop-up de erro |
