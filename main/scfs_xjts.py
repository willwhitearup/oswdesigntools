import numpy as np
import copy
# local imports
from efthymiou.scf import x1, x2, x3, x4


class XJointSCFManager:

    def __init__(self, x_axis_desc: str, input_fields: dict, stress_adjusted: bool):

        self.x_axis_desc, self.input_fields, self.stress_adjusted = x_axis_desc, input_fields, stress_adjusted

        # unpack SCF variables
        self.d1 = self.input_fields["Dx"]
        self.thk1 = self.input_fields["Tx"]
        self.d2 = self.input_fields["dax"]
        self.thk2 = self.input_fields["tax"]
        self.theta = self.input_fields["thetax"]
        self.L = self.input_fields["Lx"]  # chord length
        self.C = self.input_fields["Cx"]  # chord end fixity (default as 0.7 in dnvrpc203)
        self.params = None

        self.scf_a_axial_chord_saddles = []  # x1
        self.scf_a_axial_chord_crowns = []  # x2
        self.scf_a_axial_brace_saddles = []  # x3
        self.scf_a_axial_brace_crowns = []  #x4


    def get_joint_scfs(self, load_type):
        self._generate_variable_list()
        self._joint_scf_variations(load_type)

    def _generate_variable_list(self, fmin=0.8, fmax=1.2, nvars=11):
        # generated required array for float used to calculate corresponding array of scfs
        param_strt, param_end = fmin * self.input_fields[self.x_axis_desc], fmax * self.input_fields[self.x_axis_desc]
        self.params = np.linspace(param_strt, param_end, nvars)

    def _calculate_scfs(self, d1, d2, thk1, thk2, theta, L, load_type, ndps=5):

        # calculate SCFs with varied parameter
        if load_type == "balanced_forces":
            # AXIAL LOAD SCFs-------------------------------------------------------------------------------------------------------
            # brace A, crowns and saddles
            scf_a_axial_chord_saddle = x1(d1, d2, thk1, thk2, theta)
            scf_a_axial_chord_crown = x2(d1, d2, thk1, thk2, theta)

            # brace side
            scf_a_axial_brace_saddle = x3(d1, d2, thk1, thk2, theta)
            scf_a_axial_brace_crown = x4(d1, d2, thk1)

        elif load_type == "single_brace_load":

            pass

        return scf_a_axial_chord_saddle, scf_a_axial_chord_crown, scf_a_axial_brace_saddle, scf_a_axial_brace_crown


    def _joint_scf_variations(self, load_type):

        # create local variables originally equal to class attributes (floats are immutable so this is ok)
        d1, thk1 = self.d1, self.thk1
        d2, thk2 = self.d2, self.thk2
        theta = self.theta
        L = self.L

        for param in self.params:
            # determine which parameter has been selected to vary by User
            if self.x_axis_desc == "Dx":
                d1 = copy.copy(param)
            elif self.x_axis_desc == "Tx":
                thk1 = copy.copy(param)
            elif self.x_axis_desc == "dax":
                d2 = copy.deepcopy(param)
            elif self.x_axis_desc == "tax":
                thk2 = copy.deepcopy(param)
            elif self.x_axis_desc == "thetax":
                theta = copy.deepcopy(param)
            elif self.x_axis_desc == "Lx":
                L = copy.deepcopy(param)

            # AXIAL
            # chord side
            scf_a_axial_chord_saddle, scf_a_axial_chord_crown, scf_a_axial_brace_saddle, scf_a_axial_brace_crown = self._calculate_scfs(d1, d2, thk1, thk2, theta, L, load_type)


            # AXIAL SCFs---------------------------------------------------
            # brace A
            self.scf_a_axial_chord_saddles.append(scf_a_axial_chord_saddle)  # chord side
            self.scf_a_axial_chord_crowns.append(scf_a_axial_chord_crown)
            self.scf_a_axial_brace_saddles.append(scf_a_axial_brace_saddle)
            self.scf_a_axial_brace_crowns.append(scf_a_axial_brace_crown)