


class Tower:

    def __init__(self, rna_cog, interface_elev, moment_interface_del, shear_interface_del):

        self.rna_cog = rna_cog
        self.interface_elev = interface_elev
        self.moment_interface_del = moment_interface_del
        self.shear_interface_del = shear_interface_del

        self.c_o_a_LAT = None
        self._calculate_coa()

    def _calculate_coa(self):
        # centre of action calculation
        # print(f"WTG interface DELs have been provided. Centre of action can be calculated..!")
        c_o_a_interface = self.moment_interface_del / self.shear_interface_del
        self.c_o_a_LAT = c_o_a_interface + self.interface_elev