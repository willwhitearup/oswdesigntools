import numpy as np
import copy
# local imports
from efthymiou.scf import x1, x2, x3, x4, t8, t9, x5, x6, x7, t1, t2, t3, t4, t6, x8, t7, t10, t11
from routing.core import tubular_cross_section_area, tubular_second_moment_of_area


class XTYJointSCFManager:
    """defines the JointSCFManager for X and TY Joints
    """
    def __init__(self, x_axis_desc: str, input_fields: dict, stress_adjusted: bool, joint_type: str):

        self.x_axis_desc, self.input_fields, self.stress_adjusted = x_axis_desc, input_fields, stress_adjusted
        self.joint_type = joint_type

        # unpack SCF variables. Done like this as Flask app requires unique global variables depending on site
        self.d1, self.thk1 = self.input_fields["D"], self.input_fields["T"]
        self.d2, self.thk2 = self.input_fields["d"], self.input_fields["t"]
        self.theta = self.input_fields["theta"]
        self.L = self.input_fields["L"]  # chord length
        self.C = self.input_fields["C"]  # chord end fixity (default as 0.7 in dnvrpc203)

        self.params = None

        self.scf_axial_a_chord_saddles = []  # x1
        self.scf_axial_a_chord_crowns = []  # x2
        self.scf_axial_a_brace_saddles = []  # x3
        self.scf_axial_a_brace_crowns = []  #x4

        self.scf_ipb_a_chord_crowns = []  # t8
        self.scf_ipb_a_brace_crowns = []  # t9
        self.scf_opb_a_chord_saddles, self.scf_opb_a_brace_saddles = [], []

        self.scf_axial_a_chord_saddle, self.scf_axial_a_chord_crown = None, None
        self.scf_axial_a_brace_saddle, self.scf_axial_a_brace_crown = None, None
        self.scf_ipb_a_chord_crown, self.scf_ipb_a_brace_crown = None, None
        self.scf_opb_a_chord_saddle, self.scf_opb_a_brace_saddle = None, None

        # stress adjusted SCFs brace A
        self.scf_axial_a_chord_crowns_adj = None # chordside
        self.scf_axial_a_chord_saddles_adj = None # chordside
        self.scf_axial_a_brace_crowns_adj = None
        self.scf_axial_a_brace_saddles_adj = None
        self.scf_ipb_a_chord_crowns_adj = None
        self.scf_opb_a_chord_saddles_adj = None

        # section properties----------------------------------------------------
        # chord section properties
        self.area_chord_nominal = None
        self.ixx_chord_nominal = None

        # brace a nominal section properties
        self.area_brace_a_nominal = None
        self.ixx_brace_a_nominal = None

        # store area and bending stiffness ratios for each brace
        self.brace_a_area_ratios = []
        self.brace_a_bending_stiffness_ratios = []

    def get_joint_scfs(self, load_type):

        if self.joint_type == "x":

            # get individual SCFs
            (self.scf_axial_a_chord_saddle, self.scf_axial_a_chord_crown, self.scf_axial_a_brace_saddle, self.scf_axial_a_brace_crown,
             self.scf_ipb_a_chord_crown, self.scf_ipb_a_brace_crown, self.scf_opb_a_chord_saddle, self.scf_opb_a_brace_saddle) = (
                self._calculate_scfs_x_joint(self.d1, self.d2, self.thk1, self.thk2, self.theta, self.L, load_type))

        elif self.joint_type == "ty":

            # get individual SCFs
            (self.scf_axial_a_chord_saddle, self.scf_axial_a_chord_crown, self.scf_axial_a_brace_saddle, self.scf_axial_a_brace_crown,
             self.scf_ipb_a_chord_crown, self.scf_ipb_a_brace_crown, self.scf_opb_a_chord_saddle, self.scf_opb_a_brace_saddle) = (
                self._calculate_scfs_ty_joint(self.d1, self.d2, self.thk1, self.thk2, self.theta, self.L, load_type))

        # get SCF trends
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
        self.area_brace_a_nominal = tubular_cross_section_area(self.d2, self.thk2)
        self.ixx_brace_a_nominal = tubular_second_moment_of_area(self.d2, self.thk2)

    def _generate_variable_list(self, fmin=0.8, fmax=1.2, nvars=11):
        # generated required array for float used to calculate corresponding array of scfs
        param_strt, param_end = fmin * self.input_fields[self.x_axis_desc], fmax * self.input_fields[self.x_axis_desc]
        self.params = np.linspace(param_strt, param_end, nvars)

    def convert_angles_to_degrees(self, x_axis_desc):
        """method to allow for conversion from radians to degrees (for plotting purposes)
        """
        if self.params is not None:
            if x_axis_desc == "theta":
                self.params = np.degrees(self.params)
        else:
            print("Angles not converted to degrees as params initialised as another variable type...Continuing.")

    def _calculate_scfs_x_joint(self, d1, d2, thk1, thk2, theta, L, load_type, ndps=5):

        # calculate SCFs with varied parameter
        if load_type == "balanced_forces":
            # AXIAL SCFs------------------------------------
            scf_axial_a_chord_saddle = x1(d1, d2, thk1, thk2, theta)  # chord side
            scf_axial_a_chord_crown = x2(d1, d2, thk1, thk2, theta)
            scf_axial_a_brace_saddle = x3(d1, d2, thk1, thk2, theta)  # brace side
            scf_axial_a_brace_crown = x4(d1, d2, thk1)
            # IPB SCFS-------------------------------------
            scf_ipb_a_chord_crown = t8(d1, d2, thk1, thk2, theta)
            scf_ipb_a_brace_crown = t9(d1, d2, thk1, thk2, theta)
            # OPB SCFS-------------------------------------
            scf_opb_a_chord_saddle = x5(d1, d2, thk1, thk2, theta)
            scf_opb_a_brace_saddle = x6(d1, d2, thk1, thk2, theta)

        elif load_type == "single_brace_load":
            c = 0.7  # todo, make this user input
            # AXIAL SCFs------------------------------------
            scf_axial_a_chord_saddle = x7(d1, d2, thk1, thk2, L, theta, c)  # chord side
            scf_axial_a_chord_crown = t6(d1, d2, thk1, thk2, L, theta, c)
            scf_axial_a_brace_saddle = x8(d1, d2, thk1, thk2, L, theta)  # brace side  # todo short chords saddle SCF reductions allowed (see eqn 19)
            scf_axial_a_brace_crown = t7(d1, d2, thk1, thk2, L, c)
            # IPB SCFS-------------------------------------
            scf_ipb_a_chord_crown = t8(d1, d2, thk1, thk2, theta)
            scf_ipb_a_brace_crown = t9(d1, d2, thk1, thk2, theta)
            # OPB SCFS-------------------------------------
            scf_opb_a_chord_saddle = t10(d1, d2, thk1, thk2, theta)
            scf_opb_a_brace_saddle = t11(d1, d2, thk1, thk2, theta)

        scfs = (scf_axial_a_chord_saddle, scf_axial_a_chord_crown, scf_axial_a_brace_saddle, scf_axial_a_brace_crown,
                scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_opb_a_chord_saddle, scf_opb_a_brace_saddle)

        scfs = [round(scf, ndps) for scf in scfs]
        return scfs

    def _calculate_scfs_ty_joint(self, d1, d2, thk1, thk2, theta, L, load_type, ndps=5):
        """load_type is only single_brace for a TY joint. Just included for consistency with other joints
        """
        c = 0.7  # todo, make this user input
        # AXIAL SCFs------------------------------------
        # end fixed
        scf_axial_a_chord_saddle = t1(d1, d2, thk1, thk2, theta) # chord side
        scf_axial_a_chord_crown = t2(d1, d2, thk1, thk2, L, theta)
        scf_axial_a_brace_saddle = t3(d1, d2, thk1, thk2, L, theta) # brace side
        scf_axial_a_brace_crown = t4(d1, d2, thk1, thk2, L)
        # todo general fixity conditions
        # IPB SCFS-------------------------------------
        scf_ipb_a_chord_crown = t8(d1, d2, thk1, thk2, theta)
        scf_ipb_a_brace_crown = t9(d1, d2, thk1, thk2, theta)
        # OPB SCFS-------------------------------------
        scf_opb_a_chord_saddle = t10(d1, d2, thk1, thk2, theta)
        scf_opb_a_brace_saddle = t11(d1, d2, thk1, thk2, theta)

        scfs = (scf_axial_a_chord_saddle, scf_axial_a_chord_crown, scf_axial_a_brace_saddle, scf_axial_a_brace_crown,
                scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_opb_a_chord_saddle, scf_opb_a_brace_saddle)

        scfs = [round(scf, ndps) for scf in scfs]
        return scfs

    def _calculate_brace_property_ratios(self, d2, thk2):
        """calculate ratios between the nominally provided brace section properties and the range of properties (defined
        by params)
        """
        # calculate brace area and Ixx at each increment of param
        area_brace_a, ixx_brace_a = tubular_cross_section_area(d2, thk2), tubular_second_moment_of_area(d2, thk2)

        # calculate area ratios for braces. Req'd for axial stress adjusted SCFs
        self.brace_a_area_ratios.append(self.area_brace_a_nominal / area_brace_a)  # brace A

        # calculate bending stiffness ratios for brace A
        brace_a_bending_stiffness_ratio = (self.ixx_brace_a_nominal * (d2 / 2.)) / (ixx_brace_a * (self.d2 / 2.))
        self.brace_a_bending_stiffness_ratios.append(brace_a_bending_stiffness_ratio)

    def _calculate_stress_adj_scfs(self):

        ## BRACE A
        # brace A chord-side SCFs - stress adjusted
        self.scf_axial_a_chord_crowns_adj = list(np.array(self.scf_axial_a_chord_crowns) * np.array(self.brace_a_area_ratios))
        self.scf_axial_a_chord_saddles_adj = list(np.array(self.scf_axial_a_chord_saddles) * np.array(self.brace_a_area_ratios))
        self.scf_ipb_a_chord_crowns_adj = list(self.scf_ipb_a_chord_crowns * np.array(self.brace_a_bending_stiffness_ratios))
        self.scf_opb_a_chord_saddles_adj = list(self.scf_opb_a_chord_saddles * np.array(self.brace_a_bending_stiffness_ratios))

        # brace A brace-side SCFs - stress adjusted
        self.scf_axial_a_brace_crowns_adj = list(np.array(self.scf_axial_a_brace_crowns) * np.array(self.brace_a_area_ratios))
        self.scf_axial_a_brace_saddles_adj = list(np.array(self.scf_axial_a_brace_saddles) * np.array(self.brace_a_area_ratios))
        self.scf_ipb_a_brace_crowns_adj = list(self.scf_ipb_a_brace_crowns * np.array(self.brace_a_bending_stiffness_ratios))
        self.scf_opb_a_brace_saddles_adj = list(self.scf_opb_a_brace_saddles * np.array(self.brace_a_bending_stiffness_ratios))

    def _joint_scf_variations(self, load_type):

        # create local variables originally equal to class attributes (floats are immutable so this is ok)
        d1, thk1 = self.d1, self.thk1
        d2, thk2 = self.d2, self.thk2
        theta = self.theta
        L = self.L

        for param in self.params:
            # determine which parameter has been selected to vary by User
            if self.x_axis_desc == "D":
                d1 = copy.copy(param)
            elif self.x_axis_desc == "T":
                thk1 = copy.copy(param)
            elif self.x_axis_desc == "d":
                d2 = copy.deepcopy(param)
            elif self.x_axis_desc == "t":
                thk2 = copy.deepcopy(param)
            elif self.x_axis_desc == "theta":
                theta = copy.deepcopy(param)
            elif self.x_axis_desc == "L":
                L = copy.deepcopy(param)

            # get all SCFs
            if self.joint_type == "x":
                (scf_axial_a_chord_saddle, scf_axial_a_chord_crown, scf_axial_a_brace_saddle, scf_axial_a_brace_crown,
                 scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_opb_a_chord_saddle, scf_opb_a_brace_saddle) = (
                    self._calculate_scfs_x_joint(d1, d2, thk1, thk2, theta, L, load_type))
            elif self.joint_type == "ty":
                (scf_axial_a_chord_saddle, scf_axial_a_chord_crown, scf_axial_a_brace_saddle, scf_axial_a_brace_crown,
                 scf_ipb_a_chord_crown, scf_ipb_a_brace_crown, scf_opb_a_chord_saddle, scf_opb_a_brace_saddle) = (
                    self._calculate_scfs_ty_joint(d1, d2, thk1, thk2, theta, L, load_type))

            # AXIAL SCFs---------------------------------------------------
            self.scf_axial_a_chord_saddles.append(scf_axial_a_chord_saddle)  # chord side
            self.scf_axial_a_chord_crowns.append(scf_axial_a_chord_crown)
            self.scf_axial_a_brace_saddles.append(scf_axial_a_brace_saddle)
            self.scf_axial_a_brace_crowns.append(scf_axial_a_brace_crown)
            # IPB SCFS
            self.scf_ipb_a_chord_crowns.append(scf_ipb_a_chord_crown)
            self.scf_ipb_a_brace_crowns.append(scf_ipb_a_brace_crown)
            # OPB SCFS
            self.scf_opb_a_chord_saddles.append(scf_opb_a_chord_saddle)
            self.scf_opb_a_brace_saddles.append(scf_opb_a_brace_saddle)

            # calculate area and stiffness ratios
            self._calculate_brace_property_ratios(d2, thk2)

        # calculate stress adjusted scfs
        self._calculate_stress_adj_scfs()
