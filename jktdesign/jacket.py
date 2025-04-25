import numpy as np


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
        self.xjt_elevs = {}  # store the x joint elevations as well (note the x values are always 0 in the centre)

        self.warning_strings = []  # todo

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
        self._calculate_x_brace_elevations()

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

    @staticmethod
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

            x_intersection, y_intersection = Jacket.line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)

            assert np.isclose(x_intersection, 0.), "Error with x joint calc.."

            self.xjt_elevs[f"xjt_{k_this}"] = y_intersection







