

class SteelMaterial:

    youngs_modulus = 210e9  # Pa
    poissons_ratio = 0.3

    gamma_m = 1.1

    # Yield strengths (Pa) by grade and thickness ranges (max thickness inclusive)
    _yield_table = {
        "355": [(16, 355e6), (40, 345e6), (float("inf"), 335e6)],
        "425": [(16, 425e6), (40, 415e6), (float("inf"), 400e6)]
    }

    def __init__(self, grade: str, thickness: float):
        if grade not in self._yield_table:
            raise ValueError(f"Unknown steel grade: {grade}")
        self.grade = grade
        self._thickness = thickness  # mm

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value: float):
        self._thickness = value  # update thickness

    @property
    def yield_strength(self) -> float:
        """Return yield strength in Pa based on grade and thickness."""
        t = self._thickness
        for max_thick, yld in self._yield_table[self.grade]:
            if t <= max_thick:
                return yld

    @property
    def design_yield_strength(self):
        return self.yield_strength / self.gamma_m

    def __repr__(self):
        return (f"<SteelMaterial grade={self.grade}, thickness={self.thickness} mm, "
                f"yield_strength={self.yield_strength} Pa, "
                f"design_yield_strength={self.design_yield_strength:.1f} Pa, "
                f"E={self.youngs_modulus} Pa, ν={self.poissons_ratio}>")


if __name__ == "__main__":
    steel_plate = SteelMaterial("355", 30)

    a=1

    e=3