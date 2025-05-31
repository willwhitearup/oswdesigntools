import numpy as np
import math
import matplotlib.pyplot as plt

def calculate_angle_3pts(pt1, pt2, pt3):
    # Convert points to numpy arrays
    # e.g. pt1 [x1, y1]
    p1 = np.array(pt1)
    p2 = np.array(pt2)
    p3 = np.array(pt3)

    # Calculate vectors
    v1 = p1 - p2
    v2 = p3 - p2

    # Calculate the dot product and magnitudes of the vectors
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    # Calculate the cosine of the angle
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)

    # Calculate the angle in radians and then convert to degrees
    angle_radians = np.arccos(cos_angle)
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees

def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    (x1, y1) and (x2, y2) represent the endpoints of Line 1.
    (x3, y3) and (x4, y4) represent the endpoints of Line 2.
    """
    # Calculate slopes (m1, m2) and y-intercepts (b1, b2)
    m1 = (y2 - y1) / (x2 - x1)
    m2 = (y4 - y3) / (x4 - x3)
    b1 = y1 - m1 * x1
    b2 = y3 - m2 * x3

    # Solve for intersection point
    x_intersection = (b2 - b1) / (m1 - m2)
    y_intersection = m1 * x_intersection + b1

    return x_intersection, y_intersection


def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def perpendicular(v):
    return np.array([-v[1], v[0]])

def line_kink_intersection(p1, d1, p2, d2):
    A = np.array([d1, -d2]).T
    if np.linalg.matrix_rank(A) < 2:
        return None  # lines are parallel
    t = np.linalg.solve(A, p2 - p1)
    return p1 + t[0] * d1

def construct_true_constant_width_path(width, *more_pts):
    #pts = [np.array(pt1), np.array(pt2)] + [np.array(p) for p in more_pts]

    pts = [np.array(p) for p in more_pts]

    tangents = [normalize(pts[i+1] - pts[i]) for i in range(len(pts) - 1)]
    normals = [perpendicular(t) * (width / 2) for t in tangents]

    left_pts = [pts[0] + normals[0]]
    right_pts = [pts[0] - normals[0]]

    for i in range(1, len(pts) - 1):
        p = pts[i]
        l1, d1 = p + normals[i-1], tangents[i-1]
        l2, d2 = p + normals[i], tangents[i]
        r1, r2 = p - normals[i-1], p - normals[i]

        left = line_kink_intersection(l1, d1, l2, d2)
        if left is None:
            left = p + normalize(normals[i-1] + normals[i]) * (width / 2)

        right = line_kink_intersection(r1, d1, r2, d2)
        if right is None:
            right = p - normalize(normals[i-1] + normals[i]) * (width / 2)

        left_pts.append(left)
        right_pts.append(right)

    left_pts.append(pts[-1] + normals[-1])
    right_pts.append(pts[-1] - normals[-1])

    trapo = []
    for i in range(len(pts) - 1):
        trapezium = np.array([left_pts[i],
                              right_pts[i],
                              right_pts[i + 1],
                              left_pts[i + 1]])
        trapo.append(trapezium)

    trapeziums = []
    for trap in trapo:
        xs, ys = trap[:, 0], trap[:, 1]
        trapeziums.append([xs, ys])

    return trapeziums

def find_longest_segment(*points):
    """ e.g. pass in pt1, pt2, pt3, pt4
    Returns: (length, (start_point, end_point)) from pt1, pt2....
    """
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    lengths = []
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        length = math.dist(p1, p2)
        lengths.append((length, (p1, p2)))

    longest = max(lengths, key=lambda x: x[0])
    return longest  # (length, (start_point, end_point))

def create_points_on_line(pt1, pt2, l1, l2):
    """pt1 = [0, 0], pt2 = [10, 0]
    p1, p2 = create_points_on_line(pt1, pt2, 3, 7)
    Returns: [3.0, 0.0], Point at l2: [7.0, 0.0]
    """
    if l2 <= l1:
        raise Exception(f"Line split must have l2 greater than l1. Exiting..!")
    pt1, pt2 = np.array(pt1), np.array(pt2)
    # Direction vector and length of the full segment
    direction = pt2 - pt1
    total_length = np.linalg.norm(direction)
    # Normalize direction vector
    unit_vector = direction / total_length
    # Compute points at distances l1 and l2 from pt1
    p_l1, p_l2 = pt1 + l1 * unit_vector, pt1 + l2 * unit_vector
    pt_l1, pt_l2 = p_l1.tolist(), p_l2.tolist()
    return pt_l1, pt_l2

def create_2D_cone(pt1, pt2, w1, w2):
    pt1 = np.array(pt1)
    pt2 = np.array(pt2)
    direction = pt2 - pt1
    perp = np.array([-direction[1], direction[0]])
    perp_unit = perp / np.linalg.norm(perp)
    offset1 = (w1 / 2) * perp_unit
    offset2 = (w2 / 2) * perp_unit
    corner1 = pt1 + offset1
    corner2 = pt1 - offset1
    corner3 = pt2 - offset2
    corner4 = pt2 + offset2
    # Collect coordinates
    xvals = [corner1[0], corner2[0], corner3[0], corner4[0], corner1[0]]
    yvals = [corner1[1], corner2[1], corner3[1], corner4[1], corner1[1]]
    return xvals, yvals

def plot_bevelled_leg(trapeziums, *pts_list):

    fig, ax = plt.subplots()
    colors = ['skyblue', 'lightgreen', 'salmon', 'plum', 'khaki', 'lightcoral', 'lightsteelblue']
    for i, (xs, ys) in enumerate(trapeziums):
        color = colors[i % len(colors)]
        ax.fill(xs, ys, color=color, alpha=0.7, edgecolor='black', label=f'Segment {i + 1}')

    pts = np.array(pts_list)
    ax.plot(pts[:, 0], pts[:, 1], '--o', color='black', label='Path')
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    plt.title("True Constant-Width Path with Segmented Trapeziums")
    plt.show()

def plot_2D_cone(xvals, yvals, pt1, pt2):
    # Plotting
    plt.figure(figsize=(6, 4))
    plt.plot(xvals, yvals, 'b-', linewidth=2, label='cone')
    plt.fill(xvals, yvals, color='lightblue', alpha=0.5)
    plt.plot(*pt1, 'ro', label='pt1')
    plt.plot(*pt2, 'go', label='pt2')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.title("Symmetric cone Between pt1 and pt2")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()
    return None


def extend_middle_points_to_target_y(x, y, target_y):
    if len(x) != 4 or len(y) != 4:
        raise ValueError("x and y must be lists of 4 elements each.")

    # Copy original points
    new_x = x[:]
    new_y = y[:]

    # Extend pt2 (index 1) along vector from pt1 (index 0) to pt2
    dx12 = x[1] - x[0]
    dy12 = y[1] - y[0]
    if dy12 == 0:
        raise ValueError("Cannot extend pt2 vertically from pt1 if dy is zero.")
    scale2 = (target_y - y[0]) / dy12
    new_x[1] = x[0] + dx12 * scale2
    new_y[1] = y[0] + dy12 * scale2

    # Extend pt3 (index 2) along vector from pt4 (index 3) to pt3
    dx43 = x[2] - x[3]
    dy43 = y[2] - y[3]
    if dy43 == 0:
        raise ValueError("Cannot extend pt3 vertically from pt4 if dy is zero.")
    scale3 = (target_y - y[3]) / dy43
    new_x[2] = x[3] + dx43 * scale3
    new_y[2] = y[3] + dy43 * scale3

    mid_x = (new_x[1] + new_x[2]) / 2
    mid_y = (new_y[1] + new_y[2]) / 2
    can_pt_top = [mid_x, mid_y]
    return new_x, new_y, can_pt_top



if __name__ == "__main__":

    # Define points and width
    pt1 = [0, 0]
    pt2 = [2, 3]
    pt3 = [5, 4]
    pt4 = [7, 2]

    pts_list = [pt1, pt2, pt3, pt4]
    width = 1.0

    trapeziums, pts = construct_true_constant_width_path(width, *pts_list)
    plot_bevelled_leg(trapeziums, pts)
    longest_seg = find_longest_segment(pt1, pt2, pt3, pt4)
    pt_l1, pt_l2 = create_points_on_line(longest_seg[1][0], longest_seg[1][1], 0.1, 0.2)
    # create a cone in 2D
    xvals, yvals = create_2D_cone([0, 1], [10, 10], 4, 2)
    plot_2D_cone(xvals, yvals)