"""Ponto de entrada para executar o algoritmo genético de posicionamento de antenas."""

from __future__ import annotations
from pathlib import Path

import config
from genetic_algorithm import GeneticAlgorithm, Individual
from problem_domain import Problem, load_clients, Client


def _gerar_e_salvar_relatorio(
    problem: Problem,
    ga: GeneticAlgorithm,
    best_individual: Individual,
) -> Path:
    """Gera um relatório completo da execução e o salva em um arquivo de texto."""
    # Decodifica as coordenadas do melhor indivíduo encontrado
    best_coordinates = problem.decode(best_individual.genes)
    bits_as_str = "".join(str(bit) for bit in best_individual.genes)

    # Monta as seções do relatório usando f-strings multilinhas para clareza
    resumo_execucao = f"""
=== Resultado da Otimização ===
Clientes totais: {len(problem.clients)}
Antenas instaladas: {config.NUM_ANTENNAS}
Melhor cobertura encontrada: {best_individual.fitness} clientes
Gerações executadas: {ga.generations_run}

Posições das antenas (x, y):
"""
    # Adiciona as coordenadas de cada antena
    for idx, (x, y) in enumerate(best_coordinates, start=1):
        resumo_execucao += f"  Antena {idx:02d}: ({x}, {y})\n"

    resumo_execucao += f"""
Cromossomo binário:
{bits_as_str}
"""

    params_ga = f"""
=== Parâmetros do Algoritmo Genético ===
POPULATION_SIZE: {config.POPULATION_SIZE}
MAX_GENERATIONS: {config.MAX_GENERATIONS}
ELITISM_COUNT: {config.ELITISM_COUNT}
CROSSOVER_RATE: {config.CROSSOVER_RATE}
MUTATION_RATE: {config.MUTATION_RATE}
MAX_STAGNANT_GENERATIONS: {config.MAX_STAGNANT_GENERATIONS}
RANDOM_SEED: {config.RANDOM_SEED}
"""

    params_problema = f"""
=== Parâmetros do Problema ===
NUM_ANTENAS: {config.NUM_ANTENNAS}
BITS_PER_COORD: {config.BITS_PER_COORD}
MAP_WIDTH: {config.MAP_WIDTH}
MAP_HEIGHT: {config.MAP_HEIGHT}
ANTENNA_RADIUS: {config.ANTENNA_RADIUS}
"""
    # Junta todas as seções em um único texto
    conteudo_final = resumo_execucao.strip() + "\n" + params_ga.strip() + "\n" + params_problema.strip()

    # Define o caminho e salva o arquivo
    output_file = config.CLIENT_DATA_FILE.parent / "relatorio_execucao.txt"
    output_file.write_text(conteudo_final, encoding="utf-8")
    
    return output_file


def main() -> None:
    """Função principal que orquestra a execução do algoritmo genético."""
    # --- 1. Carregamento e Validação dos Dados ---
    try:
        clients = load_clients(config.CLIENT_DATA_FILE)
        if not clients:
            raise SystemExit("Nenhum cliente foi carregado do arquivo de dados.")
    except FileNotFoundError as exc:
        raise SystemExit(f"Arquivo de clientes não encontrado: {exc}") from exc

    # --- 2. Configuração do Problema e do Algoritmo ---
    problem = Problem(
        clients=clients,
        num_antennas=config.NUM_ANTENNAS,
        bits_per_coord=config.BITS_PER_COORD,
        map_width=config.MAP_WIDTH,
        map_height=config.MAP_HEIGHT,
        coverage_radius=config.ANTENNA_RADIUS,
    )
    ga = GeneticAlgorithm(problem)

    # --- 3. Execução do Algoritmo ---
    print("Iniciando otimização com Algoritmo Genético...")
    best_individual = ga.run()

    # --- 4. Geração e Salvamento do Relatório ---
    report_path = _gerar_e_salvar_relatorio(problem, ga, best_individual)
    print(f"\nOtimização concluída. Relatório salvo em: {report_path}")


if __name__ == "__main__":
    main()