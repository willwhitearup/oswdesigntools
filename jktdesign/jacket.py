import numpy as np
import copy
from jktdesign.geom_utils import line_intersection, calculate_angle_3pts, extend_middle_points_to_target_y
from jktdesign.joint import Joint2D
from jktdesign.leg import Leg


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
        self.batter_1_wp, self.batter_2_wp = None, None
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
        self.kjt_edits = {}  # defines whether kJoint Can needs to be edited as top or bottom is too close to a batter elev

        # xjt
        self.xjt_elevs = {}  # store the x joint elevations as well (note the x values are always 0 in the centre)
        self.xjt_angles = {}  # brace angles measured from the vertical axis (similar to a batter angle, but for braces)
        self.xjt_wps = {}

        # Joint2D (k and x jts), Leg (leg and brace section) objects storage
        self.joint_objs = []  # list to store Joint2D objects
        self.leg_objs = []  # list to store Leg objects (for leg sections)
        self.brace_a_objs = []  # list to store Leg objects (for brace a sections)
        self.brace_b_objs = []  # list to store Leg objects (for brace b sections)
        self.brace_hz_objs = []  # list to store Leg objects (for braze horizontals)

        self.warnings = {}  # todo

        # run methods
        # check validity of inputs for jackets
        self._jacket_validity()


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
        """2nd batter is generally just above the top of piles
        """
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
        self.batter_1_wp = [-self.batter_1_width / 2, self.batter_1_elev]
        self.batter_2_wp = [-self.batter_2_width / 2, self.batter_2_elev]
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
                leg_pt_1 = self.batter_1_wp  # defines x, y
            elif kjt_elev <= self.batter_2_elev:
                leg_pt_1 = self.batter_2_wp  # defines x, y

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
        # define other variables required of a joint e.g. angles in order to create the joint
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
            # create a copy of the joint and mirror it to get k joint on both legs in 2D
            jnt_obj_mirr = copy.deepcopy(jnt_obj)
            jnt_obj_mirr.jt_name = jt_name + "_mirr"
            jnt_obj.transform_joint(batter_angle=kjt_batter_angle, translate_by=kjt_wps, mirror=False)
            jnt_obj_mirr.transform_joint(batter_angle=kjt_batter_angle, translate_by=kjt_wps, mirror=True)
            self.joint_objs.append(jnt_obj_mirr)

        elif jt_type == "xjt":
            xjt_angle = self.xjt_angles[jt_name]
            xjt_wp = self.xjt_wps[jt_name]  # get kjt wp
            d1_theta = 2 * xjt_angle
            jnt_obj.brace_attachment_thetas(d1_theta=d1_theta, d2_theta=d1_theta+180.)
            # create the joint and transform it
            jnt_obj.create_joint()
            jnt_obj.transform_joint(batter_angle=xjt_angle, translate_by=xjt_wp, mirror=False)

        self.joint_objs.append(jnt_obj)

    def kjt_warnings_check(self):
        """public method to check for errors and warnings for the K joint design e.g. interaction with batter elevations
        """
        self._check_batter_elevs_not_in_kjts()
        self._check_kjt_ends_not_within_dist()

    def add_leg_obj(self, leg_obj: Leg, leg_cone_split_len=2500):
        """Leg objects are constructed in descending elevation. Leg sections are created using kjt co-ordinates
        Leg sections (diameters and thicknesses) have been defined by User in web app
        """
        leg_name = leg_obj.leg_name  # get the name
        leg_no = int(leg_name.split("_")[1])
        pt2_found = False
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            jt_type = jt_name.split("_")[0]
            jt_no = int(jt_name.split("_")[1])
            if jt_type == "kjt":
                if jt_no == leg_no:
                    pt1 = jnt_obj.can_pt_btm
                elif jt_no == leg_no + 1:
                    pt2 = jnt_obj.can_pt_top
                    pt2_found = True  # found pt2, so leg is definitely between 2 k joints :)
                elif not pt2_found:
                    # for the leg bottom section (between bottom k and top of pile), the pt2 resides at top of pile
                    pt2 = [-self.jacket_footprint / 2, self.pile_top_elev]

        # legs pt1 and pt2 are ALWAYS constructed from top to bottom i.e. k1 -> k2, then k2 -> k3 (descending elevation)
        y1, y2 = pt1[1], pt2[1]  # y1 must be ABOVE y2
        assert y1 > y2, f"{y1} and {y2}: K joint elevations must be in descending elevation order when defining a leg section. Exiting..."
        leg_obj.define_leg_pts(pt1, pt2)

        # add intermediate points
        # now find if any of the kink points are between the bottom of k above and above the k below
        assert self.batter_1_elev > self.batter_2_elev, "Batter elevations must be defined by descending elevation. Exiting..."
        if y2 < self.batter_1_elev < y1:
            leg_obj.define_intermediate_leg_point(self.batter_1_wp)
        if y2 < self.batter_2_elev < y1:
            leg_obj.define_intermediate_leg_point(self.batter_2_wp)

        # create the leg polygons, call all public methods
        leg_obj.construct_leg(split_len1=leg_cone_split_len)

        # create copy of leg object and mirror it
        leg_obj_mirr = copy.deepcopy(leg_obj)
        leg_obj_mirr.mirror_leg()
        leg_obj_mirr.leg_name = leg_name + "_mirr"  # todo do not need to name it mirror as now have mirror bool in obj

        self.leg_objs.append(leg_obj)
        self.leg_objs.append(leg_obj_mirr)

    def add_brace_a_obj(self, brace_obj: Leg, brace_cone_split_len=500):
        """brace a sections go in descending order from k- down to x-joints. e.g. bay 1 brace a sections go from
        k1 to x1
        """
        brace_name = brace_obj.leg_name  # get the name
        brace_no = int(brace_name.split("_")[1])
        bay_side = brace_obj.bay_side
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            kjt_mirror_flag = True if "mirr" in jt_name else False  # check if mirror
            jt_no = int(jt_name.split("_")[1])
            jt_type = jt_name.split("_")[0]
            # find k joint that attaches to bay brace e.g. bay 1 'brace a' attaches to k1
            if jt_type == "kjt" and jt_no == brace_no:
                # Initialize variables to track the lowest elevation stub
                min_y, lowest_stub = None, None

                # Loop through all stub end points to find the one with the lowest elevation (smallest y)
                for pt in jnt_obj.stub_end_pts.values():
                    x, y = pt[0], pt[1]
                    if min_y is None or y < min_y:
                        min_y = y
                        lowest_stub = pt

                # Assign to appropriate variable based on bay side and mirror flag
                if bay_side == "L" and not kjt_mirror_flag:
                    k_stub_pt = lowest_stub
                elif bay_side == "R" and kjt_mirror_flag:
                    k_stub_pt_mirr = lowest_stub

            # find x joint that attaches to bay brace e.g. bay 1 'brace a' attaches to x1
            if jt_type == "xjt" and jt_no == brace_no:
                # get the x brace stub with the highest elevation in the same bay (which will attach to original k joint stub)
                max_y, min_y = None, None
                for k, v in jnt_obj.stub_end_pts.items():
                    x, y = v[0], v[1]
                    if max_y is None or y > max_y:
                        max_y = y
                        x_stub_pt = v

                x_can_pt_top = jnt_obj.can_pt_top

        # define brace start and end pts - use descending order approach
        if bay_side == "L": brace_obj.define_leg_pts(k_stub_pt, x_stub_pt)
        else: brace_obj.define_leg_pts(k_stub_pt_mirr, x_can_pt_top)

        brace_obj.construct_leg(split_len1=brace_cone_split_len)  # construct obj using public method
        # store the brace a objs
        self.brace_a_objs.append(brace_obj)

    def add_brace_b_obj(self, brace_obj: Leg, brace_cone_split_len=500):
        """brace b sections go in descending order from x- down to k-joints. e.g. bay 1 brace b sections go from
        x1 Can section to k2 (upper stub)
        """
        brace_name = brace_obj.leg_name  # get the name
        bay_side = brace_obj.bay_side
        brace_no = int(brace_name.split("_")[1])
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            kjt_mirror_flag = True if "mirr" in jt_name else False
            jt_no = int(jt_name.split("_")[1])
            jt_type = jt_name.split("_")[0]
            # find x joint that attaches to bay brace e.g. bay 1 'brace b' attaches to x1
            if jt_type == "xjt" and jt_no == brace_no:
                # get the x brace bottom most Can point (i.e. bottom of Can)
                x_can_pt = jnt_obj.can_pt_btm
                # get the x brace stub with lowest point
                min_y = None
                for k, v in jnt_obj.stub_end_pts.items():
                    x, y = v[0], v[1]
                    if min_y is None or y < min_y:
                        min_y = y
                        x_stub_pt = v

            # Find k joint that attaches to bay brace (e.g. bay 1 'brace b' attaches to k2)
            if jt_type == "kjt" and jt_no == brace_no + 1:
                # Get the K brace stub with the highest elevation
                max_y, max_stub = None, None
                for _, (x, y) in jnt_obj.stub_end_pts.items():
                    if max_y is None or y > max_y:
                        max_y = y
                        max_stub = (x, y)

                if kjt_mirror_flag:
                    k_stub_pt_mirr = max_stub
                else:
                    k_stub_pt = max_stub

        if bay_side == "L": brace_obj.define_leg_pts(x_can_pt, k_stub_pt)
        else: brace_obj.define_leg_pts(x_stub_pt, k_stub_pt_mirr)

        brace_obj.construct_leg(split_len1=brace_cone_split_len)  # construct obj using public method
        self.brace_b_objs.append(brace_obj)

    def add_brace_hz_obj(self, brace_obj: Leg):
        """add horizontal braces if exist
        """
        brace_name = brace_obj.leg_name  # get the name
        bay_no = int(brace_name.split("_")[1])
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            kjt_mirror_flag = True if "mirr" in jt_name else False
            jt_no = int(jt_name.split("_")[1])
            jt_type = jt_name.split("_")[0]
            if jt_no == bay_no + 1 and jt_type == "kjt" and not kjt_mirror_flag:
                k_stub_pt_L = jnt_obj.stub_end_pts["brc2"]
            if jt_no == bay_no + 1 and jt_type == "kjt" and kjt_mirror_flag:
                k_stub_pt_R = jnt_obj.stub_end_pts["brc2"]

        brace_obj.define_leg_pts(k_stub_pt_L, k_stub_pt_R)
        brace_obj.construct_leg(split_len1=None)  # construct obj using public method
        self.brace_hz_objs.append(brace_obj)

    def extend_k1_to_TP(self, extend_k1: bool=True):
        """extend the k1 Can to reach the underside of the TP
        """
        if not extend_k1:
            return None

        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            jt_type = jt_name.split("_")[0]
            jt_no = int(jt_name.split("_")[1])
            if jt_type == "kjt" and jt_no == 1:
                for idx, (k, v) in enumerate(jnt_obj.joint_poly_coords_transf.items()):
                    if "can" in k:
                        xnew, ynew, can_pt_top = extend_middle_points_to_target_y(v[0], v[1], self.tp_btm)
                        jnt_obj.joint_poly_coords_transf[k] = xnew, ynew
                        jnt_obj.can_pt_top = can_pt_top  # update the co-ordinate of the top of the Can

    def _check_batter_elevs_not_in_kjts(self):
        batter_1_elev, batter_2_elev = self.batter_1_elev, self.batter_2_elev
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            if jnt_obj.jt_type == "kjt":# and "mirr" not in jt_name:
                joint_poly_coords_transf = jnt_obj.joint_poly_coords_transf
                _, can_poly_ycoords = joint_poly_coords_transf["can"]
                min_y, max_y = min(can_poly_ycoords), max(can_poly_ycoords)
                # check batter 1 elevations vs k joints!
                for idx, batter_elev in enumerate([batter_1_elev, batter_2_elev]):
                    if min_y <= batter_elev <= max_y:
                        dist_to_top = round(max_y - batter_elev, 1)
                        dist_to_btm = round(batter_elev - min_y, 1)
                        message = (f"{jt_name} Can spans batter {idx+1} elevation ({batter_elev}). "
                                   f"Move the batter {idx+1} elevation up (by {dist_to_top}) or down (by {dist_to_btm}) to avoid clash")

                        self.warnings[f"batter_{idx+1}_kjt_interaction"] = {"flag": "error", "message": message}

    def _check_kjt_ends_not_within_dist(self, dist=1000, extension_beyond_kink=3000):
        """if end of kjt is within 1000mm of the batter elevs then raise a warning a set a flag to edit the kjoint to
        extend to batter (and then edit it separately)
        """
        batter_1_elev, batter_2_elev = self.batter_1_elev, self.batter_2_elev
        for jnt_obj in self.joint_objs:
            jt_name = jnt_obj.jt_name
            if jnt_obj.jt_type == "kjt":# and "mirr" not in jt_name:
                joint_poly_coords_transf = jnt_obj.joint_poly_coords_transf
                _, can_poly_ycoords = joint_poly_coords_transf["can"]
                min_y, max_y = min(can_poly_ycoords), max(can_poly_ycoords)
                # check batter 1 and 2 elevations vs k joints!
                for idx, batter_elev in enumerate([batter_1_elev, batter_2_elev]):
                    # x, y batter point
                    if max_y < batter_elev < max_y + dist:
                        location, y_ref = "Top", max_y
                    elif min_y > batter_elev > min_y - dist:
                        location, y_ref = "Bottom", min_y
                    else:
                        location = None

                    if location:
                        message = (f"{jt_name} {location.lower()} of Can is within {dist} mm of batter {idx+1} elevation ({batter_elev}). "
                                   f"{jt_name} has been extended beyond the batter elevation by {extension_beyond_kink} mm (to avoid "
                                   f"a combined kink and thickness transition SCF)")

                        self.warnings[f"batter_{idx+1}_kjt_interaction"] = {"flag": "warning", "message": message}

                        # joint name: [batter_elev, "above"]
                        kink_loc = "above_kjt" if location == "Top" else "below_kjt"
                        self.kjt_edits[jnt_obj] = [f"batter_{idx + 1}", kink_loc]

        if self.kjt_edits:
            self._edit_kjt_Can(extension_beyond_kink)

    def _edit_kjt_Can(self, extension_beyond_kink):
        # original points all with negative x coord points
        base_batter_1_pt = [-self.batter_1_width / 2, self.batter_1_elev]
        base_batter_2_pt = [-self.batter_2_width / 2, self.batter_2_elev]
        base_jkt_top_pt = [-self.tp_width / 2, self.tp_btm]
        base_pile_top_pt = [-self.jacket_footprint / 2, self.pile_top_elev]

        for jnt_obj, (batter, kink_loc) in self.kjt_edits.items():
            if jnt_obj.mirror:
                batter_1_pt = [-base_batter_1_pt[0], base_batter_1_pt[1]]
                batter_2_pt = [-base_batter_2_pt[0], base_batter_2_pt[1]]
                jkt_top_pt = [-base_jkt_top_pt[0], base_jkt_top_pt[1]]
                pile_top_pt = [-base_pile_top_pt[0], base_pile_top_pt[1]]
            else:
                batter_1_pt = base_batter_1_pt[:]
                batter_2_pt = base_batter_2_pt[:]
                jkt_top_pt = base_jkt_top_pt[:]
                pile_top_pt = base_pile_top_pt[:]

            # define pt1 i.e. the point at which the kink is
            pt1 = batter_1_pt if batter == "batter_1" else batter_2_pt
            # calculate point in far distance to define the vector between the kink point and the location
            # at which the kjt Can will be extended.
            if kink_loc == "above_kjt" and batter == "batter_1":
                pt_in_distance = jkt_top_pt
            elif kink_loc == "above_kjt" and batter == "batter_2":
                pt_in_distance = batter_1_pt
            elif kink_loc == "below_kjt" and batter == "batter_1":
                pt_in_distance = batter_2_pt
            elif kink_loc == "below_kjt" and batter == "batter_2":
                pt_in_distance = pile_top_pt

            pt1_arr = np.array(pt1)
            pt_dist_arr = np.array(pt_in_distance)
            # Compute the direction vector from pt1 to pt_dist_arr
            direction = pt_dist_arr - pt1
            length = np.linalg.norm(direction)
            unit_vector = direction / length # Normalize the direction vector
            pt2_arr = pt1_arr + unit_vector * extension_beyond_kink
            pt2 = pt2_arr.tolist()
            jnt_obj.extend_kjt_Can_and_kink(pt1, pt2, kink_loc)




