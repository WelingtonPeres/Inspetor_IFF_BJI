# Especificação do Modelos Matemáticos e Suas Regras de Negócio (Core)

## 1. Introdução

O presente documento detalha a modelagem matemática e a lógica de negócio que fundamentam o núcleo (Core) do simulador de inspeção. O objetivo deste modelo é garantir que a avaliação do jogador seja estritamente determinística, justa e escalável, traduzindo as ações de vistoria em métricas quantificáveis de desempenho.

A arquitetura matemática foi desenhada para coibir estratégias de "chute" (seleção aleatória de opções) e recompensar a precisão técnica e a eficiência temporal do inspetor. Para isso, o sistema afasta-se de somatórios simples e adota conceitos de recuperação de informação, especificamente as métricas de **Revocação (Taxa de Descoberta)** e **Precisão (Assertividade)**, combinadas a uma função de decaimento temporal.

Este documento serve como a fonte de verdade para a implementação dos serviços de domínio, garantindo que o código reflita exatamente as regras do negócio projetadas.

## 2. Modelo de Pontuação de Cenários (Motor de Pontuação)

A pontuação total de cada cenário inspecionado é balizada por uma variável configurável chamada **Valor Base ($V_{max}$)**, que representa a nota máxima (100%) caso o jogador tenha um desempenho perfeito e em tempo ótimo. O cálculo do relatório é fragmentado em três eixos de avaliação:

### 2.1. Diagnóstico de Riscos Ocupacionais (60% do $V_{max}$)

Avalia a capacidade do jogador de classificar corretamente as anomalias ambientais presentes no cenário (Físico, Químico, Biológico, Ergonômico e Acidente), punindo o comportamento de "chute" (marcar opções aleatórias). A nota parcial de riscos ($P_{risco}$) baseia-se em métricas de recuperação de informação:

$$P_{risco} = (V_{max} \times 0.60) \times T_d \times T_p$$

As variáveis operacionais são definidas como:

* **Taxa de Descoberta ($T_d$):** Proporção de riscos reais que o jogador conseguiu encontrar.

$$T_d = \frac{\text{Riscos Corretos Marcados}}{\text{Total de Riscos no Gabarito}}$$


* **Taxa de Precisão ($T_p$):** Nível de assertividade das marcações, penalizando o jogador por assinalar riscos inexistentes.

$$T_p = \frac{\text{Riscos Corretos Marcados}}{\text{Total de Riscos Marcados}}$$


**Tratamento de Exceção (Cenário Seguro):**
Se o cenário for isento de riscos (`Total de Riscos no Gabarito == 0`):

* **Sucesso:** Se o jogador não marcar opções, a nota é integral: $P_{risco} = V_{max} \times 0.60$.
* **Falha:** Se o jogador marcar qualquer opção, a nota é zerada: $P_{risco} = 0$.

### 2.2. Diagnóstico de Fatores de Insegurança (15% do $V_{max}$)

Avalia a capacidade do jogador de identificar a causa raiz do problema ambiental (se derivou de um **Ato Inseguro** do funcionário ou de uma **Condição Insegura** do ambiente). Apenas factores presentes no gabarito são pontuáveis — a ausência correcta de um factor não gera pontos.

A nota parcial de insegurança ($P_{inseg}$) é calculada por:

$$P_{inseg} = (V_{max} \times 0.15) \times C_{exatidao}$$

Onde o coeficiente de Exatidão ($C_{exatidao}$) é a proporção de factores do gabarito que o jogador correctamente identificou, penalizada por invenções (factores marcados sem existirem no gabarito):

* $S_{ato} = 1$ se ATO_INSEGURO está presente **tanto no gabarito quanto na resposta do jogador**; caso contrário $0$.
* $S_{cond} = 1$ se CONDICAO_INSEGURA está presente **tanto no gabarito quanto na resposta do jogador**; caso contrário $0$.
* $g$ = quantidade de factores no gabarito (0, 1 ou 2).
* $m$ = quantidade de factores marcados pelo jogador (0, 1 ou 2).

$$C_{exatidao} = \frac{S_{ato} + S_{cond}}{\max(1, g, m)}$$

**Exemplo:** Se o gabarito possui apenas ATO_INSEGURO ($g = 1$) e o jogador marca apenas ATO_INSEGURO ($m = 1$), então $S_{ato}=1$, $S_{cond}=0$, denominador $= 1$, $C_{exatidao}=1$, e $P_{inseg} = V_{max} \times 0.15$. Se o jogador também inventar CONDICAO_INSEGURA ($m = 2$), o denominador sobe para $2$ e $C_{exatidao}=0.5$, reduzindo a nota para metade — a invenção penaliza o score.

Se o gabarito não tem nenhum factor ($g = 0$), $P_{inseg} = 0$ independentemente das marcações do jogador.


### 2.3. Decisão Administrativa (25% do $V_{max}$)

Avalia a proporcionalidade da ação corretiva tomada pelo técnico em relação ao quadro diagnosticado. A nota ($P_{decisao}$) é atribuída via mapeamento direto com o gabarito de ações do sistema:

* **Ação Ótima (Exata):** $P_{decisao} = V_{max} \times 0.25$
* **Ação Subótima (Excesso ou falta leve de zelo):** $P_{decisao} = V_{max} \times 0.125$
* **Ação Incorreta (Erro Técnico Grave):** $P_{decisao} = 0$

Se o jogador não identifica nenhum risco nem fator ($P_{risco} = 0$ e $P_{inseg} = 0$), a decisão é **anulada**: $P_{decisao} = 0$ mesmo quando a ação escolhida seria pontuável, pois não há diagnóstico que a sustente. O flag de domínio `decisao_anulada` expõe essa condição no `DiagnosticoPontuacaoDTO`.

### 2.4. Fator Tempo (Multiplicador de Decaimento)

O tempo investido na inspeção ($t$) atua como um coeficiente multiplicador $f(t)$ sobre a nota bruta acumulada. Se o jogador resolve dentro do tempo ideal ($T_{ideal}$), retém 100% da nota. Ultrapassado o limite, a nota decai linearmente a uma taxa de rigor $\alpha$, até um limite mínimo de retenção $L_{min}$.

Matematicamente, a função de decaimento de eficiência temporal $f(t)$ é expressa por:

$$f(t) =
\begin{cases} 
1.0, & \text{se } t \le T_{ideal} \\
\max\big(L_{min},\ 1.0 - \alpha \times (t - T_{ideal})\big), & \text{se } t > T_{ideal}
\end{cases}$$

O piso $L_{min}$ garante que a nota nunca caia abaixo de um mínimo garantido, e a função `max` remove a necessidade de um terceiro ramo explícito — assim que o decaimento linear atinge $L_{min}$, o valor congela naturalmente.

### 2.5. Equação Final Consolidada

A Pontuação Total ($PT$) extraída no final da análise do relatório integra todas as variáveis diagnósticas e administrativas submetidas ao fator de eficiência de tempo:

$$PT = (P_{risco} + P_{inseg} + P_{decisao}) \times f(t)$$


## 3. Validação de Desempenho e Condição de Vitória (Expediente)

Enquanto a Seção 2 define o aproveitamento isolado de cada inspeção, o simulador opera em ciclos de jogo chamados **Turnos (ou Expedientes)**. Cada turno é composto por uma pilha de $n$ relatórios (cenários). Para garantir o progresso na campanha do jogo (Tela de Campeão), o jogador deve demonstrar consistência ao longo de todo o expediente.

### 3.1. Cálculo da Pontuação Global do Turno

O Motor de Pontuação calcula dois grandes totalizadores ao final de um turno:

1. **Meta do Turno ($V_{total\_turno}$):** É a soma absoluta de todos os Valores Base ($V_{max}$) dos cenários sorteados para aquele dia. Representa o placar perfeito (100%).

$$V_{total\_turno} = \sum_{i=1}^{n} (V_{max})_i$$


2. **Pontuação Acumulada ($PT_{turno}$):** É o somatório de todas as Pontuações Totais ($PT$) efetivamente obtidas pelo jogador em cada um dos relatórios.

$$PT_{turno} = \sum_{i=1}^{n} (PT)_i$$


### 3.2. Regra de Aprovação (Limiar de 60%)

Para que o sistema considere o expediente bem-sucedido e dispare o gatilho da "Tela de Campeão" (Aprovação), o jogador não precisa gabaritar todos os cenários, mas deve atingir um desempenho global mínimo.

A condição matemática de vitória é dada por:

$$PT_{turno} \ge (V_{total\_turno} \times 0.60)$$

**Desdobramentos da Regra de Negócio:**

* **Aprovação (>= 60%):** O jogador demonstrou competência técnica suficiente. O `GerenciadorDeTurno` encerra o dia com sucesso.
* **Reprovação (< 60%):** O jogador cometeu demasiados erros de diagnóstico ou agiu de forma desproporcional. O sistema barra o avanço, apresenta a "Tela de Falha".

## 4. Escalonamento Dinâmico de Pontuação ($V_{max}$)

Para garantir uma recompensa justa e proporcional ao esforço cognitivo do jogador, o Valor Base absoluto de um cenário ($V_{max}$) é calculado em tempo de execução. Diferente do Tempo Ideal ($T_{ideal}$), que se mantém constante para padronizar o ritmo do expediente, o $V_{max}$ é uma composição de um valor fixo de participação acrescido de bônus quantitativos (elementos contáveis no relatório) e multiplicado pela Gravidade da cena.

### 4.1. Elementos Quantitativos (A Base de Cálculo)

O motor de pontuação varre a estrutura de dados do cenário e atribui blocos de pontos adicionais para cada elemento real que o jogador precisa analisar ou diagnosticar:

* **$V_{base}$ (Constante de Participação):** Pontos concedidos puramente por iniciar o cenário (ex: 1000 pontos).
* **$B_{risco}$ (Bônus por Risco):** Pontos adicionados por cada elemento presente no gabarito de Riscos Ocupacionais (ex: +250 pontos por risco).
* **$B_{fator}$ (Bônus por Fator de Insegurança):** Pontos adicionados por cada fator (Ato ou Condição) presente no gabarito (ex: +250 pontos por fator).
* **$B_{midia}$ (Bônus de Evidência):** Pontos adicionados pelo volume de mídia visual a ser analisado (ex: +100 pontos por Imagem, +300 pontos por Vídeo).
* **$B_{contexto}$ (Bônus de Densidade de Contexto):** Pontos adicionados pela quantidade de grupos ou pessoas envolvidas listadas na cena, aumentando a necessidade de varredura situacional (ex: +100 pontos por cada pessoa/grupo listado).

O subtotal quantitativo ($Sub_{quant}$) é o somatório destes elementos:


$$Sub_{quant} = V_{base} + \sum B_{risco} + \sum B_{fator} + \sum B_{midia} + \sum B_{contexto}$$

### 4.2. Multiplicador de Gravidade (A Dificuldade Descritiva)

A recompensa final deve refletir não apenas a quantidade de itens a analisar, mas o peso da responsabilidade (consequência do erro) e o esforço de superar "falsos alarmes". A dificuldade qualitativa do cenário ($D$), classificada de 1 a 5 pelo *Level Designer*, atua como um multiplicador direto sobre o subtotal quantitativo.

$$V_{max} = Sub_{quant} \times D$$

**Exemplo Prático de Cálculo:**
Cenário: *Laboratório de Química*

* **Descritivo:** Dificuldade $D = 4$ (Alta gravidade e dissonância).
* **Quantitativo:** * 2 Riscos (+500 pts)
* 2 Fatores (+500 pts)
* 1 Imagem (+100 pts)
* 2 Envolvidos (Professor e Alunos = +200 pts)


* **Cálculo:** $Sub_{quant} = 1000 (base) + 500 + 500 + 100 + 200 = 2300$ pontos.
* **$V_{max}$ Final:** $2300 \times 4 = \mathbf{9200\ pontos}$.


### 4.3. Janela de Eficiência (Tempo Ideal)

A fim de manter a consistência do fluxo de jogo e simular uma rotina de inspeção padronizada, o Tempo Ideal concedido para a resolução do relatório sem penalidades é estático para todos os cenários, independentemente da dificuldade.

$$T_{ideal} = 45\ segundos$$


## 5. Decomposição Item-a-Item (Scores da Tela de Diagnóstico)

Enquanto as seções anteriores definem a nota agregada de cada eixo (riscos e fatores), a tela de diagnóstico exibe a contribuição individual de cada risco e fator para o jogador. A decomposição deve respeitar uma restrição fundamental: **a soma dos scores por item deve ser exatamente igual à nota real do eixo correspondente**.

### 5.1. Decomposição de Riscos ($S_{risco}$)

Dado um cenário com $g$ riscos no gabarito, onde o jogador acertou $k$ riscos e marcou $m$ riscos no total ($m = k + \text{inventados}$), a nota real de riscos é:

$$P_{risco} = (V_{max} \times 0.60) \times \frac{k}{g} \times \frac{k}{m}$$

A decomposição item-a-item que preserva o somatório é:

| Tipo de item | Score individual |
|---|---|
| Risco **acertado** | $+ \dfrac{V_{max} \times 0.60}{g}$ |
| Risco **inventado** | $- \dfrac{V_{max} \times 0.60 \times k}{g \times m}$ |
| Risco **esquecido** | $0$ |

**Prova de fechamento:**

$$\sum S_{risco} = k \times \frac{V_{max} \times 0.60}{g} - (m - k) \times \frac{V_{max} \times 0.60 \times k}{g \times m}$$

$$= \frac{V_{max} \times 0.60 \times k}{g} \times \left(1 - \frac{m - k}{m}\right) = \frac{V_{max} \times 0.60 \times k}{g} \times \frac{k}{m} = P_{risco} \quad \checkmark$$

**Casos especiais:**

* Se o jogador não acertou nenhum risco ($k = 0$): a nota real já é $0$, e todos os scores individuais são $0$. Não há penalidade negativa visível — o total zerado é a penalidade máxima.
* Se o gabarito não possui riscos ($g = 0$) e o jogador não marcou nada ($m = 0$): não há itens a decompor; a nota é integral ($V_{max} \times 0.60$).
* Se o gabarito não possui riscos ($g = 0$) e o jogador marcou algo ($m > 0$): a nota real é $0$, e todos os scores são $0$.

### 5.2. Decomposição de Fatores de Insegurança ($S_{fator}$)

Os factores são avaliados como dois estados binários independentes: **Ato Inseguro** e **Condição Insegura**. Apenas factores presentes no gabarito são pontuados. A nota real, dado $g$ factores no gabarito e $m$ factores marcados, é:

$$P_{inseg} = (V_{max} \times 0.15) \times \frac{S_{ato} + S_{cond}}{\max(1, g, m)}$$

A decomposição item-a-item:

| Tipo de item | Score individual |
|---|---|
| Fator **acertado** (presente no gabarito e correctamente marcado) | $+ \dfrac{V_{max} \times 0.15}{\max(1, g, m)}$ |
| Fator **errado** (no gabarito mas não marcado, ou marcado sem estar no gabarito) | $0$ |
| Fator **correctamente ausente** (ausente no gabarito e não marcado) | $0$ |

**Prova de fechamento:**

$$\sum S_{fator} = S_{ato} \times \frac{V_{max} \times 0.15}{D} + S_{cond} \times \frac{V_{max} \times 0.15}{D}\quad\text{onde } D = \max(1, g, m)$$

$$= (V_{max} \times 0.15) \times \frac{S_{ato} + S_{cond}}{D} = P_{inseg} \quad \checkmark$$

Factores errados ou inventados não geram score próprio — a penalidade por invenção está embutida no denominador $D$, que dilui o valor de cada acerto quando $m > g$.

### 5.3. Valores de Calibragem (Constantes do Motor)

| Constante | Valor | Descrição |
|---|---|---|
| $T_{ideal}$ | $45\text{s}$ | Tempo sem penalidade |
| $\alpha$ | $0.007$ | Taxa de decaimento por segundo extra |
| $L_{min}$ | $0.50$ | Piso de retenção temporal (50%) |
| $V_{base}$ | $1000$ | Pontos de participação |
| $B_{risco}$ | $250$ | Bônus por risco no gabarito |
| $B_{fator}$ | $250$ | Bônus por fator no gabarito |
| $B_{imagem}$ | $100$ | Bônus por anexo de imagem |
| $B_{video}$ | $300$ | Bônus por anexo de vídeo |
| $B_{audio}$ | $200$ | Bônus por anexo de áudio |
| $B_{contexto}$ | $100$ | Bônus por pessoa envolvida |
| Limiar de Vitória | $60\%$ | Percentual mínimo de $V_{total\_turno}$ |

