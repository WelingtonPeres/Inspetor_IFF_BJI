# Avaliação (Core Gameplay) — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] Turno iniciado com sucesso
- [ ] `__relatorio_atual` contém um `Relatorio` obtido via `obter_relatorio_da_pilha()`
- [ ] O relatório ativo possui `FolhaDeGabarito` válida

### Pós-condições

- [ ] `__relatorio_atual = None` (libera o ciclo para o próximo relatório)
- [ ] `__pontuacao_acumulada_turno` acrescida da nota do relatório avaliado
- [ ] `FolhaDeResposta` anexada permanentemente ao relatório
- [ ] Nota final do relatório retornada à UI

---

## 2. Diagrama de sequência

### Fluxo principal (caminho feliz)

```mermaid
sequenceDiagram
    participant UI as View (Interface)
    participant GDT as GerenciadorDeTurno
    participant REL as Relatorio (Ativo)
    participant DIAG as DiagnosticoDeResposta
    participant DTO as DiagnosticoPontuacaoDTO
    participant MOTOR as MotorDePontuacao

    UI->>GDT: avaliar_respostas_jogador(riscos, fatores, decisao, tempo)
    activate GDT

    GDT->>GDT: __processar_submissao_jogador(riscos, fatores, decisao, tempo)
    activate GDT
    GDT-->>GDT: FolhaDeResposta
    deactivate GDT

    GDT->>REL: anexar_resposta_jogador(resposta)
    activate REL
    REL-->>GDT: void
    deactivate REL

    GDT->>GDT: Obtém gabarito: relatorio.folha_gabarito

    GDT->>DIAG: gerar_diagnostico_pontuacao(gabarito, respostas)
    activate DIAG

    DIAG-->>DTO: DiagnosticoPontuacaoDTO (frozen)

    DTO-->>DIAG: DTO congelado
    DIAG-->>GDT: DiagnosticoPontuacaoDTO
    deactivate DIAG

    GDT->>MOTOR: calcular_vmax_relatorio(relatorio)
    activate MOTOR
    MOTOR-->>GDT: v_max (float)
    deactivate MOTOR

    GDT->>MOTOR: calcular_pontuacao_relatorio(v_max, dto)
    activate MOTOR

    MOTOR->>MOTOR: _calcular_pontuacao_riscos(v_max, corretos, gabarito, marcados)
    MOTOR->>MOTOR: _calcular_pontuacao_inseguranca(v_max, acertou_ato, acertou_condicao)
    MOTOR->>MOTOR: _calcular_pontuacao_decisao(v_max, status)
    MOTOR->>MOTOR: _calcular_fator_tempo(tempo)

    MOTOR-->>GDT: nota_final (float)
    deactivate MOTOR

    GDT->>GDT: __pontuacao_acumulada_turno += nota_final
    GDT->>GDT: __relatorio_atual = None (libera para próximo)

    GDT-->>UI: pontuacao_final (float)
    deactivate GDT
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta ao usuário |
|----|---------|---------------------|---------------------|
| E1 | Turno não iniciado | `avaliar_respostas_jogador()` sem turno ativo | `Exception("[Erro - Turno] Turno ainda não iniciado")` |
| E2 | Sem relatório ativo | `avaliar_respostas_jogador()` sem `__relatorio_atual` | `RuntimeError("[Erro - Turno] Nenhum relatório foi obtido da pilha")` |
| E3 | Decisão inválida | Valor de `decisao` fora de `["INTERDITAR", "ADVERTIR", "IGNORAR"]` | `ValueError("[Erro] Decisão tomada inválida")` |
| E4 | Tempo negativo | `tempo_segundos < 0` | `ValueError("[Erro] Tempo gasto inválido")` |
| E5 | Risco inválido | Tipo de risco fora de `LISTA_RISCOS_VALIDOS` | `ValueError("[Erro] Riscos inválidos encontrados")` |
| E6 | Fator inválido | Fator fora de `FATORES_INSEGURANCA_VALIDOS` | `ValueError("[Erro] Fatores de insegurança inválidos encontrados")` |

---

### E1 — Turno não iniciado

**Condição:** `avaliar_respostas_jogador()` é chamado com `__turno_iniciado == False`.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: avaliar_respostas_jogador(...)
    activate GDT
    GDT->>GDT: Verifica __turno_iniciado
    alt False
        GDT-->>UI: Exception("[Erro - Turno] Turno ainda não iniciado")
    end
    deactivate GDT
```

**Decisão:** mesma guarda do laço de jogo — a flag de turno protege todo o ciclo de vida.

---

### E2 — Sem relatório ativo

**Condição:** `avaliar_respostas_jogador()` é chamado sem que um relatório tenha sido obtido da pilha.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: avaliar_respostas_jogador(...)
    activate GDT
    GDT->>GDT: Verifica __relatorio_atual is None
    alt True
        GDT-->>UI: RuntimeError("[Erro - Turno] Nenhum relatório foi obtido da pilha")
    end
    deactivate GDT
```

**Decisão:** impede que o sistema avalie sem um relatório em mãos; o jogador deve chamar `obter_relatorio_da_pilha()` primeiro.

---

### E3 — Decisão inválida

**Condição:** o campo `decisao` não está entre `"INTERDITAR"`, `"ADVERTIR"` ou `"IGNORAR"`.

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant FR as FolhaDeResposta

    GDT->>FR: __init__(riscos, fatores, decisao_tomada, tempo)
    activate FR
    alt decisao_tomada inválida
        FR-->>GDT: ValueError("[Erro] Decisão tomada inválida")
    end
    deactivate FR
```

**Decisão:** validação no construtor da entidade de domínio — a FolhaDeResposta não pode existir em estado inconsistente.

---

### E4 — Tempo negativo

**Condição:** `tempo_segundos < 0`.

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant FR as FolhaDeResposta

    GDT->>FR: __init__(riscos, fatores, decisao_tomada, tempo)
    activate FR
    alt tempo_gasto_segundos < 0
        FR-->>GDT: ValueError("[Erro] Tempo gasto inválido")
    end
    deactivate FR
```

**Decisão:** tempo físico não pode ser negativo; o front-end deve garantir um cronômetro que nunca dispare valores negativos.
