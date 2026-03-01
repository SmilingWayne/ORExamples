"""Visualization utilities for rectangle packing results."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from typing import List, Dict, Tuple, Optional


def visualize_cutting_result(
    grid: Tuple[int, int],
    blocks: List[Dict],
    cuts: Optional[List[List]] = None,
    title: str = "Cutting Result",
    show_dimensions: bool = True,
    figsize: Tuple[int, int] = (12, 8),
) -> plt.Figure:
    """
    Visualize the rectangle packing or cutting result.

    Parameters
    ----------
    grid : Tuple[int, int]
        Dimensions of the stock sheet (width, height).
    blocks : List[Dict]
        List of placed rectangles, each containing:
        - 'shape': (width, height)
        - 'position': (x, y) bottom-left corner
        - 'corners': list of corner coordinates
    cuts : List[List], optional
        List of cut lines, each defined by two endpoints.
    title : str, optional
        Plot title.
    show_dimensions : bool, optional
        Whether to annotate rectangle dimensions.
    figsize : Tuple[int, int], optional
        Figure size in inches.

    Returns
    -------
    plt.Figure
        The matplotlib figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.set_xlim(0, grid[0])
    ax.set_ylim(0, grid[1])

    ax.add_patch(
        patches.Rectangle(
            (0, 0),
            grid[0],
            grid[1],
            edgecolor="black",
            facecolor="none",
            linewidth=2,
        )
    )

    colors = plt.cm.tab20.colors
    random.shuffle(colors)

    for i, block in enumerate(blocks):
        shape = block["shape"]
        pos_x, pos_y = block["position"]
        width, height = shape

        color = colors[i % len(colors)]

        rect = patches.Rectangle(
            (pos_x, pos_y),
            width,
            height,
            edgecolor="black",
            facecolor=color,
            linewidth=2,
            alpha=0.7,
        )
        ax.add_patch(rect)

        center_x = pos_x + width / 2
        center_y = pos_y + height / 2
        ax.text(
            center_x,
            center_y,
            f"{i + 1}",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
        )

        if show_dimensions:
            ax.text(
                pos_x + width / 2,
                pos_y - 0.5,
                f"{width}",
                fontsize=10,
                ha="center",
                va="top",
            )
            ax.text(
                pos_x - 0.5,
                pos_y + height / 2,
                f"{height}",
                fontsize=10,
                ha="right",
                va="center",
                rotation=90,
            )

    if cuts:
        for cut in cuts:
            start, end = cut
            ax.plot(
                [start[0], end[0]],
                [start[1], end[1]],
                "r--",
                linewidth=2,
                alpha=0.7,
            )

    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Width", fontsize=12)
    ax.set_ylabel("Height", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_aspect("equal")

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    from solvers.guillotine_solver import GuillotineSolver

    grid = (129, 57)
    shapes = [(7, 5), (5, 7), (4, 6), (6, 4), (7, 9), (9, 7)]
    upper_bound = (grid[0] // shapes[0][0]) * (grid[1] // shapes[0][1])

    solver = GuillotineSolver(grid, shapes, upper_bound)
    blocks, cuts = solver.solve()

    fig = visualize_cutting_result(
        grid, blocks, cuts, title="Guillotine Cutting: 129×57 with 7×5 Rectangles"
    )
    plt.show()