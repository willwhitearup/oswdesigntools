from boltedconn.tensionerdata import BoltTensionerLibrary
import numpy as np
import math

class BoltedFlange:

    def __init__(self, outer_diameter, wall_thickness, flange_height, flange_length, bolt_tensioner_tool, ULS_bending_moment, ULS_axial_force):

        self.outer_diameter: float = outer_diameter

        self.wall_thickness: float = wall_thickness
        self.flange_height: float = flange_height
        self.flange_length: float = flange_length
        self.bolt_tensioner_tool: BoltTensionerLibrary = bolt_tensioner_tool
        self.ULS_bending_moment = ULS_bending_moment
        self.ULS_axial_force = ULS_axial_force

        self.a = None
        self.b = None
        self.b_star = None
        self._compute_geometry()


    def _compute_geometry(self):
        self.inner_diameter = self.outer_diameter - 2 * self.wall_thickness
        self.radius = self.outer_diameter / 2

        # flange geom
        self.b_star = self.bolt_tensioner_tool['le_min'] + self.wall_thickness
        self.b = self.bolt_tensioner_tool['le_min'] + 0.5 * self.wall_thickness
        self.a = self.flange_length - self.b_star

    @property
    def bolt_centre_diameter(self):  # bolt centre diameter aka BCD
        return self.outer_diameter - 2 * self.b_star

    @property
    def n_bolts(self):
        n_bolts_dp = np.radians(180) / np.asin(self.bolt_tensioner_tool["t"] / self.bolt_centre_diameter)
        n_bolts = math.floor(n_bolts_dp) - math.floor(n_bolts_dp) % 2
        return n_bolts

    @property
    def shell_section_area_single_bolt(self):
        return 0.25 * np.pi * (self.outer_diameter ** 2 - self.inner_diameter ** 2) / self.n_bolts

    @property
    def section_modulus_single_bolt(self):
        return np.pi * (self.outer_diameter / 2 - self.wall_thickness / 2) ** 2 * self.wall_thickness

    @property
    def bolt_sector_force(self):
        return (self.ULS_bending_moment / self.section_modulus_single_bolt) * self.shell_section_area_single_bolt - self.ULS_axial_force / self.n_bolts

    def geometry_validity_check(self):
        a_b_ratio = self.a / self.b
        alpha = self.flange_height / (self.a + self.b)  # G.14
        beta = ((a_b_ratio - 1.25) ** 0.32) + 0.45  # G.15
        bolt_lambda = 1 - (1 - alpha ** beta) ** 5

        if a_b_ratio <= 1.25:
            pass
        elif 1.25 < a_b_ratio <= 2.25 and (-0.12 * self.a + 0.55 <= alpha <= 1):  # G.16, G.17
            print("Extension by Tobinaga and Ishihara is being implemented through modification of the length a. See IEC guidance!")
            self.a = self.a * bolt_lambda  # G.12 — now directly overwrites a
        else:
            raise Exception(f"Invalid flange geometry. Check a and b values")





