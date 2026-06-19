# Inspetor IFF-BJI: Análise de Risco

## 1. Contexto Institucional e Extensão Curricular

Este projeto de software foi desenvolvido como atividade integrante da **Curricularização da Extensão** do Curso de **Bacharelado em Engenharia de Computação** do **Instituto Federal Fluminense (IFF) - Campus Bom Jesus do Itabapoana**, desenvolvida na disciplina de **Higiene e Segurança do Trabalho**, na grade do 8° período.

A iniciativa cumpre o papel fundamental de estender o conhecimento acadêmico gerado na instituição para a sociedade, integrando conceitos avançados de Engenharia de Computação a uma aplicação prática de Segurança do Trabalho. O sistema possui potencial direto para ser utilizado em treinamentos internos de servidores e alunos, além de capacitações externas em empresas e comunidades da região.

## 2. Apresentação do Sistema

O **Inspetor IFF-BJI: Análise de Risco** é um simulador interativo baseado na rotina técnica de um Técnico de Segurança do Trabalho dentro do ambiente do Instituto Federal Fluminense. 

No papel de um inspetor, o usuário é responsável por analisar relatórios diários, inspecionar evidências de cenários de risco em dependências institucionais, como laboratórios, oficinas e refeitórios, e tomar decisões administrativas cabíveis sob forte pressão de tempo.

A abordagem do sistema afasta-se de dinâmicas puramente recreativas ou baseadas em aleatoriedade (jogos convencionais), fundamentando-se em um **modelo matemático determinístico e avaliativo** estruturado para mensurar o desempenho técnico real do operador.


##  Documentação do Projeto e Guias

Para manter este ficheiro principal conciso, toda a documentação técnica, especificações matemáticas e guias de desenvolvimento foram modularizados. Consulte os links abaixo para compreender a fundo os detalhes do projeto:

* **[Guia de Contribuição (CONTRIBUTING.md)](CONTRIBUTING.md)**: Como configurar o ambiente local, pré-requisitos e regras para submissão de Pull Requests.
* **[Modelagem Matemática e Algoritmos](docs/MODELAGEM_MATEMATICA.md)**: Detalhamento das equações de pontuação, cálculo de exatidão e fator de decaimento temporal.
* **[Estrutura de Dados e Schema JSON](docs/ESTRUTURA_JSON.md)**: Arquitetura e tipagem dos ficheiros de persistência de cenários e relatórios.
* **[Level Design e Fluxos do Jogo](docs/Level_Design.md)**: Mapeamento da experiência do utilizador, progressão de dificuldade e mecânicas de feedback.
* **[Padrões de Nomenclatura e PEP-8](docs/PADROES_NOMENCLATURA_PEP8.md)**: Diretrizes estritas de estilo de código adotadas pela equipa de engenharia.

##  Arquitetura do Projeto (Diagrama de Classes)

O projeto segue os princípios da **Arquitetura Limpa (Clean Architecture)**, dividido em camadas concêntricas:

```mermaid
classDiagram
    %% ==================== Core Model Layer ====================
    class Anexo {
        <<abstract>>
        -__id_anexo: int
        -__caminho_arquivo: str
        +id_anexo() int
        +caminho_arquivo() str
        +get_tipo_midia()* str
        +extrair_dados() dict
    }
    class AnexoImagem {
        +get_tipo_midia() str
    }
    class AnexoVideo {
        +get_tipo_midia() str
    }
    class AnexoAudio {
        +get_tipo_midia() str
    }
    class FolhaDeInspecao {
        <<abstract>>
        -__riscos: List[str]
        -__fatores_inseguranca: List[str]
        +riscos() List[str]
        +fatores_inseguranca() List[str]
        +contar_riscos() int
        +contar_fatores() int
    }
    class FolhaDeGabarito {
        -__decisao_otima: str
        -__decisao_boa: str
        +decisao_otima() str
        +decisao_boa() str
    }
    class FolhaDeResposta {
        -__decisao_tomada: str
        -__tempo_gasto_segundos: int
        +decisao_tomada() str
        +tempo_gasto_segundos() int
    }
    class Relatorio {
        -__id_cenario: int
        -__titulo: str
        -__atividade: str
        -__local: str
        -__texto_descricao: str
        -__envolvidos: List[str]
        -__cursos: List[str]
        -__dificuldade: int
        -__anexos: List[Anexo]
        -__folha_gabarito: FolhaDeGabarito
        -__folha_resposta: FolhaDeResposta
        +id_cenario() int
        +titulo() str
        +atividade() str
        +local() str
        +texto_descricao() str
        +envolvidos() List[str]
        +dificuldade() int
        +cursos() List[str]
        +folha_gabarito() FolhaDeGabarito
        +folha_resposta_jogador() FolhaDeResposta
        +extrair_apresentacao_relatorio() dict
        +obter_anexos() List[Anexo]
        +adicionar_anexo(anexo) void
        +possui_anexos() bool
        +anexar_resposta_jogador(resposta) void
    }
    AnexoImagem --|> Anexo
    AnexoVideo --|> Anexo
    AnexoAudio --|> Anexo
    FolhaDeGabarito --|> FolhaDeInspecao
    FolhaDeResposta --|> FolhaDeInspecao
    Relatorio *-- Anexo
    Relatorio *-- FolhaDeGabarito
    Relatorio *-- FolhaDeResposta

    %% ==================== Core Services Layer ====================
    class MotorDePontuacao {
        +calcular_pontuacao_relatorio(v_max, dto) float
        +calcular_meta_turno(relatorios) float
        +conferir_condicao_vitoria(nota, v_max) bool
        -_calcular_pontuacao_riscos(...) float
        -_calcular_pontuacao_inseguranca(...) float
        -_calcular_pontuacao_decisao(...) float
        -_calcular_fator_tempo(tempo) float
    }
    class DiagnosticoDeResposta {
        +gerar_diagnostico_pontuacao(gabarito, respostas) DiagnosticoPontuacaoDTO
    }
    class DiagnosticoFeedback {
        <<stub>>
    }
    MotorDePontuacao ..> DiagnosticoPontuacaoDTO : depende
    DiagnosticoDeResposta ..> DiagnosticoPontuacaoDTO : cria
    DiagnosticoDeResposta --> FolhaDeGabarito : usa
    DiagnosticoDeResposta --> FolhaDeResposta : usa

    %% ==================== Core DTOs ====================
    class DiagnosticoPontuacaoDTO {
        <<dataclass frozen>>
        qnt_riscos_marcados: int
        qnt_riscos_gabarito: int
        qnt_riscos_corretos_marcados: int
        estado_ato: bool
        estado_condicao: bool
        status_decisao_jogador: str
        tempo_resposta_segundos: float
    }

    %% ==================== Infrastructure Layer ====================
    class RepositorioJSON {
        -__diretorio_base: Path
        +curso_selecionado: str
        +quantidade_gerada: int
        +extrair_dados() List[DadosCenarioDTO]
        -__validar_esquema_basico(dados) void
        -__traduzir_erro_validacao(...) void
    }
    class FabricaDeRelatorios {
        +construir_pilha(dados) List[Relatorio]
        -__construir_relatorio(dto) Relatorio
        -__extrair_instanciar_anexos(dto) List[Anexo]
    }
    class DadosCenarioDTO {
        <<dataclass>>
        id_cenario: int
        titulo: str
        dificuldade: int
        atividade: str
        local: str
        texto_descricao: str
        envolvidos: List[str]
        cursos: List[str]
        riscos: List[str]
        fatores_inseguranca: List[str]
        decisao_otima: str
        decisao_boa: str
        anexos: List[DadosAnexoDTO]
    }
    class DadosAnexoDTO {
        <<dataclass>>
        id_anexo: int
        tipo: str
        caminho_arquivo: str
    }
    DadosCenarioDTO *-- DadosAnexoDTO
    RepositorioJSON ..> DadosCenarioDTO : produz
    FabricaDeRelatorios ..> DadosCenarioDTO : consome
    FabricaDeRelatorios ..> Relatorio : produz
    FabricaDeRelatorios ..> Anexo : instancia

    %% ==================== Application Layer ====================
    class GerenciadorDeTurno {
        <<stub>>
    }
    class GameManager {
        <<stub>>
    }

    %% ==================== Config ====================
    class LoggingConfig {
        +setup_logging() void
    }
```

### Legenda das Camadas

| Camada | Diretório | Responsabilidade |
|--------|-----------|------------------|
| **Core (Domain)** | `core/model/`, `core/services/`, `core/dtos/` | Regras de negócio e entidades — **sem dependências externas** |
| **Infrastructure** | `infrastructure/` | Repositório, fábrica e DTOs de persistência |
| **Application** | `application/controllers/` | Orquestração dos casos de uso (em implementação) |
| **View** | `view/` | Interface com o utilizador (PySide6) |
| **Config** | `config/` | Configuração centralizada (logging, etc.) |
