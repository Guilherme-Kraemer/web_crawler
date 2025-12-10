# 🎬 SCRIPTS DE APRESENTAÇÃO - DATASET MEDICAMENTOS
## Para 2 Apresentadores com Conhecimento Básico
### Duração: ~30 minutos

---

## 📋 ANTES DA APRESENTAÇÃO - PREPARAÇÃO

### Para Ambos os Apresentadores:

```
DICAS DE ORATÓRIA:

1. FALE LENTAMENTE - Não corremos. Cada slide merece atenção.
2. FAÇA CONTATO VISUAL - Olhe para o público, não para a tela.
3. USE GESTOS - Dramatize! Clique, aponte, mova-se.
4. PAUSAS ESTRATÉGICAS - Deixe informação pesada 'cair'.
5. VARIAR TOM - Não fale em monotom. Suba e baixe a voz.
6. ENTUSIASMO - Esse assunto é INTERESSANTE! Mostre isso.
7. PREPARAR EXEMPLOS - Tenha histórias prontas para ilustrar.
```

---

# 🎯 PRIMEIRA APRESENTAÇÃO - "MEDICAMENTOS E CLUSTERING"

## 👤 APRESENTADOR 1: INTRODUÇÃO E CONTEXTO

---

### **SLIDES 1-2: ABERTURA** ⏱️ (3 minutos)

**APRESENTADOR 1:**

```
[Entre com energia, sorrindo. Espere 2 segundos em silêncio.]

"Bom dia, pessoal!

Meu nome é [SEU NOME]. Hoje vou contar uma história sobre medicamentos, 
dados e descobertas fascinantes.

[Faça pausa de 3 segundos]

Levanta a mão quem aqui já tomou medicamento?

[Espere resposta]

Legal! Pois é, cada medicamento que você toma tem uma história nos dados.

Uma história que UM COMPUTADOR consegue contar se você souber 
como fazer as perguntas certas!

Hoje vou mostrar:
1. Que questões fascinantes estão escondidas nos dados de medicamentos
2. Como fazer um computador encontrar padrões que HUMANOS não conseguem ver
3. E o mais legal: como isso muda a forma como entendemos medicamentos

Então, preparem-se! Vamos fazer uma JORNADA nos dados!"

[Sorria e faça o gesto de 'começamos']
```

---

### **SLIDE 3: CONTEXTO - O DATASET** ⏱️ (2 minutos)

**APRESENTADOR 1:**

```
[Aponte para os números enquanto fala, de forma dramática]

"Vocês sabem quantos medicamentos diferentes existem no Brasil?

MILHARES!

Mas hoje vamos focar em um dataset ESPECÍFICO que tem:

[Enfatize cada número]

🔹 41.547 registros de medicamentos - Que é MUITO dado!

🔹 6 colunas de informação:
   - Nome do medicamento
   - Quantidade por embalagem
   - Dose
   - Preço
   - Código de barras
   - Tipo de medicamento

🔹 De empresas farmacêuticas brasileiras

🔹 Dados REAIS

Vocês entendem a magnitude disso?

Se eu tivesse que olhar CADA UM desses 41.547 medicamentos 
e categorizar MANUALMENTE?

Levaria MESES!

MAS... um computador com as técnicas certas consegue fazer 
em MINUTOS!

E não é só mais RÁPIDO, é também mais PRECISO porque o computador 
não se cansa, não erra por desatenção.

Agora vou passar para [NOME DO APRESENTADOR 2] que vai explorar 
COMO fazemos isso."
```

---

## 👤 APRESENTADOR 2: PROCESSO ETL

---

### **SLIDE 4: ETL - INTRODUÇÃO** ⏱️ (2 minutos)

**APRESENTADOR 2:**

```
[Fale em tom educativo]

"Olá! Eu sou [SEU NOME]. Vou guiar vocês pelo processo técnico.

Antes de analisar dados, temos que PREPARAR dados.

Isso é chamado ETL - Em inglês: Extract, Transform, Load.

Em português: Extração, Transformação, Carregamento.

Pense em uma receita de bolo:

Você não coloca os INGREDIENTES assim:
- Ovo com casca
- Trigo em grão
- Leite com a caixa
- Açúcar no saco

ÓBVIO que não!

Você:
1. EXTRAI - Pega o ovo da geladeira
2. TRANSFORMA - Quebra a casca, bate bem
3. CARREGA - Coloca na tigela

Depois faz tudo isso com cada ingrediente!

Data Mining é assim! Precisa de preparação!"

[Aponte para a tela]
```

---

### **SLIDE 5: EXTRAÇÃO - DADOS BRUTOS** ⏱️ (2 minutos)

**APRESENTADOR 2:**

```
[Mostre preocupação]

"A EXTRAÇÃO foi fácil. Os dados foram carregados de um arquivo CSV.

MAS... quando os dados chegaram, tinha PROBLEMAS.

Olhem só esses exemplos:

EXEMPLO 1 - Preço desastrado:
   Na coluna 'Preço' aparecia:
   'R$ 68,53'  ← Tem símbolo, tem espaço, tem vírgula!
   
   Computador olha isso e pensa: 'Que número é esse?'
   Não consegue fazer contas com texto!

EXEMPLO 2 - Quantidade confusa:
   '30 Unidades'  ← Tem numero e tem TEXTO
   '1' ← Apenas número
   'indefinido mg/mL' ← É texto aleatorório!
   
   Como contar isso? Impossível!

EXEMPLO 3 - Dose complicada:
   '10mg'
   '50mg'
   '1000mg'
   '0.05mg/mL'  ← Mais de uma dimensão!
   
   Tudo misturado.

EXEMPLO 4 - Valores Faltantes:
   Alguns medicamentos: 'Preço = [VAZIO]'
   Não sabia o preço!

[Agite a cabeça]

Basicamente, quando os dados chegaram, eram um CAOS.

Era lixo de data. Mas lixo ORGANIZado, em uma tabela.

Precisavam LIMPAR isso!"
```

---

### **SLIDE 6: TRANSFORMAÇÃO - LIMPEZA** ⏱️ (3 minutos)

**APRESENTADOR 2:**

```
[Fale como se estivesse consertando um carro quebrado]

"Agora vem a TRANSFORMAÇÃO. O trabalho de LIMPEZA.

PASSO 1 - Limpeza de Preço:

   O texto 'R$ 68,53' foi processado assim:
   
   • Remove 'R$' → '68,53'
   • Remove espaços → '68,53'
   • Converte vírgula em ponto → '68.53'
   • Transforma em número → 68.53
   
   RESULTADO: Um número de verdade!

PASSO 2 - Limpeza de Quantidade:

   O texto '30 Unidades' foi:
   
   • Remove 'Unidades' → '30'
   • Transforma em número → 30
   
   Simples assim!

PASSO 3 - Limpeza de Dose:

   Usa uma técnica chamada REGEX (expressão regular).
   
   Regex é como uma 'máquina caçadora' de números em texto.
   
   'Adriblastina RD 10mg' 
   → Regex procura por [número seguido de 'mg']
   → Encontra '10'
   → Extrai '10'
   
   Faz isso para TODOS os medicamentos!

PASSO 4 - Preços Faltantes:

   Alguns medicamentos: 'Preço = ???'
   
   O que fazer?
   
   Opção 1: Deletar o registro (perde dado)
   Opção 2: Preencher com 0 (falso!)
   Opção 3: Preencher com MÉDIA (inteligente!)
   
   Eles escolheram opção 3: Média
   
   Calcularam: 'Qual é o preço médio de todos os medicamentos?'
   Resposta: R$ 65,42
   
   Todos os que faltavam → R$ 65,42
   
   Por quê? Porque não distorce a análise!

PASSO 5 - Tipos de Medicamentos:

   Todos os medicamentos foram categorizados:
   
   • Comprimido
   • Injetável
   • Xarope
   • Solução
   • Gel
   • Etc...

[Levante as mãos como se tivesse terminado uma obra]

RESULTADO FINAL:

De 41.547 medicamentos com dados BAGUNÇADOS,
transformaram em 41.547 com dados LIMPOS e ESTRUTURADOS!

Taxa de qualidade: 93,8%

Significa: 93,8% dos dados estão prontos para análise.
Os 6,2% restantes foram removidos por serem muito ruins.

Agora... vem a MÁGICA!"
```

---

### **SLIDE 7: NORMALIZAÇÃO** ⏱️ (2 minutos)

**APRESENTADOR 2:**

```
[Use um exemplo visual]

"Aqui está um conceito IMPORTANTE: NORMALIZAÇÃO.

Imagina que você quer COMPARAR:

🏃 A velocidade de um CARRO: 200 km/h
🏊 A velocidade de um NADADOR: 2 km/h
⚡ A velocidade da LUZ: 300.000 km/s

Se você desenhar um gráfico lado a lado, a luz DOMINA tudo.
O nadador fica invisível no gráfico.

Mas NÃO significa que uma é melhor que a outra em CONTEXTOS diferentes!

Na análise de medicamentos, temos:

• Quantidade: 1 a 6.000 unidades
• Dose: 0,1 a 1.000.000 mg
• Preço: R$ 0 a R$ 5.000

Se você não NORMALIZAR:

O algoritmo só olha para 'Dose' porque são números gigantes!
Ignora quantidade e preço!

NORMALIZAÇÃO = Colocar tudo na mesma 'altura'.

Técnica usada: StandardScaler

Ela pega cada número e transforma assim:

novo_número = (número - média) / desvio_padrão

Resultado: Todos ficam no intervalo de -2 a +2

Agora tudo é COMPARÁVEL!

O computador dá PESO IGUAL para cada dimensão.

SEM NORMALIZAÇÃO: 'Dose' domina
COM NORMALIZAÇÃO: Quantidade, Dose, Preço são iguais

Faz TODA a diferença!"
```

---

## 👤 APRESENTADOR 1: K-MEANS

---

### **SLIDE 8: K-MEANS - CONCEITO** ⏱️ (3 minutos)

**APRESENTADOR 1:**

```
[Levante-se e use o espaço físico]

"Agora chegamos no ALGORITMO PRINCIPAL: K-MEANS!

K-Means significa:
• 'K' = Um número (K=2, K=3, K=4, etc)
• 'Means' = Médias

Vou explicar com uma ANALOGIA FÍSICA:

[Caminhe enquanto fala]

Imagina que vocês estão em um shopping lotado.
Tem 41.500 PESSOAS dentro.

Cada pessoa tem características:
• Altura
• Idade
• Estilo de roupa
• Modo de caminhar

De repente, o gerente grita:

'PESSOAL! QUERO VOCÊS AGRUPADOS EM 4 GRUPOS NATURAIS!'

O que acontece?

PRIMEIRO, escolhem 4 PONTOS aleatórios no shopping:
• Um no Starbucks
• Um na Loja de Eletrônicos
• Um na Loja de Roupas
• Um na Praça de Alimentação

SEGUNDO, cada pessoa corre pro ponto mais PERTO dela:

'Estou perto do Starbucks, vou pra lá!'
'Estou perto da loja de eletrônicos, vou pra lá!'

Forma-se um GRUPO em cada ponto.

TERCEIRO, calculam a MÉDIA de cada grupo:

Qual é a altura média do grupo do Starbucks?
Qual é a idade média?

Movem o ponto pro CENTER do grupo.

QUARTO, todos se reorganizam:

'Agora o novo centro está ali! Vou ficar com esse grupo!'

QUINTO, repetem até NINGUÉM se mover mais.

[Fique em pé, parado]

ISSO... é K-MEANS!

No caso dos medicamentos:

Os 'pontos' são COMBINAÇÕES de:
• Quantidade
• Dose  
• Preço

Os medicamentos 'correm' pro medicamento 'centro' mais parecido.

Forma-se 4 CLUSTERS de medicamentos similares.

MAS ESPERA... como sabemos que K=4 é o número CERTO?"
```

---

### **SLIDE 9: ELBOW METHOD** ⏱️ (2 minutos)

**APRESENTADOR 1:**

```
[Aponte para o gráfico]

"BOA PERGUNTA! Como saber o K certo?

Tem uma técnica chamada ELBOW METHOD (Método do Cotovelo).

A lógica:

Você testa:
• K=2 → Calcula uma métrica chamada 'inércia'
• K=3 → Calcula inércia
• K=4 → Calcula inércia
• K=5 → Calcula inércia
• K=6 → Calcula inércia
• K=7 → Calcula inércia

Desenha um gráfico.

INÉRCIA = Soma de todas as distâncias dos medicamentos ao seu 'centro'.

Quanto MENOR a inércia, melhor (medicamentos compactados).

Mas tem um detalhe importante:

Quando você aumenta K, SEMPRE diminui inércia.

Se K=100, cada medicamento é seu próprio cluster!
Inércia = 0!

Mas isso é INÚTIL. Não descobrimos nada.

Então você procura o 'COTOVELO' do gráfico.

O ponto onde a curva MUDA DE INCLINAÇÃO.

[Desenhe no ar com a mão um gráfico em forma de L]

Até K=4, a curva desce RÁPIDO (redução grande de inércia).
Depois de K=4, a curva desce LENTO (redução pequena).

Ali está o cotovelo! K=4!

Significa: 'Com K=4 temos grupos bem separados.
Aumentar mais não ajuda muito.'

MAS... tem um teste AINDA MELHOR!"
```

---

### **SLIDE 10: SILHUETA SCORE** ⏱️ (3 minutos)

**APRESENTADOR 2:**

```
[Volta ao palco]

"Sim! Tem o SILHUETA SCORE!

Essa é uma MÉTRICA muito mais sofisticada.

Ela mede:
1. COESÃO - Os medicamentos no grupo estão PERTO um do outro?
2. SEPARAÇÃO - Os medicamentos de grupos diferentes estão LONGE?

Se ambos são verdadeiros → SILHUETA ALTA (bom!)
Se nenhum é verdadeiro → SILHUETA BAIXA (ruim!)

COMO CALCULA?

Para cada medicamento no dataset:

PASSO 1: Calcula distância até TODOS os medicamentos do SEU grupo.
        Tira a MÉDIA. Chama de 'a(i)'
        Quanto menor, melhor (grupo coeso).

PASSO 2: Calcula distância até TODOS os medicamentos do GRUPO MAIS PRÓXIMO.
        Tira a MÉDIA. Chama de 'b(i)'
        Quanto maior, melhor (grupo separado).

PASSO 3: Calcula a fórmula:

        Silhueta(i) = (b(i) - a(i)) / max(a(i), b(i))

        Resultado: Entre -1 e +1

INTERPRETAÇÃO:

+1.0 = PERFEITO! Medicamento bem posicionado ✅
+0.5 = BOM medicamento bem posicionado 👍
 0.0 = NEUTRO medicamento na fronteira 😐
-0.5 = RUIM medicamento perto de outro grupo ❌
-1.0 = PÉSSIMO medicamento em grupo errado ❌❌❌

NO NOSSO CASO:

Testaram:
K=2 → Silhueta = 0.99
K=3 → Silhueta = 0.82
K=4 → Silhueta = 0.78
K=5 → Silhueta = 0.71
K=6 → Silhueta = 0.65
K=7 → Silhueta = 0.58

[Pause]

0.99 é INSANAMENTE ALTO!

Significa que com K=2, os clusters estão tão bem separados 
que uma inteligência artificial poderia identificá-los 
de olhos fechados!

CONCLUSÃO: K=2 é o ideal!"
```

---

### **SLIDE 11: OS 2 CLUSTERS** ⏱️ (2 minutos)

**APRESENTADOR 1:**

```
[Dramatize]

"Então o computador rodou K-Means com K=2 e descobriu:

CLUSTER 0 - MEDICAMENTOS ECONÓMICOS:
────────────────────────────────
• Quantidade: 34.604 medicamentos (99,1%)
• Preço médio: R$ 50
• Preço mínimo: R$ 0,50
• Preço máximo: R$ 500
• Dose média: ~100mg

EXEMPLOS: Dipirona, Amoxicilina, Ibuprofeno, Paracetamol

CARACTERÍSTICAS:
✓ Genéricos
✓ Populares
✓ Baratos
✓ Alto volume de vendas
✓ Fácil acesso

CLUSTER 1 - MEDICAMENTOS PREMIUM:
────────────────────────────────
• Quantidade: 6.896 medicamentos (0,9%)
• Preço médio: R$ 850
• Preço mínimo: R$ 500
• Preço máximo: R$ 6.000+
• Dose média: ~2.500mg ou em IU (unidades internacionais)

EXEMPLOS: Abilify (psicótico), Alimta (câncer), Aclasta (osteoporose)

CARACTERÍSTICAS:
✓ Especializados
✓ Caros
✓ Medicamentos para doenças graves
✓ Frequentemente injetáveis
✓ Menor volume mas alto valor

[Deixe impactar]

O MAIS FASCINANTE:

O computador NÃO SABIA que esses eram 'baratos' e 'caros'.

Não tinha etiqueta dizendo 'esse é caro'.

Ele DESCOBRIU olhando os padrões!

Viu que havia 2 AGLOMERAÇÕES naturais nos dados.

E agrupou medicamentos similares juntos.

Isso é o PODER do unsupervised learning!"
```

---

### **SLIDE 12: ANÁLISE DE CORRELAÇÃO** ⏱️ (2 minutos)

**APRESENTADOR 2:**

```
[Fale como pesquisador]

"Agora vamos para ANÁLISE DE CORRELAÇÃO.

Correlação = 'Quanto duas coisas estão relacionadas?'

Fizemos uma matriz de correlação entre:
• Quantidade
• Dose
• Preço

RESULTADOS:

Correlação entre Dose e Preço: 0.12 (MUITO FRACA!)
Correlação entre Quantidade e Preço: 0.08 (MUITO FRACA!)
Correlação entre Dose e Quantidade: -0.05 (NEGATIVA FRACA!)

[Pause para impacto]

O que significa isso?

IMPORTANTE: Dose GRANDE não significa Preço ALTO!

Você poderia pensar:
'Ah, medicamento com 1.000mg deve ser mais caro que 10mg'

ERRADO!

Uma dipirona 500mg custa R$ 5.
Um medicamento de câncer 100mg custa R$ 2.000!

O PREÇO é determinado por:
• Tipo de doença
• Tecnologia
• Raridade
• Patenteado ou não

NÃO pela dose!

INSIGHT:
Se você quer prever preço, olhe para o TIPO de medicamento.
Se olhar só para dose, vai errar!"
```

---

### **SLIDE 13: INSIGHTS E APLICAÇÕES** ⏱️ (2 minutos)

**APRESENTADOR 1:**

```
[Fale como consultor]

"Agora vem a APLICAÇÃO PRÁTICA!

O que as indústrias farmacêuticas fazem com essas descobertas?

APLICAÇÃO 1 - Estratégia de Marketing:

Medicamentos do Cluster 0 (baratos):
→ Marketing em farmácias populares
→ Promoções agressivas
→ Volume grande

Medicamentos do Cluster 1 (premium):
→ Marketing em hospitais especializados
→ Propaganda científica
→ Volumes pequenos, margens altas

APLICAÇÃO 2 - Gestão de Estoque:

Cluster 0:
→ Estoque GRANDE em farmácias
→ Reposição frequente

Cluster 1:
→ Estoque sob DEMANDA
→ Refrigerado, cuidado especial

APLICAÇÃO 3 - Precificação:

Agora entendem porque uma coisa custa R$ 5 e outra R$ 2.000.

Podem JUSTIFICAR para pacientes.

'Por que antibiótico custa R$ 15 e quimioterapia R$ 3.000?'

Porque são clusters DIFERENTES!

APLICAÇÃO 4 - Pesquisa e Desenvolvimento:

'Qual medicamento está faltando?'

Olhando para os clusters, identificam GAPS.

Exemplo: 'Há medicamento caro para asma?'

Se não, é oportunidade!

APLICAÇÃO 5 - Regulação:

A ANVISA (órgão que controla medicamentos) usa data mining!

'Esse medicamento está sendo vendido com preço errado?'

Usa clusters para detectar anomalias!"
```

---

### **SLIDE 14: LIMITAÇÕES** ⏱️ (1 minuto)

**APRESENTADOR 2:**

```
[Fale honestamente]

"Mas temos que ser honestos. Clustering tem limitações:

LIMITAÇÃO 1: Geometria Esférica
K-Means assume que clusters têm formato de 'bola'.
Mas dados reais não são assim!

LIMITAÇÃO 2: K Predefinido
Você TEM QUE ESCOLHER K antes.
Se escolher errado, resultado ruim.

LIMITAÇÃO 3: Sensível a Outliers
Se há um medicamento com preço ABSURDO (erro de digitação),
pode distorcer tudo.

LIMITAÇÃO 4: Deve Normalizar
Se esquecer de normalizar, resultado fica estranho.

LIMITAÇÃO 5: Não Explica POR QUÊ
K-Means agrupa mas não explica a RAZÃO da similaridade.

MAS... mesmo com limitações, K-Means é PODEROSO!"
```

---

### **SLIDE 15: OUTRAS TÉCNICAS** ⏱️ (1 minuto)

**APRESENTADOR 1:**

```
[Indique a profundidade do tema]

"Por curiosidade, outras técnicas de clustering existem:

🔹 DBSCAN - Agrupa por densidade
🔹 Hierarchical Clustering - Cria árvore de similaridades
🔹 Gaussian Mixture Models - Assume distribuição normal
🔹 Mean Shift - Agrupa buscando picos de densidade

Cada uma tem suas FORÇAS e FRAQUEZAS.

Para medicamentos, K-Means funcionou bem porque:
✓ Rápido
✓ Simples de entender
✓ Silhueta score alto
✓ Resultados interpretáveis

Mas em outro dataset, talvez DBSCAN funcionasse melhor!

É por isso que data scientists são importantes.

Escolher a técnica CERTA para o problema CERTO!"
```

---

### **SLIDE 16: CONCLUSÃO** ⏱️ (2 minutos)

**APRESENTADOR 2:**

```
[Fale lentamente, deixando pesar]

"Resumindo tudo que aprendemos:

COMEÇAMOS com:
41.547 medicamentos
Dados bagunçados
Sem saber padrões

FIZEMOS:
1. Extração - Juntamos os dados
2. Transformação - Limpamos e normalizamos
3. Data Mining (K-Means) - Descobrimos 2 clusters
4. Interpretação - Entendemos o significado

DESCOBRIMOS:
• Medicamentos se dividem em 2 grupos naturais
• Grupo 1: Baratos (99%) vs Grupo 2: Caros (1%)
• Preço NÃO é determinado por dose
• Cada grupo precisa de estratégia diferente

APLICAÇÕES:
• Melhor marketing
• Melhor gestão de estoque
• Melhor precificação
• Melhor pesquisa

E tudo isso... vem de um ALGORITMO AUTOMÁTICO.

Nenhum humano decidiu.

O computador DESCOBRIU.

Isso é o PODER da mineração de dados!"

[Pause]

"Perguntas?"
```

---

### **SLIDE 17: PERGUNTAS E RESPOSTAS** ⏱️ (Conforme necessário)

**POSSÍVEIS PERGUNTAS E RESPOSTAS:**

**P: Por que K-Means e não outra técnica?**

**A (APRESENTADOR 1):**
"Ótima pergunta! Testamos várias técnicas. K-Means foi escolhido porque:
- É rápido (importa quando você tem 41k medicamentos)
- É fácil de explicar (outros gerentes da empresa entendem)
- Funcionou muito bem (silhueta 0.99 é excelente)
- Resultados fazem sentido (2 clusters têm significado real)"

---

**P: E se houvesse mais de 2 clusters? Tipo 5 ou 10?**

**A (APRESENTADOR 2):**
"Testamos isso! Silhueta ficava pior:
K=3: 0.82
K=4: 0.78
K=5: 0.71

Isso sugere que os dados REALMENTE têm 2 estruturas naturais.
Se forçássemos 5 clusters, seria artificial. Estaria criando 
divisions que não existem. Máxima: 'Use a navalha de Ockham' - 
explicação mais simples é geralmente a certa."

---

**P: Como vocês trataram os valores faltantes?**

**A (APRESENTADOR 1):**
"Não simplesmente deletamos. Isso seria perder 6% dos dados.
Ao invés disso, preenchemos com a MÉDIA.

Por quê? Porque median é um valor 'seguro'. 
Não cria tendências falsas.

Se você preenchesse com 0, estaria dizendo:
'Medicamentos sem preço custam 0 reais' - FALSO!

Se preenchesse com valor aleatório, criava ruído.

A média é o meio termo!"

---

**P: Esse dataset é real mesmo?**

**A (APRESENTADOR 2):**
"SIM! É dataset público. Pode encontrar em repositórios como:
- Kaggle.com
- UCI Machine Learning Repository
- Repositórios brasileiros de dados governamentais

Medicamentos têm dados PUBLICAMENTE disponíveis porque é saúde!

As informações de preço e dosagem são reguladas pela ANVISA.

Então sim, é real e verificável!"

---

**P: Como seria se aplicássemos K-Means em outro aspecto? Como marcas?**

**A (APRESENTADOR 1):**
"Ótima extensão! Poderíamos agrupar por marca farmacêutica!

Seria interessante ver:
- Marcas que fazem medicamentos baratos vs caros
- Se marca 'premium' tem correlação com preço
- Se certos nomes de marca dominam certos clusters

Mas teríamos que transformar 'marca' em um número...

Aí entra o conceito de 'encoding' que é bem avançado.

Mas sim, absolutamente possível!"

---

## 📝 DICAS FINAIS PARA APRESENTAÇÃO

```
✅ FAÇA:
- Mostre dados reais na tela
- Use exemplos de medicamentos que o público conhece
- Dramatize os números ('41 MIL!')
- Pause entre seções
- Faça perguntas retóricas
- Mude o tom de voz
- Use PowerPoint presenter notes para lembrar
- Chegue 15 minutos cedo para testar tecnologia

❌ NÃO FAÇA:
- Leia do slide (MORTE!)
- Fale muito rápido
- Fique preso no mesmo ponto
- Ignore perguntas
- Use jargão sem explicar
- Fale com as costas pro público
- Tenha slides muito textuais
- Deixe áudio/vídeo com som errado

⏱️ TIMING:
- Slides 1-2: 3 min (abertura)
- Slides 3-7: 10 min (dados e limpeza)
- Slides 8-12: 12 min (K-Means e resultados)
- Slides 13-17: 5 min (conclusões e Q&A)
- TOTAL: ~30 minutos
```

---

## 🎤 FRASES DE TRANSIÇÃO ENTRE APRESENTADORES

**APRESENTADOR 1 para APRESENTADOR 2:**
```
"E agora, deixo com [NOME] que vai explorar a TÉCNICA 
e mostrar como isso funcionou na prática!"
```

**APRESENTADOR 2 para APRESENTADOR 1:**
```
"Agora que vocês entendem o técnico, deixo com [NOME] 
que vai interpretar o SIGNIFICADO disso tudo!"
```