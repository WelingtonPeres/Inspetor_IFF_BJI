# Arquitetura Limpa: Inspetor IFF-BJI

## 1. Visão Geral

O projeto **Inspetor IFF-BJI: Análise de Risco** adota os princípios da **Arquitetura Limpa (Clean Architecture)** para garantir separação rigorosa de responsabilidades, testabilidade e manutenibilidade do código. Este documento descreve a organização real das camadas, suas responsabilidades e as regras de dependência entre elas, conforme implementadas no código-fonte.

---

## 2. Mapa de Camadas e Diretórios

| Camada | Diretório | Responsabilidade | Pode importar |
|--------|-----------|------------------|---------------|
| **Domain (Core)** | `core/model/`, `core/services/`, `core/dtos/` | Regras de negócio e entidades | Apenas stdlib e a si mesma |
| **Infrastructure** | `infrastructure/` | Persistência, leitura de arquivos, DTOs de transporte | `core/`, stdlib, bibliotecas externas |
| **Application** | `application/controllers/` | Orquestração dos casos de uso | `core/`, `infrastructure/`, `config/` |
| **Config** | `config/` | Configuração centralizada | Apenas stdlib |
| **View** | `view/` | Interface com o usuário (PySide6, planejada) | `application/` |

### Regra de Dependência (Direção Única)

As dependências apontam **sempre para dentro**:

```
view/  ──>  application/  ──>  core/  <──  infrastructure/
                │                              │
                └───────── config/ ────────────┘
```

Nenhuma camada interna (`core/`) pode conhecer ou importar uma camada externa (`infrastructure/`, `application/`, `view/`).

---

## 3. Camada de Domínio (`core/`)

### 3.1. Entidades (`core/model/`)

Contém as classes que representam os conceitos centrais do negócio, sem qualquer dependência externa ou de infraestrutura.

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

### 3.1.1. Tratamento de Exceções nas Entidades

As entidades de domínio são agnósticas não sabem se o dado veio de um clique do mouse na UI ou de um arquivo no disco. O papel delas **não é** tratar erros de sistema (arquivo não encontrado, conexão perdida), mas sim **garantir Invariantes de Negócio**. O tratamento de exceções nas entidades segue quatro princípios fundamentais:

#### Princípio 1: Estado Sempre Válido (Fail Fast)

Uma entidade nunca deve existir em um estado inválido na memória. O construtor (`__init__`) atua como o guardião implacável, se tentarem instanciar um `Relatorio` com `dificuldade = 6`, a classe deve levantar um erro **instantaneamente** no construtor.



#### Princípio 2: Validação de Regra de Negócio vs. Validação de Formato

A entidade valida **Semântica (Negócio)**, não **Sintaxe (Formato)**.

**O que a entidade DEVE validar:**
- "A dificuldade deve ser entre 1 e 5": regra do jogo.
- "A decisão tomada deve ser `INTERDITAR`, `ADVERTIR` ou `IGNORAR`": regra do jogo.
- "Riscos inválidos não podem ser registrados": regra do jogo.

**O que a entidade NÃO deve validar:**
- Não deve fazer *cast* de tipos (`int(dificuldade)`). tipo correto.
- Não deve verificar formato de data, expressões regulares ou parsing de strings. 



#### Princípio 3: Exceções Agnósticas e Puras

Uma entidade jamais deve lançar `JsonDecodeError`, `FileNotFoundError`, `Http404NotFound` ou qualquer exceção específica de infraestrutura ou interface.

**Use exceções nativas do Python puras:**
- `ValueError`: para valores de negócio inválidos (a escolha primária do projeto).
- `TypeError`: para tipos inaceitáveis (raro, já que Type Hints previnem a maioria).

**Padrão do projeto (Tags):** Como estabelecido nas convenções do projeto, use **tags** nas mensagens para rastreamento:

```python
raise ValueError("[Erro - Relatorio] A lista de envolvidos não pode estar vazia.")
raise ValueError("[Erro - Anexo] id_anexo não pode ser negativo: -3")
```

A tag `[Erro - NomeDaClasse]` permite identificar rapidamente em qual entidade o erro ocorreu, sem precisar de exceções personalizadas ou hierarquias complexas.

#### Princípio 4: Proteção contra Mutabilidade (Setters Fechados)

Se o construtor blindou a criação, você não pode deixar que as propriedades sejam alteradas depois de forma descontrolada.

### 3.2. Serviços de Domínio (`core/services/`)

Serviços stateless que operam sobre as entidades de domínio.

| Arquivo | Classe | Função |
|---------|--------|--------|
| `core/services/motor_de_pontuacao.py` | `MotorDePontuacao` | Motor matemático de pontuação (Vmax, riscos, fatores, decisão, tempo) |
| `core/services/diagnostico_de_resposta.py` | `DiagnosticoDeResposta` | Confronta gabarito × resposta do jogador |
| `core/services/diagnostico_feedback.py` | `DiagnosticoFeedback` | *Stub*, feedback textual futuro (código comentado) |

### 3.2.1. Serviços de Domínio

Os serviços de domínio são o **cálculo puro, apátrida e determinístico**. Eles implementam a lógica que não pertence a nenhuma entidade isoladamente. 

#### Princípio 1: Cálculo Apátrida (Stateless)

Um serviço de domínio **não guarda estado** entre chamadas. Métodos recebem dados, processam e devolvem um resultado, sem efeitos colaterais nem atributos mutáveis.

**Referência:** `MotorDePontuacao.calcular_pontuacao_relatorio(v_max, dados_pontuacao)` recebe os operandos e retorna `float`. Quem persiste a pontuação acumulada é o `GerenciadorDeTurno` (camada de aplicação), não o motor.


#### Princípio 2: Determinismo Absoluto

Dado o mesmo input A, o serviço **sempre** devolve o mesmo output B. O simulador rejeita aleatoriedade, os serviços são funções puras.

- `random()` é proibido dentro de `core/services/`.
- Leitura de relógio (`datetime.now()`) é proibida, o tempo gasto pelo jogador é recebido como argumento (`tempo_segundos: float`) para o cálculo do fator tempo.
- Qualquer componente não-determinístico deve viver na camada de Infraestrutura.

#### Princípio 3: Orquestração entre Entidades 

O serviço é o local correto para lógicas que fariam uma entidade violar sua Responsabilidade Única.

**Exemplo:** `FolhaDeGabarito` sabe as respostas certas. `FolhaDeResposta` sabe o que o jogador marcou. Nenhuma das duas deve ter um método `comparar_com()`. O `DiagnosticoDeResposta` é o serviço que recebe ambas, confronta os dados e produz o diagnóstico, mantendo as entidades limpas e cada uma com seu propósito único.

#### Princípio 4: Cegueira Total de Infraestrutura

Assim como as entidades, os serviços em `core/services/` não podem:
- Ler ou escrever arquivos (JSON, TXT, etc.)
- Fazer requisições web
- Usar `print()` para depuração (o `logging` é a única ponte permitida)
- Importar qualquer coisa de `infrastructure/` ou `view/`

#### Princípio 5: Comunicação via DTOs Congelados

Serviços geram relatórios complexos de seus cálculos. Em vez de dicionários soltos (sujeitos a chaves digitadas errado), devem retornar DTOs congelados (`frozen=True` dataclasses).

**Referência:** `DiagnosticoDeResposta.gerar_diagnostico_pontuacao()` retorna `DiagnosticoPontuacaoDTO`, congelado, com type hints precisos, impossível de ser adulterado após a criação. O controlador recebe os dados já mastigados e seguros.

### 3.3. DTOs de Domínio (`core/dtos/`)

Dataclasses congeladas (`frozen=True`) para transporte de operandos matemáticos entre serviços.

| Arquivo | DTO | Campos |
|---------|-----|--------|
| `core/dtos/diagnostico_pontuacao.py` | `DiagnosticoPontuacaoDTO` | `qnt_riscos_marcados`, `qnt_riscos_gabarito`, `qnt_riscos_corretos_marcados`, `estado_ato`, `estado_condicao`, `status_decisao_jogador`, `tempo_resposta_segundos` |

### 3.3.1. DTOs de Domínio

Os DTOs de domínio são os **mensageiros blindados**. Sua filosofia resume-se a: Imutabilidade, Tipagem Forte e Zero Comportamento.

#### Princípio 1: Imutabilidade

Um DTO de domínio nunca deve ser alterado depois de criado. Em Python, implementa-se com `@dataclass(frozen=True)`.

**Referência:** `DiagnosticoPontuacaoDTO` em `core/dtos/diagnostico_pontuacao.py` é `frozen=True`. Se um programador tentar `dto.qnt_riscos_marcados = 0` dentro do `MotorDePontuacao`, o Python levanta `FrozenInstanceError` imediatamente, protegendo a integridade dos dados originais gerados pelo `DiagnosticoDeResposta`.

#### Princípio 2: Zero Lógica de Negócio 

Para entidades, um "Modelo Anémico" é um anti-padrão. Para DTOs, a anemia é o objetivo.

Um DTO de domínio contém **apenas atributos**. Nenhum método como `calcular_media()`, `validar_regra()` ou `salvar_no_banco()`. A única exceção são utilitários simples como `__str__` ou `to_dict()` para depuração.

#### Princípio 3: O Contrato Inquebrável entre Serviços

DTOs existem para evitar que métodos recebam 15 parâmetros avulsos ou dependam de `dict` genéricos. Sempre que um serviço precisar passar dados complexos para outro ou devolver resultados mastigados ao controlador, usa-se um DTO.

#### Princípio 4: Cegueira Total do Mundo Externo

Assim como tudo em `core/`, os DTOs de domínio não conhecem o mundo real:
- Nunca conter anotações de serialização web (Pydantic, Marshmallow).
- Nunca conter mapeamento de banco de dados (SQLAlchemy).
- Devem ser Python puro.

Se for preciso transportar dados de/para a infraestrutura, usa-se `infrastructure/dtos/`.

### 3.4. Violação Conhecida

**`core/model/folha_de_inspecao.py`** importa a biblioteca externa `unidecode` para normalização de acentos. Segundo a Arquitetura Limpa pura, a camada `core/` não deveria ter dependências externas. Esta violação é tolerada no projeto atual por se tratar de uma biblioteca de utilidade genérica (transformação de strings), sem acoplamento, banco de dados ou interface. Caso a regra seja aplicada rigidamente no futuro, a normalização deverá ser movida para a camada de infraestrutura ou implementada com stdlib.

---

## 4. Camada de Infraestrutura (`infrastructure/`)

Responsável por lidar com o mundo externo: Sistema de arquivos, serialização JSON e construção de objetos de domínio a partir de dados persistidos.

### 4.1. DTOs de Infraestrutura (`infrastructure/dtos/`)

Dataclasses mutáveis que transportam dados brutos do arquivo JSON para a fábrica.

| Arquivo | DTO | Campos |
|---------|-----|--------|
| `infrastructure/dtos/dados_cenario.py` | `DadosAnexoDTO` | `id_anexo`, `tipo`, `caminho_arquivo` |
| `infrastructure/dtos/dados_cenario.py` | `DadosCenarioDTO` | `id_cenario`, `titulo`, `dificuldade`, `atividade`, `local`, `texto_descricao`, `envolvidos`, `curso`, `riscos`, `fatores_inseguranca`, `decisao_otima`, `decisao_boa`, `anexos` |

### 4.2. Repositório (`infrastructure/repository/`)

| Arquivo | Classe | Função |
|---------|--------|--------|
| `infrastructure/repository/repositorio_json.py` | `RepositorioJSON` | Lê, valida (schema JSON) e filtra arquivos `.json` do diretório base, retornando DTOs |

Dependência externa: `jsonschema` (validação de schemas).

### 4.2.1. Filosofia do Repositório

É a fronteira entre o mundo dos dados adormecidos no arquivo e o mundo das regras vivas da aplicação. 

#### Princípio 1: A Fronteira Exclusiva de Dados Persistidos 

O repositório não sabe que existe um jogador. Seu único trabalho é garantir que os dados "adormecidos" no disco acordem no formato correto para a aplicação usar.

Ele valida **exclusivamente a estrutura do arquivo externo** (usando `jsonschema`): verifica se a chave `"titulo"` existe no JSON, se `"dificuldade"` veio preenchida como número em vez de texto.

**A diferença crucial:** A entidade barra o jogador de tentar inventar uma `dificuldade = 6` na hora de jogar. O repositório barra o arquivo JSON de tentar injetar uma string `"difícil"` onde deveria estar um número.



#### Princípio 2: Tratamento Resiliente de I/O Físico

O repositório lida com erros **físicos e lógicos da máquina**: Arquivo não encontrado, JSON mal formatado, perda de conexão. Blocos `try/except` para `FileNotFoundError`, `json.JSONDecodeError` e `ValidationError` vivem exclusivamente aqui.

**Como falhar:** Se `cenario_10.json` estiver corrompido, o repositório isola a falha, registra no log (`logger.error(...)`) e continua carregando os dados saudáveis. Um arquivo quebrado nunca deve fazer o jogo inteiro fechar.

#### Princípio 3: Anemia de Regras de Negócio 

O repositório sabe como extrair a informação, mas é cego para as regras do jogo. Nunca deve calcular a nota de um relatório, nem verificar se a resposta de um JSON faz sentido no contexto do jogo.

**A única lógica permitida:** Lógica de Consulta (Query). Filtrar todos os arquivos cujo campo `curso` seja igual a `T_MEIO_AMBIENTE` é o máximo de inteligência que esta classe deve ter.

#### Princípio 4: A Conversão para DTOs de Infraestrutura (O Molde)

O repositório não deve deixar vazar dicionários puros do Python (`dict` do `json.load`) para o resto do sistema, pois a aplicação não tem como adivinhar o que está dentro deles.

Ele pega o JSON validado e preenche um **DTO mutável de Infraestrutura**, como o `DadosCenarioDTO`. Esse DTO serve como um molde padronizado, a partir do momento em que o dado sai do repositório em formato de DTO, a próxima camada (a Fábrica) sabe exatamente com quais atributos pode trabalhar, beneficiando do auto-complete da IDE e dos type hints.

#### Princípio 5: Isolamento de Tecnologia

Para a camada de Aplicação (`GerenciadorDeTurno`), o repositório é uma ilusão. O controlador chama `extrair_dados()` e recebe DTOs prontos. Toda a complexidade de importar `json`, usar `pathlib` para achar pastas e abrir arquivos fica trancada na Infraestrutura.

Se amanhã você decidir trocar os JSONs por um banco SQLite ou dados na nuvem, você altera apenas o repositório. O resto do jogo continua funcionando sem notar a diferença.

### 4.3. Fábrica (`infrastructure/factory/`)

| Arquivo | Classe | Função |
|---------|--------|--------|
| `infrastructure/factory/fabrica_de_relatorios.py` | `FabricaDeRelatorios` | Converte `DadosCenarioDTO` em entidades `Relatorio` (com `FolhaDeGabarito` e `Anexo`) |

### 4.3.1. Filosofia da Fábrica

A fábrica é a **linha de montagem e camada anticorrupção** (Anti-Corruption Layer). É o único lugar do sistema autorizado a conhecer os dois mundos em simultâneo, a Infraestrutura (DTOs) e o Domínio .

#### Princípio 1: A Ponte entre Dois Mundos 

A fábrica é a fronteira oficial onde a infraestrutura morre e o domínio nasce. Recebe `DadosCenarioDTO` (do repositório) e devolve entidades `Relatorio` (do `core/model/`).

Isto impede que o `GerenciadorDeTurno` (aplicação) precise saber como desempacotar um DTO. 

#### Princípio 2: Encapsulamento da Complexidade de Instanciação

Criar um objeto rico do domínio raramente é um simples `Objeto()`. A fábrica assume o trabalho pesado, para criar um `Relatorio`, ela primeiro instancia a `FolhaDeGabarito`, depois verifica o tipo de cada anexo no DTO (`AnexoImagem`, `AnexoVideo` ou `AnexoAudio`), cria o anexo, instancia o `Relatorio` e pendura o anexo lá dentro.



#### Princípio 3: A Camada Anticorrupção 

A fábrica confia que o repositório validou a sintaxe (ex.: dificuldade é um número), mas é durante a montagem na fábrica que as regras de negócio das entidades são postas à prova.

A fábrica **não** deve fazer validações de negócio. As entidades já fazem isso nos seus próprios construtores. A fábrica simplesmente tenta construir a entidade. Se o JSON tiver um risco que não existe nas regras do jogo, quando a fábrica tentar criar a `FolhaDeGabarito`, a própria entidade vai lançar o `ValueError`. 


#### Princípio 4: Zero Comportamento de Jogo 

A fábrica só sabe criar as peças do tabuleiro, ela não sabe jogar. Não deve ordenar os relatórios por dificuldade, não deve embaralhar a lista (a menos que seja um requisito estrito de criação) e definitivamente não deve calcular o `v_max` das entidades que acabou de criar. Ela constrói as entidades e sai de cena.

---

## 5. Camada de Aplicação (`application/controllers/`)

Orquestra os casos de uso do jogo, conectando a infraestrutura ao domínio.

| Arquivo | Classe | Função |
|---------|--------|--------|
| `application/controllers/gerenciador_de_turno.py` | `GerenciadorDeTurno` | Gerencia o ciclo de vida de um turno (expediente): iniciar, obter relatórios, avaliar respostas, verificar vitória |
| `application/controllers/game_manager.py` | `GameManager` | *Stub*, gerenciamento geral do jogo (futuro) |

### Fluxo de Orquestração do `GerenciadorDeTurno`

```
iniciar_turno()
  ├── RepositorioJSON.extrair_dados()        → List[DadosCenarioDTO]
  ├── FabricaDeRelatorios.construir_pilha()  → List[Relatorio]
  └── MotorDePontuacao.calcular_meta_turno() → float (Vmax total)

obter_relatorio_da_pilha()
  └── pop() da pilha interna (LIFO)

avaliar_respostas_jogador(riscos, fatores, decisao, tempo)
  ├── __processar_submissao_jogador()        → FolhaDeResposta
  ├── Relatorio.anexar_resposta_jogador()
  ├── DiagnosticoDeResposta.gerar_diagnostico_pontuacao() → DiagnosticoPontuacaoDTO
  ├── MotorDePontuacao.calcular_vmax_relatorio()          → float (Vmax individual)
  ├── MotorDePontuacao.calcular_pontuacao_relatorio()     → float (pontuação final)
  └── acumula pontuação no turno

verificar_vitoria_do_turno()
  └── MotorDePontuacao.conferir_condicao_vitoria() → bool (>= 60%)
```

### 5.1. Filosofia dos Controladores

O controlador é o **maestro**. Ele não executa trabalho braçal, mas sim coordena o fluxo do caso de uso.

#### Princípio 1: Delegação Absoluta 

O controlador não faz trabalho braçal. Se encontrar um `if` dentro de um controlador validando regra de negócio ou resolvendo equação matemática, está errado.

O `GerenciadorDeTurno` delega tudo: Pede à fábrica para construir relatórios, pede ao `DiagnosticoDeResposta` para avaliar acertos, pede ao `MotorDePontuacao` para calcular a nota. O controlador é apenas um fluxograma vivo do caso de uso: "lê dados, monta relatório, avalia resposta, guarda nota".

#### Princípio 2: O Guardião do Estado da Aplicação

Ao contrário dos serviços de domínio, a camada de aplicação existe para **manter o estado**. É aqui que habitam variáveis como `__turno_iniciado`, `__pontuacao_acumulada` e `__pilha_relatorios`.

O controlador sabe exatamente em que fase o jogador está, se já terminou o expediente e se pode ou não pedir o próximo relatório. O estado deve estar fortemente protegido por **guardas** que impedem a execução fora de ordem.


#### Princípio 3: A Alfândega da Interface Gráfica 
A View  é burra. O controlador é o único ponto de contacto entre a interface e o coração do jogo. A interface passa apenas dados primitivos (textos, números, listas de strings). O controlador pega esses dados crus, traduz para entidades ou DTOs, invoca os serviços e devolve o resultado.

**Nunca,** sob nenhuma circunstância, um controlador importa elementos da interface. Não podem existir imports aqui dentro, nem referências a botões, janelas ou labels.

#### Princípio 4: O Ponto de Injeção de Dependências

O controlador é o ponto de encontro da Arquitetura Limpa. É aqui que o `core/` e a `infrastructure/` se abraçam. O controlador (ou quem o invoca) instancia o `RepositorioJSON`, o `MotorDePontuacao` e junta todas as peças.

**Testabilidade:** Como o controlador coordena muitos serviços externos, ele deve permitir que suas dependências sejam facilmente mockadas nos testes. Atualmente o `GerenciadorDeTurno` instancia suas dependências internamente, exigindo `unittest.mock.patch` nos testes. O ideal futuro é recebê-las por injeção no construtor.

---

## 6. Camada de Configuração (`config/`)

Centraliza constantes e configurações do projeto, sem dependências de outras camadas.

| Arquivo | Conteúdo |
|---------|----------|
| `config/constants.py` | `DIRETORIO_BASE`, `QUANTIDADE_GERACAO`, `CURSOS` |
| `config/logging_config.py` | `setup_logging()`: logging para ambientes dev/staging/prod |

---

## 7. Camada de Visualização (`view/`)

Diretório reservado para a futura interface PySide6. Atualmente contém apenas as subpastas vazias `components/` e `screens/`. Nenhum código implementado.

A camada visual segue o padrão **Passive View (Humble Object)** do MVP. A interface é burra: não toma decisões, não valida regras, não calcula nada. Ela apenas exibe o que o controlador manda e escuta o que o usuário faz.

### 7.1. Filosofia da View

#### Princípio 1: A View Burra (Passive View)

A interface gráfica não tem inteligência de negócio. Ela não toma decisões, apenas repete o que lhe disseram e escuta o que o usuário faz.

Se o jogador precisa escolher entre advertir ou interditar, a view captura o clique do botão e diz ao controlador: `gerenciador.processar_submissao(..., decisao="INTERDITAR")`. Nunca a view deve conter `if decisao == "INTERDITAR"` seguido de cálculo de pontuação.

#### Princípio 2: A Quarentena Tecnológica 

A camada `view/` é o único local do projeto autorizado a conhecer o framework de interface gráfica. Todos os `import PySide6.QtWidgets`, `QMainWindow`, `QPushButton` e manipulações de CSS/estilos vivem estritamente dentro da pasta `view/`.

#### Princípio 3: Diálogo Protegido 

A view é uma consumidora do controlador. Ela pede os dados, mas não os manipula. A view chama `gerenciador.obter_relatorio_da_pilha()` e recebe um `Relatorio`. Tem permissão para **ler** as propriedades (`relatorio.titulo`, `relatorio.texto_descricao`) para preencher labels na tela.

**Nunca** a view modifica a entidade. Não deve existir código na view que faça `relatorio.texto_descricao = "Novo texto"`.

#### Princípio 4: Gestão de Erros via UI 

A view não previne erros de negócio, ela apenas os exibe de forma elegante. Quando a view chama o `GerenciadorDeTurno` para submeter uma inspeção, deve envolver a chamada em um `try/except ValueError`. Se o domínio rejeitar a ação (ex.: "Falta selecionar uma decisão"), a view captura o `ValueError` e exibe um pop-up/modal vermelho com a mensagem de erro que veio do motor.

**Por quê?** Mantém a interface agradável (evita que o jogo feche na cara do jogador) usando as validações rigorosas que já existem no `core/`.

#### Princípio 5: Separação Interna (Componentes vs. Telas)

Para não criar arquivos de UI com milhares de linhas, a responsabilidade é dividida dentro da própria `view/`:

- **`view/screens/`**: As janelas principais (`TelaPrincipal`, `TelaDeLogin`, `TelaDeInspecao`). Coordenam o layout global.
- **`view/components/`**: Os blocos de Lego reutilizáveis. Se o jogo tem um botão de decisão verde que brilha, cria-se `BotaoAcao(QPushButton)` dentro de `components/`. As `screens` apenas instanciam estes componentes.

---

## 8. Convenções de Importação

- **Intra-pacote (mesmo diretório):** imports relativos com `.`
  ```python
  from .folha_de_inspecao import FolhaDeInspecao         # core/model/
  from ..dtos.dados_cenario import DadosCenarioDTO        # infrastructure/
  ```
- **Entre pacotes:** imports absolutos
  ```python
  from core.model.relatorio import Relatorio              # infrastructure/ → core/
  from infrastructure.factory.fabrica_de_relatorios import FabricaDeRelatorios  # application/ → infrastructure/
  ```
- **Não há arquivos `__init__.py`**: todos os pacotes são *namespace packages* (PEP 420).

---

## 9. Fluxo de Dados Completo

```
[Arquivos JSON]
       │
       ▼
RepositorioJSON (infrastructure/repository/)
  ├── Lê arquivo .json
  ├── Valida contra JSON_SCHEMA
  ├── Filtra por curso selecionado
  └── Retorna List[DadosCenarioDTO]
       │
       ▼
FabricaDeRelatorios (infrastructure/factory/)
  ├── Cria FolhaDeGabarito (core/model/)
  ├── Cria Relatorio (core/model/)
  ├── Cria AnexoImagem/Video/Audio (core/model/)
  └── Retorna List[Relatorio]
       │
       ▼
GerenciadorDeTurno (application/controllers/)
  ├── Armazena pilha de relatórios
  ├── Entrega um relatório por vez ao jogador
  │       │
  │       ▼ (Jogador preenche)
  │   FolhaDeResposta (core/model/)
  │       │
  │       ▼
  ├── DiagnosticoDeResposta (core/services/)
  │   └── Retorna DiagnosticoPontuacaoDTO (core/dtos/)
  │       │
  │       ▼
  ├── MotorDePontuacao (core/services/)
  │   ├── calcular_vmax_relatorio()
  │   ├── calcular_pontuacao_relatorio()
  │   └── Retorna float (pontuação do relatório)
  │       │
  │       ▼
  └── Acumula pontuação no turno
       │
       ▼
  verificar_vitoria_do_turno() → bool (aprovado/reprovado)
```

---

## 10. Diagrama de Dependências (Arquivo por Arquivo)

```
main.py
  └── config.logging_config

application/controllers/gerenciador_de_turno.py
  ├── config.constants
  ├── core.model.relatorio
  ├── core.model.folha_de_resposta
  ├── core.services.motor_de_pontuacao
  ├── core.services.diagnostico_de_resposta
  ├── infrastructure.factory.fabrica_de_relatorios
  └── infrastructure.repository.repositorio_json

infrastructure/factory/fabrica_de_relatorios.py
  ├── core.model.relatorio
  ├── core.model.folha_de_gabarito
  ├── core.model.anexo
  └── infrastructure.dtos.dados_cenario

infrastructure/repository/repositorio_json.py
  └── infrastructure.dtos.dados_cenario
  └── jsonschema (externa)

core/services/motor_de_pontuacao.py
  ├── core.dtos.diagnostico_pontuacao
  └── core.model.relatorio

core/services/diagnostico_de_resposta.py
  ├── core.model.folha_de_gabarito
  ├── core.model.folha_de_resposta
  ├── core.dtos.diagnostico_pontuacao
  └── core.services.diagnostico_feedback

core/model/relatorio.py
  ├── core.model.anexo
  ├── core.model.folha_de_gabarito
  └── core.model.folha_de_resposta

core/model/folha_de_gabarito.py
  └── core.model.folha_de_inspecao

core/model/folha_de_resposta.py
  └── core.model.folha_de_inspecao

core/model/folha_de_inspecao.py
  └── unidecode (externa) ⚠️ violação

core/model/anexo.py
  └── (stdlib apenas)
```

---

## 11. Boas Práticas e Restrições

- **Nunca importar bibliotecas externas em `core/`**, a menos que seja estritamente necessário e devidamente justificado (vide seção 3.4).
- **Nunca importar `infrastructure/` ou `application/` dentro de `core/`**: a seta de dependência sempre aponta para dentro.
- **DTOs de fronteira:** Use `infrastructure/dtos/` para transporte de dados brutos (mutáveis) e `core/dtos/` para operandos de negócio (congelados).
- **Injeção de dependência:** O `GerenciadorDeTurno` instancia suas dependências internamente. Para testes, utilize `unittest.mock.patch` para substituir `RepositorioJSON`, `FabricaDeRelatorios` e `MotorDePontuacao`.
- **Namespace packages:** Não crie arquivos `__init__.py`. O projeto usa pacotes implícitos (PEP 420).
