import numpy as np
import matplotlib.pyplot as plt
import copy

from jktdesign.geom_utils import construct_true_constant_width_path, check_is_horizontal_rectangle

"""
Joint geometry calculated using Joint Detailing guidance.
See ISO 19902 2020 figure 14.2-3 (pg. 162)
Units passed to Object are mm and degrees throughout
"""

class Joint2D:
    """defines the Joint2D object
    """
    def __init__(self, Dc, tc,
                 d1, t1, d1_theta=None,
                 d2=None, t2=None, d2_theta=None,
                 d3=None, t3=None, d3_theta=None, jt_name=None,
                 jt_type=None,  # either xjt or kjt
                 joint_gap=100):

        # define the joint
        self.Dc = Dc  # Can diameter, defines the OD
        self.tc = tc  # Can thickness
        self.d1, self.t1, self.d1_theta = d1, t1, d1_theta  # define brace 1 stub
        self.d2, self.t2, self.d2_theta = d2, t2, d2_theta  # define brace 2 stub
        self.d3, self.t3, self.d3_theta = d3, t3, d3_theta  # define brace 3 stub
        self.jt_name = jt_name  # k jt name e.g. 'kjt_1', 'kjt_2' ...
        self.jt_type = jt_type  # joint type, either "kjt", "xjt"
        self.joint_gap = joint_gap

        # X joint checker
        if self.d2_theta is not None and self.d2_theta < 0:
            print(f"X joint identified for {self.jt_name}. Only 2 braces allowed! joint gaps are auto set to be 0.")
            self.joint_gap = 0.  # joint gaps are irrelevant for X joints
            assert self.d3 is None, "Check shows that 3 brace attachments specified for an X joint! Exiting...!"

        # populate the following attributes using Joint Detailing rules in ISO 19902
        self.can_length = None
        self.can_poly_coords = None
        # wire end coords
        self.b1_wire_end_coords = None
        self.b2_wire_end_coords = None
        self.b3_wire_end_coords = None
        # brace polygon coords
        self.b1_poly_coords = None
        self.b2_poly_coords = None
        self.b3_poly_coords = None
        # Can coords
        self.can_poly_coords = None
        # joint poly coords in a dict
        self.joint_poly_coords = {}
        self.joint_poly_coords_transf = None
        # tranformations
        self._transf_method_called = False
        self.batter_angle = None
        self.translate_by = None
        self.mirror = None
        # stub and can end points
        self.stub_start_pts = {}  # dict of the stub start points (i.e. point of connection to the Chord surface)
        self.stub_end_pts = {}  # dict of the stub ends only
        self.can_pt_top, self.can_pt_btm = None, None  # list, of the top and bottom of the Can [xtop, ytop], [xbtm, ybtm]
        self.kinked_can = False  # set to True if the Can extends over a batter kink point
        self.pt_kink = None

    def brace_attachment_thetas(self, d1_theta=None, d2_theta=None, d3_theta=None):
        """method allows brace theta angles to be defined after object initiated
        """
        if d1_theta is not None:
            self.d1_theta = d1_theta
        if d2_theta is not None:
            self.d2_theta = d2_theta
        if d3_theta is not None:
            self.d3_theta = d3_theta

    def create_joint(self):
        """public method to create the joint, K or X joint allowed
        """
        self.calc_stub_wire_end_coords()
        self.calc_stub_poly_coords()
        self.calc_can_length()
        self.calc_can_poly_coords()
        self.get_joint_poly_coords()  # store all the joint coords in dict

    @staticmethod
    def chord_brace_attachment_length(d, d_theta):
        """define brace attachment length of brace straight to chord (in 2D view only)
        d, d_theta: floats, brace diameter and brace angle in degrees
        """
        return abs(d / np.sin(np.radians(d_theta)))

    @staticmethod
    def get_stub_length(d, d_theta):
        """when stub attaches to chord at an angle some of it overlaps into the chord surface (either at top or bottom)
        d, d_theta: floats, brace diameter and brace angle in degrees
        """
        stub_length = abs(0.5 * d / np.tan(np.radians(d_theta))) + max(d, 600)
        return stub_length

    def get_brace_wire_end_coords(self, d, d_theta):
        # start coord at chord surf
        m1x, m1y = 0.5 * self.Dc, (0.5 * self.Dc) / np.tan(np.radians(d_theta))
        # end at stub end
        stub_length = self.get_stub_length(d, d_theta)
        if d_theta > 180:
            m1x = -1 * m1x
            m1y = -(0.5 * self.Dc) / np.tan(np.radians(d_theta))
        m2x = m1x + stub_length * np.sin(np.radians(d_theta))
        m2y = m1y + stub_length * np.cos(np.radians(d_theta))
        # 1D co-ord wire ends (list format)
        wire_end_coords = [[m1x, m2x], [m1y, m2y]]
        return wire_end_coords

    def calc_stub_wire_end_coords(self):
        # wire end coords of the stub Joints centred about 0, 0 and orientated vertically
        # wire end coords start at the chord surf and end at the end of the brace stub
        self.b1_wire_end_coords = self.get_brace_wire_end_coords(self.d1, self.d1_theta)
        self.b2_wire_end_coords = self.get_brace_wire_end_coords(self.d2, self.d2_theta) if self.d2 is not None else None
        self.b3_wire_end_coords = self.get_brace_wire_end_coords(self.d3, self.d3_theta) if self.d3 is not None else None

    @staticmethod
    def get_brace_coords(wire_end_coords, d, d_theta):
        """brace polygon
        """
        # unpack wire end coords
        m1x, m2x, m1y, m2y = wire_end_coords[0][0], wire_end_coords[0][1], wire_end_coords[1][0], wire_end_coords[1][1]
        # vertical distance up and down the chord surf from centre pt
        v = (0.5 * d) / np.sin(np.radians(d_theta))
        # stub points on the chord surface
        x1, x2 = m1x, m1x
        y1, y2 = m1y - v, m1y + v
        # x and y dist at brace stub end to the end pt
        oo = (0.5 * d) * np.sin(np.radians(d_theta))
        aa = (0.5 * d) * np.cos(np.radians(d_theta))
        # stub points at the stub end (continuing in clockwise rotation from pts 1 and 2
        x3, x4 = m2x - aa, m2x + aa
        y3, y4 = m2y + oo, m2y - oo
        # 4 points only to define the polygon (do not close the polygon)
        return [[x1, x2, x3, x4], [y1, y2, y3, y4]]

    def calc_stub_poly_coords(self, apply_joint_gaps: bool=False):
        self.b1_poly_coords = Joint2D.get_brace_coords(self.b1_wire_end_coords, self.d1, self.d1_theta)
        self.b2_poly_coords = Joint2D.get_brace_coords(self.b2_wire_end_coords, self.d2, self.d2_theta) if self.d2 is not None else None
        self.b3_poly_coords = Joint2D.get_brace_coords(self.b3_wire_end_coords, self.d3, self.d3_theta) if self.d3 is not None else None

        # todo not yet implemented - joint gaps change the architecture, brace angles and joint wps...
        # apply joint gaps vertically
        if self.jt_type == "kjt" and apply_joint_gaps:
            print("***********")
            print(self.jt_name)
            # 2 braces
            if self.b2_poly_coords is not None and self.b3_poly_coords is None:
                b1_to_can_yvals = self.b1_poly_coords[1][:2]
                b2_to_can_yvals = self.b2_poly_coords[1][:2]
                y_gap = min(b1_to_can_yvals) - max(b2_to_can_yvals)
                if y_gap < self.joint_gap:
                    if y_gap < 0.:  # if negative gap i.e. overlap
                        self.b1_poly_coords[1][0] = self.b1_poly_coords[1][0] + 0.5 * abs(y_gap) + 0.5 * self.joint_gap
                        self.b1_poly_coords[1][1] = self.b1_poly_coords[1][1] + 0.5 * abs(y_gap) + 0.5 * self.joint_gap
                        self.b2_poly_coords[1][0] = self.b2_poly_coords[1][0] - 0.5 * abs(y_gap) - 0.5 * self.joint_gap
                        self.b2_poly_coords[1][1] = self.b2_poly_coords[1][1] - 0.5 * abs(y_gap) - 0.5 * self.joint_gap
                    else:
                        self.b1_poly_coords[1][0] = self.b1_poly_coords[1][0] - 0.5 * abs(y_gap) + 0.5 * self.joint_gap
                        self.b1_poly_coords[1][1] = self.b1_poly_coords[1][1] - 0.5 * abs(y_gap) + 0.5 * self.joint_gap
                        self.b2_poly_coords[1][0] = self.b2_poly_coords[1][0] + 0.5 * abs(y_gap) - 0.5 * self.joint_gap
                        self.b2_poly_coords[1][1] = self.b2_poly_coords[1][1] + 0.5 * abs(y_gap) - 0.5 * self.joint_gap

                    # determine updated WPs
                    brc1_wp = (self.b1_poly_coords[1][0] + self.b1_poly_coords[1][1]) / 2
                    brc2_wp = (self.b2_poly_coords[1][0] + self.b2_poly_coords[1][1]) / 2

            # 3 braces, only the top and bottom braces move (centre horz stays still)
            elif self.b2_poly_coords is not None and self.b3_poly_coords is not None:
                b1_to_can_yvals = self.b1_poly_coords[1][:2]
                b2_to_can_yvals = self.b2_poly_coords[1][:2]
                b3_to_can_yvals = self.b3_poly_coords[1][:2]
                y_gap_1_2 = min(b1_to_can_yvals) - max(b2_to_can_yvals)  # gap b1 to b2
                y_gap_2_3 = min(b2_to_can_yvals) - max(b3_to_can_yvals)  # gap b2 to b3
                # top brace to central horz brace
                if y_gap_1_2 < self.joint_gap:
                    if y_gap_1_2 < 0:  # if gap is negative (i.e. overlapping)
                        self.b1_poly_coords[1][0] = self.b1_poly_coords[1][0] + abs(y_gap_1_2) + self.joint_gap
                        self.b1_poly_coords[1][1] = self.b1_poly_coords[1][1] + abs(y_gap_1_2) + self.joint_gap
                    else:
                        self.b1_poly_coords[1][0] = self.b1_poly_coords[1][0] -abs(y_gap_1_2) + self.joint_gap
                        self.b1_poly_coords[1][1] = self.b1_poly_coords[1][1] -abs(y_gap_1_2) + self.joint_gap

                # btm brace to central horz brace
                if y_gap_2_3 < self.joint_gap:  # if gap exists but less than allowable joint_gap
                    if y_gap_2_3 < 0:
                        self.b3_poly_coords[1][0] = self.b3_poly_coords[1][0] - abs(y_gap_2_3) - self.joint_gap
                        self.b3_poly_coords[1][1] = self.b3_poly_coords[1][1] - abs(y_gap_2_3) - self.joint_gap
                    else:
                        self.b3_poly_coords[1][0] = self.b3_poly_coords[1][0] + abs(y_gap_2_3) - self.joint_gap
                        self.b3_poly_coords[1][1] = self.b3_poly_coords[1][1] + abs(y_gap_2_3) - self.joint_gap

                # determine updated WPs for top and btm braces
                brc1_wp = (self.b1_poly_coords[1][0] + self.b1_poly_coords[1][1]) / 2
                brc3_wp = (self.b3_poly_coords[1][0] + self.b3_poly_coords[1][1]) / 2


    def calc_can_length(self):
        """get joint can total length and brace stub lengths

            diameters (floats) defined as ODs
            theta angles (floats) defined in degrees
        """
        if self.d3 is not None and self.d2 is None:
            raise Exception("Braces numbering must be defined in ascending order. Exiting...")

        # chord can length------------------------------------------------------
        c_ends = 2 * max(self.Dc / 4, 300)  # top and bottom of chord Can length, see ISO 19902
        b1_att_len = self.chord_brace_attachment_length(self.d1, self.d1_theta)
        b2_att_len = self.chord_brace_attachment_length(self.d2, self.d2_theta) if self.d2 is not None else 0.
        b3_att_len = self.chord_brace_attachment_length(self.d3, self.d3_theta) if self.d3 is not None else 0.

        if self.d2 is not None:
            self.can_length = c_ends + b1_att_len + b2_att_len + b3_att_len + self.joint_gap
        elif self.d3 is not None:
            self.can_length = c_ends + b1_att_len + b2_att_len + b3_att_len + 2 * self.joint_gap
        else:
            self.can_length = c_ends + b1_att_len + b2_att_len + b3_att_len  # no joint gap exists as 1 brace attachment only

    def calc_can_poly_coords(self):
        """creates Can rectangle (polygon). Can ALWAYS has square ends (i.e. joint Cans never bevelled / kinked)
        """
        # translate the joint chord Can to be central about the braces
        if self.d2 is None:
            mtrans_ch_top = self.b1_wire_end_coords[1][0]
            mtrans_ch_btm = self.b1_wire_end_coords[1][0]
        elif self.d3 is None:
            mtrans_ch_top = max(self.b1_wire_end_coords[1][0], self.b2_wire_end_coords[1][0])
            mtrans_ch_btm = min(self.b1_wire_end_coords[1][0], self.b2_wire_end_coords[1][0])
        else:
            mtrans_ch_top = max(self.b1_wire_end_coords[1][0], self.b2_wire_end_coords[1][0], self.b3_wire_end_coords[1][0])
            mtrans_ch_btm = min(self.b1_wire_end_coords[1][0], self.b2_wire_end_coords[1][0], self.b3_wire_end_coords[1][0])

        # joint Can poly coords, about the 0, 0 point (list of [[x1, x2...], [y1, y2...]]
        # 4 points only to define a polygon rectangle
        self.can_poly_coords = [[-self.Dc / 2, -self.Dc / 2, self.Dc / 2, self.Dc / 2],
                                [mtrans_ch_btm - self.can_length / 2, mtrans_ch_top + self.can_length / 2,
                                 mtrans_ch_top + self.can_length / 2, mtrans_ch_btm - self.can_length / 2]]

    def get_joint_poly_coords(self):
        # put everything into a single dict, cos then easy to do transforms on
        self.joint_poly_coords["can"] = self.can_poly_coords
        self.joint_poly_coords["brc1"] = self.b1_poly_coords
        if self.d2 is not None:
            self.joint_poly_coords["brc2"] = self.b2_poly_coords
        if self.d3 is not None:
            self.joint_poly_coords["brc3"] = self.b3_poly_coords

    @staticmethod
    def rotation_matrix(theta):  # 2D rotation matrix: rotates anticlockwise
        return np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta), np.cos(theta)]])

    def transform_joint(self, batter_angle: float = None, translate_by: list = None, mirror: bool = False):
        """transform the 2D joint 'joint_poly_coords' var (centred about 0,0) to the WP of the actual joint and at
        correct batter angle. creates new var 'joint_poly_coords_transf'.

        Can also mirror joint about the x=0 (y-axis) line.

        Transformations in order:
            1. Rotate Joint
            2. Translate Joint
            3. Mirror Joint

        Args:
            translate_by: list, to translate the joint to e.g. [10, 0]
            rotate_by: float, degrees of rotate
            mirror: bool, True to mirror about the x=0 (y-axis) line

        Returns:
            updates the self.joint_poly_coords_transf attribute
        """

        if self._transf_method_called:
            raise RuntimeError("Transformation method already ran. It can only be called once! Exiting...!")

        self.batter_angle = batter_angle
        self.translate_by = translate_by
        self.mirror = mirror

        self.joint_poly_coords_transf = copy.deepcopy(self.joint_poly_coords)

        # rotate first about the 0, 0
        if batter_angle is not None:
            # convert to kink angle (i.e.
            rotate_by = -90 + batter_angle if batter_angle >= 0 else 90 + batter_angle

            for k, (xs, ys) in self.joint_poly_coords_transf.items():
                polygon = np.array(list(zip(xs, ys)))
                r_matrix = Joint2D.rotation_matrix(np.radians(rotate_by))
                rotated_polygon = np.dot(polygon, r_matrix.T)
                self.joint_poly_coords_transf[k][0] = rotated_polygon[:, 0].tolist()
                self.joint_poly_coords_transf[k][1] = rotated_polygon[:, 1].tolist()

        # translate to where it needs to be
        if translate_by is not None:
            for k, (xs, ys) in self.joint_poly_coords_transf.items():
                self.joint_poly_coords_transf[k][0] = [x + translate_by[0] for x in xs]
                self.joint_poly_coords_transf[k][1] = [y + translate_by[1] for y in ys]

        # mirror joint
        if mirror:
            for k, (xs, ys) in self.joint_poly_coords_transf.items():
                x_mirrored = [-xi for xi in xs]
                self.joint_poly_coords_transf[k][0] = x_mirrored

        self._transf_method_called = True

        # get the end pts of the Can and stubs
        self.get_transf_can_wire_end_pts()
        self.get_transf_stub_end_pt()

    def get_transf_can_wire_end_pts(self):
        """get the start and end point of the line defining the Can. This must be called after the transformation!
        """
        if self.joint_poly_coords_transf:
            # top 2 points of the Can
            xt1, yt1 = self.joint_poly_coords_transf["can"][0][1], self.joint_poly_coords_transf["can"][1][1]
            xt2, yt2 = self.joint_poly_coords_transf["can"][0][2], self.joint_poly_coords_transf["can"][1][2]
            self.can_pt_top = [(xt1 + xt2) / 2, (yt1 + yt2) / 2]

            # bottom 2 points of the Can
            xb1, yb1 = self.joint_poly_coords_transf["can"][0][3], self.joint_poly_coords_transf["can"][1][3]
            xb2, yb2 = self.joint_poly_coords_transf["can"][0][0], self.joint_poly_coords_transf["can"][1][0]
            self.can_pt_btm = [(xb1 + xb2) / 2, (yb1 + yb2) / 2]

    def extend_kjt_Can_and_kink(self, pt1, pt2, kink_loc):
        """pt1 = [x1, y1], pt2 = [x2, y2]
        pt1, [x, y], list, is the point of the kink itself
        pt2, [x, y], list, is the point at which either top (or the bottom) of the Can extends to
        """
        if kink_loc not in ["above_kjt", "below_kjt"]:
            raise Exception("Define kink location correctly")

        x1, y1 = pt1[0], pt1[1]
        x2, y2 = pt2[0], pt2[1]
        self.kinked_can = True
        self.pt_kink = pt1
        if kink_loc == "below_kjt":
            assert y2 < y1, "Error with editing Can of kjt to include kink below btm of Can. Exiting..."
            trapeziums = construct_true_constant_width_path(self.Dc, self.can_pt_top, pt1, pt2)
            self.can_pt_btm = pt2

        elif kink_loc == "above_kjt":
            assert y2 > y1, "Error with editing Can of kjt to include kink above top of Can. Exiting..."
            trapeziums = construct_true_constant_width_path(self.Dc, self.can_pt_btm, pt1, pt2)
            self.can_pt_top = pt2

        self.joint_poly_coords_transf["can"] = trapeziums

    def get_transf_stub_end_pt(self):
        """get the start and end point of the line defining the Stubs. This must be called after the transformation!
        """
        # get (x, y) pt of the transformed stub end
        if self.joint_poly_coords_transf:
            for k, v in self.joint_poly_coords_transf.items():
                if k == "can":
                    continue
                else:
                    # brace stub start points on chord surface
                    x0 = (v[0][0] + v[0][1]) / 2
                    y0 = (v[1][0] + v[1][1]) / 2
                    self.stub_start_pts[k] = [x0, y0]
                    # brace stub end points
                    x = (v[0][2] + v[0][3]) / 2
                    y = (v[1][2] + v[1][3]) / 2
                    self.stub_end_pts[k] = [x, y]

    def plot_2D_joint(self):
        """plot the 2D joint using matplotlib
        """
        # plot can
        plt.plot(self.can_poly_coords[0], self.can_poly_coords[1])
        # plot brace 1 stub outlines
        plt.plot(self.b1_poly_coords[0], self.b1_poly_coords[1])
        plt.plot([0] + self.b1_wire_end_coords[0], [0] + self.b1_wire_end_coords[1])
        # plot brace 2 and brace 3 stub outlines (if exists)
        if self.d2 is not None:
            plt.plot(self.b2_poly_coords[0], self.b2_poly_coords[1])
            plt.plot([0] + self.b2_wire_end_coords[0], [0] + self.b2_wire_end_coords[1])
        if self.d3 is not None:
            plt.plot(self.b3_poly_coords[0], self.b3_poly_coords[1])
            plt.plot([0] + self.b3_wire_end_coords[0], [0] + self.b3_wire_end_coords[1])

        # plot 0, 0 lines
        plt.axhline(y=0, color='r', linestyle='--')
        plt.axvline(x=0, color='r', linestyle='--')

        # plot the transformed joint
        if self.joint_poly_coords_transf:
            for k, v in self.joint_poly_coords_transf.items():
                plt.plot(v[0], v[1])

            # show horizontal and vertical lines to intersect at the centre of the transformed joint
            if self.translate_by is not None:
                xm = -self.translate_by[0] if self.mirror is not None and self.mirror else self.translate_by[0]
                plt.axhline(y=self.translate_by[1], color='y', linestyle='--')
                plt.axvline(x=xm, color='y', linestyle='--')

        # plot it!
        plt.axis('equal')
        plt.show()


if __name__ == "__main__":

    # K JOINT
    # need brace stub coords
    # Dc, tc  = 2000, 80
    # # top brace
    # d1, t1 = 400, 40
    # d1_theta = 175  # degrees defined from vertical
    # # btm brace
    # d2, t2 = 400, 40
    # d2_theta = 90  # degrees defined from vertical
    #
    # # btm brace
    d3, t3 = 400, 40
    # d3_theta = 150  # degrees defined from vertical
    #
    # jnt_obj = Joint2D(Dc, tc, d1, t1, d1_theta, d2, t2, d2_theta, d3, t3, d3_theta, joint_gap=100)
    # jnt_obj.create_joint()
    #
    # # try out the transforms!
    # joint_poly_coords = jnt_obj.joint_poly_coords
    # #jnt_obj.transform_joint(batter_angle=72, translate_by=[-21227, 9413], mirror=False)
    # jnt_obj.transform_joint(batter_angle=90, translate_by=[0, 0], mirror=False)
    # jnt_obj.plot_2D_joint()

    # X JOINT  # todo!!! make it work for x joint !!!
    # need brace stub coords
    Dc, tc  = 2000, 80
    # top brace
    d1, t1 = 400, 40
    d1_theta = 120  # degrees defined from vertical
    # btm brace
    d2, t2 = 600, 40
    d2_theta = 120 + 180  # degrees defined from vertical

    jnt_obj = Joint2D(Dc, tc, d1, t1, d1_theta, d2, t2, d2_theta, joint_gap=0)
    jnt_obj.create_joint()

    # try out the transforms!
    joint_poly_coords = jnt_obj.joint_poly_coords
    #jnt_obj.transform_joint(batter_angle=0, translate_by=[-21227, 9413], mirror=False)
    #jnt_obj.transform_joint(batter_angle=90, translate_by=[0, 0], mirror=False)
    jnt_obj.plot_2D_joint()




