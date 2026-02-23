from boltedconn.boltdata import Bolt
from boltedconn.steel import SteelMaterial
from boltedconn.tensionerdata import BoltTensionerLibrary
import numpy as np
import math

class BoltedFlange:

    def __init__(self, outer_diameter, wall_thickness, flange_height, flange_length, bolt_tensioner_tool, bolt_obj, flange_steel, tower_wall_steel,
                 ULS_bending_moment, ULS_axial_force):

        self.outer_diameter: float = outer_diameter

        self.wall_thickness: float = wall_thickness
        self.flange_height: float = flange_height
        self.flange_length: float = flange_length
        self.bolt_tensioner_tool: BoltTensionerLibrary = bolt_tensioner_tool
        self.bolt_obj: Bolt = bolt_obj
        self.flange_steel: SteelMaterial = flange_steel
        self.tower_wall_steel: SteelMaterial = tower_wall_steel
        self.ULS_bending_moment = ULS_bending_moment
        self.ULS_axial_force = ULS_axial_force

        self.valid_geom = True  # assume valid geom
        self.Fu_convergence = True
        self.a = None
        self.b = None
        self.b_star = None
        self._compute_geometry()

        # failure modes
        self.Fu_A = None
        self.Fu_B = None
        self.Fu_D = None
        self.Fu_E = None

    def _compute_geometry(self):
        self.inner_diameter = self.outer_diameter - 2 * self.wall_thickness
        self.radius = self.outer_diameter / 2

        # flange geom
        self.b_star = self.bolt_tensioner_tool['le_min'] + self.wall_thickness
        self.b = self.bolt_tensioner_tool['le_min'] + 0.5 * self.wall_thickness
        self.a = self.flange_length - self.b_star

        washer_annulus = 0.5 * (self.bolt_obj.washer_diameter - self.bolt_obj.hole_diameter)
        self.b_dashE = self.b - 0.5 * self.bolt_obj.hole_diameter - 0.5 * washer_annulus

        self.bolt_centre_diameter = self.outer_diameter - 2 * self.b_star
        n_bolts_dp = np.radians(180) / np.asin(self.bolt_tensioner_tool["t"] / self.bolt_centre_diameter)
        self.n_bolts = math.floor(n_bolts_dp) - math.floor(n_bolts_dp) % 2

        # width at the hole
        self.c = np.pi * self.bolt_centre_diameter / self.n_bolts
        self.c = np.pi * (self.bolt_centre_diameter - self.wall_thickness) / self.n_bolts
        self.c_dash = self.c - self.bolt_obj.hole_diameter


    @property
    def shell_section_area_single_bolt(self):
        return 0.25 * np.pi * (self.outer_diameter ** 2 - self.inner_diameter ** 2) / self.n_bolts

    @property
    def section_modulus_single_bolt(self):
        return np.pi * (self.outer_diameter / 2 - self.wall_thickness / 2) ** 2 * self.wall_thickness

    @property
    def bolt_sector_force(self):
        return (self.ULS_bending_moment / self.section_modulus_single_bolt) * self.shell_section_area_single_bolt - self.ULS_axial_force / self.n_bolts

    def geometry_validity_check(self, maintain_a_b_ratio_1_25=False):
        a_b_ratio = self.a / self.b
        alpha = self.flange_height / (self.a + self.b)  # G.14
        beta = ((a_b_ratio - 1.25) ** 0.32) + 0.45  # G.15
        bolt_lambda = 1 - (1 - alpha ** beta) ** 5

        if 0. < a_b_ratio <= 1.25:
            pass
        elif 1.25 < a_b_ratio <= 2.25 and (-0.12 * self.a + 0.55 <= alpha <= 1):  # G.16, G.17
            print("Extension by Tobinaga and Ishihara is being implemented through modification of the length a. See IEC guidance!")
            self.a = self.a * bolt_lambda  # G.12 — now directly overwrites a
            if maintain_a_b_ratio_1_25:
                self.valid_geom = False
        else:
            self.valid_geom = False
            # raise Exception(f"Invalid flange geometry. Check a and b values")

    def calc_flange_plastic_hinge_resistance(self):
        """See annex G IEC
        """
        self.M_dash_pl2 = self.c_dash * self.flange_height ** 2 * self.flange_steel.design_yield_strength / 4  # G.7
        self.M_pl2 = self.c * self.flange_height ** 2 * self.flange_steel.design_yield_strength / 4  # G.8
        self.dM_pl2 = (self.bolt_obj.F_tR / 2) * ((self.bolt_obj.washer_diameter + self.bolt_obj.hole_diameter) / 4)  # G.9
        # Resistance of the tower shell / flange for plastic hinges in/close to the tower shell
        self.M_pl_Bl = (self.c * self.wall_thickness ** 2 / 4) * self.tower_wall_steel.design_yield_strength  # G.10
        self.M_pl_Fl = (self.c * self.flange_height ** 2 / 4) * self.flange_steel.design_yield_strength  # G.10

    def calc_bolted_connection_failure_modes(self, Fu=1e6):
        """Failure modes require iterative procedure
        """
        tolerance = 1  # find Fu to within 1 N tolerance
        max_iter = 1000
        i = 0

        while True:
            # G.11
            N = V = Fu
            N_pl_Bl = self.tower_wall_steel.design_yield_strength * self.wall_thickness * self.c
            V_pl_Fl = self.flange_steel.design_yield_strength * self.flange_height * (self.c / np.sqrt(3))
            M_pl_N_Bl = (1 - (N / N_pl_Bl) ** 2) * self.M_pl_Bl
            M_pl_V_Fl = np.sqrt(1 - (V / V_pl_Fl) ** 2) * self.M_pl_Fl
            self.M_pl3 = min(M_pl_N_Bl, M_pl_V_Fl)

            # bolt failure modes
            Fu_A = self.bolt_obj.F_tR
            Fu_B = (self.bolt_obj.F_tR * self.a + self.M_pl3) / (self.a + self.b)
            Fu_D = (self.M_dash_pl2 + self.dM_pl2 + self.M_pl3) / self.b
            Fu_E = (self.M_pl2 + self.M_pl3) / self.b_dashE

            Fu_min = min(Fu_A, Fu_B, Fu_D, Fu_E)

            # Check convergence
            if abs(Fu - Fu_min) < tolerance:
                print(f"Fu={Fu}. Iteratively found in {i} loops")
                break

            Fu = Fu_min  # update Fu for next iteration

            i += 1
            if i > max_iter:

                self.Fu_convergence = False
                # raise RuntimeError("Fu iteration did not converge")

        self.Fu_A = Fu_A
        self.Fu_B = Fu_B
        self.Fu_D = Fu_D
        self.Fu_E = Fu_E

    def calc_util(self):
        Fu_dict = {
            "A": self.Fu_A,
            "B": self.Fu_B,
            "D": self.Fu_D,
            "E": self.Fu_E
        }
        self.failure_mode_governing = min(Fu_dict, key=Fu_dict.get)
        self.Fu_resistance_governing = Fu_dict[self.failure_mode_governing]

        # calculate util
        self.util = self.bolt_sector_force / self.Fu_resistance_governing










