import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def get_unit_normal(p1, p2, width):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = np.hypot(dx, dy)
    nx, ny = -dy / length, dx / length  # Perpendicular (normal) vector
    return (nx * width / 2, ny * width / 2)

def build_beveled_leg(p_start, p_mid, p_end, width):
    # Directions
    n1 = get_unit_normal(p_start, p_mid, width)
    n2 = get_unit_normal(p_mid, p_end, width)

    # Bisector normal
    n1_vec = np.array(p_mid) - np.array(p_start)
    n2_vec = np.array(p_end) - np.array(p_mid)

    n1_norm = n1_vec / np.linalg.norm(n1_vec)
    n2_norm = n2_vec / np.linalg.norm(n2_vec)
    bisector = n1_norm + n2_norm
    bisector /= np.linalg.norm(bisector)

    # Normal offset direction (rotate 90 deg)
    bnorm = np.array([-bisector[1], bisector[0]]) * (width / 2)

    # First rectangle: pt1 to ptxxx
    rect1_xs = [p_start[0] + n1[0], p_start[0] - n1[0], p_mid[0] - bnorm[0], p_mid[0] + bnorm[0]]
    rect1_ys = [p_start[1] + n1[1], p_start[1] - n1[1], p_mid[1] - bnorm[1], p_mid[1] + bnorm[1]]
    polygon1 = [rect1_xs, rect1_ys]

    rect2_xs = [p_mid[0] + bnorm[0], p_mid[0] - bnorm[0], p_end[0] - n2[0], p_end[0] + n2[0]]
    rect2_ys = [p_mid[1] + bnorm[1], p_mid[1] - bnorm[1], p_end[1] - n2[1], p_end[1] + n2[1]]
    polygon2 = [rect2_xs, rect2_ys]
    return polygon1, polygon2

# Example points
pt1 = (1, 1)
ptxxx = (2, 1.5)
pt2 = (3, 1)
width = 0.2

polygon1, polygon2 = build_beveled_leg(pt1, ptxxx, pt2, width)

# Plotting
fig, ax = plt.subplots()
ax.plot(*zip(pt1, ptxxx, pt2), 'k--o', label='Center Lines')

# Add rectangles
patch1 = Polygon(list(zip(*polygon1)), closed=True, color='skyblue', alpha=0.7)
patch2 = Polygon(list(zip(*polygon2)), closed=True, color='lightgreen', alpha=0.7)

ax.add_patch(patch1)
ax.add_patch(patch2)

ax.set_aspect('equal')
ax.legend()
plt.grid(True)
plt.title("Beveled Connection Between Two Legs")
plt.show()
