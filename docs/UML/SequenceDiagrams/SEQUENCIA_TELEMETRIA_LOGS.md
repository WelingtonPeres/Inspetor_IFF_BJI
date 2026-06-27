# Telemetria / Logs — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] `setup_logging()` chamado uma vez no entry-point (`main.py`)
- [ ] Diretório `logs/` criado automaticamente com permissão de escrita
- [ ] Variável de ambiente `APP_ENV` definida (`development`, `staging` ou `production`)
- [ ] Módulos importam `logging` e criam `logger = logging.getLogger(__name__)`

### Pós-condições

- [ ] Mensagens de DEBUG/INFO gravadas em `logs/app.log` (com rotação de 10 MB)
- [ ] Mensagens de ERROR/CRITICAL gravadas em `logs/errors.log`
- [ ] Console colorido exibindo logs em tempo real (apenas em development/staging)
- [ ] Nenhuma exceção não tratada escapa sem registro

---

## 2. Diagrama de sequência

### Fluxo principal — Inicialização do logging

```mermaid
sequenceDiagram
    participant Main as main.py
    participant LogConfig as logging_config.py
    participant Logging as logging (stdlib)
    participant FileApp as app.log (RotatingFileHandler)
    participant FileErr as errors.log (RotatingFileHandler)
    participant Console as stdout (StreamHandler)

    Main->>LogConfig: setup_logging()
    activate LogConfig

    LogConfig->>LogConfig: Lê APP_ENV e LOG_LEVEL
    LogConfig->>LogConfig: Cria diretório logs/
    LogConfig->>Logging: dictConfig(LOGGING_CONFIG)

    Logging->>Console: Handler ativado (nível DEBUG)
    Logging->>FileApp: Handler ativado (nível INFO, 10MB rotation)
    Logging->>FileErr: Handler ativado (nível ERROR, 10MB rotation)

    LogConfig->>Logging: logger.info("Logging inicializado")
    Logging->>Console: "[INFO] logging_config.setup_logging():XX | Logging inicializado"
    Logging->>FileApp: "[INFO] logging_config.setup_logging():XX | Logging inicializado"

    LogConfig-->>Main: void
    deactivate LogConfig
```

### Fluxo principal — Log durante o Game Loop

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant DIAG as DiagnosticoDeResposta
    participant MOTOR as MotorDePontuacao
    participant REPO as RepositorioJSON
    participant FAB as FabricaDeRelatorios
    participant Logger as logging (stdlib)
    participant FileApp as app.log
    participant FileErr as errors.log

    Note over REPO: Durante extrair_dados()
    REPO->>Logger: logger.warning("Cenário com chave ausente...")
    Logger->>FileApp: [WARNING] repositorio_json.extrair_dados():XX | ...

    Note over MOTOR: Durante calcular_vmax_relatorio()
    MOTOR->>Logger: logger.warning("Relatório X sem gabarito. Vmax tratado como 0")
    Logger->>FileApp: [WARNING] motor_de_pontuacao.calcular_vmax_relatorio():XX | ...

    Note over FAB: Durante construção de relatórios
    FAB->>Logger: logger.error("Falha ao construir relatório...")
    Logger->>FileErr: [ERROR] fabrica_de_relatorios.__instanciar_relatorio_unico():XX | ...
    Logger->>FileApp: [ERROR] fabrica_de_relatorios.__instanciar_relatorio_unico():XX | ...

    FAB->>Logger: logger.warning("Tipo de anexo desconhecido...")
    Logger->>FileApp: [WARNING] fabrica_de_relatorios.__extrair_instanciar_anexos():XX | ...
```

### Fluxo de auditoria — Log de fim de expediente

```mermaid
sequenceDiagram
    participant GM as GameManager
    participant Logger as logging (stdlib)
    participant FileApp as app.log
    participant FileErr as errors.log

    GM->>Logger: logger.info("Turno finalizado | perfil=T_MEIO_AMBIENTE | nota=85.5/100.0 | status=APROVADO")
    Logger->>FileApp: [INFO] game_manager.~:XX | Turno finalizado | ...

    alt Nota abaixo do limiar
        GM->>Logger: logger.warning("Turno REPROVADO | perfil=T_QUIMICA | nota=42.0/100.0")
        Logger->>FileApp: [WARNING] game_manager.~:XX | Turno REPROVADO | ...
    end

    alt Erro crítico
        GM->>Logger: logger.error("Falha ao gerar certificado | erro=...")
        Logger->>FileErr: [ERROR] game_manager.~:XX | Falha ao gerar certificado
    end
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Comportamento |
|----|---------|---------------------|---------------|
| E1 | Handler de arquivo sem espaço | Disco cheio durante rotação | `RotatingFileHandler` falha silenciosamente; console ainda funciona |
| E2 | Ambiente sem `APP_ENV` | Variável não definida | Fallback para `development` (modo verboso seguro) |
| E3 | Log de exceção não capturada | Erro fora dos blocos try/except | `logging.exception()` registra stacktrace completo em `errors.log` |
| E4 | Nível inválido via `LOG_LEVEL` | Valor digitado incorretamente | Fallback para o nível do ambiente |

---

### E1 — Disco cheio

**Condição:** o diretório `logs/` está em um volume sem espaço.

```mermaid
sequenceDiagram
    participant Modulo as Qualquer módulo
    participant Logger as logging (stdlib)
    participant Handler as RotatingFileHandler

    Modulo->>Logger: logger.error("Falha crítica")
    Logger->>Handler: doRoll() / write()
    Handler->>Handler: IOError: [Errno 28] No space left on device
    Handler-->>Logger: Falha silenciosa (ano mínimo)
```

**Decisão:** o `RotatingFileHandler` da stdlib não propaga exceções de I/O para o chamador. O console continua operacional. Em produção, o handler `console` é o único ativo, evitando dependência de disco.

---

### E2 — Ambiente sem `APP_ENV`

**Condição:** variável `APP_ENV` não definida no sistema.

```mermaid
sequenceDiagram
    participant Main as main.py
    participant LogConfig as logging_config.py

    Main->>LogConfig: setup_logging()
    LogConfig->>LogConfig: os.getenv("APP_ENV", "development")
    LogConfig->>LogConfig: Fallback para "development"
    LogConfig->>LogConfig: LOG_LEVEL = "DEBUG"
    LogConfig->>Main: Logging verboso ativado
```

**Decisão:** `development` é o fallback seguro — logs detalhados em ambiente local nunca escondem informação. Em produção, o deploy define `APP_ENV=production` para reduzir ruído.

---

### E3 — Exceção não capturada

**Condição:** erro inesperado escapa sem try/except no código de aplicação.

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant Logger as logging (stdlib)
    participant FileErr as errors.log

    GDT->>GDT: Erro inesperado (ex: KeyError)
    GDT->>Logger: logger.exception("Erro não tratado em GerenciadorDeTurno")
    Logger->>FileErr: [ERROR] ... | Erro não tratado em GerenciadorDeTurno
    Note over FileErr: Stacktrace completo<br/>gravado automaticamente
```

**Decisão:** `logger.exception()` é usado em blocos `except` para registrar o stacktrace completo. O erro é então relançado ou convertido em mensagem amigável para a UI, garantindo rastreabilidade sem vazar detalhes internos.
