# Minimum Circle Cover (Smallest Enclosing Circle) Problem

## Problem Definition

Given a set of points in the plane, find the circle of minimum radius that encloses all points.

This is also known as the **smallest enclosing circle problem** or **minimum bounding circle problem**.

## Algorithms Implemented

### 1. Welzl's Randomized Algorithm (Primary)

Welzl's algorithm (1991) is a randomized incremental algorithm that runs in expected linear time O(n).

#### Key Idea:
- Randomly permute the input points
- Maintain a current circle that encloses processed points
- When a point lies outside the current circle, recursively compute a new circle that must include this point on its boundary
- The recursion uses a "support set" of points that must lie on the circle's boundary

#### Algorithm Steps:
```
function welzl(P, R):
    if P is empty or |R| = 3:
        return trivial_circle(R)

    choose random p ∈ P
    D = welzl(P \ {p}, R)

    if p ∈ D:
        return D
    else:
        return welzl(P \ {p}, R ∪ {p})
```

#### Time Complexity:
- Expected O(n) where n is number of points
- Worst case O(n!) but practically very efficient

#### Space Complexity:
- O(n) due to recursion stack

### 2. Naive Brute Force Algorithm (For Verification)

Examines all possible circles defined by:
1. Single points (radius 0)
2. Pairs of points (diameter circle)
3. Triples of points (circumcircle)

Time complexity: O(n⁴) - only suitable for small n (≤ 10)

## Implementation Details

### Data Structures

#### `Point` class:
- Stores coordinates as numpy array
- Supports n-dimensional points (though some operations are 2D-specific)
- Methods for distance calculation and vector operations

#### `Circle` class:
- Stores center (Point) and radius
- `contains()` method checks if a point is inside (with tolerance)
- Static methods for constructing circles from 1-3 points

### Key Functions

1. `circle_from_two_points(p1, p2)`:
   - Returns circle with diameter p1-p2
   - Center is midpoint, radius is half distance

2. `circle_from_three_points(p1, p2, p3)`:
   - Returns circumcircle through three points
   - Uses determinant formula for 2D points
   - Handles collinear points by falling back to diameter circle

3. `welzl_algorithm(points, support)`:
   - Recursive implementation of Welzl's algorithm
   - Uses backtracking for support set management

4. `min_circle_welzl(points, random_seed)`:
   - Wrapper that shuffles points and calls welzl_algorithm
   - Supports reproducible results via random seed

## Usage Example

```python
from min_circle_cover import Point, min_circle_welzl

# Create points
points = [
    Point([0, 0]),
    Point([1, 0]),
    Point([0, 1]),
    Point([0.5, 0.5])
]

# Compute minimum enclosing circle
circle = min_circle_welzl(points, random_seed=42)

print(f"Center: {circle.center.coords}")
print(f"Radius: {circle.radius}")

# Check if all points are inside
for p in points:
    print(f"Point {p.coords} inside: {circle.contains(p)}")
```

## Extension to Higher Dimensions

### Current Limitations:
1. `circle_from_three_points` uses 2D-specific formula
2. Base case for Welzl assumes at most 3 support points (in 2D)

### Generalization Approach:

#### For d-dimensional spheres:
1. A sphere in d dimensions is defined by d+1 points in general position
2. Welzl's algorithm generalizes with support set size ≤ d+1
3. Circumsphere calculation requires solving linear equations

#### Required Changes:
1. Replace `circle_from_three_points` with `sphere_from_points` that:
   - Solves linear system for center coordinates
   - Uses more robust numerical methods (SVD for near-degenerate cases)

2. Update base case condition from `|R| = 3` to `|R| = d+1`

3. Use dimensional geometry libraries for robust computations

### Suggested Implementation Path:
```python
class Sphere:
    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

    @staticmethod
    def from_points(points: List[Point]) -> 'Sphere':
        """Compute smallest sphere enclosing given points (1 to d+1 points)."""
        # Use linear algebra to solve for center
        # Radius = distance from center to any point
        pass

def welzl_nd(points: List[Point], support: List[Point], dimension: int) -> Sphere:
    """Welzl algorithm for d-dimensional spheres."""
    if len(points) == 0 or len(support) == dimension + 1:
        return Sphere.from_points(support)
    # ... similar to 2D version
```

## Higher-Dimensional Implementation

A complete implementation for arbitrary dimensions is provided in `min_sphere_cover.py`. This implementation generalizes Welzl's algorithm to d-dimensional spaces.

### Key Features:
1. **Dimension-agnostic**: Works for any dimension d ≥ 2
2. **Robust geometry**: Uses least-squares solving for circumsphere computation
3. **Degeneracy handling**: Falls back to subset methods for collinear/coplanar points
4. **Backward compatibility**: For 2D points, results match the 2D circle implementation

### Usage Example:
```python
from min_sphere_cover import PointND, min_sphere_welzl

# 3D points
points = [
    PointND([0, 0, 0]),
    PointND([1, 0, 0]),
    PointND([0, 1, 0]),
    PointND([0, 0, 1])
]

sphere = min_sphere_welzl(points, random_seed=42)
print(f"Center: {sphere.center.coords}")
print(f"Radius: {sphere.radius}")
```

### Implementation Notes:
- The `SphereND` class represents spheres in n-dimensional space
- `SphereND.from_points()` uses linear least squares to compute the smallest enclosing sphere for 1 to d+1 points
- The Welzl algorithm is parameterized by dimension, with base case `|support| = d+1`
- For degenerate cases (points lying on a lower-dimensional subspace), the algorithm automatically falls back to appropriate subsets

## Performance Considerations

### Numerical Stability:
- Use tolerance (1e-9) for containment checks
- Handle near-collinear/coplanar points gracefully
- Consider using `decimal` or `fractions` for exact arithmetic in small cases

### Large Point Sets:
- Welzl algorithm works well for thousands of points
- For very large sets, consider approximation algorithms
- Parallelization possible: partition points, compute circles, merge

## Applications

1. **Computer Graphics**: Bounding volumes for collision detection
2. **Geographic Information Systems**: Service area determination
3. **Robotics**: Workspace analysis and path planning
4. **Machine Learning**: Support vector data description (one-class classification)
5. **Manufacturing**: Minimum material usage for circular parts

## Testing and Validation

The implementation includes:
1. Unit tests for basic cases (1-3 points)
2. Comparison with brute force for small n
3. Random point generation for stress testing

To run tests:
```python
python min_circle_cover.py
```

## Visualization

A visualization script `visualize.py` is provided to generate plots of points and their minimum enclosing circles.

### Features:
- Points displayed as blue circles
- Minimum enclosing circle shown in red
- Circle center marked with red 'x'
- Radius shown as green dashed line
- Information box with center coordinates, radius, and coverage statistics
- Multiple example configurations

### Generated Examples:
1. **Triangle**: Three points forming a right triangle
2. **Random**: 20 random points in [-5,5] range
3. **Clustered**: Points in two Gaussian clusters with an outlier

### Usage:
```python
python visualize.py
```

This will generate three PNG files:
- `fig/min_circle_triangle.png`
- `fig/min_circle_random.png`
- `fig/min_circle_clustered.png`

### Custom Visualization:
```python
from visualize import plot_min_circle
from min_circle_cover import Point, min_circle_welzl

points = [Point([0,0]), Point([1,0]), Point([0,1])]
circle = min_circle_welzl(points, random_seed=42)
fig, ax = plot_min_circle(points, circle, "My Points")
plt.savefig('my_circle.png')
```

## References

1. Welzl, E. (1991). Smallest enclosing disks (balls and ellipsoids). In *New Results and New Trends in Computer Science*.
2. de Berg, M., et al. (2008). *Computational Geometry: Algorithms and Applications*.
3. Wikipedia: [Smallest-circle problem](https://en.wikipedia.org/wiki/Smallest-circle_problem)

## Future Work

1. Optimize d-dimensional implementation for very high dimensions (d > 100)
2. Add 3D visualization for sphere cover
3. Implement approximation algorithms for very large sets
4. Add support for weighted points
5. Integrate with geometric libraries (Shapely, CGAL)

## License

This implementation is provided for educational and research purposes.