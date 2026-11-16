# Arquitetura Limpa: Inspetor IFF-BJI

## 1. Visão Geral

O projeto **Inspetor IFF-BJI** adota os princípios da **Arquitetura Limpa (Clean Architecture)** para garantir separação de responsabilidades, testabilidade e manutenibilidade do código. Este documento descreve a organização das camadas, suas responsabilidades e as regras de dependência entre elas, conforme implementadas no código-fonte.

---

## 2. Mapa de Camadas e Diretórios

| Camada | Diretório | Responsabilidade | Pode importar |
|--------|-----------|------------------|---------------|
| **Domain (Core)** | `core/model/`, `core/services/`, `core/dtos/`, `core/interfaces/` | Entidades, regras de negócio, cálculo de pontuação e portas do domínio | stdlib e a si mesma |
| **Infrastructure** | `infrastructure/` | Leitura de arquivos JSON, DTOs de transporte, fábrica de entidades | `core/`, stdlib, bibliotecas externas |
| **Application** | `application/controllers/`, `application/interfaces/` | Orquestração dos casos de uso e contrato da interface (`IGameView`) | `core/`, `infrastructure/`, `config/` |
| **View** | `view/` | Interface com o usuário (PySide6) | `application/interfaces/`, DTOs e portas de `core/` |
| **Config** | `config/` | Constantes e configuração de logging | stdlib |
| **Composição** | `main.py` | Cria a view e o `GameManager`, conecta os sinais e inicia o Qt | Todas |

### Regra de Dependência (Direção Única)

As dependências apontam **sempre para dentro**:

```
view/  ──>  application/  ──>  core/  <──  infrastructure/
                │                              ▲
                └──────────────────────────────┘
        config/ é consumida por application/ e por main.py
```

Nenhum módulo de `core/` importa `infrastructure/`, `application/` ou `view/`. Os pontos em que o código se afasta desta regra estão registrados na [seção 10](#10-desvios-conhecidos).

---

## 3. Camada de Domínio (`core/`)

### 3.1. Entidades (`core/model/`)

Classes que representam os conceitos centrais do jogo.

| Arquivo | Classe | Tipo |
|---------|--------|------|
| `core/model/anexo.py` | `Anexo` | Abstrata |
| `core/model/anexo.py` | `AnexoImagem`, `AnexoVideo`, `AnexoAudio` | Concretas |
| `core/model/folha_de_inspecao.py` | `FolhaDeInspecao` | Abstrata |
| `core/model/folha_de_gabarito.py` | `FolhaDeGabarito` | Concreta (herda `FolhaDeInspecao`) |
| `core/model/folha_de_resposta.py` | `FolhaDeResposta` | Concreta (herda `FolhaDeInspecao`) |
| `core/model/relatorio.py` | `Relatorio` | Concreta |

**Árvore de herança:**

```
Anexo (ABC)
 ├── AnexoImagem
 ├── AnexoVideo
 └── AnexoAudio

FolhaDeInspecao (ABC)
 ├── FolhaDeGabarito
 └── FolhaDeResposta
```

**Invariantes validadas nos construtores:**

| Entidade | Regras |
|----------|--------|
| `Anexo` | `id_anexo` não negativo; `caminho_arquivo` não vazio |
| `FolhaDeInspecao` | Normaliza riscos e fatores (sem acentos, maiúsculas) e rejeita valores fora de `LISTA_RISCOS_VALIDOS` e `FATORES_INSEGURANCA_VALIDOS` |
| `FolhaDeGabarito` | Decisões dentro de `INTERDITAR`, `ADVERTIR`, `IGNORAR`; `decisao_otima` diferente de `decisao_boa` |
| `FolhaDeResposta` | Decisão válida; `tempo_gasto_segundos` não negativo |
| `Relatorio` | `id_cenario` ≥ 1; `titulo`, `envolvidos` e `cursos` não vazios; `dificuldade` entre 1 e 5 |

### 3.1.1. Tratamento de Exceções nas Entidades

As entidades de domínio são agnósticas: não sabem se o dado veio de um clique na interface ou de um arquivo no disco. O papel delas **não é** tratar erros de sistema (arquivo não encontrado, JSON inválido), mas **garantir invariantes de negócio**. Quatro princípios orientam esse tratamento.

#### Princípio 1: Estado Sempre Válido (Fail Fast)

Uma entidade nunca existe em estado inválido na memória. O construtor (`__init__`) é o guardião: instanciar um `Relatorio` com `dificuldade = 6` levanta erro imediatamente.

#### Princípio 2: Validação de Regra de Negócio vs. Validação de Formato

A entidade valida **semântica (negócio)**, não **sintaxe (formato)**.

**O que a entidade valida:**
- "A dificuldade deve ser entre 1 e 5".
- "A decisão deve ser `INTERDITAR`, `ADVERTIR` ou `IGNORAR`".
- "Riscos fora da lista válida não podem ser registrados".

**O que a entidade não valida:**
- Conversão de tipos (`int(dificuldade)`): o dado já chega no tipo correto.
- Formato de data, expressões regulares ou parsing de strings.

#### Princípio 3: Exceções Agnósticas e Puras

Uma entidade nunca lança `JSONDecodeError`, `FileNotFoundError` ou qualquer exceção específica de infraestrutura ou interface. Usa-se `ValueError` para valores de negócio inválidos.

**Padrão do projeto (tags):** toda mensagem de erro começa com uma tag entre colchetes. As entidades usam a tag simples `[Erro]`; serviços, controladores e repositórios acrescentam o contexto (`[Erro - Turno]`, `[Erro - GameManager]`, `[Erro - Json]`, `[Erro - ParecerCIPA]`).

```python
raise ValueError("[Erro] envolvidos não pode ser vazio")                       # core/model/relatorio.py
raise ValueError(f"[Erro] id_anexo não pode ser negativo: {id_anexo}")         # core/model/anexo.py
raise RuntimeError("[Erro - Turno] Relatório anterior ainda não foi avaliado")  # application/
```

#### Princípio 4: Proteção contra Mutabilidade

Os atributos das entidades são privados (`__atributo`) e expostos apenas por `@property` de leitura. As únicas mutações permitidas passam por métodos explícitos: `Relatorio.adicionar_anexo()` e `Relatorio.anexar_resposta_jogador()`.

### 3.2. Serviços de Domínio (`core/services/`)

| Arquivo | Classe | Função |
|---------|--------|--------|
| `core/services/motor_de_pontuacao.py` | `MotorDePontuacao` | Motor matemático: Vmax, notas de riscos, fatores e decisão, fator tempo, scores por item e condição de vitória |
| `core/services/diagnostico_de_resposta.py` | `DiagnosticoDeResposta` | Confronta gabarito × resposta do jogador e produz os DTOs de pontuação e de feedback |

As fórmulas implementadas estão em [Modelagem matemática](../game-design/modelagem-matematica.md).

### 3.2.1. Filosofia dos Serviços de Domínio

Os serviços de domínio são **cálculo puro, sem estado e determinístico**. Implementam a lógica que não pertence a nenhuma entidade isoladamente.

#### Princípio 1: Cálculo sem Estado (Stateless)

Um serviço de domínio não guarda estado entre chamadas. `MotorDePontuacao.calcular_pontuacao_relatorio(v_max, dados_pontuacao)` recebe os operandos e retorna `float`. Quem acumula a pontuação do turno é o `GerenciadorDeTurno` (camada de aplicação), não o motor.

#### Princípio 2: Determinismo

Dado o mesmo input, o serviço **sempre** devolve o mesmo output.

- `random` não é usado em `core/services/`.
- Leitura de relógio (`datetime.now()`) não é usada: o tempo gasto pelo jogador chega como argumento (`tempo_resposta_segundos`).
- Componentes não determinísticos (sorteio de cenários, sorteio de pareceres) vivem na camada de infraestrutura.

#### Princípio 3: Orquestração entre Entidades

O serviço é o local das lógicas que fariam uma entidade violar a responsabilidade única. `FolhaDeGabarito` sabe as respostas certas; `FolhaDeResposta` sabe o que o jogador marcou; nenhuma tem um método `comparar_com()`. O `DiagnosticoDeResposta` recebe ambas e produz o diagnóstico.

#### Princípio 4: Cegueira de Infraestrutura

Os serviços em `core/services/` não leem nem escrevem arquivos, não fazem requisições, não usam `print()` (o `logging` é a única ponte permitida) e não importam nada de `infrastructure/` ou `view/`.

#### Princípio 5: Comunicação via DTOs Congelados

Em vez de dicionários soltos, os serviços retornam DTOs congelados:

- `DiagnosticoDeResposta.gerar_diagnostico_pontuacao()` → `DiagnosticoPontuacaoDTO` (operandos).
- `DiagnosticoDeResposta.gerar_feedback()` → `DiagnosticoFeedbackDTO` (itens acertados, esquecidos e inventados).
- `MotorDePontuacao.calcular_pontuacao_detalhada()` → `DiagnosticoPontuacaoDTO` completo, com subtotais e nota final.

### 3.3. DTOs de Domínio (`core/dtos/`)

Dataclasses congeladas (`frozen=True`).

| Arquivo | DTO | Conteúdo |
|---------|-----|----------|
| `core/dtos/diagnostico_pontuacao.py` | `DiagnosticoPontuacaoDTO` | Operandos: `qnt_riscos_marcados`, `qnt_riscos_gabarito`, `qnt_riscos_corretos_marcados`, `estado_ato`, `estado_condicao`, `status_decisao_jogador`, `tempo_resposta_segundos`, `qnt_fatores_gabarito`, `qnt_fatores_marcados`. Resultados: `pontuacao_final`, `nota_riscos`, `nota_fatores`, `nota_decisao`, `pontos_bonus_tempo`, `decisao_anulada` |
| `core/dtos/diagnostico_feedback.py` | `DiagnosticoFeedbackDTO` | `riscos_acertados`, `riscos_esquecidos`, `riscos_inventados`, `fatores_acertados`, `fatores_esquecidos`, `fatores_inventados`, `decisao_tomada`, `decisao_esperada`, `score_por_risco`, `score_por_fator` |
| `core/dtos/resultado_diagnostico.py` | `ResultadoDiagnosticoDTO` | Agrupa `pontuacao` (`DiagnosticoPontuacaoDTO`) e `feedback` (`DiagnosticoFeedbackDTO`); é o objeto entregue à view |
| `core/dtos/parecer_cipa.py` | `ParecerCIPA` | `numero` (formato `NNN/AAAA`), `referencia`, `texto` |

### 3.3.1. Filosofia dos DTOs de Domínio

#### Princípio 1: Imutabilidade

Um DTO de domínio não é alterado depois de criado (`@dataclass(frozen=True)`). Tentar `dto.qnt_riscos_marcados = 0` levanta `FrozenInstanceError`. Quando um DTO precisa ser enriquecido, cria-se uma nova instância: é o que o `GerenciadorDeTurno` faz ao preencher `score_por_risco` e `score_por_fator` no feedback.

#### Princípio 2: Sem Lógica de Negócio

Um DTO contém apenas atributos. A exceção é o `ParecerCIPA`, um *value object* que valida o próprio formato em `__post_init__` (texto e referência não vazios, número no padrão `NNN/AAAA`).

#### Princípio 3: Contrato entre Serviços

DTOs evitam métodos com muitos parâmetros avulsos ou dependentes de `dict` genéricos. Sempre que um serviço passa dados complexos a outro ou devolve resultados ao controlador, usa-se um DTO.

#### Princípio 4: Cegueira do Mundo Externo

DTOs de domínio são Python puro: sem anotações de serialização nem mapeamento de banco de dados. Dados brutos de arquivo trafegam em `infrastructure/dtos/`.

### 3.4. Portas do Domínio (`core/interfaces/`)

| Arquivo | Interface | Função |
|---------|-----------|--------|
| `core/interfaces/i_pareceres_cipa.py` | `IPareceresCIPA` | Contrato `obter_parecer_para_curso(curso) -> ParecerCIPA`, implementado na infraestrutura e consumido pelas telas de fim de jogo |

A porta aplica a Inversão de Dependência: o domínio define o contrato e a infraestrutura fornece a implementação.

---

## 4. Camada de Infraestrutura (`infrastructure/`)

Lida com o mundo externo: sistema de arquivos, serialização JSON e construção de objetos de domínio a partir de dados persistidos.

### 4.1. DTOs de Infraestrutura (`infrastructure/dtos/`)

Dataclasses mutáveis que transportam os dados brutos do JSON até a fábrica.

| Arquivo | DTO | Campos |
|---------|-----|--------|
| `infrastructure/dtos/dados_cenario.py` | `DadosAnexoDTO` | `id_anexo`, `tipo`, `caminho_arquivo` |
| `infrastructure/dtos/dados_cenario.py` | `DadosCenarioDTO` | `id_cenario`, `titulo`, `dificuldade`, `atividade`, `local`, `texto_descricao`, `envolvidos`, `curso`, `riscos`, `fatores_inseguranca`, `decisao_otima`, `decisao_boa`, `anexos` |

### 4.2. Repositórios (`infrastructure/repository/`)

| Arquivo | Classe | Função |
|---------|--------|--------|
| `repositorio_json.py` | `RepositorioJSON` | Lê os arquivos `.json` de `resources/data/`, valida contra `JSON_SCHEMA`, filtra por curso, sorteia e devolve `DadosCenarioDTO` |
| `repositorio_pareceres_cipa.py` | `RepositorioDePareceresCIPA` | Implementa `IPareceresCIPA`: carrega `view/assets/textos/pareceres_gameover.json` e devolve um parecer aleatório por curso, com fallback para `DEFAULT` |
| `repositorio_pareceres_cipavitoria.py` | `RepositorioDePareceresCIPAVitoria` | Subclasse do anterior que carrega `pareceres_gamewin.json` |

Dependência externa: `jsonschema` (validação de schemas). O formato dos cenários está em [Estrutura JSON](../dados/estrutura-json.md).

### 4.2.1. Filosofia do Repositório

#### Princípio 1: Fronteira dos Dados Persistidos

O repositório não sabe que existe um jogador. Ele valida **a estrutura do arquivo externo** com `jsonschema`: se a chave `"titulo"` existe, se `"dificuldade"` é um inteiro entre 1 e 5, se os valores enumerados são válidos. A entidade barra regras de negócio; o repositório barra arquivos malformados.

#### Princípio 2: Tratamento de I/O

Erros físicos e de formato são tratados exclusivamente aqui, de duas formas:

- **`RepositorioJSON` falha rápido.** Diretório inexistente ou sem arquivos `.json` levanta `FileNotFoundError`/`NotADirectoryError` no construtor. Um arquivo com sintaxe inválida, vazio ou fora do schema interrompe `extrair_dados()` com `ValueError`, `KeyError` ou `TypeError`, conforme o tipo de violação. O `GameManager` captura a falha, exibe o erro e volta ao menu.
- **`RepositorioDePareceresCIPA` é tolerante.** Arquivo ausente ou inválido gera um aviso no log e um repositório vazio; a falta de parecer só aparece como `ParecerCIPAIndisponivelError` quando nem o curso nem o `DEFAULT` têm textos.

#### Princípio 3: Sem Regras de Negócio

O repositório sabe extrair a informação, mas não calcula notas nem avalia respostas. A lógica permitida é de consulta: filtrar cenários por curso, embaralhar a lista (`random.shuffle`) e limitar a quantidade a `QUANTIDADE_GERACAO`.

**Regra de filtro por curso:** um cenário é incluído quando o curso selecionado está na lista `curso` do cenário, ou quando o curso selecionado é `DEFAULT` (que recebe todos os cenários).

#### Princípio 4: Conversão para DTOs de Infraestrutura

O repositório não deixa vazar `dict` do `json.load` para o resto do sistema. Ele preenche `DadosCenarioDTO`, e a partir daí a fábrica trabalha com atributos tipados.

#### Princípio 5: Isolamento de Tecnologia

Para a camada de aplicação, o repositório é uma caixa-preta: o `GerenciadorDeTurno` chama `extrair_dados()` e recebe DTOs prontos. Trocar JSON por SQLite ou por uma API exigiria alterar apenas o repositório.

### 4.3. Fábrica (`infrastructure/factory/`)

| Arquivo | Classe | Função |
|---------|--------|--------|
| `infrastructure/factory/fabrica_de_relatorios.py` | `FabricaDeRelatorios` | Converte `DadosCenarioDTO` em entidades `Relatorio` (com `FolhaDeGabarito` e `Anexo`) |

### 4.3.1. Filosofia da Fábrica

A fábrica é a **camada anticorrupção**: o único lugar autorizado a conhecer ao mesmo tempo os DTOs de infraestrutura e as entidades de domínio.

#### Princípio 1: Ponte entre Dois Mundos

Recebe `DadosCenarioDTO` e devolve `Relatorio`. Isso impede que o `GerenciadorDeTurno` precise saber como desempacotar um DTO.

#### Princípio 2: Encapsulamento da Instanciação

Para criar um `Relatorio`, a fábrica instancia a `FolhaDeGabarito`, depois o `Relatorio`, depois cada anexo conforme o tipo (`AnexoImagem`, `AnexoVideo` ou `AnexoAudio`) e os adiciona ao relatório.

#### Princípio 3: Camada Anticorrupção

A fábrica não faz validação de negócio; apenas tenta construir as entidades. Se uma entidade rejeitar o dado com `ValueError`, a fábrica registra o erro no log e **descarta aquele cenário**, seguindo com os demais. Anexos de tipo desconhecido são ignorados com aviso.

#### Princípio 4: Sem Comportamento de Jogo

A fábrica não ordena relatórios, não embaralha a lista e não calcula `v_max`. Ela constrói as entidades e sai de cena.

---

## 5. Camada de Aplicação (`application/`)

Orquestra os casos de uso do jogo, conectando a infraestrutura ao domínio e comandando a view por meio de um contrato.

| Arquivo | Classe | Função |
|---------|--------|--------|
| `application/controllers/game_manager.py` | `GameManager` | Presenter do jogo: máquina de estados (menu, expediente, resultado), campanha, criação do `GerenciadorDeTurno` e ponte com a view |
| `application/controllers/gerenciador_de_turno.py` | `GerenciadorDeTurno` | Ciclo de vida de um turno (expediente): carregar relatórios, entregar um por vez, avaliar respostas, verificar vitória |
| `application/interfaces/i_game_view.py` | `IGameView`, `MotivoTutorial` | Contrato que a view implementa e enum do motivo de abertura do tutorial |

### 5.1. Fluxo do `GameManager`

Os sinais da view são conectados aos métodos do `GameManager` em `main.py`:

| Sinal da view | Método do `GameManager` | Efeito |
|---------------|-------------------------|--------|
| `iniciar_solicitado` | `on_iniciar_solicitado()` | Abre o tutorial (`MotivoTutorial.NOVO_JOGO`) |
| `tutorial_finalizado(motivo)` | `on_tutorial_finalizado()` | Em novo jogo, abre a seleção de perfil |
| `perfil_confirmado(str)` | `iniciar_expediente()` | Inicia a campanha e o primeiro dia |
| `submeter_respostas(dict)` | `processar_submissao()` | Avalia o relatório e exibe o diagnóstico |
| `continuar_solicitado` | `avancar_fila_ou_dia()` | Próximo relatório, próximo dia ou fim da campanha |
| `jogar_novamente_solicitado` | `reiniciar_expediente()` | Recomeça com o mesmo perfil |
| `voltar_menu_solicitado` | `carregar_menu_principal()` | Descarta o turno e volta ao menu |
| `help_solicitado` | `on_help_solicitado()` | Abre o tutorial em modo consulta |
| `sair_solicitado` | `encerrar_aplicacao()` | Fecha a janela (idempotente) |

A campanha dura `CAMPANHA_DURACAO_DIAS` dias (atualmente 1). Ao fim do último dia, `GameManager` consulta `verificar_vitoria_do_turno()` e chama `view.exibir_resultado(...)`.

### 5.2. Fluxo do `GerenciadorDeTurno`

```
iniciar_turno()
  ├── RepositorioJSON.extrair_dados()        → List[DadosCenarioDTO]
  ├── FabricaDeRelatorios.construir_pilha()  → List[Relatorio]
  └── MotorDePontuacao.calcular_meta_turno() → float (Vmax do turno)

obter_relatorio_da_pilha()
  └── pop() da pilha interna (LIFO)

avaliar_respostas_jogador(riscos, fatores, decisao, tempo) → ResultadoDiagnosticoDTO
  ├── cria a FolhaDeResposta e anexa ao Relatorio
  ├── DiagnosticoDeResposta.gerar_diagnostico_pontuacao() → DiagnosticoPontuacaoDTO (operandos)
  ├── DiagnosticoDeResposta.gerar_feedback()              → DiagnosticoFeedbackDTO
  ├── MotorDePontuacao.calcular_vmax_relatorio()          → float
  ├── MotorDePontuacao.calcular_scores_por_item()         → scores por risco e por fator
  ├── MotorDePontuacao.calcular_pontuacao_detalhada()     → DiagnosticoPontuacaoDTO completo
  └── acumula pontuacao_final no turno

verificar_vitoria_do_turno()
  └── MotorDePontuacao.conferir_condicao_vitoria() → bool (≥ 60% do Vmax do turno)
```

### 5.3. Filosofia dos Controladores

#### Princípio 1: Delegação

O controlador não executa regra de negócio nem cálculo. O `GerenciadorDeTurno` pede à fábrica que construa relatórios, ao `DiagnosticoDeResposta` que avalie acertos e ao `MotorDePontuacao` que calcule a nota.

#### Princípio 2: Guardião do Estado

Ao contrário dos serviços de domínio, a camada de aplicação mantém estado: `__turno_iniciado`, `__pontuacao_acumulada_turno`, `__pilha_relatorios` e `__relatorio_atual` no turno; `__estado_atual`, `__dias_concluidos` e `__pontuacao_global` no `GameManager`. **Guardas** impedem a execução fora de ordem (iniciar o turno duas vezes, pedir um relatório com outro pendente, verificar vitória com relatórios na pilha).

#### Princípio 3: Fronteira com a Interface

A interface entrega apenas dados primitivos (`dict` com listas de strings, decisão e tempo). O controlador traduz para entidades, invoca os serviços e devolve o resultado. Os controladores **não importam PySide6**: o `GameManager` conhece apenas o contrato `IGameView`.

#### Princípio 4: Tratamento de Erros

`GameManager.processar_submissao()` captura `ValueError` (erro de negócio) e repassa a mensagem com `view.exibir_popup_erro()`; qualquer outra exceção é registrada no log e exibida como erro interno genérico. Falhas ao carregar o dia devolvem o jogador ao menu.

#### Princípio 5: Injeção de Dependências

O `GameManager` recebe a view por injeção no construtor (`GameManager(view: IGameView)`), o que permite testá-lo com um mock. O `GerenciadorDeTurno` instancia `MotorDePontuacao`, `DiagnosticoDeResposta` e `RepositorioJSON` internamente; nos testes, usa-se `unittest.mock.patch`.

---

## 6. Camada de Configuração (`config/`)

| Arquivo | Conteúdo |
|---------|----------|
| `config/constants.py` | `DIRETORIO_BASE` (`resources/data`), `QUANTIDADE_GERACAO` (relatórios por turno, atualmente 1), `CURSOS`, `TEMA_PADRAO` (`"dark"` ou `"light"`) |
| `config/logging_config.py` | `setup_logging()`: nível e destinos de log conforme `APP_ENV` (`development`, `staging`, `production`) ou `LOG_LEVEL` |

---

## 7. Camada de Visualização (`view/`)

A interface é implementada em PySide6 e segue o padrão **Passive View** do MVP: `JanelaPrincipal` implementa `IGameView`, o `GameManager` atua como presenter. A estrutura de pastas, a hierarquia de widgets e os padrões de sinais e estilos estão detalhados em [Arquitetura da View](view.md).

### 7.1. Filosofia da View

#### Princípio 1: View Passiva

A interface não toma decisões de negócio. Quando o jogador submete uma inspeção, a `PaginaInspecao` coleta as marcações e emite `submeter_respostas(dict)`; a pontuação é calculada no domínio e volta pronta em um `ResultadoDiagnosticoDTO`.

#### Princípio 2: Quarentena Tecnológica

`view/` e `main.py` são os únicos locais que importam PySide6. Widgets, sinais, QSS e reprodução de mídia vivem dentro de `view/`.

#### Princípio 3: Dados Somente Leitura

A view não recebe entidades. O relatório chega como `dict` gerado por `Relatorio.extrair_apresentacao_relatorio()` (sem o gabarito), e o diagnóstico chega como DTO congelado.

#### Princípio 4: Erros Exibidos, não Decididos

A view não valida regras: ela exibe o que o presenter manda. `JanelaPrincipal.exibir_popup_erro()` mostra a mensagem em um `QMessageBox`.

---

## 8. Convenções de Importação

- **Dentro do mesmo pacote de camada**, usam-se imports relativos em `core/model/` e `infrastructure/repository/`:
  ```python
  from .folha_de_inspecao import FolhaDeInspecao         # core/model/
  from ..dtos.dados_cenario import DadosCenarioDTO        # infrastructure/repository/
  ```
- **Entre pacotes**, imports absolutos:
  ```python
  from core.model.relatorio import Relatorio
  from infrastructure.factory.fabrica_de_relatorios import FabricaDeRelatorios
  ```
- **Não há arquivos `__init__.py`**: todos os pacotes são *namespace packages* (PEP 420).

---

## 9. Fluxo de Dados Completo

```
[resources/data/*.json]
       │
       ▼
RepositorioJSON (infrastructure/repository/)
  ├── Lê e valida contra JSON_SCHEMA
  ├── Filtra por curso, embaralha e limita a QUANTIDADE_GERACAO
  └── Retorna List[DadosCenarioDTO]
       │
       ▼
FabricaDeRelatorios (infrastructure/factory/)
  ├── Cria FolhaDeGabarito, Relatorio e Anexos (core/model/)
  └── Retorna List[Relatorio]
       │
       ▼
GerenciadorDeTurno (application/controllers/)
  ├── Guarda a pilha e entrega um relatório por vez
  │       │
  │       ▼  GameManager → view.renderizar_relatorio(dict)
  │   [Jogador preenche a inspeção]
  │       │
  │       ▼  view.submeter_respostas(dict) → GameManager.processar_submissao()
  ├── FolhaDeResposta (core/model/)
  ├── DiagnosticoDeResposta → DiagnosticoPontuacaoDTO + DiagnosticoFeedbackDTO
  ├── MotorDePontuacao → Vmax, scores por item, pontuação detalhada
  └── Retorna ResultadoDiagnosticoDTO e acumula a nota do turno
       │
       ▼
GameManager → view.exibir_tela_diagnostico(resultado)
       │
       ▼  (pilha vazia, último dia)
GerenciadorDeTurno.verificar_vitoria_do_turno() → bool
       │
       ▼
GameManager → view.exibir_resultado(pontuacao_global, dias_concluidos, venceu)
  └── A tela de fim de jogo pede um ParecerCIPA ao repositório de pareceres
```

---

## 10. Desvios Conhecidos

Pontos em que o código atual se afasta da regra de dependência ou dos princípios acima. São tolerados, mas não devem ser replicados.

| Onde | Desvio | Caminho de correção |
|------|--------|---------------------|
| `core/model/folha_de_inspecao.py` | Importa a biblioteca externa `unidecode` para remover acentos | Normalizar com stdlib (`unicodedata`) ou mover a normalização para a infraestrutura |
| `view/expediente/tela.py`, `paginas/game_over.py`, `paginas/game_win.py` | Importam as classes concretas de `infrastructure/repository/` para os pareceres da CIPA | Injetar um `IPareceresCIPA` a partir de `main.py` |
| `application/controllers/game_manager.py` | `__mascarar_perfil()` redireciona todo curso válido para `DEFAULT`, porque só há cenários marcados como `DEFAULT`; para isso importa `RepositorioJSON` dentro do método | Remover a máscara quando houver cenários por curso |
| `config/constants.py` e `RepositorioJSON.CURSOS_VALIDOS` | A lista de cursos está duplicada (e repetida no `JSON_SCHEMA`) | Usar `config.constants.CURSOS` como fonte única |

---

## 11. Diagrama de Dependências (Arquivo por Arquivo)

```
main.py
  ├── application.controllers.game_manager
  ├── config.constants
  ├── config.logging_config
  └── view.main_window

application/controllers/game_manager.py
  ├── application.controllers.gerenciador_de_turno
  ├── application.interfaces.i_game_view
  ├── core.dtos.resultado_diagnostico
  └── infrastructure.repository.repositorio_json (import local, ver seção 10)

application/controllers/gerenciador_de_turno.py
  ├── config.constants
  ├── core.dtos.diagnostico_pontuacao
  ├── core.dtos.diagnostico_feedback
  ├── core.dtos.resultado_diagnostico
  ├── core.model.relatorio
  ├── core.model.folha_de_resposta
  ├── core.services.motor_de_pontuacao
  ├── core.services.diagnostico_de_resposta
  ├── infrastructure.factory.fabrica_de_relatorios
  └── infrastructure.repository.repositorio_json

application/interfaces/i_game_view.py
  └── core.dtos.resultado_diagnostico

infrastructure/factory/fabrica_de_relatorios.py
  ├── core.model.relatorio
  ├── core.model.folha_de_gabarito
  ├── core.model.anexo
  └── infrastructure.dtos.dados_cenario

infrastructure/repository/repositorio_json.py
  ├── infrastructure.dtos.dados_cenario
  └── jsonschema (externa)

infrastructure/repository/repositorio_pareceres_cipa.py
  ├── core.dtos.parecer_cipa
  └── core.interfaces.i_pareceres_cipa

infrastructure/repository/repositorio_pareceres_cipavitoria.py
  └── infrastructure.repository.repositorio_pareceres_cipa

core/services/motor_de_pontuacao.py
  ├── core.dtos.diagnostico_pontuacao
  ├── core.dtos.diagnostico_feedback
  └── core.model.relatorio

core/services/diagnostico_de_resposta.py
  ├── core.model.folha_de_gabarito
  ├── core.model.folha_de_resposta
  ├── core.dtos.diagnostico_pontuacao
  └── core.dtos.diagnostico_feedback

core/interfaces/i_pareceres_cipa.py
  └── core.dtos.parecer_cipa

core/dtos/resultado_diagnostico.py
  ├── core.dtos.diagnostico_pontuacao
  └── core.dtos.diagnostico_feedback

core/model/relatorio.py
  ├── core.model.anexo
  ├── core.model.folha_de_gabarito
  └── core.model.folha_de_resposta

core/model/folha_de_gabarito.py, core/model/folha_de_resposta.py
  └── core.model.folha_de_inspecao

core/model/folha_de_inspecao.py
  └── unidecode (externa, ver seção 10)

core/model/anexo.py
  └── (stdlib apenas)
```

---

## 12. Boas Práticas e Restrições

- **Não importar bibliotecas externas em `core/`.**
- **Não importar `infrastructure/`, `application/` ou `view/` dentro de `core/`**: a seta de dependência aponta sempre para dentro.
- **Não importar PySide6 fora de `view/` e `main.py`.**
- **DTOs de fronteira:** `infrastructure/dtos/` para dados brutos (mutáveis) e `core/dtos/` para dados de negócio (congelados).
- **Novas ações da interface:** declarar o método em `IGameView` antes de implementá-lo em `JanelaPrincipal`.
- **Namespace packages:** não criar arquivos `__init__.py`.
