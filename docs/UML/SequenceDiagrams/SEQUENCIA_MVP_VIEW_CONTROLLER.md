# Integração View-Controller (MVP) — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] Aplicação PySide6 inicializada com `QApplication` e `setup_logging()`
- [ ] `GameManager` instanciado com um perfil de curso válido
- [ ] `TelaDeExpediente` construída e conectada aos sinais do `GameManager`
- [ ] Turno ainda não iniciado (botão "Iniciar Expediente" visível)

### Pós-condições

- [ ] Turno iniciado e `TelaDeExpediente` exibindo o primeiro relatório
- [ ] Ou: mensagem de erro exibida em `QMessageBox` sem corromper o estado da View
- [ ] Todos os `ValueError` e `RuntimeError` do domínio convertidos em pop-ups modais

---

## 2. Diagrama de sequência

### Fluxo principal (caminho feliz)

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente (PySide6)
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno

    User->>Tela: Clica "INICIAR EXPEDIENTE"
    activate Tela

    Tela->>Tela: Desabilita botão "Iniciar"
    Tela->>GM: iniciar_turno(perfil)
    activate GM

    GM->>GDT: iniciar_turno(perfil)
    activate GDT

    GDT-->>GM: True
    deactivate GDT

    GM-->>Tela: True
    deactivate GM

    Tela->>Tela: Habilita painel de jogo
    Tela->>GM: obter_relatorio_da_pilha()
    activate GM
    GM->>GDT: obter_relatorio_da_pilha()
    activate GDT
    GDT-->>GM: Relatorio
    deactivate GDT
    GM-->>Tela: Relatorio
    deactivate GM

    Tela->>Tela: Renderiza dados na tela<br/>(título, local, anexos, opções)
    Tela-->>User: Interface pronta para resposta
    deactivate Tela
```

### Fluxo alternativo — Erro de domínio capturado pelo Facade

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente (PySide6)
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno

    User->>Tela: Submete resposta sem preencher decisão
    activate Tela

    Tela->>GM: avaliar_respostas_jogador([], [], "", 45)
    activate GM

    GM->>GDT: avaliar_respostas_jogador(...)
    activate GDT

    GDT->>GDT: __processar_submissao_jogador(...)
    GDT-->>GM: ValueError("[Erro] Decisão tomada inválida")
    deactivate GDT

    GM->>GM: Captura exceção<br/>e extrai mensagem
    GM-->>Tela: {"erro": "Decisão tomada inválida"}
    deactivate GM

    Tela->>Tela: QMessageBox.critical("Erro", msg)
    Tela-->>User: Pop-up vermelho com a mensagem
    deactivate Tela
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta na UI |
|----|---------|---------------------|----------------|
| E1 | Decisão não preenchida | Jogador submete sem decisão ou valor inválido | `QMessageBox.critical("Decisão inválida")` |
| E2 | Tempo negativo ou zerado | Cronômetro corrompido ou manipulado | `QMessageBox.critical("Tempo inválido")` |
| E3 | Curso inválido | Perfil não reconhecido na inicialização | `QMessageBox.critical("Curso não encontrado")` |
| E4 | Nenhum arquivo JSON | Diretório de dados vazio ou ausente | `QMessageBox.critical("Dados do curso não encontrados")` |
| E5 | Turno já iniciado | Duplo clique no botão "Iniciar" | Botão já desabilitado; fallback silencioso |
| E6 | Erro inesperado (5xx lógico) | Falha interna sem mensagem amigável | `QMessageBox.critical("Erro interno")` + log |

---

### E1 — Decisão não preenchida

**Condição:** o jogador submete a resposta com `decisao == ""` ou valor fora de `["INTERDITAR", "ADVERTIR", "IGNORAR"]`.

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente (PySide6)
    participant GM as GameManager (Facade)
    participant GDT as GerenciadorDeTurno

    User->>Tela: Clica "SUBMETER" sem decisão
    Tela->>GM: avaliar_respostas_jogador(riscos, fatores, "", tempo)
    GM->>GDT: avaliar_respostas_jogador(...)
    GDT-->>GM: ValueError("[Erro] Decisão tomada inválida")
    GM-->>Tela: {"erro": "Decisão inválida"}

    Tela->>Tela: QMessageBox.critical(
    Note over Tela: "Erro de validação",<br/>"Selecione uma decisão<br/>administrativa antes<br/>de submeter.")
    Tela-->>User: Pop-up vermelho
```

**Decisão:** o `GameManager` atua como barreira de exceções: nenhum `ValueError` ou `RuntimeError` do domínio vaza para a View. Toda exceção é convertida em um dicionário `{"erro": msg}` que a UI lê para exibir o `QMessageBox`.

---

### E4 — Nenhum arquivo JSON

**Condição:** o diretório base não contém arquivos `.json` ou o diretório não existe.

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente (PySide6)
    participant GM as GameManager (Facade)
    participant REPO as RepositorioJSON

    User->>Tela: Clica "INICIAR EXPEDIENTE"
    Tela->>GM: iniciar_turno(perfil)
    GM->>REPO: __init__(diretorio, curso, qtd)
    REPO-->>GM: FileNotFoundError
    GM-->>Tela: {"erro": "Dados do curso não encontrados"}

    Tela->>Tela: QMessageBox.critical(
    Note over Tela: "Erro de inicialização",<br/>"Os dados do curso<br/>não foram encontrados.<br/>Contate o administrador.")
    Tela-->>User: Pop-up vermelho
```

**Decisão:** o Facade unifica todos os erros de I/O (FileNotFoundError, JSONDecodeError, ValidationError) em uma única mensagem amigável. O detalhe técnico vai para o arquivo de log (`errors.log`) via `logger.error()`.

---

### E5 — Turno já iniciado

**Condição:** duplo clique acidental no botão "Iniciar Expediente".

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Tela as TelaDeExpediente (PySide6)

    User->>Tela: Clique duplo em "INICIAR EXPEDIENTE"
    Tela->>Tela: Botão já desabilitado
    Tela-->>User: Clique ignorado (botão grayed out)
```

**Decisão:** a UI desabilita o botão na primeira chamada, antes mesmo de contactar o `GameManager`. Isso evita chamadas redundantes e dá feedback visual imediato ao usuário. A guarda no `GerenciadorDeTurno` é a proteção em nível de domínio caso a UI falhe.
