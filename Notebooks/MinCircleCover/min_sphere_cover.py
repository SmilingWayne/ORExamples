"""
Minimum Enclosing Sphere (Smallest Enclosing Ball) Problem
Extension to arbitrary dimensions using Welzl's algorithm.
"""

import random
import numpy as np
from typing import List, Optional

class PointND:
    """Point in n-dimensional space."""
    def __init__(self, coordinates: List[float]):
        self.coords = np.array(coordinates, dtype=float)
        self.dim = len(coordinates)

    def __repr__(self):
        return f"PointND({self.coords})"

    def __sub__(self, other):
        return self.coords - other.coords

    def distance_to(self, other) -> float:
        return np.linalg.norm(self.coords - other.coords)

    def squared_distance_to(self, other) -> float:
        diff = self.coords - other.coords
        return np.dot(diff, diff)


class SphereND:
    """Sphere in n-dimensional space."""
    def __init__(self, center: PointND, radius: float):
        self.center = center
        self.radius = radius

    def __repr__(self):
        return f"SphereND(center={self.center}, radius={self.radius})"

    def contains(self, point: PointND, tolerance: float = 1e-9) -> bool:
        """Check if point is inside the sphere (including boundary)."""
        dist = self.center.distance_to(point)
        return dist <= self.radius + tolerance

    @staticmethod
    def from_points(points: List[PointND]) -> Optional['SphereND']:
        """
        Compute the smallest sphere enclosing given points (0 to d+1 points).
        Returns None if points is empty.
        """
        n = len(points)
        if n == 0:
            return None
        if n == 1:
            return SphereND(points[0], 0.0)

        # For 2 or more points, solve linear system
        # Center c satisfies: ||p_i - c||^2 = R^2 for all i
        # Subtract first equation from others to get linear equations
        dim = points[0].dim
        if n == 2:
            # Sphere with diameter p1-p2
            center_coords = (points[0].coords + points[1].coords) / 2.0
            center = PointND(center_coords.tolist())
            radius = points[0].distance_to(points[1]) / 2.0
            return SphereND(center, radius)

        # For 3 or more points up to d+1
        # Solve linear system: A * c = b
        # where A_ij = 2*(p_{i+1,j} - p_{1,j}), b_i = ||p_{i+1}||^2 - ||p_1||^2
        # After solving for c, radius = distance(c, p_1)
        # Build linear system A * c = b
        A = np.zeros((n-1, dim))
        b = np.zeros(n-1)

        p0 = points[0].coords
        p0_sq = np.dot(p0, p0)

        for i in range(1, n):
            pi = points[i].coords
            A[i-1] = 2.0 * (pi - p0)
            b[i-1] = np.dot(pi, pi) - p0_sq

        try:
            # Use least squares to handle non-square matrices
            # lstsq returns solution, residuals, rank, singular values
            center_coords, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
            center_coords = center_coords + p0
            center = PointND(center_coords.tolist())

            # Compute radius as maximum distance to ensure enclosure
            radius = 0.0
            for p in points:
                dist = center.distance_to(p)
                if dist > radius:
                    radius = dist

            return SphereND(center, radius)

        except np.linalg.LinAlgError:
            # Points are degenerate (collinear/coplanar)
            # Fall back to subset of points
            # Recursively try subsets of size n-1
            best_sphere = None
            best_radius = float('inf')

            for i in range(n):
                subset = points[:i] + points[i+1:]
                sphere = SphereND.from_points(subset)
                if sphere is None:
                    continue
                # Check if sphere encloses all points
                if all(sphere.contains(p) for p in points):
                    if sphere.radius < best_radius:
                        best_sphere = sphere
                        best_radius = sphere.radius

            if best_sphere is not None:
                return best_sphere

            # If still fails, use brute force (for small n)
            return SphereND.brute_force(points)

    @staticmethod
    def brute_force(points: List[PointND]) -> 'SphereND':
        """Brute force algorithm for testing small sets."""
        n = len(points)
        dim = points[0].dim if n > 0 else 2

        # Try all subsets of size 1 to dim+1
        from itertools import combinations
        best_sphere = None
        best_radius = float('inf')

        for k in range(1, min(dim+2, n+1)):
            for indices in combinations(range(n), k):
                subset = [points[i] for i in indices]
                sphere = SphereND.from_points(subset)
                if sphere is None:
                    continue
                if all(sphere.contains(p) for p in points):
                    if sphere.radius < best_radius:
                        best_sphere = sphere
                        best_radius = sphere.radius

        if best_sphere is None:
            # Fallback: bounding box sphere
            if n == 0:
                return SphereND(PointND([0.0]*dim), 0.0)
            # Compute bounding box and use its center
            coords = np.array([p.coords for p in points])
            min_vals = coords.min(axis=0)
            max_vals = coords.max(axis=0)
            center_coords = (min_vals + max_vals) / 2.0
            center = PointND(center_coords.tolist())
            radius = max(center.distance_to(p) for p in points)
            return SphereND(center, radius)

        return best_sphere


def welzl_nd(points: List[PointND], support: List[PointND] = None, dim: int = None) -> SphereND:
    """
    Welzl's randomized algorithm for smallest enclosing sphere in d dimensions.

    Args:
        points: List of points to enclose.
        support: Points that must lie on the boundary of the sphere.
        dim: Dimension of space. If None, inferred from points or support.

    Returns:
        Smallest sphere enclosing all points.
    """
    if support is None:
        support = []

    # Determine dimension if not provided
    if dim is None:
        if points:
            dim = points[0].dim
        elif support:
            dim = support[0].dim
        else:
            dim = 2  # default

    # Base case: no points left or support has dim+1 points
    if len(points) == 0 or len(support) == dim + 1:
        sphere = SphereND.from_points(support)
        if sphere is None:
            # Empty support - return dummy sphere with correct dimension
            return SphereND(PointND([0.0]*dim), 0.0)
        return sphere

    # Randomly select a point
    idx = random.randrange(len(points))
    p = points[idx]

    # Recursively compute sphere without p
    remaining = points[:idx] + points[idx+1:]
    sphere = welzl_nd(remaining, support, dim)

    # If p is not inside the sphere, add to support and recompute
    if sphere is None or not sphere.contains(p):
        support.append(p)
        sphere = welzl_nd(remaining, support, dim)
        support.pop()  # backtrack

    return sphere


def min_sphere_welzl(points: List[PointND], random_seed: Optional[int] = None) -> SphereND:
    """Wrapper for Welzl algorithm in d dimensions with optional random seed."""
    if random_seed is not None:
        random.seed(random_seed)

    # Determine dimension from first point
    if not points:
        raise ValueError("No points provided")
    dim = points[0].dim

    # Shuffle points for randomized algorithm
    shuffled = points.copy()
    random.shuffle(shuffled)

    return welzl_nd(shuffled, [], dim)


# Example usage and testing
if __name__ == "__main__":
    # Test 2D points (should match circle results)
    print("Testing 2D points (triangle):")
    p1 = PointND([0, 0])
    p2 = PointND([1, 0])
    p3 = PointND([0, 1])
    points_2d = [p1, p2, p3]

    sphere = min_sphere_welzl(points_2d, random_seed=42)
    print(f"Sphere: {sphere}")
    for p in points_2d:
        print(f"  Point {p.coords} inside: {sphere.contains(p)}")

    # Test 3D points
    print("\nTesting 3D points (tetrahedron):")
    p1 = PointND([0, 0, 0])
    p2 = PointND([1, 0, 0])
    p3 = PointND([0, 1, 0])
    p4 = PointND([0, 0, 1])
    points_3d = [p1, p2, p3, p4]

    sphere = min_sphere_welzl(points_3d, random_seed=42)
    print(f"Sphere: {sphere}")
    for p in points_3d:
        print(f"  Point {p.coords} inside: {sphere.contains(p)}")

    # Test random points in 4D
    print("\nTesting random 4D points:")
    random.seed(42)
    random_points = [PointND([random.uniform(-5, 5) for _ in range(4)]) for _ in range(10)]
    sphere = min_sphere_welzl(random_points, random_seed=42)
    print(f"Sphere radius: {sphere.radius}")

    # Check containment
    outside = []
    for p in random_points:
        if not sphere.contains(p):
            outside.append(p)

    if outside:
        print(f"Warning: {len(outside)} points may be outside sphere")
    else:
        print("All points enclosed successfully.")

    print("\nDone.")