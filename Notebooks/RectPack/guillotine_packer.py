"""Guillotine cutting solver based on Furini et al. (2016) using OR-Tools CP-SAT."""

from typing import Tuple, List, Dict, Set
from dataclasses import dataclass, field
from queue import SimpleQueue
from ortools.sat.python import cp_model


@dataclass(eq=True, frozen=True, unsafe_hash=True)
class Rect:
    """Immutable rectangle representation."""
    width: int
    height: int


class GuillotineSolver:
    """
    Guillotine cutting model based on Furini et al. (2016).
    
    References:
        Fabio Furini, Enrico Malaguti, Dimitri Thomopulos (2016) 
        Modeling Two-Dimensional Guillotine Cutting Problems via Integer Programming. 
        INFORMS Journal on Computing 28(4):736-751.
    """

    def __init__(
        self,
        grid: Tuple[int, int],
        shapes: List[Tuple[int, int]],
        upper_bound: int,
    ):
        self.grid = grid
        self.shapes = shapes
        self.upper_bound = upper_bound
        self.orients = {"h", "v"}

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.cap_j: Dict[int, Rect] = {}
        self.cap_j_plates: Set[int] = set()
        self.cap_j_items: Set[int] = set()
        self.cut_pos_dict: Dict[Tuple[int, str], List[int]] = {}
        self.plate_cut_dict: Dict[Tuple[int, int, str], List[int]] = {}
        self.inverse_plate_cut_dict: Dict[Tuple[int, str], List[Tuple[int, int]]] = {}
        self.cut_set: Set[Tuple[int, int, str]] = set()

        self.y: Dict[int, cp_model.IntVar] = {}
        self.x: Dict[Tuple[int, int, str], cp_model.IntVar] = {}

    def solve(self) -> Tuple[List[Dict], List[List]]:
        """Execute the complete solving pipeline."""
        self._plate_variable_enumeration()
        self._set_variables()
        self._set_objective()
        self._set_constraints()
        self._optimize()
        return self._post_process()

    def _plate_variable_enumeration(self):
        """Enumerate all possible plates and cut positions."""
        cut_pos_dict = {}
        shape_j = set()
        cap_j = {}
        inverse_cap_j = {}
        cap_j_set = set()
        un_processed = set()

        grid_rect = Rect(self.grid[0], self.grid[1])
        cap_j[0] = grid_rect
        inverse_cap_j[grid_rect] = 0
        cap_j_set.add(grid_rect)
        un_processed.add(0)

        for shape in self.shapes:
            rect_shape = Rect(shape[0], shape[1])
            count = len(cap_j)
            cap_j[count] = rect_shape
            inverse_cap_j[rect_shape] = count
            cap_j_set.add(rect_shape)
            shape_j.add(count)

        x_set = set()
        cut_dict = {}
        inverse_cut_dict = {}

        while un_processed:
            plate_idx = un_processed.pop()
            plate = cap_j[plate_idx]
            for o in self.orients:
                positions = self._compute_possible_cut_positions(plate, o)
                cut_pos_dict[(plate_idx, o)] = positions
                for position in positions:
                    plate1, plate2 = self._cut(plate, o, position)

                    if plate1 not in cap_j_set:
                        count = len(cap_j)
                        cap_j[count] = plate1
                        inverse_cap_j[plate1] = count
                        cap_j_set.add(plate1)
                        un_processed.add(count)

                    if plate2 not in cap_j_set:
                        count = len(cap_j)
                        cap_j[count] = plate2
                        inverse_cap_j[plate2] = count
                        cap_j_set.add(plate2)
                        un_processed.add(count)

                    cut_key = (plate_idx, position, o)
                    x_set.add(cut_key)

                    plate1_idx = inverse_cap_j[plate1]
                    plate2_idx = inverse_cap_j[plate2]
                    cut_dict[cut_key] = [plate1_idx, plate2_idx]

                    inverse_cut_dict.setdefault((plate1_idx, o), []).append(
                        (position, plate_idx)
                    )
                    inverse_cut_dict.setdefault((plate2_idx, o), []).append(
                        (position, plate_idx)
                    )

        self.cap_j = cap_j
        self.cap_j_items = shape_j
        self.cut_set = x_set
        self.plate_cut_dict = cut_dict
        self.inverse_plate_cut_dict = inverse_cut_dict
        self.cut_pos_dict = cut_pos_dict
        self.cap_j_plates = set(cap_j.keys()).difference(shape_j)

    def _set_variables(self):
        """Create decision variables."""
        for j in self.cap_j_items:
            self.y[j] = self.model.NewIntVar(0, self.upper_bound, f"y_{j}")

        for cut_key in self.cut_set:
            self.x[cut_key] = self.model.NewIntVar(0, self.upper_bound, f"x_{cut_key}")

    def _set_objective(self):
        """Set objective: maximize the number of produced items."""
        self.model.Maximize(sum(self.y[j] for j in self.cap_j_items))

    def _set_constraints(self):
        """Add problem constraints."""
        for j in self.cap_j_items:
            incoming_cuts = []
            for o in self.orients:
                if (j, o) in self.inverse_plate_cut_dict:
                    for pos, plate in self.inverse_plate_cut_dict[(j, o)]:
                        cut_key = (plate, pos, o)
                        if cut_key in self.x:
                            incoming_cuts.append(self.x[cut_key])

            outgoing_cuts = []
            for o in self.orients:
                if (j, o) in self.cut_pos_dict:
                    for pos in self.cut_pos_dict[(j, o)]:
                        cut_key = (j, pos, o)
                        if cut_key in self.x:
                            outgoing_cuts.append(self.x[cut_key])

            self.model.Add(sum(incoming_cuts) - sum(outgoing_cuts) - self.y[j] >= 0)

        for j in self.cap_j_plates:
            if j == 0:
                continue

            incoming_cuts = []
            for o in self.orients:
                if (j, o) in self.inverse_plate_cut_dict:
                    for pos, plate in self.inverse_plate_cut_dict[(j, o)]:
                        cut_key = (plate, pos, o)
                        if cut_key in self.x:
                            incoming_cuts.append(self.x[cut_key])

            outgoing_cuts = []
            for o in self.orients:
                if (j, o) in self.cut_pos_dict:
                    for pos in self.cut_pos_dict[(j, o)]:
                        cut_key = (j, pos, o)
                        if cut_key in self.x:
                            outgoing_cuts.append(self.x[cut_key])

            self.model.Add(sum(incoming_cuts) - sum(outgoing_cuts) >= 0)

        original_cuts = []
        for o in self.orients:
            if (0, o) in self.cut_pos_dict:
                for pos in self.cut_pos_dict[(0, o)]:
                    cut_key = (0, pos, o)
                    if cut_key in self.x:
                        original_cuts.append(self.x[cut_key])

        if original_cuts:
            self.model.Add(sum(original_cuts) <= 1)

    def _optimize(self):
        """Configure and run the solver."""
        self.solver.parameters.max_time_in_seconds = 3600
        self.solver.parameters.num_search_workers = 8

        status = self.solver.Solve(self.model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            raise RuntimeError("No solution found!")

    def _post_process(self) -> Tuple[List[Dict], List[List]]:
        """Extract and return the solution."""
        result_y = {}
        result_x = {}

        for j in self.cap_j_items:
            value = self.solver.Value(self.y[j])
            if value > 0:
                result_y[j] = value

        for cut_key in self.cut_set:
            value = self.solver.Value(self.x[cut_key])
            if value > 0:
                plate_idx, pos, o = cut_key
                result_x[plate_idx] = ((pos, o), value)

        return self._get_final_results(result_y, result_x)

    def _compute_possible_cut_positions(self, plate: Rect, o: str) -> List[int]:
        """Compute feasible cut positions for a plate."""
        positions = set()

        if o == "h":
            for shape in self.shapes:
                if shape[1] <= plate.height:
                    for h in range(shape[1], plate.height, shape[1]):
                        positions.add(h)
            positions = [p for p in positions if 0 < p < plate.height]

        elif o == "v":
            for shape in self.shapes:
                if shape[0] <= plate.width:
                    for w in range(shape[0], plate.width, shape[0]):
                        positions.add(w)
            positions = [p for p in positions if 0 < p < plate.width]

        else:
            raise ValueError(f"Unknown cut orientation: {o}")

        return sorted(positions)

    def _cut(self, plate: Rect, o: str, pos: int) -> Tuple[Rect, Rect]:
        """Execute a guillotine cut on a plate."""
        if o == "v":
            plate1 = Rect(pos, plate.height)
            plate2 = Rect(plate.width - pos, plate.height)
        elif o == "h":
            plate1 = Rect(plate.width, pos)
            plate2 = Rect(plate.width, plate.height - pos)
        else:
            raise ValueError(f"Unknown cut orientation: {o}")
        return plate1, plate2

    def _get_final_results(
        self, result_y: Dict[int, int], result_x: Dict[int, Tuple[Tuple[int, str], int]]
    ) -> Tuple[List[Dict], List[List]]:
        """Extract placed blocks and cut lines from the solution."""
        blocks = []
        cuts = []

        unprocessed = SimpleQueue()
        unprocessed.put((0, 0, 0))

        while not unprocessed.empty():
            plate_idx, start_x, start_y = unprocessed.get()
            plate = self.cap_j[plate_idx]

            if plate_idx in result_x:
                (pos, orient), _ = result_x[plate_idx]
                plate1_idx, plate2_idx = self.plate_cut_dict[(plate_idx, pos, orient)]
                plate1 = self.cap_j[plate1_idx]
                plate2 = self.cap_j[plate2_idx]

                if orient == "h":
                    cuts.append([[start_x, start_y + pos], [start_x + plate.width, start_y + pos]])
                    unprocessed.put((plate1_idx, start_x, start_y))
                    unprocessed.put((plate2_idx, start_x, start_y + pos))

                elif orient == "v":
                    cuts.append([[start_x + pos, start_y], [start_x + pos, start_y + plate.height]])
                    unprocessed.put((plate1_idx, start_x, start_y))
                    unprocessed.put((plate2_idx, start_x + pos, start_y))
            else:
                if plate_idx in self.cap_j_items:
                    blocks.append({
                        "shape": (plate.width, plate.height),
                        "position": (start_x, start_y),
                        "corners": [
                            [start_x, start_y],
                            [start_x + plate.width, start_y],
                            [start_x + plate.width, start_y + plate.height],
                            [start_x, start_y + plate.height],
                            [start_x, start_y],
                        ],
                    })

        return blocks, cuts


if __name__ == "__main__":
    grid = (129, 57)
    shapes = [(7, 5), (5, 7), (4, 6), (6, 4), (7, 9), (9, 7)]
    upper_bound = (grid[0] // shapes[0][0]) * (grid[1] // shapes[0][1])

    solver = GuillotineSolver(grid, shapes, upper_bound)
    blocks, cuts = solver.solve()

    print(f"Produced {len(blocks)} rectangles")
    for block in blocks:
        print(f"Rectangle {block['shape']} at position {block['position']}")

    print(f"Generated {len(cuts)} cut lines")
    for i, cut in enumerate(cuts):
        print(f"Cut {i + 1}: from {cut[0]} to {cut[1]}")