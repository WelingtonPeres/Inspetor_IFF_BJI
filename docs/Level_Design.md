# Diretrizes de Level Design: Metodologia de Classificação de Cenários (Descritivo)

A definição do Nível de Dificuldade ($D$) de um cenário de inspeção varia de 1 a 5. Ela não é ditada pela quantidade de itens a serem clicados, mas sim pela **Carga Cognitiva** e pelo **Peso da Responsabilidade** exigidos do jogador. O criador do nível deve avaliar o cenário através de quatro eixos qualitativos:

1. **Gravidade e Consequência (O Peso do Erro):** Qual é o impacto real se o inspetor falhar? Um risco ergonômico ignorado gera dor a longo prazo (baixa gravidade). Um risco químico explosivo ignorado gera uma catástrofe imediata (altíssima gravidade). Cenários mais graves possuem dificuldade maior, pois a margem para negligência é zero.
2. **Densidade Textual e Ambiguidade:** O texto do relatório é direto e aponta o problema, ou contém jargões, excesso de informações e "ruído" para cansar a leitura do inspetor?
3. **Camuflagem Visual (Anexos):** Na mídia anexada, a infração está em primeiro plano e centralizada, ou está subtilmente escondida no fundo de um ambiente caótico?
4. **Dissonância Cognitiva (Falsos Alarmes):** O cenário induz o jogador ao erro? O texto elogia a organização do local (gerando um falso senso de segurança), enquanto a imagem mostra um risco letal camuflado?

Com base nestes eixos, a inspeção deve ser enquadrada em um dos seguintes perfis:

#### Nível 1: Básico (Introdutório)

* **Foco:** Baixa gravidade e familiarização visual.
* **Características:** O risco presente tem impacto leve (ex: ergonômico ou físico de baixa intensidade). O texto é curto e objetivo. A imagem é limpa e o problema está no centro da tela.
* **Exemplo:** *Um aluno sentado de forma torta em frente a um computador no laboratório de informática. Consequência do erro: Leve desconforto.*

#### Nível 2: Intermediário (Rotina Operacional)

* **Foco:** Inspeção diária comum. Início da exigência de atenção aos detalhes.
* **Características:** Gravidade moderada. O texto descreve o ambiente de forma natural, sem entregar o problema de imediato. A imagem possui mais elementos decorativos que exigem que o jogador procure a anomalia.
* **Exemplo:** *Alunos utilizando tornos mecânicos. O texto descreve a aula normal, mas a imagem mostra uma pequena poça de óleo perto da área de passagem. Consequência do erro: Queda ou escorregão.*

#### Nível 3: Avançado (Análise Crítica e Ruído)

* **Foco:** Introdução de "Falsos Alarmes" e gravidade considerável.
* **Características:** O cenário tenta enganar o jogador. O texto elogia o uso de EPIs ou fala de um barulho alto (induzindo a marcar Risco Físico). O jogador precisa separar o que é apenas desorganização do que é de fato um fator de insegurança.
* **Exemplo:** *Oficina. O texto afirma que as máquinas fazem muito barulho, mas mostra os alunos com protetores auriculares (Falso Alarme de Risco Físico). No entanto, um aluno opera a máquina com uma corrente no pescoço (Ato Inseguro). Consequência do erro: Acidente grave com a máquina.*

#### Nível 4: Inspetor (Alta Pressão e Dissonância)

* **Foco:** Alta gravidade e contradição de informações.
* **Características:** O que está escrito no relatório contradiz subtilmente a foto. O cenário exige profundo conhecimento técnico. A gravidade é alta, e o excesso de zelo (parar tudo sem motivo) ou a negligência têm pesos pesados.
* **Exemplo:** *Laboratório de Química. O relatório afirma que "todos os protocolos de segurança química foram seguidos e a aula flui bem". A imagem mostra alunos manuseando ácidos, mas a capela de exaustão no fundo está com a luz vermelha de "Motor Desligado". Consequência do erro: Intoxicação respiratória coletiva.*

#### Nível 5: Especialista (Risco Iminente e Caos)

* **Foco:** Risco Iminente de Morte/Catástrofe e ambiente caótico. O teste definitivo.
* **Características:** A gravidade é extrema. A decisão administrativa muitas vezes exige INTERDITAR o local para salvar vidas. O ambiente visual é poluído, com pessoas fazendo múltiplas coisas. A pressão mental de "Não posso deixar passar nada" dita a dificuldade.
* **Exemplo:** *Obras de expansão do campus. Texto confuso misturando termos de engenharia civil. A imagem mostra trabalhos simultâneos: solda perto de material inflamável e trabalho em altura num andaime improvisado, apoiado sobre tijolos soltos. Consequência do erro: Fatalidade.*
