# Padrões de Nomenclatura - Inspetor IFF BJI

## Visão Geral

Este documento estabelece os padrões de nomenclatura para todo o projeto **Inspetor IFF BJI**, seguindo rigorosamente o **PEP 8** (Python Enhancement Proposal 8) - o guia oficial de estilo do Python.

Aderir a estes padrões é fundamental para:
- ✅ Manter o código legível e profissional
- ✅ Facilitar a manutenção e contribuição de novos desenvolvedores
- ✅ Evitar bugs relacionados a inconsistências de nomenclatura
- ✅ Demonstrar maturidade e respeito aos padrões da comunidade global Python


## 1. Classes (PascalCase / CapWords)

### Regra
O nome de uma classe deve começar com letra **maiúscula**, e cada palavra subsequente também deve ter a primeira letra **maiúscula**, sem espaços ou underlines.

### Padrão
```
PascalCase (CapWords)
```

### ✅ Exemplos Corretos
```python
class Relatorio:
    pass

class FolhaDeInspecao:
    pass

class DiagnosticoDeResposta:
    pass

class MotorDePontuacao:
    pass

class FabricaDeRelatorios:
    pass

class RepositorioJSON:
    pass

class AnexoImagem:
    pass
```

### ❌ Exemplos Incorretos
```python
class relatorio:          # Começa com minúscula
    pass

class folha_de_inspecao:  # Usa snake_case (padrão Java/C#)
    pass

class ANALISADOR:         # Usa UPPER_SNAKE_CASE (reservado para constantes)
    pass
```

## 2. Variáveis (snake_case)

### Regra
As variáveis devem ser escritas **inteiramente em letras minúsculas**. Se o nome tiver mais de uma palavra, elas devem ser separadas por um **underline (_)**.

### Padrão
```
snake_case
```

### ✅ Exemplos Corretos
```python
id_cenario = 42
pontuacao_total = 100
riscos_marcados = ["Físico", "Químico"]
texto_descricao = "Descrição do cenário"
lista_relatorios = []
tempo_gasto_segundos = 120
```

### ❌ Exemplos Incorretos
```python
idCenario = 42                    # camelCase (padrão Java)
PontuacaoTotal = 100              # PascalCase (padrão Java)
RiscosMarçados = ["Físico"]       # PascalCase
RISCOS_MARCADOS = []              # UPPER_SNAKE_CASE (reservado para constantes)
```

## 3. Métodos e Funções (snake_case)

### Regra
Seguem exatamente a mesma regra das variáveis. Tudo em **minúsculo**, separado por **underlines**.

### Padrão
```
snake_case
```

### ✅ Exemplos Corretos
```python
def calcular_pontuacao(relatorio):
    """Calcula a pontuação do relatório."""
    pass

def extrair_apresentacao_relatorio(self):
    """Extrai dados de apresentação do relatório."""
    pass

def verificar_condicao_vitoria(pontuacao):
    """Verifica se o jogador ganhou."""
    pass

def adicionar_anexo(self, anexo):
    """Adiciona um anexo ao relatório."""
    pass

def obter_anexos(self):
    """Retorna a lista de anexos."""
    pass

def buscar_dados_relatorios(self, perfil, quantidade):
    """Busca dados de relatórios no JSON."""
    pass
```

### ❌ Exemplos Incorretos
```python
def calcularPontuacao(relatorio):         # camelCase
    pass

def CalcularPontuacao(relatorio):         # PascalCase
    pass

def CALCULAR_PONTUACAO(relatorio):        # UPPER_SNAKE_CASE
    pass

def extrairApresentacaoRelatorio(self):   # camelCase
    pass
```


## 4. Atributos de Classe e Encapsulamento

### Regra
Os atributos também seguem o **snake_case**, mas o Python usa uma convenção visual com **underlines** para simular o comportamento de atributos públicos, protegidos e privados (já que o Python não tem as palavras-chave `public`, `protected` ou `private` nativamente).

### Padrão: Atributo Público (snake_case)
```python
self.titulo              # Qualquer parte do sistema pode ler e alterar
self.envolvidos          # Atributo público
self.dificuldade         # Atributo público
```

### ✅ Exemplos Corretos - Públicos
```python
class Relatorio:
    def __init__(self, titulo, envolvidos):
        self.titulo = titulo
        self.envolvidos = envolvidos
        self.dificuldade = 1
```

### Padrão: Atributo "Protegido" / Uso Interno (_snake_case)
```python
self._id_cenario         # UM underline na frente
self._anexos             # Indica atributo protegido
self._folha_gabarito     # Uso interno apenas
```

**Significado:** É um aviso para os outros programadores: *"Por favor, não altere ou acesse esta variável diretamente de fora da classe. Use um método para isso (como um `@property`)."*

### ✅ Exemplos Corretos - Protegidos
```python
class Relatorio:
    def __init__(self, id_cenario, anexos):
        self.__id_cenario = id_cenario
        self.__anexos = anexos
        self.__folha_gabarito = None
        self.__folha_resposta = None
    
    # Acesso controlado via property
    @property
    def id_cenario(self) -> int:
        return self.__id_cenario
    
    @property
    def anexos(self) -> List[Anexo]:
        return self.__anexos
    
    def adicionar_anexo(self, anexo: Anexo):
        """Método para modificar a lista protegida."""
        self.__anexos.append(anexo)
```

### Padrão: Atributo "Privado" (Name Mangling) (__snake_case)
```python
self.__senha             # DOIS underlines na frente
```

**Significado:** O interpretador do Python vai ativamente renomear esta variável nos bastidores para dificultar muito que ela seja acessada por fora ou sobrescrita por herança. Geralmente, usamos apenas um underline (_) na maioria das arquiteturas.

### ✅ Exemplos Corretos - Privados (raros)
```python
class Usuario:
    def __init__(self, nome, senha):
        self.__senha = senha  # Realmente privado
        self._nome = nome     # Protegido (mais comum)
```

## 5. Constantes (UPPER_SNAKE_CASE)

### Regra
Se você tem um valor que **nunca deve mudar** durante a execução do programa, deve usar **tudo em maiúsculo**, separado por **underline**.

### Padrão
```
UPPER_SNAKE_CASE
```

### ✅ Exemplos Corretos
```python
class MotorDePontuacao:
    # Calibragem matemática
    PESO_RISCOS = 0.60
    PESO_FATORES = 0.15
    PESO_DECISAO_OTIMA = 0.25
    PESO_DECISAO_BOA = 0.125
    
    # Valores de pontuação
    VALOR_BASE_PARTICIPACAO = 1000
    BONUS_RISCO = 250
    BONUS_FATOR = 250
    BONUS_MIDIA_IMAGEM = 100
    BONUS_MIDIA_VIDEO = 300
    BONUS_CONTEXTO = 100
    
    # Configurações de tempo
    TEMPO_IDEAL_SEGUNDOS = 60
    TAXA_DECAIMENTO_ALFA = 0.01
    LIMITE_MINIMO_RETENCAO = 0.20
    LIMIAR_VITORIA_TURNO = 0.60
```

### ❌ Exemplos Incorretos
```python
VALOR_MAXIMO = 100      # Correto, mas muito genérico
valor_maximo = 100      # Incorreto - parece variável
ValorMaximo = 100       # Incorreto - parece classe
```

## Resumo Visual

```python
class MotorDePontuacao:              # Classe: PascalCase
    
    LIMITE_MINIMO_RETENCAO = 0.5     # Constante: UPPER_SNAKE_CASE

    def __init__(self, taxa: float):
        self.taxa_padrao = taxa      # Atributo Público: snake_case
        self._cache_calculo = {}     # Atributo Protegido: _snake_case
        self.__senha_interna = ""    # Atributo Privado: __snake_case

    def calcular_pontuacao(self):    # Método: snake_case
        pontuacao_final = 100        # Variável: snake_case
        return pontuacao_final
    
    def _metodo_auxiliar(self):      # Método protegido: _snake_case
        pass
```

## Checklist de Implementação

Ao escrever novo código, use este checklist:

- [ ] Todas as **classes** usam **PascalCase**?
- [ ] Todos os **métodos** usam **snake_case**?
- [ ] Todas as **variáveis** usam **snake_case**?
- [ ] Atributos protegidos têm **um underline** (`_atributo`)?
- [ ] Atributos privados têm **dois underlines** (`__atributo`)? (raro)
- [ ] Todas as **constantes** usam **UPPER_SNAKE_CASE**?
- [ ] Não há **camelCase** em métodos ou variáveis?
- [ ] Não há **PascalCase** em variáveis ou funções?

---

##  Referências

- **[PEP 8 - Official Python Style Guide](https://www.python.org/dev/peps/pep-0008/)** - Leitura obrigatória
- **[PEP 3131 - Supporting Non-ASCII Identifiers](https://www.python.org/dev/peps/pep-3131/)** - Para nomes com acentos
- **[Code Style Guide for This Project](./PADROES_NOMENCLATURA_PEP8.md)** - Este documento

---

## 🚨 Aplicação Gradual

Este documento foi aplicado ao projeto no commit de refatoração. Qualquer novo código deve seguir estes padrões **imediatamente**.

Para código legado ainda não refatorado, será feita uma migração gradual mantendo compatibilidade.
