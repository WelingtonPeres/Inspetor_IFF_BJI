# [Nome do fluxo] — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

Liste o que deve ser verdadeiro antes do fluxo iniciar:

- [ ] Condição 1 (ex: usuário possui cadastro ativo no sistema)
- [ ] Condição 2 (ex: serviço de autenticação está disponível)
- [ ] Condição 3 (ex: conexão com o banco de dados estabelecida)

### Pós-condições

Liste o estado esperado ao final do fluxo com sucesso:

- [ ] Pós-condição 1 (ex: sessão criada e token JWT emitido)
- [ ] Pós-condição 2 (ex: último acesso do usuário atualizado)
- [ ] Pós-condição 3 (ex: log de autenticação registrado)

---

## 2. Diagrama de sequência

### Fluxo principal (caminho feliz)

```mermaid
sequenceDiagram
    actor Usuário
    participant Frontend
    participant API
    participant Banco as Banco de Dados

    Usuário->>Frontend: Ação inicial
    Frontend->>API: Requisição
    API->>Banco: Consulta
    Banco-->>API: Resposta
    API-->>Frontend: Resultado
    Frontend-->>Usuário: Feedback
```

### Fluxo alternativo (opcional)

> Descreva aqui quando este fluxo alternativo ocorre e como ele difere do principal.

```mermaid
sequenceDiagram
    actor Usuário
    participant Frontend
    participant API

    Usuário->>Frontend: Ação alternativa
    Frontend->>API: Requisição alternativa
    API-->>Frontend: Resposta alternativa
    Frontend-->>Usuário: Feedback alternativo
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta ao usuário | HTTP |
|----|---------|---------------------|---------------------|------|
| E1 | [Nome do erro] | [O que causou] | [Mensagem exibida] | 4xx |
| E2 | [Nome do erro] | [O que causou] | [Mensagem exibida] | 5xx |
| E3 | [Nome do erro] | [O que causou] | [Mensagem exibida] | 4xx |

---

### E1 — [Nome do cenário de erro]

**Condição:** descreva quando este erro ocorre.

```mermaid
sequenceDiagram
    actor Usuário
    participant Frontend
    participant API

    Usuário->>Frontend: Ação
    Frontend->>API: Requisição
    API-->>Frontend: 4xx Código de erro
    Frontend-->>Usuário: Mensagem de erro
```

**Decisão:** explique a escolha técnica ou de segurança por trás do comportamento.

---

### E2 — [Nome do cenário de erro]

**Condição:** descreva quando este erro ocorre.

```mermaid
sequenceDiagram
    actor Usuário
    participant Frontend
    participant API
    participant Serviço

    Usuário->>Frontend: Ação
    Frontend->>API: Requisição
    API->>Serviço: Chamada
    note over Serviço: Indisponível ou timeout
    API-->>Frontend: 5xx Código de erro
    Frontend-->>Usuário: Tente novamente em instantes
```

**Decisão:** explique o comportamento de fallback ou retry adotado.

---

### E3 — [Nome do cenário de erro]

**Condição:** descreva quando este erro ocorre.

```mermaid
sequenceDiagram
    actor Usuário
    participant Frontend
    participant API
    participant Cache

    Usuário->>Frontend: Ação
    Frontend->>API: Requisição
    API->>Cache: Verifica limite
    Cache-->>API: Limite atingido
    API-->>Frontend: 429 Too Many Requests
    Frontend-->>Usuário: Aguarde X minutos
```

**Decisão:** explique a estratégia de rate limiting ou bloqueio adotada.
