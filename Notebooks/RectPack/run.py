"""Example usage of rectangle packing solvers."""

import matplotlib.pyplot as plt
from set_cover_packer import SetCoverSolver
from guillotine_packer import GuillotineSolver
from visualize import visualize_cutting_result


def run_set_cover_example():
    """Run the SetCoverSolver example."""
    print("=== Set Cover Solver ===")
    grid = (53, 32)
    shapes = [(7, 5), (5, 7)]
    upper_bound = (grid[0] // shapes[0][0]) * (grid[1] // shapes[0][1])

    solver = SetCoverSolver(grid, shapes, upper_bound)
    solution = solver.solve()

    print(f"Placed {len(solution)} rectangles")
    for block in solution:
        print(f"  Rectangle {block['shape']} at {block['position']}")

    fig = visualize_cutting_result(
        grid, solution, title = f"Set Cover Packing: {grid[0]}x{grid[1]} with Rectangles"
    )
    plt.savefig("./Notebooks/RectPack/fig/set_cover_pack.png")
    print("Saved  figure ✅.")

def run_guillotine_example():
    """Run the GuillotineSolver example."""
    print("\n=== Guillotine Solver ===")
    grid =  (23, 34)
    shapes = [(7, 5), (5, 7), (4, 9)]
    upper_bound = (grid[0] // shapes[0][0]) * (grid[1] // shapes[0][1])

    solver = GuillotineSolver(grid, shapes, upper_bound)
    blocks, cuts = solver.solve()

    print(f"Produced {len(blocks)} rectangles")
    for block in blocks:
        print(f"  Rectangle {block['shape']} at {block['position']}")
    print(f"Generated {len(cuts)} cut lines")

    fig = visualize_cutting_result(
        grid, blocks, cuts, title=f"Guillotine Cutting: {grid[0]}x{grid[1]} with Multiple Shapes"
    )
    # plt.show()
    plt.savefig("./Notebooks/RectPack/fig/guillotine.png")
    print("Saved  figure ✅.")


if __name__ == "__main__":
    # run_set_cover_example()
    run_guillotine_example()