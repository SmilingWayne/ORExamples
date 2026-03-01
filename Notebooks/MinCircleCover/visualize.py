#!/usr/bin/env python3
"""
Visualization for Minimum Circle Cover algorithm.
"""

import sys
sys.path.insert(0, '.')

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving files
import matplotlib.pyplot as plt
import numpy as np
import random
import os
from min_circle_cover import Point, min_circle_welzl


def ensure_fig_dir():
    """Ensure the fig directory exists."""
    os.makedirs('fig', exist_ok=True)


def plot_min_circle(points, circle, title="Minimum Enclosing Circle"):
    """
    Plot points and the minimum enclosing circle.

    Args:
        points: List of Point objects
        circle: Circle object from min_circle_welzl
        title: Plot title
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Extract point coordinates
    x_coords = [p.coords[0] for p in points]
    y_coords = [p.coords[1] for p in points]

    # Plot points
    ax.scatter(x_coords, y_coords, c='blue', s=50, alpha=0.7, label='Points')

    # Plot circle
    center = circle.center.coords
    radius = circle.radius

    # Create circle patch
    circle_patch = plt.Circle(center, radius,
                             fill=False,
                             edgecolor='red',
                             linewidth=2,
                             linestyle='-',
                             alpha=0.8,
                             label='Minimum Enclosing Circle')
    ax.add_patch(circle_patch)

    # Plot center point
    ax.scatter([center[0]], [center[1]], c='red', s=100, marker='x', linewidths=3, label='Circle Center')

    # Plot radius line from center to a point on circle
    angle = np.pi / 4  # 45 degrees
    radius_point = [center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)]
    ax.plot([center[0], radius_point[0]], [center[1], radius_point[1]],
            'g--', alpha=0.6, linewidth=2, label='Radius')

    # Set plot limits with some padding
    all_x = x_coords + [center[0]]
    all_y = y_coords + [center[1]]
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)

    # Add padding (20% of range or 1 unit, whichever is larger)
    x_padding = max(1.0, 0.2 * (x_max - x_min))
    y_padding = max(1.0, 0.2 * (y_max - y_min))

    ax.set_xlim(x_min - x_padding, x_max + x_padding)
    ax.set_ylim(y_min - y_padding, y_max + y_padding)

    # Set aspect ratio to equal
    ax.set_aspect('equal', adjustable='box')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add title and labels
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('X coordinate', fontsize=12)
    ax.set_ylabel('Y coordinate', fontsize=12)

    # Add legend
    ax.legend(loc='upper right', fontsize=10)

    # Add information text box
    info_text = f"""Circle Information:
    Center: ({center[0]:.3f}, {center[1]:.3f})
    Radius: {radius:.3f}
    Points Covered: {len(points)}
    All Points Inside: {all(circle.contains(p) for p in points)}"""

    # Place text box in upper left corner
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # Add some statistics about point distances
    distances = [circle.center.distance_to(p) for p in points]
    max_distance = max(distances)
    avg_distance = np.mean(distances)

    stats_text = f"""Point Statistics:
    Max Distance: {max_distance:.3f}
    Avg Distance: {avg_distance:.3f}
    Points on Boundary: {sum(abs(d - radius) < 1e-9 for d in distances)}"""

    ax.text(0.02, 0.15, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

    return fig, ax


def example_triangle():
    """Example with triangle points."""
    print("Generating visualization for triangle points...")

    points = [
        Point([0, 0]),
        Point([1, 0]),
        Point([0, 1])
    ]

    circle = min_circle_welzl(points, random_seed=42)

    fig, ax = plot_min_circle(points, circle, "Minimum Enclosing Circle - Triangle")
    plt.tight_layout()
    ensure_fig_dir()
    plt.savefig('fig/min_circle_triangle.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'fig/min_circle_triangle.png'")
    # plt.show()


def example_random():
    """Example with random points."""
    print("\nGenerating visualization for random points...")

    random.seed(42)
    points = [Point([random.uniform(-5, 5), random.uniform(-5, 5)]) for _ in range(20)]

    circle = min_circle_welzl(points, random_seed=42)

    fig, ax = plot_min_circle(points, circle, "Minimum Enclosing Circle - Random Points")
    plt.tight_layout()
    ensure_fig_dir()
    plt.savefig('fig/min_circle_random.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'fig/min_circle_random.png'")
    # plt.show()


def example_clustered():
    """Example with clustered points."""
    print("\nGenerating visualization for clustered points...")

    points = []

    # Cluster 1
    for _ in range(12):
        x = random.gauss(0, 1)
        y = random.gauss(0, 1)
        points.append(Point([x, y]))

    # Cluster 2
    for _ in range(24):
        x = random.gauss(7, 0.8)
        y = random.gauss(3, 0.8)
        points.append(Point([x, y]))

    # Outlier
    points.append(Point([-4, 7]))

    circle = min_circle_welzl(points, random_seed=42)

    fig, ax = plot_min_circle(points, circle, "Minimum Enclosing Circle - Clustered Points")
    plt.tight_layout()
    ensure_fig_dir()
    plt.savefig('fig/min_circle_clustered.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to 'fig/min_circle_clustered.png'")
    # plt.show()


def interactive_example():
    """Create an interactive visualization with multiple test cases."""
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button

    # Create test cases
    test_cases = {
        "Triangle": [
            Point([0, 0]),
            Point([1, 0]),
            Point([0, 1])
        ],
        "Square": [
            Point([0, 0]),
            Point([1, 0]),
            Point([1, 1]),
            Point([0, 1])
        ],
        "Line": [
            Point([0, 0]),
            Point([2, 0]),
            Point([4, 0]),
            Point([6, 0])
        ],
        "Circle Points": [
            Point([np.cos(theta), np.sin(theta)])
            for theta in np.linspace(0, 2*np.pi, 12, endpoint=False)
        ]
    }

    # Add some noise to circle points
    for p in test_cases["Circle Points"]:
        p.coords[0] += random.uniform(-0.1, 0.1)
        p.coords[1] += random.uniform(-0.1, 0.1)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (name, points) in enumerate(test_cases.items()):
        if idx >= 4:
            break

        ax = axes[idx]

        # Compute minimum circle
        circle = min_circle_welzl(points, random_seed=42)

        # Plot
        x_coords = [p.coords[0] for p in points]
        y_coords = [p.coords[1] for p in points]

        ax.scatter(x_coords, y_coords, c='blue', s=40, alpha=0.7)

        # Plot circle
        center = circle.center.coords
        radius = circle.radius
        circle_patch = plt.Circle(center, radius, fill=False, edgecolor='red', linewidth=2, alpha=0.8)
        ax.add_patch(circle_patch)

        # Plot center
        ax.scatter([center[0]], [center[1]], c='red', s=80, marker='x', linewidths=2)

        # Set aspect ratio
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{name} ({len(points)} points)", fontsize=12, fontweight='bold')

        # Add info text
        info_text = f"Center: ({center[0]:.2f}, {center[1]:.2f})\nRadius: {radius:.2f}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    ensure_fig_dir()
    plt.savefig('fig/min_circle_comparison.png', dpi=150, bbox_inches='tight')
    print("Saved comparison visualization to 'fig/min_circle_comparison.png'")
    # plt.show()


def main():
    """Main function to run visualizations."""
    print("Minimum Circle Cover Visualization")
    print("=" * 50)

    # Check if matplotlib is available
    try:
        import matplotlib
    except ImportError:
        print("Error: matplotlib is required for visualization.")
        print("Install it with: pip install matplotlib")
        return

    # Run examples
    example_triangle()
    example_random()
    example_clustered()

    print("\n" + "=" * 50)
    print("Visualization completed. Check the generated PNG files.")


if __name__ == "__main__":
    main()