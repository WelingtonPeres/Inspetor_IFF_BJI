# Documentação Oficial da Estrutura de Dados JSON
## Simulador Gamificado de Inspeção de Segurança do Trabalho

---

## 1. Visão Geral e Propósito

A estrutura de dados JSON descrita neste documento serve como **fonte de verdade centralizada** para a criação e definição de todos os cenários (níveis) do simulador de inspeção de Segurança do Trabalho. 

Cada arquivo JSON representa uma inspeção completa e deve ser consumido pelo módulo `RepositorioJSON` da aplicação, responsável pela desserialização automática dos dados em objetos de domínio. Esta abordagem garante:

- **Separação clara** entre definição de dados (JSON) e lógica de negócio (código);
- **Escalabilidade** ao permitir adicionar novos cenários sem modificação do código fonte;
- **Validação centralizada** através de um contrato de dados rígido;
- **Rastreabilidade** de todas as inspeções e suas regras associadas.

Desenvolvedores e *Level Designers* devem seguir rigorosamente este modelo ao criar novos cenários para garantir compatibilidade e funcionamento correto da aplicação.

---

## 2. JSON Schema — Estrutura Base

O modelo estrutural genérico abaixo define o esqueleto que **todos** os cenários devem respeitar:

```json
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
      "acao_otima": "string",
      "acao_subotima": "string"
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
```

**Notas sobre tipos de dados:**
- `int` — número inteiro sem casas decimais;
- `string` — texto entre aspas duplas (`"`);
- `[...]` — array (lista ordenada de elementos do mesmo tipo);
- `{...}` — objeto JSON (conjunto de pares chave-valor).

---

## 3. Dicionário de Dados e Regras de Negócio

A tabela a seguir descreve cada atributo, seu tipo, propósito e restrições:

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos / Restrições |
|-------|------|-------------|-----------|-------------------------------|
| **id_cenario** | `int` | Sim | Identificador único numérico do cenário. Funciona como chave primária no sistema. | Número inteiro positivo. Deve ser único em toda a aplicação. |
| **titulo** | `string` | Sim | Nome de exibição do cenário na interface gráfica. | Qualquer texto descritivo (sem restrições especiais). |
| **dificuldade** | `int` | Sim | Nível de dificuldade da inspeção. Funciona como multiplicador para cálculos de pontuação máxima (Vmax) e tempo ideal. | `1`, `2`, `3`, `4` ou `5` apenas. |

### Objeto `relatorio`

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos / Restrições |
|-------|------|-------------|-----------|-------------------------------|
| **atividade** | `string` | Sim | Descrição da atividade ou processo que foi inspecionado. | Texto descritivo livre. |
| **local** | `string` | Sim | Local físico onde a inspeção ocorreu. | Texto descritivo livre. |
| **envolvidos** | `string[]` | Sim | Lista de pessoas ou grupos envolvidos na inspeção. | Array de strings. Pode conter uma ou várias pessoas/grupos. |
| **texto_descricao** | `string` | Sim | Texto narrativo base que apresenta o cenário, as observações e o contexto da inspeção ao jogador. | Texto descritivo livre, sem limite de caracteres. |
| **curso** | `string[]` | Sim | Array de cursos para os quais este cenário é aplicável. Permite segmentação de conteúdo por modalidade de formação. | `DEFAULT`, `T_QUIMICA`, `T_INFORMATICA`, `T_AGROPECUARIA`, `T_ALIMENTOS`, `T_MEIO_AMBIENTE`, `T_ZOOTECNIA`, `CT_ALIMENTOS`, `E_COMPUTACAO`. O valor `DEFAULT` representa disponibilidade para todos os cursos. |

### Seção de Riscos e Fatores de Insegurança

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos |
|-------|------|-------------|-----------|-----------------|
| **riscos** | `string[]` | Sim | Array de riscos identificados durante a inspeção. | `FISICO`, `QUIMICO`, `BIOLOGICO`, `ERGONOMICO`, `ACIDENTE` |
| **fatores_inseguranca** | `string[]` | Sim | Array de categorias de fatores causadores do risco. | `ATO_INSEGURO`, `CONDICAO_INSEGURA` |

**Explicação dos Riscos:**
- **FISICO:** Riscos relacionados a agentes físicos (barulho, vibrações, radiação, temperatura extrema, etc.);
- **QUIMICO:** Exposição a substâncias químicas perigosas (ácidos, bases, tóxicos, vapores);
- **BIOLOGICO:** Contato com agentes biológicos (bactérias, vírus, fungos, parasitas);
- **ERGONOMICO:** Inadequação de posturas, movimentos repetitivos ou sobrecarga física;
- **ACIDENTE:** Risco de traumatismos diretos (quedas, cortes, esmagamentos, etc.).

**Explicação dos Fatores de Insegurança:**
- **ATO_INSEGURO:** Comportamento ou decisão humana que contribuiu para o risco (não usar EPI, ignorar procedimento, etc.);
- **CONDICAO_INSEGURA:** Falha no ambiente, equipamento ou sistema que criou o risco (máquina sem proteção, piso molhado, ventilação ineficiente, etc.).

### Seção de Decisão Administrativa

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos |
|-------|------|-------------|-----------|-----------------|
| **acao_otima** | `string` | Sim | Ação mais apropriada a ser tomada diante do risco identificado. | `ADVERTIR`, `INTERDITAR`, `IGNORAR` |
| **acao_subotima** | `string` | Sim | Ação alternativa (menos apropriada) que também é válida. | `ADVERTIR`, `INTERDITAR`, `IGNORAR` |

**Explicação das Ações:**
- **ADVERTIR:** Orientar e notificar sobre o risco, exigindo conformidade com as normas;
- **INTERDITAR:** Suspender imediatamente a atividade até que o risco seja eliminado;
- **IGNORAR:** Considerar o risco como aceitável ou negligenciável em contexto específico.

**Restrição Crítica:** `acao_otima` e `acao_subotima` **nunca podem conter o mesmo valor** no mesmo cenário. Esta distinção garante a distribuição correta de pontos na rubrica de avaliação (25% para ação ótima, 12,5% para ação subótima).

### Seção de Cursos

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos |
|-------|------|-------------|-----------|-----------------|
| **curso** | `string[]` | Sim | Array de cursos para segmentação de cenários por modalidade de formação. | Ver tabela de valores abaixo. |

**Valores Aceitos e Significado das Abreviaturas:**

| Valor | Significado | Descrição |
|-------|------------|----------|
| `DEFAULT` | Padrão / Todos | Representa disponibilidade para **todos os cursos**. Use este valor como fallback quando o cenário é genérico e aplicável universalmente. |
| `T_QUIMICA` | **T**écnico em Química | Cenários específicos para alunos do curso Técnico em Química. |
| `T_INFORMATICA` | **T**écnico em Informática | Cenários específicos para alunos do curso Técnico em Informática. |
| `T_AGROPECUARIA` | **T**écnico em Agropecuária | Cenários específicos para alunos do curso Técnico em Agropecuária. |
| `T_ALIMENTOS` | **T**écnico em Alimentos | Cenários específicos para alunos do curso Técnico em Alimentos. |
| `T_MEIO_AMBIENTE` | **T**écnico em Meio Ambiente | Cenários específicos para alunos do curso Técnico em Meio Ambiente. |
| `T_ZOOTECNIA` | **T**écnico em Zootecnia | Cenários específicos para alunos do curso Técnico em Zootecnia. |
| `CT_ALIMENTOS` | **C**iência e **T**ecnologia em Alimentos | Cenários específicos para alunos do curso de Ciência e Tecnologia em Alimentos. |
| `E_COMPUTACAO` | **E**ngenharia em Computação | Cenários específicos para alunos do curso de Engenharia de Computação. |

**Regras para o Campo `curso`:**
- O array **pode conter um ou múltiplos valores** (ex: `["T_QUIMICA", "CT_ALIMENTOS"]` para um cenário compartilhado);
- Se um cenário é exclusivamente para um curso, use apenas um valor no array;
- Não misture `DEFAULT` com outros valores no mesmo array (ex: `["DEFAULT", "T_QUIMICA"]` é redundante);
- Sempre use **MAIÚSCULAS** e **sem acentos**, exatamente como especificado acima.

### Objeto `anexos` (Array de Evidências)

| Chave | Tipo | Obrigatório | Descrição | Valores Aceitos / Restrições |
|-------|------|-------------|-----------|-------------------------------|
| **id_anexo** | `int` | Sim | Identificador único do anexo dentro do cenário. | Número inteiro positivo. Deve ser único dentro do array `anexos`. |
| **tipo** | `string` | Sim | Classificação do tipo de mídia. | `IMAGEM`, `VIDEO` |
| **caminho_arquivo** | `string` | Sim | Caminho relativo do arquivo de mídia a partir da raiz da aplicação. | Caminho válido no formato `pasta/subpasta/arquivo.extensao`. |

---

## 4. Exemplo Prático Completo

O cenário a seguir ilustra a implementação correta de uma inspeção em ambiente de laboratório:

```json
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
      "acao_otima": "INTERDITAR",
      "acao_subotima": "ADVERTIR"
    },
    "curso": [
      "T_QUIMICA",
      "CT_ALIMENTOS"
    ]
  },
  "anexos": [
    {
      "id_anexo": 201,
      "tipo": "IMAGEM",
      "caminho_arquivo": "midia/imagens/lab_quimica_capela_desligada.png"
    }
  ]
}
```

**Análise do Exemplo:**
- O cenário possui dificuldade nível 4, indicando elevada complexidade na identificação de riscos;
- Dois riscos foram identificados: um de natureza química (vapores) e outro de acidente potencial (lesões);
- Ambos os fatores aparecem: ato inseguro (falta de EPI) e condição insegura (equipamento desligado);
- A ação ótima é **INTERDITAR** (ação mais severa), pois o risco é crítico e imediato;
- A ação subótima é **ADVERTIR** (ação menos severa), aceitável apenas se o equipamento for ativado imediatamente;
- Uma imagem de evidência é anexada ao cenário.

---

## 5. Diretrizes de Integração e Cuidados

Ao criar ou modificar cenários JSON, respeite rigorosamente as seguintes diretrizes para evitar erros críticos, falhas de desserialização e comportamentos inesperados:

### 5.1 Case-Sensitivity (Sensibilidade a Maiúsculas/Minúsculas)

O parser de validação da aplicação diferencia **rigorosamente** maiúsculas de minúsculas. 

❌ **Exemplos de erros comuns:**
- `"Quimico"` em vez de `"QUIMICO"` 
- `"químico"` (com acento) em vez de `"QUIMICO"`
- `" QUIMICO "` (com espaços extras)
- `"advertir"` (minúsculas) em vez de `"ADVERTIR"`

✅ **Regra:** Use sempre **MAIÚSCULAS** e **sem acentos** para os valores enumerados (riscos, fatores, ações), exatamente como especificado neste documento.

### 5.2 Sintaxe JSON Estrita

JSON é um formato rígido que não perdoa erros de sintaxe:

❌ **Erros frequentes:**
- Vírgula sobrando no último elemento: `["FISICO", "QUIMICO",]`
- Aspas simples em vez de duplas: `'ADVERTIR'` ao invés de `"ADVERTIR"`
- Caractere não escapado em strings: quebra de linha literal dentro de um texto
- Chaves ou colchetes desbalanceados

✅ **Verificação:** Antes de enviar um JSON para produção, valide-o através de um validador online genérico (ex: jsonlint.com) ou manualmente verificando a correspondência de todas as chaves e colchetes.

### 5.3 Integridade de Caminhos (Path Validation)

O campo `caminho_arquivo` não é verificado automaticamente pelo sistema. Erros de digitação resultarão em:
- Quadros em branco na interface gráfica;
- Falhas silenciosas ao carregar mídia;
- Exceções não capturadas em certas condições.

✅ **Boas práticas:**
- Use caminhos **relativos** à pasta raiz da aplicação (ex: `midia/imagens/cenario_01.png`);
- Verifique manualmente se o arquivo existe no caminho especificado;
- Use separadores `/` (barra) em vez de `\` (contrabarra), mesmo no Windows;
- Mantenha nomes de arquivos simples, sem espaços ou caracteres especiais;
- Documente a estrutura de pastas de mídia em um arquivo `README.md` dedicado.

### 5.4 Consistência Lógica das Decisões Administrativas

A distinção entre `acao_otima` e `acao_subotima` é **fundamental** para o algoritmo de pontuação:

❌ **Erro crítico:**
```json
"decisao_administrativa": {
  "acao_otima": "INTERDITAR",
  "acao_subotima": "INTERDITAR"
}
```

✅ **Correto:**
```json
"decisao_administrativa": {
  "acao_otima": "INTERDITAR",
  "acao_subotima": "ADVERTIR"
}
```

**Impacto:** Se ambas as ações forem iguais, a distribuição percentual de pontos será corrompida (não haverá gradação entre resposta correta e subótima), afetando a justiça e o equilíbrio do jogo.

### 5.5 Validação e Testes

Antes de incluir um novo cenário na aplicação principal:

1. **Valide o JSON:** Use um validador JSON online ou um linter local;
2. **Verifique os Enums:** Confirme que todos os valores enumerados (riscos, fatores, ações) estão exatamente como especificado;
3. **Teste os Caminhos:** Garanta que todos os arquivos em `anexos` existem e são acessíveis;
4. **Revise a Lógica:** Confirme que `acao_otima ≠ acao_subotima`;
5. **Teste na Aplicação:** Carregue o cenário na aplicação e valide que a interface exibe corretamente todos os dados e mídia.

### 5.6 Versionamento e Manutenção

- Mantenha um histórico de versões dos arquivos JSON (use Git);
- Documente alterações significativas em um arquivo `CHANGELOG.md`;
- Evite modificar o `id_cenario` de cenários já publicados (quebra referências externas);
- Ao descontinuar um cenário, marque-o como archived em vez de deletar.

---

## Conclusão

A estrutura JSON aqui documentada é o contrato fundamental entre o sistema de armazenamento de dados e a lógica de negócio do simulador. Sua correta implementação garante:

- ✅ Funcionamento confiável da aplicação;
- ✅ Facilidade de manutenção e extensão;
- ✅ Experiência consistente para o usuário final;
- ✅ Conformidade com os padrões de qualidade do projeto.

Distribua este documento aos membros da equipe responsáveis pela criação de novos cenários e mantenha-o atualizado conforme evoluções do sistema.

---

**Documento gerado:** 4 de junho de 2026  

