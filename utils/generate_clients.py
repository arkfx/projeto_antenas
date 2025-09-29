from __future__ import annotations

import argparse
import csv
import math
from random import Random
from typing import Sequence

import config


def _generate_clients(count: int, rng: Random, cluster_count: int) -> list[tuple[str, int, int]]:
    """Gera dados de clientes em um número definido de clusters."""
    if count <= 0:
        return []

    width, height = config.MAP_WIDTH, config.MAP_HEIGHT
    shortest_side = min(width, height)

    def _sample_coordinate(center: float, spread: float, upper_bound: int) -> int:
        value = center
        for _ in range(8):
            value = rng.gauss(center, spread)
            if 0 <= value <= upper_bound:
                break
        return int(round(max(0.0, min(float(upper_bound), value))))

    cluster_sizes = [1] * cluster_count
    for _ in range(max(0, count - cluster_count)):
        cluster_sizes[rng.randrange(cluster_count)] += 1

    clusters = [
        (rng.uniform(0, width), rng.uniform(0, height), rng.uniform(0.025, 0.05) * shortest_side)
        for _ in range(cluster_count)
    ]

    clients: list[tuple[str, int, int]] = []
    client_id = 1
    for (cx, cy, spread), size in zip(clusters, cluster_sizes):
        for _ in range(size):
            x = _sample_coordinate(cx, spread, width)
            y = _sample_coordinate(cy, spread, height)
            clients.append((f"C{client_id:03d}", x, y))
            client_id += 1

    return clients


def main(argv: Sequence[str] | None = None) -> None:
    """Função principal que analisa args, gera e escreve os dados dos clientes."""
    parser = argparse.ArgumentParser(
        description="Gera clientes sintéticos respeitando os limites do mapa definidos em config.py."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=(config.MAP_HEIGHT * config.MAP_WIDTH) // 16,
        help="Quantidade de clientes a gerar (padrão 6.25% do maximo de clientes).",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=4,
        help="Número de clusters de clientes a serem gerados (padrão: 4).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=config.RANDOM_SEED,
        help="Semente aleatória a usar (padrão: RANDOM_SEED de config.py).",
    )
    args = parser.parse_args(argv)
    rng = Random(args.seed)
    rows = _generate_clients(args.count, rng, args.clusters)
    target = config.CLIENT_DATA_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "x", "y"])
        writer.writerows(rows)

    print(f"{len(rows)} clientes escritos em {target}")


if __name__ == "__main__":
    main()