"""parametros de configuração para o problema de posicionamento de antenas.
o setup atual implementa:
Modelo de fitness baseado em numero de clientes atendidos
Seleção por roleta
Cruzamento de dois pontos
Mutação de inversão de bits
Critério de parada baseado em convergência de fitness
"""
from __future__ import annotations

from pathlib import Path

# parametros do problema
NUM_ANTENNAS: int = 4
MAP_WIDTH: int = 1000
MAP_HEIGHT: int = 1000
BITS_PER_COORD: int = 10 # precisão maxima de 1023 no mapa(2^10 - 1)
ANTENNA_RADIUS: float = 100.0
CLIENT_DATA_FILE: Path = Path(__file__).resolve().parent / "data" / "clients.csv"
    
# Parametros do algoritmo genético
POPULATION_SIZE: int = 100
MAX_GENERATIONS: int = 1000
ELITISM_COUNT: int = 10
CROSSOVER_RATE: float = 0.5
MUTATION_RATE: float = 0.05

# Critério de parada (F2: fitness convergência)
MAX_STAGNANT_GENERATIONS: int = 50

# Controle de aleatoriedade
RANDOM_SEED: int | None = None

# Barra de progresso
SHOW_PROGRESS: bool = True
PROGRESS_BAR_WIDTH: int = 40