# Fim de Expediente (Auditoria / Game Over) — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] Turno iniciado e todos os relatórios da pilha já foram avaliados
- [ ] `__relatorio_atual is None` (nenhum relatório pendente)
- [ ] `__pilha_relatorios` vazia
- [ ] `__pontuacao_acumulada_turno` e `__v_max_turno` calculados ao longo do turno

### Pós-condições

- [ ] `verificar_vitoria_do_turno()` retorna `True` ou `False`
- [ ] Auditoria de expediente gerada com nota final, status e desempenho por categoria
- [ ] UI exibe tela de certificado (aprovado) ou notificação de reciclagem (reprovado)
- [ ] Log de auditoria registrado em disco

---

## 2. Diagrama de sequência

### Fluxo principal (caminho feliz — Aprovado)

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno
    participant MOTOR as MotorDePontuacao

    User->>Tela: Clica "OBTER PRÓXIMO"
    activate Tela

    Tela->>GM: obter_relatorio_da_pilha()
    activate GM
    GM->>GDT: obter_relatorio_da_pilha()
    activate GDT

    GDT->>GDT: Verifica __pilha_relatorios
    alt Pilha vazia
        GDT-->>GM: RuntimeError("[Erro - Turno] Lista de Relatorios ainda tem elementos")
        deactivate GDT
        GM-->>Tela: {"fim_turno": True}

        Tela->>GM: verificar_vitoria_do_turno()
        activate GM
        GM->>GDT: verificar_vitoria_do_turno()
        activate GDT

        GDT->>GDT: Confere __relatorio_atual is None
        GDT->>GDT: Confere pilha vazia
        GDT->>MOTOR: conferir_condicao_vitoria(nota, v_max)
        activate MOTOR
        MOTOR-->>GDT: True (nota >= 60%)
        deactivate MOTOR

        GDT-->>GM: True
        deactivate GDT
        GM-->>Tela: {"aprovado": True, "nota": 85.5, "total": 100.0}
        deactivate GM

        Tela->>Tela: Exibe tela de certificado
        Tela-->>User: "PARABÉNS! Inspetor Aprovado"
    end
    deactivate Tela
```

### Fluxo alternativo — Reprovado

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno
    participant MOTOR as MotorDePontuacao

    User->>Tela: Última submissão concluída
    Tela->>GM: verificar_vitoria_do_turno()
    GM->>GDT: verificar_vitoria_do_turno()
    GDT->>MOTOR: conferir_condicao_vitoria(nota, v_max)
    MOTOR-->>GDT: False (nota < 60%)
    GDT-->>GM: False
    GM-->>Tela: {"aprovado": False, "nota": 42.0, "total": 100.0}

    Tela->>Tela: Exibe notificação de reciclagem
    Tela-->>User: "EXPEDIENTE REPROVADO<br/>Treinamento adicional necessário"
```

### Fluxo de auditoria — Geração do relatório final

```mermaid
sequenceDiagram
    participant Tela as TelaDeExpediente
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno
    participant AUDITORIA as Sistema de Certificação

    Tela->>GM: gerar_relatorio_auditoria()
    activate GM

    GM->>GDT: obter_pontuacao_acumulada()
    activate GDT
    GDT-->>GM: {"pontuacao": 85.5, "v_max": 100.0, "qtd_relatorios": 5}
    deactivate GDT

    GM->>AUDITORIA: certificar_expediente(nota, v_max, relatorios)
    activate AUDITORIA

    Note over AUDITORIA: Cálculo final:<br/>- Nota percentual: 85.5%<br/>- Status: APROVADO<br/>- Menção: "A - Excelente"<br/>- Data/hora do expediente

    AUDITORIA-->>GM: CertificadoDTO
    deactivate AUDITORIA

    GM-->>Tela: CertificadoDTO
    deactivate GM

    Tela->>Tela: Renderiza certificado<br/>ou reciclagem
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta ao usuário |
|----|---------|---------------------|---------------------|
| E1 | Turno não iniciado | `verificar_vitoria_do_turno()` sem turno ativo | `Exception("[Erro - Turno] Turno ainda não iniciado")` |
| E2 | Relatório pendente | Turno ainda tem relatório ativo sem avaliação | `RuntimeError("[Erro - Turno] Relatório pendente de avaliação")` |
| E3 | Pilha não vazia | Ainda há relatórios não jogados na pilha | `ValueError("[Erro - Turno] Lista de Relatorios ainda tem elementos")` |

---

### E1 — Turno não iniciado

**Condição:** `verificar_vitoria_do_turno()` chamado sem `__turno_iniciado`.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: verificar_vitoria_do_turno()
    activate GDT
    GDT->>GDT: Verifica __turno_iniciado
    alt False
        GDT-->>UI: Exception("[Erro - Turno] Turno ainda não iniciado")
    end
    deactivate GDT
```

**Decisão:** guarda padrão do `GerenciadorDeTurno` — sem turno, nenhuma operação de verificação faz sentido.

---

### E2 — Relatório pendente

**Condição:** jogador tentou encerrar sem avaliar o último relatório.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: verificar_vitoria_do_turno()
    activate GDT
    GDT->>GDT: Verifica __relatorio_atual is None
    alt Não é None
        GDT-->>UI: RuntimeError("[Erro - Turno] Relatório pendente de avaliação")
    end
    deactivate GDT
```

**Decisão:** impede que o sistema gere auditoria com dados incompletos. O jogador precisa submeter ou descartar o relatório ativo.

---

### E3 — Pilha não vazia

**Condição:** jogador tentou encerrar o turno com relatórios não jogados.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: verificar_vitoria_do_turno()
    activate GDT
    GDT->>GDT: Verifica len(__pilha_relatorios) != 0
    alt Ainda há elementos
        GDT-->>UI: ValueError("[Erro - Turno] Lista de Relatorios ainda tem elementos")
    end
    deactivate GDT
```

**Decisão:** a integridade da auditoria exige que todos os cenários do turno tenham sido respondidos. O jogador deve completar a pilha inteira antes de ver seu resultado final.
