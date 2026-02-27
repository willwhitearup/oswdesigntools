

class SteelMaterial:

    youngs_modulus = 210000  # MPa
    poissons_ratio = 0.3

    gamma_m = 1.1

    # Yield strengths (Pa) by grade and thickness ranges (max thickness inclusive)
    _yield_table = {
        "355": [(16, 355), (40, 345), (float("inf"), 325)],
        "420": [(16, 420), (40, 410), (float("inf"), 400)],
        "460": [(16, 460), (40, 450), (float("inf"), 440)]
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
                f"yield_strength={self.yield_strength} MPa, "
                f"design_yield_strength={self.design_yield_strength:.1f} MPa, "
                f"E={self.youngs_modulus} MPa, ν={self.poissons_ratio}>")


# bolt materials------------------------------------------------------------------------------------
class BoltMaterial:

    def __init__(self, name, fyb, fub):

        self.name = name
        self.fyb = fyb
        self.fub = fub


class BoltMaterialLibrary:

    _materials = {
        "4.6":  {"fyb": 240, "fub": 400},
        "4.8":  {"fyb": 320, "fub": 400},
        "5.6":  {"fyb": 300, "fub": 500},
        "5.8":  {"fyb": 400, "fub": 500},
        "6.8":  {"fyb": 480, "fub": 600},
        "8.8":  {"fyb": 640, "fub": 800},
        "10.9": {"fyb": 900, "fub": 1000},
    }

    @classmethod
    def create(cls, grade_name):
        data = cls._materials.get(grade_name)

        if not data:
            raise ValueError(f"Bolt material grade '{grade_name}' not found.")

        return BoltMaterial(
            name=grade_name,
            fyb=data["fyb"],
            fub=data["fub"]
        )

if __name__ == "__main__":
    steel_plate = SteelMaterial("355", 30)

    a=1

    e=3