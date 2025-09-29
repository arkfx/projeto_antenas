from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any, Sequence
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.patches import Circle
import numpy as np
import config

def _load_clients(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    x_coords: list[int] = []
    y_coords: list[int] = []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                x = int(row["x"])
                y = int(row["y"])
            except (TypeError, ValueError, KeyError) as exc:  # pragma: no cover - defensive
                raise ValueError(f"Linha inválida no CSV: {row}") from exc
            x_coords.append(x)
            y_coords.append(y)

    if not x_coords:
        raise ValueError("O arquivo de clientes não contém registros.")

    return np.array(x_coords, dtype=float), np.array(y_coords, dtype=float)


_ANTENNA_LINE_RE = re.compile(
    r"Antena\s+\d+:\s*\((?P<x>-?\d+(?:\.\d+)?),\s*(?P<y>-?\d+(?:\.\d+)?)\)",
    re.IGNORECASE,
)


def _load_antennas(report_path: Path) -> list[tuple[float, float]]:
    if not report_path.exists():
        raise FileNotFoundError(f"Arquivo de relatório não encontrado: {report_path}")

    positions: list[tuple[float, float]] = []
    for raw_line in report_path.read_text(encoding="utf-8").splitlines():
        match = _ANTENNA_LINE_RE.search(raw_line)
        if match:
            x_coord = float(match.group("x"))
            y_coord = float(match.group("y"))
            positions.append((x_coord, y_coord))

    if not positions:
        raise ValueError(
            "Nenhuma coordenada de antena foi encontrada no relatório fornecido."
        )

    return positions


def _build_heatmap(
    x: np.ndarray,
    y: np.ndarray,
    *,
    bins: int,
    cmap: str,
) -> tuple[Any, Any]:
    fig, ax = plt.subplots(figsize=(8, 8))
    heatmap = ax.hist2d(
        x,
        y,
        bins=bins,
        range=[[0, config.MAP_WIDTH], [0, config.MAP_HEIGHT]],
        cmap=cmap,
    )

    cbar = fig.colorbar(heatmap[3], ax=ax, pad=0.02)
    cbar.set_label("Clientes por célula", fontsize=10)

    ax.set_title("Mapa de calor de densidade de clientes")
    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")
    ax.set_xlim(0, config.MAP_WIDTH)
    ax.set_ylim(0, config.MAP_HEIGHT)
    ax.set_aspect("equal", adjustable="box")

    return fig, ax


def _overlay_antennas(
    ax: Axes,
    positions: Sequence[tuple[float, float]],
    *,
    radius: float,
) -> None:
    if radius <= 0:
        raise ValueError("O raio da antena deve ser positivo.")

    x_coords, y_coords = zip(*positions)

    ax.scatter(
        x_coords,
        y_coords,
        s=90,
        c="#00d5ff",
        edgecolors="black",
        linewidths=0.8,
        zorder=5,
        label="Antenas",
    )

    for idx, (x_coord, y_coord) in enumerate(positions, start=1):
        circle = Circle(
            (x_coord, y_coord),
            radius,
            fill=False,
            edgecolor="#00d5ff",
            linewidth=1.2,
            linestyle="--",
            alpha=0.85,
            zorder=4,
        )
        ax.add_patch(circle)

        label = ax.text(
            x_coord,
            y_coord,
            f"A{idx}",
            fontsize=8,
            color="white",
            ha="center",
            va="center",
            zorder=6,
        )
        label.set_path_effects(
            [patheffects.Stroke(linewidth=2, foreground="black"), patheffects.Normal()]
        )

    ax.legend(loc="upper right")


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualiza os clientes como um mapa de calor baseado nas coordenadas de config.MAP_WIDTH e config.MAP_HEIGHT.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=config.CLIENT_DATA_FILE,
        help="Arquivo CSV de entrada (padrão: data/clients.csv).",
    )
    parser.add_argument(
        "--bins",
        type=int,
        default=100,
        help="Número de divisões em cada eixo para o histograma 2D (padrão: 100).",
    )
    parser.add_argument(
        "--cmap",
        default="plasma",
        help="Mapa de cores do matplotlib a ser utilizado (padrão: plasma).",
    )
    parser.add_argument(
        "--antennas",
        type=Path,
        default=config.CLIENT_DATA_FILE.parent / "relatorio_execucao.txt",
        help="Arquivo de relatório contendo as coordenadas das antenas (padrão: data/relatorio_execucao.txt).",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=config.ANTENNA_RADIUS,
        help="Raio de cobertura utilizado para desenhar cada antena (padrão: config.ANTENNA_RADIUS).",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.bins <= 0:
        parser.error("--bins deve ser um número inteiro positivo.")
    if args.radius <= 0:
        parser.error("--radius deve ser um número positivo.")

    return args


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)

    csv_path = args.input.resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {csv_path}")

    x, y = _load_clients(csv_path)
    fig, ax = _build_heatmap(x, y, bins=args.bins, cmap=args.cmap)

    try:
        antenna_positions = _load_antennas(args.antennas)
    except FileNotFoundError as exc:
        print(f"Aviso: {exc}. Nenhuma antena será desenhada.")
        antenna_positions = []
    except ValueError as exc:
        print(f"Aviso: {exc} Nenhuma antena será desenhada.")
        antenna_positions = []

    if antenna_positions:
        _overlay_antennas(ax, antenna_positions, radius=args.radius)
    else:
        ax.text(
            0.02,
            0.98,
            "Sem antenas para exibir",
            transform=ax.transAxes,
            fontsize=9,
            color="white",
            ha="left",
            va="top",
            path_effects=[
                patheffects.Stroke(linewidth=2, foreground="black"),
                patheffects.Normal(),
            ],
        )

    plt.show()


if __name__ == "__main__":
    main()
