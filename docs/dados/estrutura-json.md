# Estrutura de Dados JSON dos Cenários

---

## 1. Visão Geral e Propósito

Os cenários (relatórios de inspeção) do simulador são definidos em arquivos JSON na pasta `resources/data/`. Hoje todos estão em `resources/data/cenarios.json`.

Cada arquivo contém uma **lista de cenários**. O `RepositorioJSON` lê todos os arquivos `*.json` da pasta, valida cada um contra um schema e converte os cenários em objetos que a aplicação transforma em entidades de domínio. Esta abordagem garante:

- **Separação** entre definição de dados (JSON) e lógica de negócio (código);
- **Escalabilidade**: novos cenários entram sem alteração do código-fonte;
- **Validação centralizada** por um contrato de dados rígido.

Desenvolvedores e *Level Designers* devem seguir este modelo ao criar cenários. A classificação de dificuldade está em [Level Design](../game-design/level-design.md).

---

## 2. Estrutura Base

A raiz do arquivo é **sempre uma lista** (`[...]`), mesmo que contenha um único cenário:

```json
[
  {
    "id_cenario": "int",
    "titulo": "string",
    "dificuldade": "int",
    "relatorio": {
      "atividade": "string",
      "local": "string",
      "envolvidos": ["string"],
      "texto_descricao": "string",
      "riscos": ["string"],
      "fatores_inseguranca": ["string"],
      "decisao_administrativa": {
        "decisao_otima": "string",
        "decisao_boa": "string"
      },
      "curso": ["string"]
    },
    "anexos": [
      {
        "id_anexo": "int",
        "tipo": "string",
        "caminho_arquivo": "string"
      }
    ]
  }
]
```

**Regras estruturais:**

- Todas as chaves mostradas acima são **obrigatórias**.
- **Chaves extras não são aceitas** em nenhum nível: uma chave fora do modelo faz o arquivo ser rejeitado.
- A lista da raiz não pode estar vazia.

---

## 3. Dicionário de Dados e Regras de Negócio

### Raiz do cenário

| Chave | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id_cenario** | `int` | Identificador numérico do cenário. | Inteiro maior ou igual a 1. Deve ser único entre todos os cenários (a unicidade não é verificada pelo sistema). |
| **titulo** | `string` | Nome exibido na barra de título da janela de inspeção. | Não vazio. |
| **dificuldade** | `int` | Nível de dificuldade. Multiplica a pontuação máxima do cenário (Vmax). | `1` a `5`. |
| **relatorio** | objeto | Conteúdo e gabarito do cenário. | Ver abaixo. |
| **anexos** | lista | Evidências de mídia. | Pode ser uma lista vazia (`[]`). |

### Objeto `relatorio`

| Chave | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **atividade** | `string` | Atividade ou processo inspecionado. | Texto livre. |
| **local** | `string` | Local físico da inspeção. | Texto livre. |
| **envolvidos** | `string[]` | Pessoas ou grupos envolvidos. Cada item soma pontos ao Vmax. | Ao menos 1 item. |
| **texto_descricao** | `string` | Narrativa apresentada ao jogador. | Texto livre. |
| **riscos** | `string[]` | Riscos presentes no cenário (gabarito). | Ao menos 1 item. Valores: `FISICO`, `QUIMICO`, `BIOLOGICO`, `ERGONOMICO`, `ACIDENTE`. |
| **fatores_inseguranca** | `string[]` | Causas do risco (gabarito). | Ao menos 1 item. Valores: `ATO_INSEGURO`, `CONDICAO_INSEGURA`. |
| **decisao_administrativa** | objeto | Decisões pontuáveis. | Ver abaixo. |
| **curso** | `string[]` | Cursos aos quais o cenário se aplica. | Ao menos 1 item. Ver a seção de cursos. |

> **Cenário sem riscos:** o motor de pontuação prevê o caso de um cenário seguro (gabarito sem riscos ou sem fatores), descrito em [Modelagem matemática](../game-design/modelagem-matematica.md). O schema atual, porém, exige ao menos um risco e um fator, de modo que esse tipo de cenário ainda não pode ser cadastrado.

**Riscos:**
- **FISICO:** agentes físicos (ruído, vibração, radiação, temperatura extrema);
- **QUIMICO:** exposição a substâncias químicas perigosas (ácidos, bases, tóxicos, vapores);
- **BIOLOGICO:** contato com agentes biológicos (bactérias, vírus, fungos, parasitas);
- **ERGONOMICO:** postura inadequada, movimentos repetitivos ou sobrecarga física;
- **ACIDENTE:** risco de traumatismo direto (quedas, cortes, esmagamentos).

**Fatores de insegurança:**
- **ATO_INSEGURO:** comportamento ou decisão humana que contribuiu para o risco (não usar EPI, ignorar procedimento);
- **CONDICAO_INSEGURA:** falha no ambiente, equipamento ou sistema (máquina sem proteção, piso molhado, ventilação ineficiente).

### Objeto `decisao_administrativa`

| Chave | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| **decisao_otima** | `string` | Ação mais apropriada. Vale 25% do Vmax. | `ADVERTIR`, `INTERDITAR`, `IGNORAR` |
| **decisao_boa** | `string` | Ação alternativa aceitável. Vale 12,5% do Vmax. | `ADVERTIR`, `INTERDITAR`, `IGNORAR` |

**Ações:**
- **ADVERTIR:** orientar e notificar sobre o risco, exigindo conformidade com as normas;
- **INTERDITAR:** suspender a atividade até que o risco seja eliminado;
- **IGNORAR:** considerar que não há risco que justifique ação.

**Restrição:** `decisao_otima` e `decisao_boa` **não podem ter o mesmo valor**. Essa regra não está no schema; é validada pela entidade `FolhaDeGabarito`, e um cenário que a viole é descartado na carga, com registro no log.

### Lista `curso`

| Valor | Curso |
|-------|-------|
| `DEFAULT` | Perfil padrão (ver regra abaixo) |
| `T_QUIMICA` | Técnico em Química |
| `T_INFORMATICA` | Técnico em Informática |
| `T_AGROPECUARIA` | Técnico em Agropecuária |
| `T_ALIMENTOS` | Técnico em Alimentos |
| `T_MEIO_AMBIENTE` | Técnico em Meio Ambiente |
| `T_ZOOTECNIA` | Técnico em Zootecnia |
| `CT_ALIMENTOS` | Ciência e Tecnologia de Alimentos |
| `E_COMPUTACAO` | Engenharia de Computação |

**Como o filtro por curso funciona:**

- Um cenário é oferecido a um perfil quando o identificador do perfil aparece na lista `curso` do cenário.
- O perfil `DEFAULT` é a exceção: ele recebe **todos** os cenários, independentemente da lista.
- Um cenário marcado apenas com `["DEFAULT"]` só é oferecido ao perfil `DEFAULT`.
- A lista pode ter vários valores (ex.: `["T_QUIMICA", "CT_ALIMENTOS"]` para um cenário compartilhado).

> **Situação atual:** os 12 cenários existentes estão marcados como `["DEFAULT"]`. Por isso o `GameManager` redireciona temporariamente qualquer perfil escolhido para `DEFAULT`. Quando houver cenários por curso, esse redirecionamento será removido e o filtro acima passará a valer para todos os perfis.

### Lista `anexos`

| Chave | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id_anexo** | `int` | Identificador do anexo. | Inteiro não negativo. Deve ser único (a unicidade não é verificada pelo sistema). |
| **tipo** | `string` | Tipo de mídia. Define o player e o bônus no Vmax (imagem +100, áudio +200, vídeo +300). | `IMAGEM`, `VIDEO`, `AUDIO` |
| **caminho_arquivo** | `string` | Caminho do arquivo de mídia, relativo à raiz do projeto. | Não vazio. Ex.: `resources/anexos/videos/arquivo.mp4`. |

As mídias ficam em `resources/anexos/`, em subpastas por tipo. Hoje existe `resources/anexos/videos/`.

---

## 4. Exemplo Completo

Arquivo com um cenário:

```json
[
  {
    "id_cenario": 2,
    "titulo": "Inspeção: Laboratório de Química",
    "dificuldade": 4,
    "relatorio": {
      "atividade": "Manipulação de reagentes e soluções ácidas",
      "local": "Laboratório de Química - Bloco C",
      "envolvidos": [
        "Professor orientador",
        "Alunos do 2º ano do Ensino Médio Técnico"
      ],
      "texto_descricao": "Durante a aula prática, observou-se que alunos manuseavam frascos de ácido clorídrico sem o uso de óculos de proteção e luvas adequadas. Além disso, a capela de exaustão encontrava-se com o motor desligado, permitindo o acúmulo e dispersão de vapores tóxicos no ambiente.",
      "riscos": [
        "QUIMICO",
        "ACIDENTE"
      ],
      "fatores_inseguranca": [
        "ATO_INSEGURO",
        "CONDICAO_INSEGURA"
      ],
      "decisao_administrativa": {
        "decisao_otima": "INTERDITAR",
        "decisao_boa": "ADVERTIR"
      },
      "curso": [
        "T_QUIMICA",
        "CT_ALIMENTOS"
      ]
    },
    "anexos": [
      {
        "id_anexo": 201,
        "tipo": "VIDEO",
        "caminho_arquivo": "resources/anexos/videos/capela_desligada.mp4"
      }
    ]
  }
]
```

**Análise do exemplo:**
- Dificuldade 4: o Vmax do cenário é multiplicado por 4;
- Dois riscos: químico (vapores) e de acidente (lesões);
- Dois fatores: ato inseguro (falta de EPI) e condição insegura (equipamento desligado);
- A ação ótima é **INTERDITAR**, pois o risco é crítico e imediato; **ADVERTIR** é a alternativa aceitável;
- O cenário é oferecido aos perfis `T_QUIMICA`, `CT_ALIMENTOS` e `DEFAULT`.

---

## 5. Como o Sistema Reage a Erros

| Problema | Comportamento |
|----------|---------------|
| Pasta `resources/data/` ausente ou sem arquivos `.json` | `FileNotFoundError`; o expediente não inicia |
| Sintaxe JSON inválida | `ValueError` identificando o arquivo; o expediente não inicia |
| Raiz que não é uma lista, ou lista vazia | `TypeError` ou `ValueError`; o expediente não inicia |
| Chave obrigatória ausente ou chave extra | `KeyError`; o expediente não inicia |
| Tipo errado ou valor fora dos enumerados | `TypeError` ou `ValueError`; o expediente não inicia |
| `decisao_otima` igual a `decisao_boa`, ou outra regra de entidade violada | O cenário é descartado, com erro no log; os demais são carregados |
| Arquivo de mídia inexistente | Aviso no log; o anexo aparece sem conteúdo |

**Um único arquivo inválido impede o carregamento de todos os cenários**, inclusive os de outros arquivos da pasta. Quando o expediente não inicia, o jogo exibe a mensagem de erro e volta ao menu.

---

## 6. Diretrizes de Criação

### 6.1. Maiúsculas e acentos

A validação do schema compara os valores enumerados **exatamente**.

❌ **Erros comuns:**
- `"Quimico"` em vez de `"QUIMICO"`
- `"químico"` (com acento) em vez de `"QUIMICO"`
- `" QUIMICO "` (com espaços)
- `"advertir"` em vez de `"ADVERTIR"`

✅ **Regra:** valores de riscos, fatores, decisões, cursos e tipos de anexo sempre em **MAIÚSCULAS** e **sem acentos**.

### 6.2. Sintaxe JSON

❌ **Erros frequentes:**
- Vírgula sobrando no último elemento: `["FISICO", "QUIMICO",]`
- Aspas simples em vez de duplas: `'ADVERTIR'`
- Quebra de linha literal dentro de um texto
- Chaves ou colchetes desbalanceados

### 6.3. Caminhos de mídia

A existência do arquivo em `caminho_arquivo` não é verificada na carga dos cenários.

✅ **Boas práticas:**
- Usar caminhos relativos à raiz do projeto (ex.: `resources/anexos/videos/cenario_01.mp4`). Eles são resolvidos a partir do diretório em que o jogo é iniciado, por isso execute `python main.py` na raiz;
- Usar `/` como separador, mesmo no Windows;
- Manter nomes de arquivo simples, sem espaços nem caracteres especiais;
- Conferir se o arquivo existe no caminho informado.

### 6.4. Checklist antes de enviar um cenário

1. A raiz do arquivo é uma lista e não há chaves fora do modelo;
2. Os valores enumerados estão exatamente como neste documento;
3. `riscos`, `fatores_inseguranca`, `envolvidos` e `curso` têm ao menos um item;
4. `decisao_otima` é diferente de `decisao_boa`;
5. Os arquivos de `anexos` existem;
6. Os testes passam (`pytest`);
7. O cenário abre no jogo e exibe os dados e a mídia corretamente. Como cada expediente sorteia `QUANTIDADE_GERACAO` cenários (`config/constants.py`, atualmente 1), aumente esse valor temporariamente para ver o seu cenário com mais facilidade.

### 6.5. Versionamento

- O histórico do Git é o registro de mudanças dos cenários: descreva alterações relevantes na mensagem de commit;
- Evite alterar o `id_cenario` de cenários já publicados.
