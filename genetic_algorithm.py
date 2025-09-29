"""Algoritmo genético central para o posicionamento de antenas."""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, replace
from typing import List, Sequence, Tuple

from . import config
from .problem_domain import Problem


@dataclass(slots=True)
class Individual:
    """Representa uma única solução candidata (cromossomo + fitness)."""
    genes: List[int]
    fitness: int = -1

    def clone(self) -> "Individual":
        """Cria uma cópia rasa deste indivíduo."""
        # Usar dataclasses.replace é uma forma mais limpa de clonar.
        return replace(self)


class ProgressBar:
    """Controla a exibição da barra de progresso no console."""
    def __init__(self, total: int):
        self.total = max(total, 1)
        self.bar_width = max(config.PROGRESS_BAR_WIDTH, 10)
        self._printed = False

    def update(self, generation: int, best_fitness: int, stagnant: int) -> None:
        """Atualiza e renderiza a barra de progresso."""
        if not config.SHOW_PROGRESS:
            return

        percent = int(round((generation / self.total) * 100))
        filled = int(round((generation / self.total) * self.bar_width))
        bar = "#" * filled + "-" * (self.bar_width - filled)

        stagnation_info = ""
        if config.MAX_STAGNANT_GENERATIONS > 0:
            stagnation_info = f" | Estagnacao: {stagnant}/{config.MAX_STAGNANT_GENERATIONS}"

        status = (
            f"\rProgresso GA: [{bar}] {percent:3d}% "
            f"Geracao {generation}/{self.total} | Melhor fitness: {best_fitness}{stagnation_info}"
        )
        sys.stdout.write(status)
        sys.stdout.flush()
        self._printed = True

    def finish(self) -> None:
        """Finaliza a barra de progresso com uma nova linha."""
        if self._printed and config.SHOW_PROGRESS:
            sys.stdout.write("\n")
            sys.stdout.flush()
        self._printed = False


class GeneticAlgorithm:
    """Algoritmo genético binário para o problema de posicionamento de antenas."""

    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.population: List[Individual] = []
        self._rng = random.Random(config.RANDOM_SEED)
        self.generations_run: int = 0

    def run(self) -> Individual:
        """Executa o algoritmo genético e retorna o melhor indivíduo encontrado."""
        progress_bar = ProgressBar(config.MAX_GENERATIONS)
        
        self._initialize_population()
        self._evaluate_population()

        best_overall = max(self.population, key=lambda ind: ind.fitness).clone()
        stagnant_generations = 0

        progress_bar.update(0, best_overall.fitness, stagnant_generations)

        for i in range(1, config.MAX_GENERATIONS + 1):
            self.generations_run = i
            
            # 1. Evolução: Cria a próxima geração
            self.population = self._breed_next_generation()
            
            # 2. Avaliação: Calcula o fitness da nova população
            self._evaluate_population()

            # 3. Atualização: Verifica o progresso e o melhor indivíduo
            current_best = max(self.population, key=lambda ind: ind.fitness)
            if current_best.fitness > best_overall.fitness:
                best_overall = current_best.clone()
                stagnant_generations = 0
            else:
                stagnant_generations += 1

            progress_bar.update(i, best_overall.fitness, stagnant_generations)

            # 4. Critério de Parada: Verifica estagnação
            if stagnant_generations >= config.MAX_STAGNANT_GENERATIONS:
                break
        
        progress_bar.finish()
        return best_overall

    def _initialize_population(self) -> None:
        """Cria a população inicial com cromossomos aleatórios."""
        chromosome_length = self.problem.chromosome_length
        self.population = [
            Individual([self._rng.randint(0, 1) for _ in range(chromosome_length)])
            for _ in range(config.POPULATION_SIZE)
        ]

    def _evaluate_population(self) -> None:
        """Calcula o fitness de cada indivíduo na população atual."""
        for individual in self.population:
            individual.fitness = self.problem.calculate_fitness(individual.genes)
    
    def _breed_next_generation(self) -> List[Individual]:
        """Cria a próxima geração através de elitismo, seleção, crossover e mutação."""
        # Elitismo: os melhores indivíduos passam diretamente para a próxima geração.
        elite = sorted(self.population, key=lambda ind: ind.fitness, reverse=True)
        next_generation = [ind.clone() for ind in elite[:config.ELITISM_COUNT]]
        
        # Preenche o resto da população com descendentes.
        while len(next_generation) < config.POPULATION_SIZE:
            parent1 = self._roulette_selection()
            parent2 = self._roulette_selection()
            
            if self._rng.random() < config.CROSSOVER_RATE:
                child_genes_a, child_genes_b = self._crossover(parent1.genes, parent2.genes)
            else:
                child_genes_a, child_genes_b = parent1.genes[:], parent2.genes[:]

            self._mutate(child_genes_a)
            self._mutate(child_genes_b)
            
            next_generation.append(Individual(child_genes_a))
            if len(next_generation) < config.POPULATION_SIZE:
                next_generation.append(Individual(child_genes_b))
        
        return next_generation[:config.POPULATION_SIZE]

    def _roulette_selection(self) -> Individual:
        """Seleciona um indivíduo usando o método da roleta."""
        # `random.choices` é a forma moderna e eficiente de fazer seleção por roleta.
        weights = [max(ind.fitness, 0) for ind in self.population]
        
        # O `k=1` retorna uma lista com 1 item, então pegamos o primeiro com `[0]`.
        return self._rng.choices(self.population, weights=weights, k=1)[0]

    def _crossover(self, parent_a: List[int], parent_b: List[int]) -> Tuple[List[int], List[int]]:
        """Executa crossover de dois pontos."""
        length = len(parent_a)
        if length < 3:
            return parent_a[:], parent_b[:]
        
        # Escolhe dois pontos de corte distintos e ordenados.
        p1, p2 = sorted(self._rng.sample(range(1, length), 2))
        
        # Cria os filhos trocando o segmento central.
        child1 = parent_a[:p1] + parent_b[p1:p2] + parent_a[p2:]
        child2 = parent_b[:p1] + parent_a[p1:p2] + parent_b[p2:]
        
        return child1, child2

    def _mutate(self, genes: List[int]) -> None:
        """Aplica mutação de inversão de bit (bit-flip) nos genes."""
        for i in range(len(genes)):
            if self._rng.random() < config.MUTATION_RATE:
                genes[i] = 1 - genes[i] # Forma simples de inverter 0 e 1.