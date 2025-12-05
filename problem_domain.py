"""Utilidades específicas do problema para o algoritmo genético de posicionamento de antenas."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class Client:
    """Representação imutável de um ponto de demanda (cliente)."""
    identifier: str
    x: float
    y: float


def load_clients(csv_path: Path) -> list[Client]:
    """Carrega o conjunto de clientes a partir de um arquivo CSV usando o módulo `csv`."""
    clients = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row or len(row) < 3:
                continue
            try:
                # Desempacota e converte de uma vez
                identifier, x_str, y_str = row[:3]
                clients.append(Client(identifier, float(x_str), float(y_str)))
            except ValueError:
                # Trata cabeçalho ou linhas malformadas sem interromper
                continue
    return clients


class Problem:
    """Encapsula o domínio de posicionamento de antenas para cromossomos binários."""
    def __init__(
        self,
        *,
        clients: list[Client],
        num_antennas: int,
        bits_per_coord: int,
        map_width: int,
        map_height: int,
        coverage_radius: float,
    ) -> None:
        self.clients = clients
        self.num_antennas = num_antennas
        self.bits_per_coord = bits_per_coord
        self.map_width = map_width
        self.map_height = map_height
        self.coverage_radius = coverage_radius
        self.chromosome_length = num_antennas * bits_per_coord * 2
        self._clients_array = np.array(
            [(client.x, client.y) for client in clients],
            dtype=float,
        )
        self._radius_sq = float(coverage_radius) ** 2

    def decode(self, genes: Sequence[int]) -> list[tuple[int, int]]:
        """Converte um cromossomo binário em coordenadas de antenas."""
        if len(genes) != self.chromosome_length:
            raise ValueError("Tamanho do cromossomo inconsistente.")

        coords = []
        genes_per_antenna = self.bits_per_coord * 2
        for i in range(self.num_antennas):
            start = i * genes_per_antenna
            mid = start + self.bits_per_coord
            end = start + genes_per_antenna

            x_val = _bits_to_int(genes[start:mid])
            y_val = _bits_to_int(genes[mid:end])

            coords.append((min(x_val, self.map_width), min(y_val, self.map_height)))
        return coords

    def calculate_fitness(self, genes: Sequence[int]) -> int:
        """Avalia o fitness como o número de clientes distintos cobertos."""
        if self._clients_array.size == 0:
            return 0

        antenna_positions = np.asarray(self.decode(genes), dtype=float)
        if antenna_positions.size == 0:
            return 0

        deltas = self._clients_array[:, None, :] - antenna_positions[None, :, :]
        distances_sq = np.square(deltas, dtype=float).sum(axis=2)
        covered = np.any(distances_sq <= self._radius_sq, axis=1)
        return int(np.count_nonzero(covered))


def _bits_to_int(bits: Sequence[int]) -> int:
    """Converte uma sequência de bits (0 e 1) para um inteiro."""
    return int("".join(map(str, bits)), 2)