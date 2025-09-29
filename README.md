# **Otimização de Posicionamento de Antenas com Algoritmo Genético**

## **1\. Introdução**

Este projeto apresenta uma implementação em Python de um **Algoritmo Genético (AG)** para resolver o **Problema de Localização com Máxima Cobertura** (*Maximal Covering Location Problem*). O objetivo é determinar o posicionamento ótimo de um número fixo de antenas em um mapa 2D para maximizar o número de clientes cobertos pelo sinal.

A solução utiliza uma abordagem meta-heurística baseada nos princípios da evolução natural para explorar o vasto espaço de busca de possíveis configurações de antenas e convergir para uma solução de alta qualidade.

O projeto inclui não apenas o núcleo do algoritmo genético, mas também utilitários para gerar dados de clientes sintéticos e para visualizar os resultados de forma gráfica.

## **2\. Estrutura do Projeto**

O código é organizado de forma modular para facilitar a compreensão, manutenção e experimentação:

/  
├── main.py                 \# Ponto de entrada principal para executar a otimização.  
├── config.py               \# Arquivo central para todos os parâmetros do AG e do problema.  
├── genetic\_algorithm.py    \# Contém a lógica central do AG (classes Individual, GeneticAlgorithm).  
├── problem\_domain.py       \# Lida com a lógica específica do problema (fitness, decodificação).  
│  
├── data/  
│   ├── clients.csv         \# Dados de exemplo dos clientes a serem cobertos.  
│   └── relatorio\_execucao.txt \# Arquivo de saída gerado após a execução.  
│  
└── utils/  
    ├── generate\_clients.py \# Script para gerar novos dados de clientes sintéticos.  
    └── visualize.py        \# Script para criar uma visualização gráfica dos resultados.

## **3\. Solução Genética Aplicada**

A implementação do Algoritmo Genético segue uma abordagem clássica, detalhada abaixo:

* **Codificação**: Utiliza uma **codificação binária**. Cada solução (indivíduo) é representada por um **cromossomo**, que é uma longa cadeia de bits formada pela concatenação das coordenadas (X e Y) de todas as antenas.  
* **Função de Avaliação (Fitness)**: A aptidão de um indivíduo é calculada como o **número total de clientes únicos** que estão dentro do raio de cobertura de pelo menos uma das antenas daquela solução.  
* **Seleção**: O método de **Seleção por Roleta** é empregado. Indivíduos com maior fitness (maior cobertura de clientes) têm maior probabilidade de serem selecionados como pais para a próxima geração.  
* **Cruzamento (Crossover)**: É utilizado o **cruzamento de dois pontos**. Dois pontos de corte são sorteados no cromossomo dos pais, e o segmento central é trocado entre eles para gerar dois novos descendentes. A CROSSOVER\_RATE em config.py controla a probabilidade de ocorrência.  
* **Mutação**: A **mutação por inversão de bit** (*bit-flip*) é aplicada. Cada bit no cromossomo de um novo indivíduo tem uma pequena chance (MUTATION\_RATE) de ser invertido (0 para 1 ou 1 para 0), introduzindo diversidade na população.  
* **Estratégia de Substituição**: A nova geração é formada por uma estratégia de **elitismo**, onde os ELITISM\_COUNT melhores indivíduos da geração anterior são transferidos diretamente, garantindo a preservação das melhores soluções encontradas. O restante da população é preenchido com os descendentes do processo de reprodução.  
* **Condição de Parada**: O algoritmo para quando uma de duas condições é atendida:  
  1. Atinge o número máximo de gerações (MAX\_GENERATIONS).  
  2. A melhor solução não apresenta melhora por um número definido de gerações consecutivas (MAX\_STAGNANT\_GENERATIONS), indicando uma convergência.

## **4\. Como Usar**

### **Pré-requisitos**

* Python 3.8 ou superior  
* Matplotlib (para visualização)

### **Instalação**

1. Clone este repositório:  
   git clone \[https://github.com/arkfx/algoritmo\_genetico-antenas.git\](https://github.com/arkfx/algoritmo\_genetico-antenas.git)  
   cd algoritmo\_genetico-antenas

2. Instale as dependências (apenas matplotlib para os utilitários):  
   pip install matplotlib

### **Execução**

1. (Opcional) Gerar Novos Dados de Clientes:  
   Você pode criar um novo arquivo clients.csv com uma distribuição diferente.  
   python \-m utils.generate\_clients \--count 500 \--clusters 5

   Use python \-m utils.generate\_clients \--help para ver todas as opções.  
2. Executar a Otimização:  
   Para iniciar o algoritmo genético, execute o módulo main.  
   python \-m main

   O progresso será exibido no terminal. Ao final, um arquivo relatorio\_execucao.txt será gerado no diretório data/ com os resultados detalhados.  
3. Visualizar os Resultados:  
   Após a execução, gere um mapa de calor da densidade de clientes com a sobreposição das antenas otimizadas.  
   python \-m utils.visualize

   Isso abrirá uma janela do Matplotlib com o gráfico.

## **5\. Configuração**

Todos os parâmetros do problema e do algoritmo genético podem ser facilmente ajustados no arquivo config.py. Sinta-se à vontade para experimentar com diferentes valores para ver como eles impactam o desempenho e o resultado da otimização.

**Principais Parâmetros:**

* NUM\_ANTENNAS: Quantidade de antenas a serem posicionadas.  
* ANTENNA\_RADIUS: Raio de cobertura de cada antena.  
* POPULATION\_SIZE: Número de indivíduos em cada geração.  
* MAX\_GENERATIONS: Número máximo de iterações do algoritmo.  
* CROSSOVER\_RATE: Probabilidade de ocorrer o cruzamento.  
* MUTATION\_RATE: Probabilidade de um bit sofrer mutação.  
* MAX\_STAGNANT\_GENERATIONS: Critério de parada por convergência.