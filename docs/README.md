# Documentação — Inspetor IFF-BJI

Índice da documentação técnica do projeto, organizada pela pergunta que cada pasta responde.

## Como o código é organizado? — `arquitetura/`

- [Clean Architecture](arquitetura/clean-architecture.md) — as camadas do projeto (core, infrastructure, application, view), suas responsabilidades e regras de dependência. **Leitura obrigatória antes de contribuir.**
- [Checklist de revisão](arquitetura/checklist-revisao.md) — as 5 perguntas fundamentais de code review; nenhum PR entra sem passar por elas.
- [Arquitetura da View](arquitetura/view.md) — padrões da camada de apresentação (PySide6 + MVP, separação estrutura/estilo, signals).
- [Diagrama de classes](arquitetura/diagrama-classes.md) — visão de classes das camadas core, infrastructure e application.

## Como contribuo? — `processo/`

- [Git Flow](processo/gitflow.md) — padrão de branches e fluxo de versionamento.
- [Nomenclatura e PEP 8](processo/nomenclatura-pep8.md) — padrões de nomes para classes, métodos, variáveis e módulos.
- [Guia de contribuição](../CONTRIBUTING.md) — setup do ambiente e regras para Pull Requests (na raiz do repositório).

## Como o jogo funciona? — `game-design/` e `dados/`

- [Modelagem matemática](game-design/modelagem-matematica.md) — equações de pontuação, exatidão, decaimento temporal e condição de vitória.
- [Level design](game-design/level-design.md) — metodologia de classificação de dificuldade dos cenários.
- [Estrutura JSON](dados/estrutura-json.md) — o contrato de dados dos cenários: schema, enums e regras de validação.

## Como ele parece? — `visual/`

- [Design system](visual/design.md) — paleta, tokens de cor e esquemas claro/escuro.
- [Identidade institucional](visual/identidade.md) — regras de uso da marca, cores e tipografia do IFFluminense.
