# 🧩 Rectangle Packing

> **Constraint Programming-based 2D Rectangle Packing & Guillotine Cutting Toolkit**

A lightweight Python toolkit for solving 2D rectangle packing and guillotine cutting problems using Google's OR-Tools CP-SAT solver. Designed for integration into the `puzzlekit` ecosystem.

---


## 🎯 Overview

This project provides two distinct constraint programming approaches for 2D rectangle packing:

| Solver             | Problem Type                   | Key Idea                                            | Best For                                        |
| ------------------ | ------------------------------ | --------------------------------------------------- | ----------------------------------------------- |
| `SetCoverSolver`   | Non-guillotine packing         | Set cover + cell coverage constraints               | Small-to-medium instances, arbitrary placements |
| `GuillotineSolver` | Guillotine-constrained cutting | Recursive plate decomposition (Furini et al., 2016) | Industrial cutting, hierarchical cuts           |

---

## 🏁 Quick Start

### Example 1: Set Cover Packing

```python
from solvers.set_cover_solver import SetCoverSolver
from visualization.plot_utils import visualize_cutting_result

# Problem definition
grid = (53, 32)  # Stock sheet: 53×32 units
shapes = [(7, 5), (5, 7)]  # Allowed rectangle dimensions
upper_bound = (grid[0] // 7) * (grid[1] // 5)  # Heuristic upper limit

# Solve
solver = SetCoverSolver(grid, shapes, upper_bound)
solution = solver.solve()

# Output
print(f"✓ Placed {len(solution)} rectangles")
for block in solution:
    print(f"  • {block['shape']} @ {block['position']}")

# Visualize
fig = visualize_cutting_result(grid, solution, title="Set Cover Packing")
fig.savefig("result_setcover.png", dpi=300)
```

### Example 2: Guillotine Cutting

```python
from solvers.guillotine_solver import GuillotineSolver
from visualization.plot_utils import visualize_cutting_result

grid = (129, 57)
shapes = [(7, 5), (5, 7), (4, 6), (6, 4), (7, 9), (9, 7)]
upper_bound = (grid[0] // 4) * (grid[1] // 4)  # Conservative estimate

solver = GuillotineSolver(grid, shapes, upper_bound)
blocks, cuts = solver.solve()

print(f"✓ Produced {len(blocks)} items with {len(cuts)} guillotine cuts")

fig = visualize_cutting_result(grid, blocks, cuts, title="Guillotine Cutting")
fig.savefig("result_guillotine.png", dpi=300)
```

---

## 🧠 Algorithm Details

### Set Cover Formulation

The `SetCoverSolver` models rectangle packing as a **maximum coverage problem**:

1. **Discretization**: The stock sheet is divided into unit cells `(i, j)`.
2. **Placement Candidates**: For each shape `s`, precompute all feasible top-left positions `(x, y)` where the shape fits.
3. **Decision Variables**:
   ```python
   # x[s, n]: whether the n-th copy of shape s is used
   x[(s, n)] = model.NewBoolVar(f"x_{s}_{n}")
   
   # y[s, n, i, j]: whether copy n of shape s is placed at (i, j)
   y[(s, n, i, j)] = model.NewBoolVar(f"y_{s}_{n}_{i}_{j}")
   ```
4. **Constraints**:
   - **Assignment**: If a shape copy is used, it must be assigned to exactly one position:
     ```python
     model.Add(x[(s, n)] == sum(y[(s, n, i, j)] for (i, j) in feasible_positions))
     ```
   - **Non-overlap**: Each cell can be covered by at most one rectangle:
     ```python
     model.Add(sum(covering_vars) <= 1)  # for each cell (i, j)
     ```
5. **Objective**: Maximize the total number of placed rectangles:
   ```python
   model.Maximize(sum(x[(s, n)] for (s, n) in extended_shapes))
   ```

✅ **Strengths**: Flexible placement, no cutting constraints  
⚠️ **Limitations**: Scales with grid resolution; best for grids ≤ 100×100

---

### Guillotine Cutting Model

The `GuillotineSolver` implements the **plate decomposition model** from Furini et al. (2016):

1. **Plate Enumeration**: Recursively generate all sub-plates reachable via guillotine cuts from the original stock sheet.
   ```python
   def _plate_variable_enumeration(self):
       # BFS-style expansion of plate configurations
       while un_processed:
           plate = cap_j[plate_idx]
           for orient in ['h', 'v']:
               for pos in feasible_cut_positions(plate, orient):
                   plate1, plate2 = _cut(plate, orient, pos)
                   # Add new plates to enumeration...
   ```

2. **Flow-Based Variables**:
   - `y[j]`: Number of final items of type `j` produced
   - `x[plate, pos, orient]`: Number of times a cut is applied to a plate

3. **Flow Conservation Constraints**:
   ```python
   # For each item type j:
   # (incoming cuts) - (outgoing cuts) - (items produced) >= 0
   model.Add(sum(incoming) - sum(outgoing) - y[j] >= 0)
   
   # For intermediate plates (except root):
   model.Add(sum(incoming) - sum(outgoing) >= 0)
   
   # Root plate can be cut at most once:
   model.Add(sum(root_cuts) <= 1)
   ```

4. **Objective**: Maximize total items produced:
   ```python
   model.Maximize(sum(y[j] for j in item_indices))
   ```

✅ **Strengths**: Models industrial cutting constraints; scales better for large sheets  
⚠️ **Limitations**: Restricted to guillotine-cut patterns only

