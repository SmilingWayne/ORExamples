#!/usr/bin/env python3
"""
Example usage of minimum circle/sphere cover implementations.
"""

import sys
sys.path.insert(0, '.')

from min_circle_cover import Point, min_circle_welzl
from min_sphere_cover import PointND, min_sphere_welzl


def example_2d():
    """Example with 2D points."""
    print("=== 2D Minimum Circle Cover ===")

    # Create some points
    points = [
        Point([0, 0]),
        Point([1, 0]),
        Point([0, 1]),
        Point([0.5, 0.2]),
        Point([0.2, 0.7])
    ]

    print(f"Points: {points}")

    # Compute minimum enclosing circle
    circle = min_circle_welzl(points, random_seed=42)

    print(f"\nMinimum enclosing circle:")
    print(f"  Center: {circle.center.coords}")
    print(f"  Radius: {circle.radius}")

    # Verify all points are inside
    all_inside = all(circle.contains(p) for p in points)
    print(f"  All points inside: {all_inside}")

    return circle


def example_3d():
    """Example with 3D points."""
    print("\n=== 3D Minimum Sphere Cover ===")

    # Create a tetrahedron
    points = [
        PointND([0, 0, 0]),
        PointND([1, 0, 0]),
        PointND([0, 1, 0]),
        PointND([0, 0, 1]),
        PointND([0.5, 0.5, 0.5])
    ]

    print(f"Points: {points}")

    # Compute minimum enclosing sphere
    sphere = min_sphere_welzl(points, random_seed=42)

    print(f"\nMinimum enclosing sphere:")
    print(f"  Center: {sphere.center.coords}")
    print(f"  Radius: {sphere.radius}")

    # Verify all points are inside
    all_inside = all(sphere.contains(p) for p in points)
    print(f"  All points inside: {all_inside}")

    return sphere


def example_random_nd(dim=5, n_points=10):
    """Example with random points in d dimensions."""
    print(f"\n=== {dim}D Minimum Sphere Cover (Random Points) ===")

    import random
    random.seed(42)

    points = [
        PointND([random.uniform(-5, 5) for _ in range(dim)])
        for _ in range(n_points)
    ]

    print(f"Generated {n_points} random points in {dim}D")

    sphere = min_sphere_welzl(points, random_seed=42)

    print(f"\nMinimum enclosing sphere:")
    print(f"  Center dimension: {sphere.center.dim}")
    print(f"  Radius: {sphere.radius:.6f}")

    # Check containment
    outside = [p for p in points if not sphere.contains(p)]
    print(f"  Points outside sphere: {len(outside)}")

    if outside:
        print("  Warning: Some points may be outside due to numerical tolerance")

    return sphere


if __name__ == "__main__":
    print("Minimum Circle/Cover Examples")
    print("=" * 50)

    circle_2d = example_2d()
    sphere_3d = example_3d()
    sphere_nd = example_random_nd(dim=4, n_points=8)

    print("\n" + "=" * 50)
    print("All examples completed.")