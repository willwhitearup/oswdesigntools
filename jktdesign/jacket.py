import numpy as np
import json

from jktdesign.geom_utils import line_intersection, calculate_angle_3pts
from jktdesign.joint import Joint2D


class Jacket:

    def __init__(self, interface_elev, tp_width, tp_btm, tp_btm_k1_voffset, batter_1_theta, batter_1_elev, jacket_footprint,
                 stickup, bay_heights, btm_vert_leg_length, water_depth, single_batter: bool, bay_horizontals: list):

        self.interface_elev = interface_elev
        self.tp_width = tp_width
        self.tp_btm = tp_btm
        self.tp_btm_k1_voffset = tp_btm_k1_voffset
        self.water_depth = water_depth

        self.single_batter = single_batter
        self.batter_1_theta = batter_1_theta  # float, degrees!
        self.batter_1_elev = batter_1_elev

        self.jacket_footprint = jacket_footprint
        self.stickup = stickup
        self.pile_top_elev = -self.water_depth + self.stickup  # elevation of pile stick up top

        self.bay_heights = bay_heights  # list, define each bay height of jacket
        self.n_bays = len(self.bay_heights)

        self.btm_vert_leg_length = btm_vert_leg_length
        self.bay_horizontals = bay_horizontals  # list of bools defining whether a horizontal brace is present of not

        # batter angle data
        self.batter_1_width = None
        self.batter_2_width = self.jacket_footprint
        self.batter_2_theta = None  # float, degrees!
        self.batter_2_elev = -self.water_depth + self.stickup + self.btm_vert_leg_length
        # top and bottom allowables
        self.batter_1_elevation_min = None
        self.batter_1_elevation_max = None

        # kjt and braces
        self.kjt_elevs = {f"kjt_1": self.tp_btm - self.tp_btm_k1_voffset}  # we know k1 elevation from inputs
        self.kjt_widths = {}
        self.kjt_wps = {}  # kjt wps where braces and legs intersect at
        self.kjt_batter_angles = {}  # get the batter angle that the kjt resides on
        self.kjt_brace_angles = {}  # store the angles of each brace to leg [45, 90, 135..] etc.
        self.kjt_n_braces = {}

        # xjt
        self.xjt_elevs = {}  # store the x joint elevations as well (note the x values are always 0 in the centre)
        self.xjt_angles = {}  # brace angles measured from the vertical axis (similar to a batter angle, but for braces)
        self.xjt_wps = {}


        # Joint2D objects storage
        self.joint_objs = []  # list to store Joint2D objects

        self.warning_strings = []  # todo

        # run methods
        # check validity of inputs for jackets
        self._jacket_validity()
        self._raise_warning_strings()

        if self.single_batter:
            self._calculate_single_batter()
        else:
            self._calculate_2nd_batter()
        self._calculate_batter_elevation_limits()
        self._check_bay_heights()
        self._calculate_kjt_elevation()
        self._calculate_kjt_widths()
        self._calculate_kjt_wps()  # wps stored in dict like {k_jt*: [x, y], ...}

        self._store_kjt_batter_angles()
        self._calculate_x_brace_elevations()
        self._calculate_xjt_wps()
        # get the brace angles at each k joint
        self._get_kjt_no_of_braces()  # determine if kjt has 1, 2, or 3 brace attachments
        self._get_leg_to_brace_angles()
        self._get_brace_angles()

    def _jacket_validity(self):
        # error checking before plotting...
        if self.tp_btm > self.interface_elev:
            raise Exception(
                f"TP bottom {self.tp_btm} must be below the tower interface elevation {self.interface_elev}. Check inputs. Exiting...")

        if self.batter_1_theta is not None and self.batter_1_theta > 90:
            raise Exception(f"Batter angle at the top of jacket must not exceed vertical ({self.batter_1_theta} degree input)")

    def _raise_warning_strings(self):
        # todo
        # e.g. bottom k is within 1m of top of pile
        # bay height n is too small compared to others etc!
        self.warning_strings.append("this is a warning string example!")

    def _calculate_single_batter(self):
        if self.single_batter:
            o = self.tp_btm - (-self.water_depth + self.stickup + self.btm_vert_leg_length)
            a = (self.jacket_footprint - self.tp_width) / 2
            self.batter_1_theta = np.degrees(np.atan(o / a))
            self.batter_2_theta = self.batter_1_theta

            self.batter_1_elev = self.tp_btm - 0.5 * o  # just set the batter 1 elevation at half way (it doesnt matter)
            top_batter_dist = self.tp_btm - self.batter_1_elev  # vertical dist
            a = top_batter_dist / np.tan(np.radians(self.batter_1_theta))  # triangle width, with vertical as above
            self.batter_1_width = 2 * a + self.tp_width

    def _calculate_2nd_batter(self):

        # get width 1st batter elevation
        top_batter_dist = self.tp_btm - self.batter_1_elev  # vertical dist
        a = top_batter_dist / np.tan(np.radians(self.batter_1_theta))  # triangle width, with vertical as above
        self.batter_1_width = 2 * a + self.tp_width

        # get bottom batter angle
        btm_batter_height = self.batter_1_elev - self.batter_2_elev
        b = (self.jacket_footprint - self.batter_1_width) / 2
        self.batter_2_theta = np.degrees(np.atan(btm_batter_height / b))

    def _calculate_batter_elevation_limits(self):
        self.batter_1_elevation_min = self.pile_top_elev + self.btm_vert_leg_length
        self.batter_1_elevation_max = self.tp_btm - self.tp_btm_k1_voffset

    def _check_bay_heights(self):
        bay_height_sum = sum(self.bay_heights)
        allowable_dist = (self.tp_btm - self.tp_btm_k1_voffset) - (-self.water_depth + self.stickup)

        if bay_height_sum > allowable_dist:
            raise Exception(f"Bay heights must be less than the allowable jacket distance from top of k1 to top of pile. "
                            f"Bay heights must sum to <{allowable_dist} (currently ({bay_height_sum})). Reduce bay height inputs!")

    def _calculate_kjt_elevation(self):
        # k joint elevs
        for bidx, bay in enumerate(range(2, self.n_bays + 2)):
            self.kjt_elevs[f"kjt_{bay}"] = self.kjt_elevs[f"kjt_{bay - 1}"] - self.bay_heights[bidx]

    def _calculate_kjt_widths(self):
        # calculate j joint widths
        for kjt, kjt_elev in self.kjt_elevs.items():
            if kjt_elev >= self.batter_1_elev:  # if within 1st batter
                d = self.tp_btm - kjt_elev  # vertical distance to feature above
                w = d / np.tan(np.radians(self.batter_1_theta))  # horizontal distance of triangle
                self.kjt_widths[kjt] = self.tp_width + 2 * w  # total width
            elif kjt_elev <= self.batter_1_elev and kjt_elev >= self.batter_2_elev:  # if within 2nd batter
                d = self.batter_1_elev - kjt_elev
                w = d / np.tan(np.radians(self.batter_2_theta))
                self.kjt_widths[kjt] = self.batter_1_width + 2 * w
            # if on straight leg section above pile
            elif kjt_elev <= self.batter_2_elev and kjt_elev >= self.pile_top_elev:
                d = self.batter_2_elev - kjt_elev
                w = d / np.tan(np.radians(90.))  # above pile leg section is always vertical
                self.kjt_widths[kjt] = self.batter_2_width + 2 * w

    def _calculate_kjt_wps(self):
        # this is used as a translational transformation
        # now just store the k joint wps (where braces intersect with the leg)
        for kjt, kjt_elev in self.kjt_elevs.items():
            kjt_width = self.kjt_widths[kjt]
            self.kjt_wps[kjt] = [-kjt_width / 2, kjt_elev]

    def _calculate_xjt_wps(self):
        # this is used as a translational transformation
        # now just store the k joint wps (where braces intersect with the leg)
        for xjt, xjt_elev in self.xjt_elevs.items():
            self.xjt_wps[xjt] = [0., xjt_elev]

    def _store_kjt_batter_angles(self):
        # this is used as a rotational transformation
        for kjt, kjt_elev in self.kjt_elevs.items():
            self.kjt_batter_angles[kjt] = self.query_batter_at_elevation(kjt_elev)

    def _get_kjt_no_of_braces(self):
        # determine number of brace attachments for each k joint (if 3 then kt joint :-) )
        kjts_n_total = len(self.bay_heights) + 1  # total number of k joints
        if len(self.bay_horizontals) < kjts_n_total:
            self.bay_horizontals.insert(0, False)
            # needed because for the GET request the default only sends 1 less bay horizontal than needed as k1 never has a horizontal!

        for kjt, _ in self.kjt_elevs.items():
            kjt_no = int(kjt.split("_")[1])
            has_horz = self.bay_horizontals[kjt_no - 1]
            if kjt == "kjt_1":  # if k1
                self.kjt_n_braces[kjt] = 2 if has_horz else 1
            elif kjt == "kjt_" + str(kjts_n_total):  # if last k
                self.kjt_n_braces[kjt] = 2 if has_horz else 1
            else:  # all others
                self.kjt_n_braces[kjt] = 3 if has_horz else 2

    def _get_brace_angles(self):
        # get brace angle from vertical. Only the bottom of the bay angle is required
        for kjt, kjt_wp in self.kjt_wps.items():
            kjt_no = int(kjt.split("_")[1])
            if kjt_no == 1:
                continue

            xjt_elev_above = self.xjt_elevs.get(f"xjt_{kjt_no - 1}")
            pt1 = [kjt_wp[0], kjt_wp[1] + 1]
            pt2 = kjt_wp
            pt3 = [0, xjt_elev_above]
            brace_angle = calculate_angle_3pts(pt1, pt2, pt3)
            angle_from_vert = 90. - brace_angle

            self.xjt_angles[f"xjt_{kjt_no - 1}"] = angle_from_vert

    def _get_leg_to_brace_angles(self):
        # there are 4 points that can be used as an initial point in the angle calculation

        tp_wp = [-self.tp_width / 2, self.tp_btm]
        batter_1_wp = [-self.batter_1_width / 2, self.batter_1_elev]
        batter_2_wp = [-self.batter_2_width / 2, self.batter_2_elev]

        for kjt, kjt_wp in self.kjt_wps.items():
            kjt_no = int(kjt.split("_")[1])
            kjt_elev = kjt_wp[1]
            has_horz = self.bay_horizontals[kjt_no - 1]  # see if kjt has a horizontal member
            # using get is like try, but no error is thrown if key does not exist
            xjt_elev_above = self.xjt_elevs.get(f"xjt_{kjt_no - 1}")
            xjt_elev_below = self.xjt_elevs.get(f"xjt_{kjt_no}")

            # need to find a reference point to use as one of the 3 points to use to determine the angle
            if kjt_elev >= self.batter_1_elev:
                leg_pt_1 = tp_wp  # defines x, y
            elif kjt_elev >= self.batter_2_elev and kjt_elev < self.batter_1_elev:
                leg_pt_1 = batter_1_wp  # defines x, y
            elif kjt_elev <= self.batter_2_elev:
                leg_pt_1 = batter_2_wp  # defines x, y

            # now the 3rd point will be the x joint above or below (or both)
            d1_pt_3 = [0, xjt_elev_above] if xjt_elev_above is not None else None
            d2_pt_3 = [0, xjt_elev_below] if xjt_elev_below is not None else None
            d1_theta = calculate_angle_3pts(leg_pt_1, kjt_wp, d1_pt_3) if d1_pt_3 else None
            d2_theta = calculate_angle_3pts(leg_pt_1, kjt_wp, d2_pt_3) if d2_pt_3 else None
            # determine horizontal brace angle
            dhorz_theta = calculate_angle_3pts(leg_pt_1, kjt_wp, [-kjt_wp[0], kjt_wp[1]]) if has_horz else None

            # sort low to high to show top brace, middle brace and bottom brace
            brace_angles = [d1_theta, dhorz_theta, d2_theta]
            brace_angles = sorted(brace_angles, key=lambda x: (x is None, x))
            self.kjt_brace_angles[kjt] = brace_angles

    def _calculate_x_brace_elevations(self):

        if not self.kjt_widths:
            return None

        for idx, (kjt, this_kjt_elev) in enumerate(self.kjt_elevs.items()):
            if idx == len(self.kjt_elevs) - 1:
                break

            # get the k numbering
            k_this, k_next = idx + 1, idx + 2
            # get the elevation of the current k joint and add some info to the plot figure
            this_kjt_width = self.kjt_widths[f"kjt_{k_this}"]
            next_kjt_width = self.kjt_widths[f"kjt_{k_next}"]
            next_kjt_elev = self.kjt_elevs[f"kjt_{k_next}"]

            # through brace 1
            x1, y1 = -this_kjt_width / 2, this_kjt_elev
            x2, y2 = next_kjt_width / 2, next_kjt_elev

            # other brace 2
            x3, y3 = this_kjt_width / 2, this_kjt_elev
            x4, y4 = -next_kjt_width / 2, next_kjt_elev

            x_intersection, y_intersection = line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)

            assert np.isclose(x_intersection, 0.), "Error with x joint calc.."

            self.xjt_elevs[f"xjt_{k_this}"] = y_intersection

    def query_batter_at_elevation(self, elevation):
        if elevation >= self.batter_1_elev:
            batter_theta = self.batter_1_theta
        elif elevation >= self.batter_2_elev:
            batter_theta = self.batter_2_theta
        elif elevation < self.batter_2_elev:
            batter_theta = 90.

        return batter_theta

    def add_joint_obj(self, jnt_obj: Joint2D, jt_type="kjt"):

        # get joint name from Joint2D objects
        jt_name = jnt_obj.jt_name  # get the joint name from the Joint2D obj

        if jt_type == "kjt":
            # add the k joint brace attachment angles
            k_brace_angles = self.kjt_brace_angles[jt_name]
            d1_theta, d2_theta, d3_theta = k_brace_angles[0], k_brace_angles[1], k_brace_angles[2]
            jnt_obj.brace_attachment_thetas(d1_theta=d1_theta, d2_theta=d2_theta, d3_theta=d3_theta)
            # get batter angle on which the kjt is
            kjt_batter_angle = self.kjt_batter_angles[jt_name]
            kjt_wps = self.kjt_wps[jt_name]  # get kjt wp
            # create the joint and transform it
            jnt_obj.create_joint()
            jnt_obj.transform_joint(batter_angle=kjt_batter_angle, translate_by=kjt_wps, mirror=False)

        elif jt_type == "xjt":
            xjt_angle = self.xjt_angles[jt_name]
            xjt_wp = self.xjt_wps[jt_name]  # get kjt wp
            d1_theta = 2 * xjt_angle
            jnt_obj.brace_attachment_thetas(d1_theta=d1_theta, d2_theta=d1_theta+180.)
            # create the joint and transform it
            jnt_obj.create_joint()
            jnt_obj.transform_joint(batter_angle=xjt_angle, translate_by=xjt_wp, mirror=False)

        self.joint_objs.append(jnt_obj)








