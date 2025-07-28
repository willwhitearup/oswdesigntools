import numpy as np
import matplotlib.pyplot as plt
from jktdesign.geom_utils import find_longest_segment, create_points_on_line, create_2D_cone, plot_2D_cone, \
    construct_true_constant_width_path


class Leg:

    def __init__(self, width1, width2, thk, leg_name=None, bay_side=None, member_type=None):

        self.width1 = width1  # float, defines width1 in 2D (or diameter in 3D) of leg (must be defined by a tubular OD)
        self.width2 = width2  # float, defines width2 in 2D (or diameter in 3D) of leg (must be defined by a tubular OD)
        self.thk = thk  # float, defines thicknesses of leg
        self.leg_name = leg_name  # str, defines name of the leg section e.g. leg_1, leg_2, leg_3
        self.bay_side = bay_side  # str, either "L" or "R" left or right side of the bay (if Leg object is a brace)
        self.member_type = member_type
        self.section_alignment = None  # either 'ID_constant' or 'MD_constant'

        # attributes to populate
        self.pt1 = None  # [x1, y1]
        self.pt2 = None  # [x2, y2]
        self.pts = None  # assume initially that only 2 points (start and end) are defined
        self.mid_pts = []

        self.cone_length = None
        self.leg_a, self.leg_b = [], []
        self.leg_a_poly_coords, self.leg_b_poly_coords = None, None  # list, of lists e.g. [[x, ..], [y, ...]] defines the trapezium of coords

        self.is_cone = False
        self.longest_seg = None
        self.cone_pt1, self.cone_pt2 = None, None
        self.cone_poly_coords = None


        self.mirror = False

    def construct_leg(self, split_len1, cone_taper=None):

        ## CONE WORK ##
        # self.is_cone = True if not np.isclose(self.width1, self.width2) else False
        self._check_is_cone()  # first check if a cone is required considering the section alignment
        if self.is_cone:
            cone_taper = 4 if cone_taper is None else cone_taper
            self._calc_cone_length(cone_taper)  # cone length calc based on taper ratio of 1 in 4 default
            split_len2 = split_len1 + self.cone_length
            self._create_cone_segment(split_len1, split_len2)
            self._create_split_conical_leg_paths()
            self._create_leg_cone_poly_coords()
        ## CONE WORK END OF ##

        # i.e. if kink exists but width remains constant
        else:
            self._create_leg_poly_coords()

    def define_leg_pts(self, pt1, pt2):
        # top and bottom of Can - must correspond to the width1 and width2 float values
        self.pt1 = pt1  # [x1, y1]
        self.pt2 = pt2  # [x2, y2]
        self.pts = [self.pt1, self.pt2]

    def define_intermediate_leg_point(self, pt_mid):
        self.mid_pts.append(pt_mid)
        if len(self.mid_pts) > 4:
            raise Exception("Only 4 points total are allowed along a line leg segment. Exiting...")

        self.pts = [self.pt1] + self.mid_pts + [self.pt2]

    def set_tubular_section_alignment(self, section_alignment):
        self.section_alignment = section_alignment

    def _check_is_cone(self):
        # check ID for alignment
        if self.section_alignment == "ID_constant":
            width1_align, width2_align = self.width1 - self.thk, self.width2 - self.thk
        elif self.section_alignment == "MD_constant":
            width1_align, width2_align = self.width1 - 0.5 * self.thk, self.width2 - 0.5 * self.thk

        chk_alignment = np.isclose(width1_align, width2_align) # check to see if section widths are same or not
        self.is_cone = True if not chk_alignment else False

    def _calc_cone_length(self, cone_taper=4):
        """cone length determined by a taper based on widths at top and bottom. 1:4 is default
        """
        self.cone_length = (cone_taper * abs(self.width2 - self.width1)) / 2

    def _create_cone_segment(self, split_len1, split_len2, plot_cone=False):
        # find longest segment to put the cone into
        self.longest_seg = find_longest_segment(*self.pts)
        _, (seg_pt1, seg_pt2) = self.longest_seg  # e.g. seg_pt1: [0, 1] seg_pt2: [5, 15]

        total_dist = np.linalg.norm(np.array(seg_pt2) - np.array(seg_pt1))
        if split_len2 >= total_dist:
            raise Exception("Cone can not be created on the current leg section, as the leg is too small for a cone with specified taper! Exiting...")

        # create a cone going from pt_split1 to pt_split2
        if self.width1 > self.width2:
            self.cone_pt1, self.cone_pt2 = create_points_on_line(seg_pt1, seg_pt2, split_len1, split_len2)
            cone_xvals, cone_yvals = create_2D_cone(self.cone_pt1, self.cone_pt2, self.width1, self.width2)
        else:
            self.cone_pt1, self.cone_pt2 = create_points_on_line(seg_pt2, seg_pt1, split_len1, split_len2)
            cone_xvals, cone_yvals = create_2D_cone(self.cone_pt1, self.cone_pt2, self.width2, self.width1)

        self.cone_poly_coords = [cone_xvals, cone_yvals]

        # visualise it (internal use only!)
        if plot_cone:
            plot_2D_cone(self.cone_poly_coords[0], self.cone_poly_coords[1], self.cone_pt1, self.cone_pt2)

    def _create_split_conical_leg_paths(self):
        # get the longest segment to place a cone within
        _, (seg_pt1, seg_pt2) = self.longest_seg
        for idx, pt in enumerate(self.pts):
            self.leg_a.append(pt)
            if np.allclose(pt, seg_pt1):
                sidx = idx  # get index at which the segment to be split occurs
                break

        if self.width1 > self.width2:
            self.leg_a.append(self.cone_pt1)  # finish filling leg_a
            self.leg_b.append(self.cone_pt2)  # now fill leg_b with remaining others
        else:
            self.leg_a.append(self.cone_pt2)
            self.leg_b.append(self.cone_pt1)

        self.leg_b = self.leg_b + self.pts[sidx + 1:]

    def _create_leg_cone_poly_coords(self, plot_polys=False):
        # create the polygons for the split apart leg
        self.leg_a_poly_coords = construct_true_constant_width_path(self.width1, *self.leg_a)
        self.leg_b_poly_coords = construct_true_constant_width_path(self.width2, *self.leg_b)

        # some plotting
        if plot_polys:
            fig, ax = plt.subplots()
            for idx, (xs, ys) in enumerate(self.leg_a_poly_coords):
                ax.fill(xs, ys, label=f'leg a {idx + 1}')
            for idx, (xs, ys) in enumerate(self.leg_b_poly_coords):
                ax.fill(xs, ys, label=f'leg b {idx + 1}')
            ax.fill(self.cone_poly_coords[0], self.cone_poly_coords[1])
            ax.set_aspect('equal')
            ax.grid(True)
            ax.legend()
            plt.show()

    def _create_leg_poly_coords(self, plot_polys=False):
        # create the polygons for the leg
        # print(self.leg_name, *self.pts)
        self.leg_a_poly_coords = construct_true_constant_width_path(self.width1, *self.pts)
        # some plotting
        if plot_polys:
            fig, ax = plt.subplots()
            for idx, (xs, ys) in enumerate(self.leg_a_poly_coords):
                ax.fill(xs, ys, label=f'leg a {idx + 1}')
            ax.set_aspect('equal')
            ax.grid(True)
            ax.legend()
            plt.show()

    def mirror_leg(self):
        """transform - mirror - the leg section
        """
        self.mirror = True
        # mirror leg
        for idx, (xs, ys) in enumerate(self.leg_a_poly_coords):
            self.leg_a_poly_coords[idx][0] = [-xi for xi in xs]

        if self.leg_b_poly_coords is not None:
            for idx, (xs, ys) in enumerate(self.leg_b_poly_coords):
                self.leg_b_poly_coords[idx][0] = [-xi for xi in xs]

        if self.cone_poly_coords is not None:
            self.cone_poly_coords[0] = [-xi for xi in self.cone_poly_coords[0]]


if __name__ == "__main__":

    pt1 = [0, 0]
    ptmid1 = [0, 1]
    ptmid2 = [5, 15]
    pt2 = [10, 20]
    width1 = 2
    width2 = 2  # todo set this to equal width1 to start working on equal width sections!

    leg_obj = Leg(width1, width2, 1, 1)
    leg_obj.define_leg_pts(pt1, pt2)
    # leg_obj.define_intermediate_leg_point(ptmid1)
    leg_obj.define_intermediate_leg_point(ptmid2)
    leg_obj.construct_leg(split_len1=1)

    a=1


