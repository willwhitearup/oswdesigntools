import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


class Leg:

    def __init__(self, pt1, pt2, width1, width2=None, thk=None):

        self.pt1 = pt1  # [x1, y1]
        self.pt2 = pt2  # [x2, y2]
        self.pt_mid = None  # can be passed if a kinked leg
        self.width1 = width1

        # todo create a leg with a cone in consisting of 3 polgons:
        # todo 1 rectangle of width1, 1 cone going from width1 to width2 in slope 1 in 3, then 1 rectangle width2
        self.width2 = width2

        if np.isclose(self.width1, self.width2):
            self.width = self.width1
        else:
            print("Cone section required! TODO")  # todo

        self.thk = thk
        # list of xvals and yvals of the rectangle
        self.leg_poly_coords = None
        self.polygon1, self.polygon2 = None, None

    def create_rectangle(self):
        # Line vector
        x1, y1 = self.pt1
        x2, y2 = self.pt2
        dx, dy = x2 - x1, y2 - y1
        length = np.hypot(dx, dy)
        nx, ny = -dy / length, dx / length  # unit normal vector
        hwx, hwy = (self.width / 2) * nx, (self.width / 2) * ny
        corners = [(x1 + hwx, y1 + hwy), (x1 - hwx, y1 - hwy),
                   (x2 - hwx, y2 - hwy), (x2 + hwx, y2 + hwy)]

        xs, ys = zip(*corners)
        self.leg_poly_coords = [list(xs), list(ys)]

    @staticmethod
    def get_unit_normal(p1, p2, width):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = np.hypot(dx, dy)
        nx, ny = -dy / length, dx / length  # normal vector
        return (nx * width / 2, ny * width / 2)

    def build_kinked_leg(self, pt_mid):
        self.pt_mid = pt_mid
        # Normals of each leg (half-width)
        n1 = np.array(Leg.get_unit_normal(self.pt1, self.pt_mid, self.width))
        n2 = np.array(Leg.get_unit_normal(self.pt_mid, self.pt2, self.width))
        # Directions (unit vectors along each leg)
        d1 = np.array(self.pt_mid) - np.array(self.pt1)
        d1 /= np.linalg.norm(d1)
        d2 = np.array(self.pt2) - np.array(self.pt_mid)
        d2 /= np.linalg.norm(d2)
        # Calculate miter vector (normalized sum of normals)
        miter = n1 + n2
        miter_length = np.linalg.norm(miter)
        miter /= miter_length
        # Calculate scale factor to keep width constant:
        scale = self.width / (2 * np.dot(miter, n1 / (self.width / 2)))
        miter *= scale
        # First polygon: pt1 to pt_mid
        rect1_xs = [self.pt1[0] + n1[0], self.pt1[0] - n1[0], self.pt_mid[0] - miter[0], self.pt_mid[0] + miter[0]]
        rect1_ys = [self.pt1[1] + n1[1], self.pt1[1] - n1[1], self.pt_mid[1] - miter[1], self.pt_mid[1] + miter[1]]
        # Second polygon: pt_mid to pt2
        rect2_xs = [self.pt_mid[0] + miter[0], self.pt_mid[0] - miter[0], self.pt2[0] - n2[0], self.pt2[0] + n2[0]]
        rect2_ys = [self.pt_mid[1] + miter[1], self.pt_mid[1] - miter[1], self.pt2[1] - n2[1], self.pt2[1] + n2[1]]
        # stick them into polygon list of lists
        self.polygon1 = [rect1_xs, rect1_ys]
        self.polygon2 = [rect2_xs, rect2_ys]

    def plot_leg(self):
        fig, ax = plt.subplots()
        ax.plot([self.pt1[0], self.pt2[0]], [self.pt1[1], self.pt2[1]], 'k--', label='Center Line')
        patch = Polygon(list(zip(*self.leg_poly_coords)), closed=True, color='skyblue', label='Rectangle')
        ax.add_patch(patch)
        ax.set_aspect('equal')
        ax.legend()
        plt.grid(True)
        plt.show()

    def plot_kinked_leg(self):
        fig, ax = plt.subplots()
        ax.plot(*zip(self.pt1, self.pt_mid, self.pt2), 'k--o', label='Center Lines')
        # Add rectangles
        patch1 = Polygon(list(zip(*self.polygon1)), closed=True, color='skyblue', alpha=0.7)
        patch2 = Polygon(list(zip(*self.polygon2)), closed=True, color='lightgreen', alpha=0.7)
        ax.add_patch(patch1)
        ax.add_patch(patch2)
        ax.set_aspect('equal')
        ax.legend()
        plt.grid(True)
        plt.title("Beveled Connection Between Two Legs")
        plt.show()



pt1 = [1, 1]
pt2 = [2, 1.5]
width = 0.1

robj = Leg(pt1, pt2, width)
robj.create_rectangle()
robj.plot_leg()

pt_mid = [1, 1.5]
robj.build_kinked_leg(pt_mid)
robj.plot_kinked_leg()
a=1


