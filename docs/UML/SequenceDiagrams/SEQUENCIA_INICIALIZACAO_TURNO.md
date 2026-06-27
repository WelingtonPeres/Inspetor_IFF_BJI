# Inicialização do Expediente — Diagrama de sequência

---

## 1. Pré-condições e pós-condições

### Pré-condições

- [ ] `GerenciadorDeTurno` instanciado com um perfil de curso válido (ex: `"T_MEIO_AMBIENTE"`)
- [ ] Diretório base de cenários (`DIRETORIO_BASE`) existe e contém arquivos `*.json`
- [ ] `QUANTIDADE_GERADA` é um inteiro positivo

### Pós-condições

- [ ] Estado `__turno_iniciado = True`
- [ ] `__pilha_relatorios` populada com entidades `Relatorio` prontas para consumo
- [ ] `__v_max_turno` calculado (somatório do Vmax individual de cada relatório)
- [ ] `__pontuacao_acumulada_turno = 0.0` e `__relatorio_atual = None`

---

## 2. Diagrama de sequência

### Fluxo principal (caminho feliz)

```mermaid
sequenceDiagram
    participant UI as View (Interface)
    participant GDT as GerenciadorDeTurno
    participant REPO as RepositorioJSON
    participant FAB as FabricaDeRelatorios
    participant MOTOR as MotorDePontuacao
    participant DOMAIN as Entidades (Domínio)

    UI->>GDT: iniciar_turno("T_MEIO_AMBIENTE")
    activate GDT

    GDT->>REPO: __init__(diretorio_base, "T_MEIO_AMBIENTE", quantidade_gerada)
    activate REPO

    REPO->>REPO: __verificar_diretorio_existe()
    REPO->>REPO: __verificar_curso_valido()
    REPO->>REPO: __verificar_quantidade_gerada_valida()

    GDT->>REPO: extrair_dados()
    activate REPO

    loop Para cada arquivo *.json no diretório
        REPO->>REPO: __validar_esquema_basico(dados_brutos)
    end

    loop Para cada cenário válido
        REPO->>REPO: Filtra por curso selecionado
        REPO->>REPO: Instancia DadosAnexoDTO para cada anexo
        REPO->>REPO: Instancia DadosCenarioDTO
    end

    REPO->>REPO: Embaralha com random.shuffle
    REPO->>REPO: Limita à quantidade_gerada
    REPO-->>GDT: List[DadosCenarioDTO]
    deactivate REPO

    GDT->>FAB: construir_pilha(dados_dto)
    activate FAB

    loop Para cada DadosCenarioDTO
        FAB->>FAB: __instanciar_relatorio_unico(dto)
        activate FAB

        FAB->>DOMAIN: FolhaDeGabarito(riscos, fatores, decisao_otima, decisao_boa)
        FAB->>DOMAIN: Relatorio(id, titulo, atividade, local, ..., gabarito)

        alt Possui anexos
            FAB->>FAB: __extrair_instanciar_anexos(dto.anexos)
            loop Para cada DadosAnexoDTO
                alt tipo == "IMAGEM"
                    FAB->>DOMAIN: AnexoImagem(id, caminho)
                else tipo == "VIDEO"
                    FAB->>DOMAIN: AnexoVideo(id, caminho)
                else tipo == "AUDIO"
                    FAB->>DOMAIN: AnexoAudio(id, caminho)
                end
                DOMAIN-->>FAB: Anexo
                FAB->>DOMAIN: relatorio.adicionar_anexo(anexo)
            end
        end

        FAB-->>FAB: Relatorio instanciado
        deactivate FAB
    end

    FAB-->>GDT: List[Relatorio]
    deactivate FAB

    GDT->>MOTOR: calcular_meta_turno(lista_relatorios)
    activate MOTOR

    loop Para cada Relatorio
        MOTOR->>MOTOR: calcular_vmax_relatorio(relatorio)
    end

    MOTOR-->>GDT: v_max_total (float)
    deactivate MOTOR

    GDT-->>UI: True (sucesso)
    deactivate GDT
```

---

## 3. Fluxos de erro

### Tabela de referência rápida

| ID | Cenário | Condição de disparo | Resposta ao usuário |
|----|---------|---------------------|---------------------|
| E1 | Turno já iniciado | `iniciar_turno()` chamado duas vezes | `Exception("[Erro - Turno] Turno não pode ser iniciado mais de uma vez")` |
| E2 | Diretório não encontrado | `DIRETORIO_BASE` não existe ou não é diretório | `FileNotFoundError / NotADirectoryError` |
| E3 | Curso inválido | Perfil não pertence a `CURSOS_VALIDOS` | `ValueError("[Erro - Curso] ... não é válido")` |
| E4 | JSON mal formatado | Arquivo `.json` corrompido | `ValueError("[Erro - Json] ... está corrompido")` |
| E5 | Schema inválido | Estrutura do JSON fora do esquema | `KeyError / TypeError / ValueError` (conforme `__traduzir_erro_validacao`) |
| E6 | Nenhum cenário compatível | Nenhum cenário para o curso selecionado | `ValueError("[Aviso] Nenhum cenário encontrado")` |
| E7 | Nenhum relatório construído | Todos os DTOs falharam ao instanciar | `RuntimeError("[Erro - Turno] Nenhum relatório foi construído")` |

---

### E1 — Turno já iniciado

**Condição:** `iniciar_turno()` é invocado quando `__turno_iniciado` já é `True`.

```mermaid
sequenceDiagram
    participant UI as View
    participant GDT as GerenciadorDeTurno

    UI->>GDT: iniciar_turno("T_MEIO_AMBIENTE")
    activate GDT
    GDT->>GDT: Verifica __turno_iniciado
    alt Já iniciado
        GDT-->>UI: Exception("[Erro - Turno] Turno não pode ser iniciado mais de uma vez")
    end
    deactivate GDT
```

**Decisão:** turno é singleton por sessão — reiniciar exigiria um novo objeto `GerenciadorDeTurno`.

---

### E2 — Diretório não encontrado

**Condição:** o caminho `DIRETORIO_BASE` não existe ou não contém arquivos `.json`.

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant REPO as RepositorioJSON

    GDT->>REPO: __init__(diretorio_base, curso, quantidade)
    activate REPO
    REPO->>REPO: __verificar_diretorio_existe()
    alt Diretório não existe
        REPO-->>GDT: FileNotFoundError
    else Não é diretório
        REPO-->>GDT: NotADirectoryError
    else Nenhum arquivo .json
        REPO-->>GDT: FileNotFoundError
    end
    deactivate REPO
```

**Decisão:** validações defensivas falham rápido na construção do repositório, antes de qualquer I/O.

---

### E4 — JSON mal formatado

**Condição:** um arquivo `.json` do diretório contém sintaxe inválida (`json.JSONDecodeError`).

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant REPO as RepositorioJSON

    GDT->>REPO: extrair_dados()
    activate REPO
    REPO->>REPO: json.load(arquivo)
    alt JSONDecodeError
        REPO-->>GDT: ValueError("[Erro - Json] ... está corrompido")
    end
    deactivate REPO
```

**Decisão:** o erro é convertido para `ValueError` para manter a camada de aplicação independente de detalhes de parsing.

---

### E7 — Nenhum relatório construído

**Condição:** a fábrica retornou uma lista vazia (todos os DTOs falharam na instanciação).

```mermaid
sequenceDiagram
    participant GDT as GerenciadorDeTurno
    participant FAB as FabricaDeRelatorios

    GDT->>FAB: construir_pilha(dados_dto)
    activate FAB
    FAB-->>GDT: [] (lista vazia)
    deactivate FAB

    GDT->>GDT: Verifica se pilha está vazia
    alt Vazia
        GDT-->>UI: RuntimeError("[Erro - Turno] Nenhum relatório foi construído")
    end
```

**Decisão:** a guarda evita que o turno inicie sem conteúdo jogável, forçando o operador a corrigir os dados de entrada.
