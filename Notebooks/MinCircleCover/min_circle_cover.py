"""
Minimum Circle Cover (Smallest Enclosing Circle) Problem
Implementation of Welzl's randomized algorithm for 2D points.
Designed to be extensible to higher dimensions.
"""

import random
import numpy as np
from typing import List, Optional

class Point:
    """Point in n-dimensional space."""
    def __init__(self, coordinates: List[float]):
        self.coords = np.array(coordinates, dtype=float)
        self.dim = len(coordinates)

    def __repr__(self):
        return f"Point({self.coords})"

    def __sub__(self, other):
        return self.coords - other.coords

    def distance_to(self, other) -> float:
        return np.linalg.norm(self.coords - other.coords)

class Circle:
    """Circle in 2D (or sphere in higher dimensions)."""
    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

    def __repr__(self):
        return f"Circle(center={self.center}, radius={self.radius})"

    def contains(self, point: Point, tolerance: float = 1e-9) -> bool:
        """Check if point is inside the circle (including boundary)."""
        dist = self.center.distance_to(point)
        return dist <= self.radius + tolerance

    @staticmethod
    def from_points(points: List[Point]) -> Optional['Circle']:
        """Create the smallest circle enclosing given points (0-3 points in 2D).
        Returns None if points is empty."""
        n = len(points)
        if n == 0:
            return None
        if n == 1:
            return Circle(points[0], 0.0)
        if n == 2:
            return Circle.circle_from_two_points(points[0], points[1])
        if n == 3:
            return Circle.circle_from_three_points(points[0], points[1], points[2])
        # For higher dimensions or more points, use general algorithm
        # This method is for 2D only; extend for higher dimensions
        return Circle.min_circle_naive(points)

    @staticmethod
    def circle_from_two_points(p1: Point, p2: Point) -> 'Circle':
        """Circle with diameter p1-p2."""
        center_coords = (p1.coords + p2.coords) / 2.0
        center = Point(center_coords.tolist())
        radius = p1.distance_to(p2) / 2.0
        return Circle(center, radius)

    @staticmethod
    def circle_from_three_points(p1: Point, p2: Point, p3: Point) -> 'Circle':
        """Circle passing through three points (circumcircle)."""
        # Check for collinearity
        v1 = p2.coords - p1.coords
        v2 = p3.coords - p1.coords
        cross = np.cross(v1, v2) if len(v1) == 2 else np.linalg.det([v1, v2, [0,0,1]])  # 2D cross product magnitude
        if abs(cross) < 1e-12:
            # Collinear points, return circle with diameter of farthest pair
            d12 = p1.distance_to(p2)
            d23 = p2.distance_to(p3)
            d13 = p1.distance_to(p3)
            max_dist = max(d12, d23, d13)
            if max_dist == d12:
                return Circle.circle_from_two_points(p1, p2)
            elif max_dist == d23:
                return Circle.circle_from_two_points(p2, p3)
            else:
                return Circle.circle_from_two_points(p1, p3)

        # Compute circumcenter using perpendicular bisectors
        # For 2D points only
        if p1.dim != 2:
            raise NotImplementedError("Circumcircle for 3+ dimensions requires different method")

        # Convert to 2D coordinates
        x1, y1 = p1.coords
        x2, y2 = p2.coords
        x3, y3 = p3.coords

        # Using determinant formula
        A = x1*(y2 - y3) - y1*(x2 - x3) + x2*y3 - x3*y2
        B = (x1*x1 + y1*y1)*(y3 - y2) + (x2*x2 + y2*y2)*(y1 - y3) + (x3*x3 + y3*y3)*(y2 - y1)
        C = (x1*x1 + y1*y1)*(x2 - x3) + (x2*x2 + y2*y2)*(x3 - x1) + (x3*x3 + y3*y3)*(x1 - x2)

        center_x = -B/(2*A)
        center_y = -C/(2*A)
        center = Point([center_x, center_y])
        radius = center.distance_to(p1)
        return Circle(center, radius)

    @staticmethod
    def min_circle_naive(points: List[Point]) -> 'Circle':
        """Naive O(n^4) algorithm for testing small sets."""
        best_circle = None
        best_radius = float('inf')

        # Try all 1-point circles
        for p in points:
            c = Circle(p, 0.0)
            if all(c.contains(q) for q in points):
                if best_radius > 0.0:
                    best_circle = c
                    best_radius = 0.0

        # Try all 2-point circles
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                c = Circle.circle_from_two_points(points[i], points[j])
                if all(c.contains(q) for q in points):
                    if c.radius < best_radius:
                        best_circle = c
                        best_radius = c.radius

        # Try all 3-point circles
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                for k in range(j+1, len(points)):
                    c = Circle.circle_from_three_points(points[i], points[j], points[k])
                    if all(c.contains(q) for q in points):
                        if c.radius < best_radius:
                            best_circle = c
                            best_radius = c.radius

        if best_circle is None:
            raise RuntimeError("Failed to find enclosing circle")
        return best_circle


def welzl_algorithm(points: List[Point], support: List[Point] = None) -> Circle:
    """
    Welzl's randomized algorithm for smallest enclosing circle.
    Expected linear time O(n).

    Args:
        points: List of points to enclose.
        support: Points that must lie on the boundary of the circle.

    Returns:
        Smallest circle enclosing all points.
    """
    if support is None:
        support = []

    # Base cases
    if len(points) == 0 or len(support) == 3:
        circle = Circle.from_points(support)
        # If circle is None (empty support), return a dummy circle (will be replaced)
        if circle is None:
            # Return a circle that will be discarded by caller
            # Use arbitrary center and radius 0
            if points:
                # Use first point's dimension
                dim = points[0].dim
            else:
                dim = 2  # default
            return Circle(Point([0.0]*dim), 0.0)
        return circle

    # Randomly select a point
    idx = random.randrange(len(points))
    p = points[idx]

    # Recursively compute circle without p
    remaining = points[:idx] + points[idx+1:]
    circle = welzl_algorithm(remaining, support)

    # If circle is None or p is not inside the circle, add to support and recompute
    if circle is None or not circle.contains(p):
        support.append(p)
        circle = welzl_algorithm(remaining, support)
        support.pop()  # backtrack

    return circle


def min_circle_welzl(points: List[Point], random_seed: Optional[int] = None) -> Circle:
    """Wrapper for Welzl algorithm with optional random seed."""
    if random_seed is not None:
        random.seed(random_seed)

    # Shuffle points for randomized algorithm
    shuffled = points.copy()
    random.shuffle(shuffled)

    return welzl_algorithm(shuffled, [])


def min_circle_bruteforce(points: List[Point]) -> Circle:
    """Brute force algorithm for verification (small n)."""
    return Circle.min_circle_naive(points)


# Example usage and testing
if __name__ == "__main__":
    # Simple test with 3 points
    p1 = Point([0, 0])
    p2 = Point([1, 0])
    p3 = Point([0, 1])

    points = [p1, p2, p3]

    print("Testing with points:", points)

    circle_welzl = min_circle_welzl(points, random_seed=42)
    print("Welzl algorithm result:", circle_welzl)

    circle_brute = min_circle_bruteforce(points)
    print("Brute force result:", circle_brute)

    # Verify all points are inside
    for p in points:
        assert circle_welzl.contains(p), f"Point {p} not in circle"
        assert circle_brute.contains(p), f"Point {p} not in brute circle"

    print("All points enclosed successfully.")

    # Test with random points
    random_points = [Point([random.uniform(-10, 10), random.uniform(-10, 10)]) for _ in range(60)]
    print(f"\nTesting with {len(random_points)} random points")
    circle = min_circle_welzl(random_points, random_seed=42)
    print("Circle:", circle)

    # Check containment
    for p in random_points:
        if not circle.contains(p):
            print(f"Warning: Point {p} may be outside circle")

    print("Done.")