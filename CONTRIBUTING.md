
# Guia de Contribuição: Inspetor IFF-BJI

Como um projeto acadêmico e de código aberto, o **Inspetor IFF-BJI** encoraja a contribuição de alunos, pesquisadores e desenvolvedores da comunidade. Para garantir a integridade da Arquitetura Limpa e a precisão do modelo matemático, estabelecemos os seguintes pré-requisitos e fluxos de trabalho.

## 1. Ferramentas e Stack Base
Antes de iniciar a codificação, certifique-se de ter o seguinte ambiente preparado:
* **Python 3.11 ou superior:** Versão mínima exigida para garantir compatibilidade com as tipagens avançadas e recursos internos.
* **Git:** Para o controle de versão e submissão de código.
* **IDE Recomendada:** Visual Studio Code (com extensões para Python e suporte a testes) ou PyCharm.

## 2. Configuração do Ambiente Local de Desenvolvimento
Nunca instale as dependências do projeto globalmente no seu sistema operacional. Siga o fluxo de isolamento:

```bash
# 1. Faça o Fork do repositório para a sua conta do GitHub e clone localmente
git clone [https://github.com/SEU_USUARIO/Inspetor_IFF_BJI.git](https://github.com/SEU_USUARIO/Inspetor_IFF_BJI.git)
cd Inspetor_IFF_BJI

# 2. Crie e ative o ambiente virtual (Venv)
# No Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências de desenvolvimento
pip install -r requirements.txt

```

## 3. Diretrizes de Engenharia

Para que uma contribuição (Pull Request) seja aprovada, ela deve estar estritamente alinhada com as fundações arquiteturais do projeto:

* **Arquitetura Limpa (Clean Architecture):** O projeto separa rigidamente as Regras de Negócio da Aplicação (`core/`) dos Detalhes de Implementação (`infrastructure/`). 
>[!WARNING] Alerta 
    Nunca importe bibliotecas externas (como geradores de interface ou bancos de dados específicos) dentro da camada `core`.
* **Cultura de Testes (Pytest):** A qualidade matemática do simulador é inegável. Qualquer nova funcionalidade, alteração de equação ou entidade de domínio deve ser obrigatoriamente acompanhada de seus respectivos testes unitários na diretoria `test/`. Antes de qualquer submissão, execute o comando `pytest` na raiz, a suíte de testes deve passar com 100% de sucesso.
* **Padrões de Código (PEP-8):** O código Python submetido deve seguir as diretrizes oficiais de estilo (nomenclatura de classes em *PascalCase*, funções e variáveis em *snake_case*, além de *docstrings* claras para métodos complexos). Consulte a nossa documentação interna sobre [Padrões e Nomenclatura](docs/processo/nomenclatura-pep8.md).

## 4. Fluxo de Submissão (Pull Request)

1. Certifique-se de estar com a branch `develop` atualizada.
2. Crie uma *branch* semântica e isolada para a sua alteração (ex: `git checkout -b feature/novo-fator-de-decaimento` ou `fix/correcao-calculo-exatidao`).
3. Realize *commits* atômicos e com mensagens descritivas claras.
4. Envie as alterações para o seu repositório bifurcado (Fork).
5. Abra um **Pull Request (PR)** no repositório original detalhando o que foi alterado, qual problema foi resolvido e anexando os resultados dos testes locais.


