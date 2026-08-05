# Manual de Revisão: Clean Architecture - Inspetor IFF-BJI

**Objetivo:** Este documento serve como o Guia Definitivo de Code Review para o projeto. Nenhuma classe, refatoração ou nova funcionalidade deve ser mesclada na branch principal (`main`/`develop`) sem passar pelo crivo das **5 Perguntas Fundamentais**.

---

## As 5 Perguntas Fundamentais (Go / No-Go)

Se a resposta para **qualquer** uma destas 5 perguntas for negativa ou violar a regra, o código **deve ser refatorado imediatamente** antes do merge.

### 1. A Regra de Dependência

> O fluxo de dependência aponta *apenas* para dentro?

**Avaliação:** Verifique os `imports`. A camada `core/` (model, services, dtos) **jamais** pode importar arquivos de `infrastructure/` (repository, factory, dtos), `application/` (controllers) ou `view/` (interface). As camadas externas podem enxergar o núcleo, mas o núcleo é cego para o mundo externo.

**Referência no projeto:**
- ✅ Correto: `infrastructure/factory/fabrica_de_relatorios.py` importa `core.model.relatorio`
- ❌ Incorreto: `core/model/folha_de_inspecao.py` importa `unidecode` (biblioteca externa, violação tolerada mas não incentivada)

### 2. Isolamento de I/O e Frameworks

> O Domínio é agnóstico à tecnologia?

**Avaliação:** As classes em `core/model/` e `core/services/` usam PySide6, sabem ler arquivos `.json`, fazem requisições de rede ou interagem com o sistema operacional? Se sim, está errado. O núcleo deve ser "Python puro". Toda leitura de disco ou desenho de tela fica na Infraestrutura ou na View.

**Referência no projeto:**
- ✅ Correto: `core/model/relatorio.py` não sabe de onde vêm os dados, apenas valida e armazena
- ❌ Incorreto: Criar um método `Relatorio.salvar_em_json()` dentro de `core/model/`

### 3. Fronteiras e DTOs

> Estamos evitando o vazamento de Entidades?

**Avaliação:** A UI está modificando diretamente uma entidade de domínio? A comunicação entre as extremidades (View ↔ Application ↔ Infrastructure) deve utilizar DTOs ou tipos primitivos. As entidades de domínio (`Relatorio`, `FolhaDeGabarito`) nunca devem trafegar para a interface sem antes serem convertidas em dicionários ou DTOs de apresentação.

**Referência no projeto:**
- ✅ Correto: `Relatorio.extrair_apresentacao_relatorio()` retorna um `dict` seguro (sem gabarito) para a UI
- ✅ Correto: `RepositorioJSON` produz `DadosCenarioDTO` (infrastructure DTO), que é convertido por `FabricaDeRelatorios` em entidades de domínio
- ❌ Incorreto: Passar `FolhaDeGabarito` diretamente para a View

### 4. Inversão de Dependência (Injeção)

> A classe delega a criação de dependências pesadas?

**Avaliação:** Controladores e Serviços não devem instanciar diretamente classes de Banco de Dados ou IO no meio de seus métodos de negócio. Prefira receber essas instâncias prontas (Mocks em teste, Repositórios reais em produção) através dos construtores. Isso viabiliza testes unitários isolados.

**Referência no projeto:**
- ⚠️ `GerenciadorDeTurno.__init__()` instancia `MotorDePontuacao()` e `DiagnosticoDeResposta()` internamente, para testes, use `unittest.mock.patch`
- ✅ Ideal futuro: Receber `MotorDePontuacao` e `RepositorioJSON` como parâmetros do construtor

### 5. Responsabilidade Única (SRP)

> Esta classe tem apenas UM motivo para mudar?

**Avaliação:** A classe `Relatorio` sabe salvar a si mesma no JSON? O `GerenciadorDeTurno` desenha botões na tela? O `MotorDePontuacao` lê arquivos do disco? Se uma classe acumula persistência, orquestração E cálculo, ela deve ser desmembrada.

**Referência no projeto:**
- ✅ Correto: `MotorDePontuacao` só calcula; `RepositorioJSON` só lê/valida arquivos; `GerenciadorDeTurno` só orquestra o fluxo
- ❌ Incorreto: Adicionar um método `MotorDePontuacao.exportar_resultados_para_pdf()`

---

## Perguntas Adicionais de Qualidade (Refinamento)

Estas perguntas avaliam o quão limpa e segura é a implementação interna do código.

### Encapsulamento Estrito

> Os atributos internos estão protegidos usando prefixo duplo (`__`)? Os atributos que o Front-end precisa ler estão exportados apenas como `@property` (sem setters)?

**Referência:**
- ✅ Correto: `self.__pontuacao_acumulada_turno` com acesso via métodos públicos
- ✅ Correto: `@property` para `id_cenario`, `titulo`, etc. em `Relatorio`
- ❌ Incorreto: `self.pontuacao = 0` (público) sem validação

### Tratamento de Exceções

> A classe faz validação de entrada e levanta erros específicos com tags no lugar de prints ou crashes silenciosos?

**Referência:**
- ✅ Correto: `raise ValueError("[Erro - Turno] Nenhum relatório foi obtido da pilha")`
- ✅ Correto: `raise FileNotFoundError(f"[Erro - Caminho Json] O diretório {path} não foi encontrado.")`
- ❌ Incorreto: `print("Deu erro")` ou `raise Exception("erro")` sem contexto

### Testabilidade

> Consigo escrever um teste para essa classe no pytest sem precisar do banco de dados (JSON) montado ou da UI renderizada?

**Referência:**
- ✅ Correto: `MotorDePontuacao` é testado independentemente com `DiagnosticoPontuacaoDTO` mockado
- ✅ Correto: `GerenciadorDeTurno` é testado com `@patch` em `RepositorioJSON`, `FabricaDeRelatorios` e `MotorDePontuacao`
- ❌ Incorreto: Classe que exige arquivo JSON real ou PySide6 rodando para ser testada

### Linguagem Ubíqua (DDD)

> As variáveis, funções e arquivos utilizam a terminologia do negócio do jogo?

**Referência:**
- ✅ Correto: `GerenciadorDeTurno` (e não `LevelManager`), `FolhaDeResposta` (e não `AnswersSheet`), `Expediente` (e não `GameRound`)
- ❌ Incorreto: Nomes genéricos como `DataProcessor`, `GameLogic`, `FileHandler`

### Código Verboso e Documentado

> As funções possuem Type Hints rigorosas? As classes e métodos possuem Docstrings claras explicando o que fazem e por que fazem?

**Referência:**
- ✅ Correto:
  ```python
  def calcular_pontuacao_relatorio(self, v_max: float, dados_pontuacao: DiagnosticoPontuacaoDTO) -> float:
      """Calcula a pontuação final do relatório considerando riscos, fatores, decisão e tempo."""
  ```
- ❌ Incorreto:
  ```python
  def calc(v, d):
      return v * d  # ??? qual fórmula? quais parâmetros?
  ```

---

## Como Usar na Rotina Diária

### Antes de todo Commit/PR

1. Abra este arquivo
2. Percorra as **5 Perguntas Fundamentais** avaliando cada arquivo `.py` que você criou ou modificou
3. Verifique as **Perguntas Adicionais** para refinamento
4. Se o código passar em todas, está pronto para merge

### Durante o Code Review

- Se um PR violar qualquer pergunta fundamental, **bloqueie o merge** e aponte a seção específica deste documento como justificativa
- Se um PR violar apenas perguntas adicionais, **sugira melhoria** mas não necessariamente bloqueie

### Checklist Rápido (Print-Friendly)

```
[ ] 1. Dependência: core/ não importa nada externo? (fora stdlib)
[ ] 2. Isolamento: Domínio não sabe de JSON, PySide6 ou rede?
[ ] 3. Fronteiras: DTOs na comunicação entre camadas?
[ ] 4. Injeção: Dependências pesadas são injetadas, não instanciadas?
[ ] 5. SRP: Cada classe tem um único motivo para mudar?
[ ] 6. Encapsulamento: Atributos privados com __ e @property?
[ ] 7. Exceções: Erros com tags [Erro - NomeDaClasse]?
[ ] 8. Testabilidade: Testável sem JSON/UI reais?
[ ] 9. Ubiquidade: Nomes seguem o vocabulário do domínio?
[ ] 10. Documentação: Type Hints + Docstrings em todo método público?
```

---

## Estrutura de Camadas (Resumo Visual)

```
view/  ──>  application/  ──>  core/  <──  infrastructure/
                │                              │
                └───────── config/ ────────────┘
```

| Camada | Diretório | Pode importar |
|--------|-----------|---------------|
| **Domain** | `core/model/`, `core/services/`, `core/dtos/` | Apenas stdlib |
| **Infrastructure** | `infrastructure/` | `core/`, stdlib, libs externas |
| **Application** | `application/controllers/` | `core/`, `infrastructure/`, `config/` |
| **Config** | `config/` | Apenas stdlib |
| **View** | `view/` | `application/` |

---
**Documento mantido pela equipe de engenharia do Inspetor IFF-BJI.**
