import  numpy as np
from efthymiou.scf import k1, k2, t8, t9, k4, k5, t5, t7, t6, t3, k7, k6  # chord scfs
import copy

from main.core import tubular_cross_section_area, tubular_second_moment_of_area

"""
Table B-3 Stress concentration factors for simple tubular K joints
Balanced axial load
Unbalanced in plane bending
Unbalanced out of plane bending
"""

class KJointSCFManager:

    def __init__(self, x_axis_desc: str, input_fields: dict, stress_adjusted: bool):

        # define attributes
        self.x_axis_desc = x_axis_desc  # str, defines which parameter to vary
        self.input_fields = input_fields  # dict, of all joint inputs (chord and brace a and brace b...)
        self.stress_adjusted = stress_adjusted  # bool, includes allowance for nominal section size stress

        # unpack SCF variables
        self.d1 = self.input_fields["D"]
        self.thk1 = self.input_fields["T"]
        self.d2_a = self.input_fields["dA"]
        self.d2_b = self.input_fields["dB"]
        self.thk2_a, self.thk2_b = self.input_fields["tA"], self.input_fields["tB"]
        self.theta_a, self.theta_b = self.input_fields["thetaA"], self.input_fields["thetaB"]
        self.g_ab = self.input_fields["g_ab"]
        self.L = self.input_fields["L"]  # chord length
        self.C = self.input_fields["C"]  # chord end fixity (default as 0.7 in dnvrpc203)

        # store all SCFs for each load type
        # AXIAL SCFs----------------
        self.scf_a_axial_chord_crowns, self.scf_b_axial_chord_crowns = [], []
        self.scf_a_axial_brace_crowns, self.scf_b_axial_brace_crowns = [], []

        self.scf_a_axial_chord_saddles, self.scf_a_axial_brace_saddles = [], []
        self.scf_b_axial_chord_saddles, self.scf_b_axial_brace_saddles = [], []

        # IPB SCFs-----------
        self.scf_ipb_a_chord_crowns, self.scf_ipb_a_brace_crowns = [], []
        self.scf_ipb_b_chord_crowns, self.scf_ipb_b_brace_crowns = [], []

        # OPB SCFs-----------
        self.scf_opb_a_chord_saddles, self.scf_opb_a_brace_saddles = [], []
        self.scf_opb_b_chord_saddles, self.scf_opb_b_brace_saddles = [], []

        # stress adjusted SCFs brace B # chordside
        self.scf_a_axial_chord_crowns_adj = None
        self.scf_a_axial_chord_saddles_adj = None
        self.scf_a_axial_brace_crowns_adj = None
        self.scf_a_axial_brace_saddles_adj = None
        self.scf_ipb_a_chord_crowns_adj = None
        self.scf_opb_a_chord_saddles_adj = None

        # stress adjusted SCFs brace B  # chordside
        self.scf_b_axial_chord_crowns_adj = None
        self.scf_b_axial_chord_saddles_adj = None
        self.scf_b_axial_brace_crowns_adj = None
        self.scf_b_axial_brace_saddles_adj = None
        self.scf_ipb_b_chord_crowns_adj = None
        self.scf_opb_b_chord_saddles_adj = None

        # to populate
        self.params = None  # np.array

        # section properties----------------------------------------------------
        # chord section properties
        self.area_chord_nominal = None
        self.ixx_chord_nominal = None

        # brace a nominal section properties
        self.area_brace_a_nominal = None
        self.ixx_brace_a_nominal = None

        # brace b nominal section properties
        self.area_brace_b_nominal = None
        self.ixx_brace_b_nominal = None

        # store area and bending stiffness ratios for each brace
        self.brace_a_area_ratios, self.brace_b_area_ratios = [], []
        self.brace_a_bending_stiffness_ratios, self.brace_b_bending_stiffness_ratios = [], []

    def get_joint_scfs(self, load_type):
        """public method to calculate scfs for K-joint
        """
        # calculate 16 SCF vars for K joint with brace A and brace B
        (self.scf_axial_a_chord_crown, self.scf_axial_a_brace_crown, self.scf_axial_b_chord_crown, self.scf_axial_b_brace_crown,
         self.scf_axial_a_chord_saddle, self.scf_axial_a_brace_saddle, self.scf_axial_b_chord_saddle, self.scf_axial_b_brace_saddle,
         self.scf_ipb_a_chord_crown, self.scf_ipb_a_brace_crown, self.scf_ipb_b_chord_crown, self.scf_ipb_b_brace_crown,
         self.scf_opb_a_chord_saddle, self.scf_opb_a_brace_saddle, self.scf_opb_b_chord_saddle, self.scf_opb_b_brace_saddle) = (
            self._calculate_scfs(self.d1, self.d2_a, self.d2_b, self.thk1, self.thk2_a, self.thk2_b, self.theta_a, self.theta_b, self.g_ab, self.L, load_type, ndps=2))

        # calculate the SCFs with varying parameters
        self._calculate_nominal_section_properties()  # required if stress_adjusted is true
        self._generate_variable_list()
        self._joint_scf_variations(load_type)

    def _calculate_nominal_section_properties(self):
        """calculate section properties of the nominal chord and brace section properties
        """
        # chord nominal section properties
        self.area_chord_nominal = tubular_cross_section_area(self.d1, self.thk1)
        self.ixx_chord_nominal = tubular_second_moment_of_area(self.d1, self.thk1)

        # brace a nominal section properties
        self.area_brace_a_nominal = tubular_cross_section_area(self.d2_a, self.thk2_a)
        self.ixx_brace_a_nominal = tubular_second_moment_of_area(self.d2_a, self.thk2_a)

        # brace b nominal section properties
        self.area_brace_b_nominal = tubular_cross_section_area(self.d2_b, self.thk2_b)
        self.ixx_brace_b_nominal = tubular_second_moment_of_area(self.d2_b, self.thk2_b)

    def convert_angles_to_degrees(self, x_axis_desc):
        """method to allow for conversion from radians to degrees (for plotting purposes)
        """
        if self.params is not None:
            if x_axis_desc == "thetaA" or x_axis_desc == "thetaB":
                self.params = np.degrees(self.params)
        else:
            print("Angles not converted to degrees as params initialised as another variable type...Continuing.")

    def _generate_variable_list(self, fmin=0.8, fmax=1.2, nvars=11):
        # generated required array for float used to calculate corresponding array of scfs
        param_strt, param_end = fmin * self.input_fields[self.x_axis_desc], fmax * self.input_fields[self.x_axis_desc]
        self.params = np.linspace(param_strt, param_end, nvars)

    def _calculate_scfs(self, d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab, L, load_type="balanced_axial_unbalanced_moment", ndps=5):

        # calculate SCFs with varied parameter
        if load_type == "balanced_axial_unbalanced_moment":
            # AXIAL LOAD SCFs-------------------------------------------------------------------------------------------------------
            # brace A and B, crowns and saddles
            scf_axial_a_chord_crown, scf_axial_b_chord_crown, _ = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)
            scf_axial_a_brace_crown, scf_axial_b_brace_crown, _ = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)
            # saddles
            scf_axial_a_chord_saddle, scf_axial_b_chord_saddle, _ = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)
            scf_axial_a_brace_saddle, scf_axial_b_brace_saddle, _ = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)

            # IPB LOAD SCFs-------------------------------------------------------------------------------------------------------
            # brace A
            scf_ipb_a_chord_crown = t8(d1, d2_a, thk1, thk2_a, theta_a)  # chordside
            scf_ipb_a_brace_crown = t9(d1, d2_a, thk1, thk2_a, theta_a)  # braceside
            # brace B
            scf_ipb_b_chord_crown = t8(d1, d2_b, thk1, thk2_b, theta_b)  # chordside
            scf_ipb_b_brace_crown = t9(d1, d2_b, thk1, thk2_b, theta_b)  # braceside

            # OPB LOAD SCFs-------------------------------------------------------------------------------------------------------
            # brace A and brace B chord-side saddle SCFs
            scf_opb_a_chord_saddle, scf_opb_b_chord_saddle = k4(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)
            # brace A and brace B brace-side saddle SCFs
            scf_opb_a_brace_saddle, scf_opb_b_brace_saddle = k5(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)


        elif load_type == "single_brace_load":
            c = 0.7  # chord end fixity default
            ## AXIAL SCFs
            # brace A
            scf_axial_a_chord_crown = t6(d1, d2_a, thk1, thk2_a, L, theta_a, c)  # chordside
            scf_axial_a_brace_crown = t7(d1, d2_a, thk1, thk2_a, L, c)  # braceside
            scf_axial_a_chord_saddle = t5(d1, d2_a, thk1, thk2_a, L, theta_a, c) # chordside
            scf_axial_a_brace_saddle = t3(d1, d2_a, thk1, thk2_a, L, theta_a) # braceside
            # brace B
            scf_axial_b_chord_crown = t6(d1, d2_b, thk1, thk2_b, L, theta_b, c)  # chordside
            scf_axial_b_brace_crown = t7(d1, d2_b, thk1, thk2_b, L, c)  # braceside
            scf_axial_b_chord_saddle = t5(d1, d2_b, thk1, thk2_b, L, theta_b, c)  # chordside
            scf_axial_b_brace_saddle = t3(d1, d2_b, thk1, thk2_b, L, theta_b)  # braceside

            ## IPB SCFs
            # brace A
            scf_ipb_a_chord_crown = t8(d1, d2_a, thk1, thk2_a, theta_a)  # chordside
            scf_ipb_a_brace_crown = t9(d1, d2_a, thk1, thk2_a, theta_a)  # braceside
            # brace B
            scf_ipb_b_chord_crown = t8(d1, d2_b, thk1, thk2_b, theta_b)  # chordside
            scf_ipb_b_brace_crown = t9(d1, d2_b, thk1, thk2_b, theta_b)  # braceside

            ## OPB SCFs (for consistency, just written out equations twice)
            # brace A
            scf_opb_a_chord_saddle, _ = k6(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)  # chordside
            scf_opb_a_brace_saddle, _ = k7(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)  # braceside
            # brace B
            _, scf_opb_b_chord_saddle = k6(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)  # chordside
            _, scf_opb_b_brace_saddle = k7(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab)  # braceside

        else:
            print("Load type not allowed...Try again.")

        scfs = (scf_axial_a_chord_crown, scf_axial_a_brace_crown, scf_axial_b_chord_crown, scf_axial_b_brace_crown,  # brace a axial, brace b axial saddles
                scf_axial_a_chord_saddle, scf_axial_a_brace_saddle, scf_axial_b_chord_saddle, scf_axial_b_brace_saddle,  # brace a axial, brace b axial saddles
                scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_ipb_b_chord_crown, scf_ipb_b_brace_crown,  # brace a ipb, brace b ipb
                scf_opb_a_chord_saddle, scf_opb_a_brace_saddle, scf_opb_b_chord_saddle, scf_opb_b_brace_saddle)  # brace a opb, brace b opb

        scfs = [round(scf, ndps) for scf in scfs]

        return scfs

    def _calculate_brace_property_ratios(self, d2_a, d2_b, thk2_a, thk2_b):
        """calculate ratios between the nominally provided brace section properties and the range of properties (defined
        by params)
        """
        # calculate brace area and Ixx at each increment of param
        area_brace_a, ixx_brace_a = tubular_cross_section_area(d2_a, thk2_a), tubular_second_moment_of_area(d2_a, thk2_a)
        area_brace_b, ixx_brace_b = tubular_cross_section_area(d2_b, thk2_b), tubular_second_moment_of_area(d2_b, thk2_b)

        # calculate area ratios for braces. Req'd for axial stress adjusted SCFs
        self.brace_a_area_ratios.append(self.area_brace_a_nominal / area_brace_a)  # brace A
        self.brace_b_area_ratios.append(self.area_brace_b_nominal / area_brace_b)  # brace B

        # calculate bending stiffness ratios for brace A
        brace_a_bending_stiffness_ratio = (self.ixx_brace_a_nominal * (d2_a / 2.)) / (ixx_brace_a * (self.d2_a / 2.))
        self.brace_a_bending_stiffness_ratios.append(brace_a_bending_stiffness_ratio)

        # calculate bending stiffness ratios for brace B
        brace_b_bending_stiffness_ratio = (self.ixx_brace_b_nominal * (d2_b / 2.)) / (ixx_brace_b * (self.d2_b / 2.))
        self.brace_b_bending_stiffness_ratios.append(brace_b_bending_stiffness_ratio)

    def _calculate_stress_adj_scfs(self):

        ## BRACE A
        # brace A chord-side SCFs - stress adjusted
        self.scf_a_axial_chord_crowns_adj = list(np.array(self.scf_a_axial_chord_crowns) * np.array(self.brace_a_area_ratios))
        self.scf_a_axial_chord_saddles_adj = list(np.array(self.scf_a_axial_chord_saddles) * np.array(self.brace_a_area_ratios))
        self.scf_ipb_a_chord_crowns_adj = list(self.scf_ipb_a_chord_crowns * np.array(self.brace_a_bending_stiffness_ratios))
        self.scf_opb_a_chord_saddles_adj = list(self.scf_opb_a_chord_saddles * np.array(self.brace_a_bending_stiffness_ratios))

        # brace A brace-side SCFs - stress adjusted
        self.scf_a_axial_brace_crowns_adj = list(np.array(self.scf_a_axial_brace_crowns) * np.array(self.brace_a_area_ratios))
        self.scf_a_axial_brace_saddles_adj = list(np.array(self.scf_a_axial_brace_saddles) * np.array(self.brace_a_area_ratios))
        self.scf_ipb_a_brace_crowns_adj = list(self.scf_ipb_a_brace_crowns * np.array(self.brace_a_bending_stiffness_ratios))
        self.scf_opb_a_brace_saddles_adj = list(self.scf_opb_a_brace_saddles * np.array(self.brace_a_bending_stiffness_ratios))

        ## BRACE B
        # brace B chord-side SCFs - stress adjusted
        self.scf_b_axial_chord_crowns_adj = list(np.array(self.scf_b_axial_chord_crowns) * np.array(self.brace_b_area_ratios))
        self.scf_b_axial_chord_saddles_adj = list(np.array(self.scf_b_axial_chord_saddles) * np.array(self.brace_b_area_ratios))
        self.scf_ipb_b_chord_crowns_adj = list(self.scf_ipb_b_chord_crowns * np.array(self.brace_b_bending_stiffness_ratios))
        self.scf_opb_b_chord_saddles_adj = list(self.scf_opb_b_chord_saddles * np.array(self.brace_b_bending_stiffness_ratios))

        # brace B brace-side SCFs - stress adjusted
        self.scf_b_axial_brace_crowns_adj = list(np.array(self.scf_b_axial_brace_crowns) * np.array(self.brace_b_area_ratios))
        self.scf_b_axial_brace_saddles_adj = list(np.array(self.scf_b_axial_brace_saddles) * np.array(self.brace_b_area_ratios))
        self.scf_ipb_b_brace_crowns_adj = list(self.scf_ipb_b_brace_crowns * np.array(self.brace_b_bending_stiffness_ratios))
        self.scf_opb_b_brace_saddles_adj = list(self.scf_opb_b_brace_saddles * np.array(self.brace_b_bending_stiffness_ratios))

    def _joint_scf_variations(self, load_type):

        # create local variables originally equal to class attributes (floats are immutable so this is ok)
        d1, thk1 = self.d1, self.thk1
        d2_a, d2_b = self.d2_a, self.d2_b
        thk2_a, thk2_b = self.thk2_a, self.thk2_b
        theta_a, theta_b = self.theta_a, self.theta_b
        g_ab = self.g_ab
        L = self.L

        for param in self.params:

            # determine which parameter has been selected to vary by User
            if self.x_axis_desc == "D":
                d1 = copy.copy(param)
            elif self.x_axis_desc == "T":
                thk1 = copy.copy(param)
            elif self.x_axis_desc == "dA":
                d2_a = copy.deepcopy(param)
            elif self.x_axis_desc == "tA":
                thk2_a = copy.deepcopy(param)
            elif self.x_axis_desc == "thetaA":
                theta_a = copy.deepcopy(param)
            elif self.x_axis_desc == "dB":
                d2_b = copy.deepcopy(param)
            elif self.x_axis_desc == "tB":
                thk2_b = copy.deepcopy(param)
            elif self.x_axis_desc == "thetaB":
                theta_b = copy.deepcopy(param)
            elif self.x_axis_desc == "g_ab":
                g_ab = copy.deepcopy(param)
            elif self.x_axis_desc == "L":
                L = copy.deepcopy(param)


            (scf_axial_a_chord_crown, scf_axial_a_brace_crown, scf_axial_b_chord_crown, scf_axial_b_brace_crown,
             scf_axial_a_chord_saddle, scf_axial_a_brace_saddle, scf_axial_b_chord_saddle, scf_axial_b_brace_saddle,
             scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_ipb_b_chord_crown, scf_ipb_b_brace_crown,
             scf_opb_a_chord_saddle, scf_opb_a_brace_saddle, scf_opb_b_chord_saddle, scf_opb_b_brace_saddle) = (
                self._calculate_scfs(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab, L, load_type)
            )

            # STORE SCF ARRAYS

            # AXIAL SCFs---------------------------------------------------
            # brace A crowns
            self.scf_a_axial_chord_crowns.append(scf_axial_a_chord_crown)  # chord side
            self.scf_a_axial_brace_crowns.append(scf_axial_a_brace_crown)  # brace side

            # brace B crowns
            self.scf_b_axial_chord_crowns.append(scf_axial_b_chord_crown)  # chord side
            self.scf_b_axial_brace_crowns.append(scf_axial_b_brace_crown)  # brace side

            # brace A saddles
            self.scf_a_axial_chord_saddles.append(scf_axial_a_chord_saddle)  # chord side
            self.scf_a_axial_brace_saddles.append(scf_axial_a_brace_saddle)  # brace side

            # brace B saddles
            self.scf_b_axial_chord_saddles.append(scf_axial_b_chord_saddle)  # chord side
            self.scf_b_axial_brace_saddles.append(scf_axial_b_brace_saddle)  # brace side

            # IPB SCFs---------------------------------------------------
            # brace A
            self.scf_ipb_a_chord_crowns.append(scf_ipb_a_chord_crown)  # chord side
            self.scf_ipb_a_brace_crowns.append(scf_ipb_a_brace_crown)  # brace side

            # brace B
            self.scf_ipb_b_chord_crowns.append(scf_ipb_b_chord_crown)  # chord side
            self.scf_ipb_b_brace_crowns.append(scf_ipb_b_brace_crown)  # brace side

            # OPB SCFs---------------------------------------------------
            # brace A
            self.scf_opb_a_chord_saddles.append(scf_opb_a_chord_saddle)  # chord side
            self.scf_opb_a_brace_saddles.append(scf_opb_a_brace_saddle)  # brace side

            # brace B
            self.scf_opb_b_chord_saddles.append(scf_opb_b_chord_saddle)  # chord side
            self.scf_opb_b_brace_saddles.append(scf_opb_b_brace_saddle)  # brace side

            # calculate area and stiffness ratios
            self._calculate_brace_property_ratios(d2_a, d2_b, thk2_a, thk2_b)

        # calculate stress adjusted scfs
        self._calculate_stress_adj_scfs()


class ChordPropertyManager:

    def __init__(self, length, outer_diameter, thk):
        self.length, self.outer_diameter, self.thk = length, outer_diameter, thk
        self.alpha, self.gamma = None, None
        self.alpha_calc()

    def alpha_calc(self):
        self.alpha = 2 * self.length / self.outer_diameter
        self.gamma = self.outer_diameter / (2 * self.thk)




