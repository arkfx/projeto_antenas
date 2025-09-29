# Algoritmo Genético para Posicionamento de Antenas

Implementação completa de um Algoritmo Genético (AG) em Python para o problema de localização de antenas com máxima cobertura. As decisões seguem as opções solicitadas no documento *Opções.md*:

- **A1 – Codificação Binária**: cada antena é representada por 2 coordenadas codificadas em binário.
- **B1 – Modelo de Sinal Simples**: um cliente é coberto se estiver dentro de um raio fixo.
- **C1 – Seleção por Roleta**: a probabilidade de seleção é proporcional à aptidão.
- **D1 – Cruzamento de Dois Pontos**: recombinação em dois pontos sobre o cromossomo binário.
- **E1 – Mutação por Inversão de Bit**: bits são invertidos com probabilidade controlada.
- **F2 – Critério de Parada por Estagnação**: o algoritmo encerra quando não há melhoria após um número máximo de gerações.

## Estrutura do Projeto

```
projeto_antenas/
├── __init__.py
├── config.py            # Parâmetros do problema e do GA
├── genetic_algorithm.py # Núcleo do AG
├── main.py              # Ponto de entrada
├── problem_domain.py    # Carga de dados, decodificação e fitness
└── data/
    └── clients.csv      # Conjunto de clientes de exemplo
```

## Executando

1. Garanta que você esteja na raiz do repositório (o diretório que contém a pasta `projeto_antenas`).
2. Em um terminal nessa raiz, execute:

```pwsh
python -m projeto_antenas.main
```

O script carregará os clientes do arquivo CSV, executará o AG e exibirá:

- Número total de clientes
- Cobertura máxima encontrada
- Número de gerações executadas antes da estagnação
- Posições das antenas
- Cromossomo binário correspondente
- Uma barra de progresso no terminal com a geração atual, melhor fitness e estagnação

## Personalização

- Edite `config.py` para ajustar número de antenas, raio de cobertura, tamanho da população, taxas de cruzamento/mutação e critérios de parada.
- Atualize `data/clients.csv` com suas coordenadas (formato `id,x,y`).
- Para reprodutibilidade, ajuste `RANDOM_SEED` em `config.py`.
- Controle a barra de progresso pelos parâmetros `SHOW_PROGRESS` (habilita/desabilita) e `PROGRESS_BAR_WIDTH` (tamanho da barra) em `config.py`.

## Visualização dos clientes

Para inspecionar a distribuição espacial dos clientes você pode gerar um mapa de calor a partir de `data/clients.csv`:

```pwsh
python -m projeto_antenas.utils.visualize --no-show --output projeto_antenas/data/clients_heatmap.png
```

Use `--show` para abrir uma janela interativa e `--bins` para ajustar a resolução da malha.

## Dependências

O núcleo do algoritmo usa apenas a biblioteca padrão do Python (>= 3.10).

Para o script de visualização, instale também:

```pwsh
python -m pip install matplotlib
```
