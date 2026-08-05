<p align="center">
  <img src="docs/img/InspetorIFFBJI_banner.png" alt="Inspetor IFF-BJI" width="100%">
</p>

# Inspetor IFF-BJI

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](LICENSE)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green)]()

> **Simulador gamificado de análise de risco ocupacional** desenvolvido no IFF (Instituto Federal Fluminense) como atividade de Curricularização da Extensão. O jogador recebe relatórios de cenários reais em laboratórios, oficinas e refeitórios, classifica riscos e fatores de insegurança, e escolhe a intervenção cabível sob pressão de tempo. A nota sai de um modelo determinístico que pondera exatidão, completude e decaimento temporal — refletindo o que um técnico de segurança faria naquele contexto.

---

## 📋 Sumário

- [✨ Features](#-features)
- [🎮 Como Jogar](#-como-jogar)
- [🚀 Instalação Rápida](#-instalação-rápida)
- [📚 Documentação](#-documentação)
- [🏗️ Arquitetura](#-arquitetura)
- [📄 Licença](#-licença)
- [👥 Contribuidores](#-contribuidores)

---

## ✨ Features

- 🎯 **Modelo matemático determinístico** — pontuação precisa baseada em exatidão, completude e fator temporal
- 🏥 **Cenários educacionais reais** — laboratórios, oficinas e refeitórios do IFF, com relatórios autênticos
- ⚙️ **Classificação de riscos** — 5 categorias (Físico, Químico, Biológico, Ergonômico, Acidente) com análise profunda
- 🛡️ **Decisões administrativas** — três opções (Advertir, Interditar, Ignorar) com consequências reais
- ⏱️ **Pressão temporal** — penalidade por tempo decorrido, simulando realismo operacional
- 📊 **Feedback detalhado** — diagnóstico pós-decisão, pontuação por item, análise de erros
- 🎓 **Tutorial integrado** — 8 slides guiando o jogador passo a passo no primeiro acesso
- 🌙 **Tema claro e escuro** — interface adaptativa com design responsivo
- 🔧 **Arquitetura limpa** — Clean Architecture com separação rigorosa de camadas (Core, Infrastructure, Application, View)

---

## 🎮 Como Jogar

1. **Seleção de Personagem**: Escolha um dos perfis de inspetor disponíveis (papel define contexto)
2. **Leitura do Caso**: Analise o relatório da inspeção — local, atividade, envolvidos, descrição
3. **Classificação de Riscos**: Marque os riscos encontrados — cada um tem uma cor única (NR-26)
4. **Classificação de Fatores**: Identifique os fatores de insegurança — Ato Inseguro vs. Condição Insegura
5. **Decisão Administrativa**: Escolha a ação (Advertir/Interditar/Ignorar) baseado na gravidade
6. **Recebimento de Nota**: O sistema calcula sua performance e fornece feedback completo
7. **Repetição**: Simule vários casos para melhorar sua expertise em segurança ocupacional

**Objetivo**: Ser o inspetor mais preciso possível — máxima nota = análise correta e rápida.

---

## 🚀 Instalação Rápida

**Pré-requisitos:** Python 3.11+ e Git

```bash
git clone https://github.com/WelingtonPeres/Inspetor_IFF_BJI.git
cd Inspetor_IFF_BJI
python -m venv venv
# Windows (PowerShell): .\venv\Scripts\Activate.ps1
# Linux/macOS:          source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Dúvidas?** Consulte o [Guia de Contribuição](CONTRIBUTING.md) para detalhes de ambiente, dependências e troubleshooting.

---

## 📚 Documentação

Toda a documentação técnica vive em [`docs/`](docs/README.md), organizada por tema:

| Pergunta | Link |
|----------|------|
| **Como contribuo?** | [Guia de Contribuição](CONTRIBUTING.md) |
| **Como o código é organizado?** | [Arquitetura da Camada View](docs/arquitetura/view.md), [Diagrama de Classes](docs/arquitetura/diagrama-classes.md) |
| **Como o jogo funciona?** | [Modelagem Matemática](docs/game-design/modelagem-matematica.md), [Level Design](docs/game-design/level-design.md) |
| **Qual é o schema dos dados?** | [Estrutura JSON](docs/dados/estrutura-json.md) |
| **Qual é o padrão de código?** | [Nomenclatura e PEP-8](docs/processo/nomenclatura-pep8.md) |
| **Quer revisar PRs?** | [Checklist de Code Review](docs/arquitetura/checklist-revisao.md) |

**Índice completo**: [docs/README.md](docs/README.md)

---

## 🏗️ Arquitetura

O projeto segue **Arquitetura Limpa**, dividido em camadas concêntricas:

| Camada | Diretório | Responsabilidade |
|--------|-----------|------------------|
| **Core (Domain)** | `core/model/`, `core/services/`, `core/dtos/` | Regras de negócio e entidades — **sem dependências externas** |
| **Infrastructure** | `infrastructure/` | Repositório, fábrica e DTOs de persistência |
| **Application** | `application/controllers/` | Orquestração dos casos de uso |
| **View** | `view/` | Interface com o utilizador (PySide6 + Qt) |
| **Config** | `config/` | Configuração centralizada (logging, etc.) |

**Leitura recomendada**: [Clean Architecture](docs/arquitetura/clean-architecture.md)

---

## 📄 Licença

Este projeto está licenciado sob a **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** (CC BY-NC-SA 4.0).

**O que você pode fazer:**
- ✓ Usar, copiar e redistribuir
- ✓ Remixar, transformar e melhorar
- ✓ Usar em contextos educacionais

**Com a condição de:**
- Atribuir crédito ao IFF e aos autores
- Não usar para fins comerciais
- Compartilhar derivados sob a mesma licença

Para o texto legal completo, veja [LICENSE](LICENSE).

---

## 👥 Contribuidores

Veja [AUTHORS.md](AUTHORS.md) para lista completa de contribuidores, orientadores e instituições envolvidas.

### Como Contribuir

O projeto está em **desenvolvimento ativo** e aceita contribuições! 

1. Leia [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes
2. Abra uma [Issue](https://github.com/WelingtonPeres/Inspetor_IFF_BJI/issues) para reportar bugs ou propor features
3. Envie um [Pull Request](https://github.com/WelingtonPeres/Inspetor_IFF_BJI/pulls) com suas melhorias
4. Siga os [padrões de código](docs/processo/nomenclatura-pep8.md) do projeto

---

## 📊 Status do Projeto

| Aspecto | Status |
|---------|--------|
| **Desenvolvimento** | 🟢 Ativo — novas features e melhorias contínuas |
| **Estabilidade** | 🟡 Beta — testado mas em refinamento |
| **Testes** | 🟢 615+ testes automatizados passando |
| **Documentação** | 🟢 Completa e atualizada |
| **Licença** | 🟢 CC BY-NC-SA 4.0 |

---

## 🎓 Contexto Académico

Projeto desenvolvido como **Atividade de Curricularização da Extensão** na disciplina de Higiene e Segurança do Trabalho do Instituto Federal Fluminense (IFF), Campus Bom Jesus do Itabapoana.

O objetivo é criar uma ferramenta educacional imersiva que permita aos alunos e profissionais de segurança praticar análise de risco em um ambiente controlado e gamificado.

---

**Última atualização:** Agosto de 2026  
**Mantido por:** [Welington Peres Léo](https://github.com/WelingtonPeres)
