"""Set Cover based rectangle packing solver using OR-Tools CP-SAT."""

from itertools import product
from typing import Tuple, List, Dict
from ortools.sat.python import cp_model


class SetCoverSolver:
    """Solver for rectangle packing using set cover formulation."""

    def __init__(
        self,
        grid: Tuple[int, int],
        shapes: List[Tuple[int, int]],
        upper_bound: int,
    ):
        self.grid = grid
        self.shapes = shapes
        self.upper_bound = upper_bound
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.x: Dict[Tuple[int, int], cp_model.BoolVarT] = {}
        self.y: Dict[Tuple[int, int, int, int], cp_model.BoolVarT] = {}
        self.cell_neighbors: Dict[Tuple[int, int], List[Tuple[int, int, int]]] = {}
        self.cell_shapes: Dict[int, List[Tuple[int, int]]] = {}

    def solve(self) -> List[Dict]:
        """Execute the complete solving pipeline."""
        self._set_iterables()
        self._set_variables()
        self._set_objective()
        self._set_constraints()
        self._optimize()
        return self._post_process()

    def _set_iterables(self):
        """Initialize problem sets and mapping relationships."""
        self.cells = [(i, j) for i in range(self.grid[0]) for j in range(self.grid[1])]

        self.extended_shapes = [
            (s, n) for s, _ in enumerate(self.shapes) for n in range(self.upper_bound)
        ]

        self.cell_shapes = {
            s: self._generate_limited_cells(shape) for s, shape in enumerate(self.shapes)
        }

        self.cell_shape_list = [
            (s, n, i, j)
            for (s, n) in self.extended_shapes
            for (i, j) in self.cell_shapes[s]
        ]

        self.cell_neighbors = {}
        for (i, j) in self.cells:
            neighbors = []
            for s, shape in enumerate(self.shapes):
                for (k, l) in self.cell_shapes[s]:
                    if self._is_valid(i, j, k, l, shape):
                        neighbors.append((s, k, l))
            self.cell_neighbors[(i, j)] = neighbors

    def _set_variables(self):
        """Create decision variables."""
        for (s, n) in self.extended_shapes:
            self.x[(s, n)] = self.model.NewBoolVar(f"x_{s}_{n}")

        for (s, n, i, j) in self.cell_shape_list:
            self.y[(s, n, i, j)] = self.model.NewBoolVar(f"y_{s}_{n}_{i}_{j}")

    def _set_objective(self):
        """Set objective: maximize the number of placed rectangles."""
        self.model.Maximize(
            sum(self.x[(s, n)] for (s, n) in self.extended_shapes)
        )

    def _set_constraints(self):
        """Add problem constraints."""
        for (s, n) in self.extended_shapes:
            self.model.Add(
                self.x[(s, n)]
                == sum(
                    self.y[(s, n, i, j)] for (i, j) in self.cell_shapes[s]
                )
            )

        for (i, j), neighbors in self.cell_neighbors.items():
            cover_vars = []
            for (s, k, l) in neighbors:
                for n in range(self.upper_bound):
                    if (s, n, k, l) in self.y:
                        cover_vars.append(self.y[(s, n, k, l)])
            if cover_vars:
                self.model.Add(sum(cover_vars) <= 1)

    def _optimize(self):
        """Configure and run the solver."""
        self.solver.parameters.max_time_in_seconds = 3600
        self.solver.parameters.num_search_workers = 8

        status = self.solver.Solve(self.model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            raise RuntimeError("No solution found!")

    def _post_process(self) -> List[Dict]:
        """Extract and return the solution."""
        blocks = []
        for (s, n, i, j) in self.cell_shape_list:
            if self.solver.Value(self.y[(s, n, i, j)]) == 1:
                w, h = self.shapes[s]
                blocks.append({
                    "shape": (w, h),
                    "position": (i, j),
                    "corners": [
                        [i, j],
                        [i + w, j],
                        [i + w, j + h],
                        [i, j + h],
                        [i, j],
                    ],
                })
        return blocks

    def _generate_limited_cells(self, shape: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate feasible placement positions for a given shape."""
        w, h = shape
        x_points = []
        for i in range(self.grid[0] // w + 1):
            for j in range(self.grid[0] // h + 1):
                x_pos = i * w + j * h
                if x_pos <= self.grid[0] - w:
                    x_points.append(x_pos)

        y_points = []
        for i in range(self.grid[1] // h + 1):
            for j in range(self.grid[1] // w + 1):
                y_pos = i * h + j * w
                if y_pos <= self.grid[1] - h:
                    y_points.append(y_pos)

        x_points = sorted(set(x_points))
        y_points = sorted(set(y_points))

        return [(x, y) for x in x_points for y in y_points]

    def _is_valid(self, i: int, j: int, k: int, l: int, shape: Tuple[int, int]) -> bool:
        """Check if cell (i, j) is covered by shape placed at (k, l)."""
        w, h = shape
        return (k <= i < k + w) and (l <= j < l + h)


if __name__ == "__main__":
    grid = (53, 32)
    shapes = [(7, 5), (5, 7)]
    upper_bound = (grid[0] // shapes[0][0]) * (grid[1] // shapes[0][1])

    solver = SetCoverSolver(grid, shapes, upper_bound)
    solution = solver.solve()

    print(f"Placed {len(solution)} rectangles")
    for block in solution:
        print(f"Rectangle {block['shape']} at position {block['position']}")