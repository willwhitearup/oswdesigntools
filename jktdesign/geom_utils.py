import numpy as np

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