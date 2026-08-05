<p align="center">
  <img src="docs/img/InspetorIFFBJI_banner.png" alt="Inspetor IFF-BJI" width="100%">
</p>

# Inspetor IFF-BJI

> Simulador de análise de risco ocupacional desenvolvido no IFF, Campus Bom Jesus do Itabapoana, como atividade de Curricularização da Extensão na disciplina de Higiene e Segurança do Trabalho. O jogador recebe relatórios de cenários reais em laboratórios, oficinas e refeitórios, classifica riscos e fatores de insegurança, e escolhe a intervenção cabível sob pressão de tempo. A nota sai de um modelo determinístico que pondera exatidão, completude e decaimento temporal, e o resultado reflete o que um técnico de segurança faria naquele contexto.

## Sumário

- [1. Instalação Rápida](#1-instalação-rápida)
- [2. Documentação do Projeto e Guias](#2-documentação-do-projeto-e-guias)
- [3. Arquitetura do Projeto](#3-arquitetura-do-projeto)

## 1. Instalação Rápida

Pré-requisitos: **Python 3.11+** e **Git**.

```bash
git clone https://github.com/WelingtonPeres/Inspetor_IFF_BJI.git
cd Inspetor_IFF_BJI
python -m venv venv
# Windows (PowerShell): .\venv\Scripts\Activate.ps1
# Linux/macOS:          source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Dúvidas de ambiente (Python, `venv`, dependências) estão cobertas no [Guia de Contribuição](CONTRIBUTING.md); se algo ainda travar, abra uma issue.


## 2. Documentação do Projeto e Guias

Toda a documentação técnica vive em [`docs/`](docs/README.md), organizada por tema — o índice completo está em **[docs/README.md](docs/README.md)**. Atalhos mais usados:

* **[Guia de Contribuição](CONTRIBUTING.md)**: como configurar o ambiente local e submeter Pull Requests.
* **[Clean Architecture](docs/arquitetura/clean-architecture.md)**: as camadas do projeto e as regras de dependência entre elas.
* **[Modelagem Matemática](docs/game-design/modelagem-matematica.md)**: equações de pontuação, exatidão e decaimento temporal.
* **[Estrutura JSON](docs/dados/estrutura-json.md)**: o schema dos cenários e relatórios.
* **[Nomenclatura e PEP-8](docs/processo/nomenclatura-pep8.md)**: diretrizes de estilo de código.

## 3. Arquitetura do Projeto

O projeto segue os princípios da **Arquitetura Limpa (Clean Architecture)**, dividido em camadas concêntricas:


| Camada | Diretório | Responsabilidade |
|--------|-----------|------------------|
| **Core (Domain)** | `core/model/`, `core/services/`, `core/dtos/` | Regras de negócio e entidades: **sem dependências externas** |
| **Infrastructure** | `infrastructure/` | Repositório, fábrica e DTOs de persistência |
| **Application** | `application/controllers/` | Orquestração dos casos de uso |
| **View** | `view/` | Interface com o utilizador (PySide6) |
| **Config** | `config/` | Configuração centralizada (logging, etc.) |

O diagrama de classes completo das camadas internas está em [docs/arquitetura/diagrama-classes.md](docs/arquitetura/diagrama-classes.md); os padrões da camada view em [docs/arquitetura/view.md](docs/arquitetura/view.md).
