# Arquitetura de Versionamento: Git Flow

Este documento estabelece o padrão de versionamento de código do simulador. O objetivo é garantir que a linha principal de produção esteja sempre estável, enquanto o desenvolvimento de novas funcionalidades ocorre de forma isolada e segura.

## 1. As Branches Eternas (Principais)

Estas duas branches viverão desde o dia zero até ao fim do projeto. Ninguém deve fazer *commits* diretos nelas.

* **`main` :** É o código de Produção. Só recebe código que foi amplamente testado, validado e que está pronto para ser executado. O código aqui nunca está "quebrado".
* **`develop` :** É a linha principal de desenvolvimento. É aqui que todas as novas funcionalidades se encontram pela primeira vez. Reflete o estado mais atualizado do código que está pronto para o próximo lançamento, mas que ainda pode conter instabilidades isoladas.

## 2. As Branches Efêmeras (De Suporte)

Estas branches nascem para um propósito específico e morrem (são apagadas) assim que o trabalho é concluído.

### 🌱 Feature (Novas Funcionalidades)

* **De onde nascem:** `develop`
* **Para onde voltam:** `develop`
* **Nomenclatura:** `feature/nome-da-funcionalidade` (ex: `feature/repositorio-json`, `feature/testes-fabrica`)
* **Propósito:** Isolar o desenvolvimento de uma nova funcionalidade (como criar a `FabricaDeRelatorios`). O desenvolvedor pode estragar, refatorar e testar tudo aqui sem afetar o resto do projeto.

### 🐛 Bugfix (Correções de Baixa Prioridade)

* **De onde nascem:** `develop`
* **Para onde voltam:** `develop`
* **Nomenclatura:** `bugfix/nome-do-erro` (ex: `bugfix/erro-leitura-anexos`)
* **Propósito:** Corrigir erros encontrados na branch `develop` durante o desenvolvimento normal.

### 🔥 Hotfix (A Bomba-Relógio)

* **De onde nascem:** `main`
* **Para onde voltam:** `main` E `develop`
* **Nomenclatura:** `hotfix/nome-do-problema-critico` (ex: `hotfix/crash-ao-abrir-json`)
* **Propósito:** É a sirene de emergência. Se um erro crítico for descoberto no código de Produção (`main`), cria-se um *hotfix* diretamente de lá. A correção é feita rapidamente e fundida de volta na `main` e também na `develop` (para que o erro não volte a acontecer no futuro).

## 3. O Fluxo de Trabalho na Prática

Aqui está o passo a passo exato (os comandos do terminal) para o dia a dia do desenvolvimento:

**Passo 1: Começar uma nova funcionalidade**
Nunca crie a feature a partir do que você acabou de fazer. Vá sempre para ao develop primeiro e garanta que está atualizado.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/minha-nova-classe

```

**Passo 2: O Ciclo de Trabalho (Engenharia Contínua)**
Programe a sua classe, crie os testes (Pytest) e garanta que está tudo a passar. Depois, embrulhe o seu trabalho.

```bash
git add .
git commit -m "feat: cria a estrutura do DTO de cenarios"

```

**Passo 3: Enviar para a Nuvem e Solicitar Revisão**
A sua *feature* está pronta na sua máquina. Agora você envia para o GitHub e junta com a oficina (`develop`).

```bash
git push origin feature/minha-nova-classe

```

*(No GitHub, você clica no botão verde **Compare & Pull Request**. Lê o que fez, aprova a fusão para a branch `develop` e apaga a branch da feature).*

