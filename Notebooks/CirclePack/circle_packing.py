#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circle packing solution based on circlify
Supports two modes:
1. EXCLUSIVE: small circles do not contain each other (tiling mode)
2. HIERARCHICAL: small circles can be contained by larger circles (hierarchical nesting mode)

Reference: https://github.com/elmotec/circlify 
"""

import circlify
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np


class PackMode(Enum):
    """Packing mode enumeration"""
    EXCLUSIVE = "exclusive"      # Small circles do not contain each other
    HIERARCHICAL = "hierarchical"  # Allows nested containment


@dataclass
class PackResult:
    """Packing result data structure"""
    circles: List[dict]  # Each circle: {x, y, r, value, level}
    container: dict      # Container circle: {x, y, r}
    mode: str
    stats: dict


class CirclePacker:
    """
    Circle packing wrapper class based on circlify

    circlify core API [[40]][[41]]:
    - circlify.circlify(values, target_enclosure) -> List[Circle]
    - circlify.encircle(circles, level) -> List[Circle] (nested)
    - Circle object attributes: x, y, r, level, value
    """

    def __init__(self, colours: List[str] = None):
        """
        Parameters
        ----------
        colours : List[str]
            Color list for visualization
        """
        self.colours = colours or [
            '#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
            '#ff7f00', '#ffff33', '#a65628', '#f781bf'
        ]

    def pack_exclusive(self, radii: List[float], 
                       target_radius: float = 1.0,
                       padding: float = 0.01) -> PackResult:
        """
        Mode 1: Exclusive mode - all small circles do not overlap or contain each other

        Principle: Convert radii to area values, circlify allocates positions based on area proportion [[40]]

        Parameters
        ----------
        radii : List[float]
            List of small circle radii
        target_radius : float
            Container large circle radius
        padding : float
            Gap ratio between circles

        Returns
        -------
        PackResult
            Contains all circle positions and statistics
        """
        # circlify calculates based on area, convert radii to area [[40]]
        areas = [r * r for r in radii]
        
        # Target container (unit circle, circlify default)
        target_enclosure = circlify.Circle(x=0, y=0, r=target_radius)
        
        # Call circlify main function [[41]][[42]]
        circles = circlify.circlify(
            areas,
            target_enclosure=target_enclosure,
            # padding=padding
        )
        
        result_circles = []
        for i, c in enumerate(circles):
            # circlify returns r based on area, need to convert back to radius
            # But circlify already handles scaling, use directly [[40]]
            result_circles.append({
                'x': c.x,
                'y': c.y,
                'r': c.r,
                'value': areas[i],
                'original_radius': radii[i] if i < len(radii) else None,
                'level': c.level if hasattr(c, 'level') else 0,
                'colour': self.colours[i % len(self.colours)]
            })
        
        stats = self._calculate_stats(result_circles, target_radius)
        stats['mode'] = PackMode.EXCLUSIVE.value
        stats['input_count'] = len(radii)
        stats['output_count'] = len(result_circles)
        
        return PackResult(
            circles=result_circles,
            container={'x': 0, 'y': 0, 'r': target_radius},
            mode=PackMode.EXCLUSIVE.value,
            stats=stats
        )

    def pack_hierarchical(self, data: Union[List[float], List],
                          target_radius: float = 1.0,
                          padding: float = 0.02) -> PackResult:
        """
        Mode 2: Hierarchical mode - supports arbitrary depth nesting structure

        Principle: Use circlify's hierarchical structure support, supports multi-level nesting (container within container)

        Parameters
        ----------
        data : List[float] | List
            Hierarchical data with arbitrary nesting depth:
            - Flat list: single-level structure e.g. [0.1, 0.2, 0.3]
            - Nested list: multi-level structure e.g. [[0.1, 0.2], [0.3, 0.4]]
            - Deep nesting: e.g. [[[0.1, 0.2], [0.3, 0.4]], [[0.5, 0.6]]]
        target_radius : float
            Outermost container circle radius
        padding : float
            Gap ratio between levels (currently not used)

        Returns
        -------
        PackResult
            Contains all circle positions (including container circles) and statistics
        """
        # Helper function to check if data is a leaf node (list of numbers)
        def is_leaf_node(node):
            return isinstance(node, list) and len(node) > 0 and isinstance(node[0], (int, float))

        # Helper function to compute total area of a subtree
        def compute_total_area(node):
            """Compute total area of a subtree (sum of all leaf circle areas)"""
            if is_leaf_node(node):
                return sum(r * r for r in node)
            else:
                total = 0
                for child in node:
                    total += compute_total_area(child)
                return total

        # Recursive function to process nested structure
        def process_node(node_data, parent_enclosure, level=0, path=()):
            """Process a node in the hierarchy, returns list of circles"""
            circles = []

            if is_leaf_node(node_data):
                # Leaf node: pack circles directly in parent enclosure
                areas = [r * r for r in node_data]
                child_circles = circlify.circlify(
                    areas,
                    target_enclosure=parent_enclosure,
                    # padding=padding
                )

                # Add leaf circles
                for i, child in enumerate(child_circles):
                    circles.append({
                        'x': child.x,
                        'y': child.y,
                        'r': child.r,
                        'value': areas[i] if i < len(areas) else child.r * child.r,
                        'level': level,
                        'is_container': False,
                        'colour': self.colours[(sum(path) * 10 + i) % len(self.colours)],
                        'path': path + (i,)
                    })
            else:
                # Internal node: process each child group
                # Calculate area for each child group
                child_areas = []
                for child_data in node_data:
                    if is_leaf_node(child_data):
                        # Child is leaf: total area of its circles
                        child_areas.append(sum(r * r for r in child_data))
                    else:
                        # Child is internal: recursively calculate total area
                        # Use helper to compute total area of subtree
                        child_areas.append(compute_total_area(child_data))

                # Pack child containers in parent enclosure
                child_containers = circlify.circlify(
                    child_areas,
                    target_enclosure=parent_enclosure,
                    # padding=padding
                )

                # Process each child group
                for idx, (container, child_data) in enumerate(zip(child_containers, node_data)):
                    # Add container circle
                    circles.append({
                        'x': container.x,
                        'y': container.y,
                        'r': container.r,
                        'value': child_areas[idx],
                        'level': level,
                        'is_container': True,
                        'colour': '#cccccc',
                        'fill': 'none',
                        'stroke': self.colours[(sum(path) * 10 + idx) % len(self.colours)],
                        'path': path + (idx,)
                    })

                    # Create enclosure for children (slightly smaller than container)
                    child_enclosure = circlify.Circle(
                        x=container.x,
                        y=container.y,
                        r=container.r * 0.98
                        # r=container.r * 0.95  # Inner margin
                        # YOU CAN SET MARGIN (PADDING) HERE.
                    )

                    # Recursively process child data
                    child_circles = process_node(
                        child_data,
                        child_enclosure,
                        level + 1,
                        path + (idx,)
                    )
                    circles.extend(child_circles)

            return circles
        # Convert flat list to single-level nesting for backward compatibility
        if isinstance(data[0], (int, float)):
            data = [data]

        # Main outermost container
        outer_enclosure = circlify.Circle(x=0, y=0, r=target_radius)

        # Process the entire hierarchy
        result_circles = process_node(data, outer_enclosure, level=0)

        # Add outermost container circle
        result_circles.append({
            'x': 0,
            'y': 0,
            'r': target_radius,
            'value': compute_total_area(data),
            'level': -1,  # Special level for outermost container
            'is_container': True,
            'colour': '#cccccc',
            'fill': 'none',
            'stroke': '#333333',
            'path': ()
        })

        # Calculate statistics
        stats = self._calculate_stats(result_circles, target_radius)
        stats['mode'] = PackMode.HIERARCHICAL.value
        stats['num_groups'] = len(data)

        # Count containers and leaf circles
        container_count = sum(1 for c in result_circles if c.get('is_container', False))
        leaf_count = len(result_circles) - container_count
        stats['num_containers'] = container_count
        stats['num_children'] = leaf_count

        return PackResult(
            circles=result_circles,
            container={'x': 0, 'y': 0, 'r': target_radius},
            mode=PackMode.HIERARCHICAL.value,
            stats=stats
        )

    def _calculate_stats(self, circles: List[dict], container_r: float) -> dict:
        """Calculate packing statistics"""
        total_circle_area = sum(c['r'] * c['r'] for c in circles if not c.get('is_container', False))
        container_area = container_r * container_r
        
        # Check overlaps (simplified version)
        overlaps = 0
        for i, c1 in enumerate(circles):
            for _, c2 in enumerate(circles[i+1:], i+1):
                if c1.get('is_container') or c2.get('is_container'):
                    continue
                dx, dy = c1['x'] - c2['x'], c1['y'] - c2['y']
                dist_sq = dx * dx + dy * dy
                if dist_sq < (c1['r'] + c2['r']) ** 2:
                    overlaps += 1
        
        return {
            'total_circles': len(circles),
            'packing_density': total_circle_area / container_area,
            'overlaps': overlaps,
            'container_radius': container_r
        }

    def visualize(self, result: PackResult, 
                  filename: str = 'packing_result.png',
                  show_labels: bool = False,
                  figsize: Tuple[int, int] = (10, 10)):
        """
        Visualize packing result

        Parameters
        ----------
        result : PackResult
            Return result of pack_exclusive or pack_hierarchical
        filename : str
            Output file path
        show_labels : bool
            Whether to show radius labels
        """
        _, ax = plt.subplots(1, 1, figsize=figsize)
        ax.set_aspect('equal')
        
        container = result.container
        container_circle = patches.Circle(
            (container['x'], container['y']), 
            container['r'],
            fill=False, 
            linewidth=2, 
            color='#333333',
            linestyle='--'
        )
        ax.add_patch(container_circle)
        
        for circle in result.circles:
            if circle.get('is_container', False):
                patch = patches.Circle(
                    (circle['x'], circle['y']),
                    circle['r'],
                    fill=False,
                    linewidth=2,
                    color=circle.get('stroke', '#666666')
                )
            else:
                patch = patches.Circle(
                    (circle['x'], circle['y']),
                    circle['r'],
                    color=circle.get('colour', '#3498db'),
                    alpha=0.7,
                    linewidth=1,
                    edgecolor='white'
                )
            ax.add_patch(patch)
            
            # Optional: add labels
            if show_labels and not circle.get('is_container', False):
                ax.text(circle['x'], circle['y'], 
                       f"{circle['r']:.2f}",
                       ha='center', va='center', 
                       fontsize=8, color='white', fontweight='bold')
        
        margin = container['r'] * 0.1
        ax.set_xlim(-container['r'] - margin, container['r'] + margin)
        ax.set_ylim(-container['r'] - margin, container['r'] + margin)
        ax.axis('off')
        
        title = f"Circle Packing - {result.mode}\n"
        title += f"Circles: {result.stats['total_circles']}, "
        title += f"Density: {result.stats['packing_density']:.2%}"
        ax.set_title(title, fontsize=12)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Visualization saved to {filename}")

    def export_svg(self, result: PackResult, filename: str = 'packing_result.svg'):
        """Export to SVG format"""
        with open(filename, 'w') as f:
            size = 600
            margin = 50
            scale = (size - 2 * margin) / (2 * result.container['r'])
            cx, cy = size // 2, size // 2
            
            f.write(f'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">\n')
            f.write(f'  <rect width="100%" height="100%" fill="white"/>\n')
            
            r = result.container['r']
            f.write(f'  <circle cx="{cx}" cy="{cy}" r="{r*scale}" '
                   f'fill="none" stroke="#333" stroke-width="2" stroke-dasharray="5,5"/>\n')
            
            for circle in result.circles:
                x = cx + circle['x'] * scale
                y = cy - circle['y'] * scale  # SVG y-axis downward
                r_svg = circle['r'] * scale
                
                if circle.get('is_container', False):
                    f.write(f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{r_svg:.2f}" '
                           f'fill="none" stroke="{circle.get("stroke", "#666")}" '
                           f'stroke-width="2"/>\n')
                else:
                    f.write(f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{r_svg:.2f}" '
                           f'fill="{circle.get("colour", "#3498db")}" '
                           f'fill-opacity="0.7" stroke="white" stroke-width="1"/>\n')
            
            f.write('</svg>\n')
        
        print(f"SVG saved to {filename}")


# ==================== Usage Example ====================
if __name__ == '__main__':
    # Create packer object
    packer = CirclePacker()
    
    # ========== Example 1: Exclusive Mode ==========
    print("\n" + "="*50)
    print("Example 1: EXCLUSIVE mode (small circles do not contain each other)")
    print("="*50)
    
    # Generate random radii
    np.random.seed(42)
    radii = np.random.uniform(0.05, 0.15, 50).tolist()
    
    result1 = packer.pack_exclusive(radii, target_radius=1.0)
    print(f"Input circles: {result1.stats['input_count']}")
    print(f"Output circles: {result1.stats['output_count']}")
    print(f"Packing density: {result1.stats['packing_density']:.2%}")
    print(f"Overlaps: {result1.stats['overlaps']}")
    
    packer.visualize(result1, './Notebooks/CirclePack/fig/exclusive_packing.png', show_labels=True)
    packer.export_svg(result1, './Notebooks/CirclePack/fig/exclusive_packing.svg')
    
    # ========== Example 2: Hierarchical Mode ==========
    print("\n" + "="*50)
    print("Example 2: HIERARCHICAL mode (allows nested containment)")
    print("="*50)
    
    # Hierarchical data: 3 groups, each with 5-10 small circles
    hierarchical_data = [
        np.random.uniform(0.03, 0.08, 8).tolist(),
        np.random.uniform(0.04, 0.10, 6).tolist(),
        np.random.uniform(0.02, 0.06, 10).tolist(),
        np.random.uniform(0.02, 0.09, 10).tolist(),
    ]
    
    result2 = packer.pack_hierarchical(hierarchical_data, target_radius=1)
    print(f"Number of groups: {result2.stats['num_groups']}")
    print(f"Number of container circles: {result2.stats['num_containers']}")
    print(f"Number of child circles: {result2.stats['num_children']}")
    print(f"Total circles: {result2.stats['total_circles']}")
    print(f"Packing density: {result2.stats['packing_density']:.2%}")
    
    packer.visualize(result2, './Notebooks/CirclePack/fig/hierarchical_packing.png', show_labels=False)
    packer.export_svg(result2, './Notebooks/CirclePack/fig/hierarchical_packing.svg')

    # ========== Example 3: Deep Nested Mode (3 levels) ==========
    print("\n" + "="*50)
    print("Example 3: DEEP NESTED mode (3-level hierarchy)")
    print("="*50)

    # Three-level nested data: container -> groups -> subgroups -> circles
    deep_nested_data = [
        [  # First top-level group
            [0.08, 0.06, 0.04],  # First subgroup in first group
            [0.07, 0.05]         # Second subgroup in first group
        ],
        [  # Second top-level group
            [0.09, 0.07, 0.05, 0.03],  # Single subgroup in second group
        ],
        [  # Third top-level group
            [[0.06, 0.04], [0.01, 0.02, 0.03]],  # First subgroup in third group
            [0.05, 0.03],  # Second subgroup in third group
            [0.04, 0.02]   # Third subgroup in third group
        ]
    ]

    result3 = packer.pack_hierarchical(deep_nested_data, target_radius=1.0)
    print(f"Number of top-level groups: {len(deep_nested_data)}")
    print(f"Number of container circles: {result3.stats['num_containers']}")
    print(f"Number of child circles: {result3.stats['num_children']}")
    print(f"Total circles: {result3.stats['total_circles']}")
    print(f"Packing density: {result3.stats['packing_density']:.2%}")

    packer.visualize(result3, './Notebooks/CirclePack/fig/deep_nested_packing.png', show_labels=False)
    packer.export_svg(result3, './Notebooks/CirclePack/fig/deep_nested_packing.svg')

    print("\n" + "="*50)
    print("All files generated!")
    print("="*50)