
import math

class Bolt:

    gamma_m2 = 1.25
    gamma_m3 = 1.25
    gamma_m3_ser = 1.1
    gamma_m7 = 1.1
    k2 = 0.9
    ks = 1
    slip_planes = 1
    slip_factor = 0.2

    def __init__(self, name, diameter, pitch, hole_diameter, washer_diameter, nut_height, bolt_material_grade):

        self.name: str = name
        self.diameter: float = diameter
        self.pitch: float = pitch
        self.hole_diameter: float = hole_diameter
        self.washer_diameter: float = washer_diameter
        self.nut_height: float = nut_height
        self.bolt_material_grade: BoltMaterial = bolt_material_grade

        # computed vars
        self.F_tR = None

    @property
    def tensile_diameter(self):
        # ISO approximation
        return self.diameter - 0.9382 * self.pitch

    @property
    def tensile_area(self):
        return math.pi * 0.25 * self.tensile_diameter ** 2

    @property
    def design_tensile_resistance(self):
        return self.bolt_material_grade.fub * self.k2 * self.tensile_area / self.gamma_m2

    @property
    def nominal_preload(self):
        return 0.7 * self.bolt_material_grade.fub * self.tensile_area  # see DNV-ST-0126 4.9.3

    @property
    def design_preload(self):
        return self.nominal_preload / self.gamma_m7

    def calculate_yielding_bolt_force(self):
        self.F_tR = 0.9 * self.tensile_area * self.bolt_material_grade.fub / 1.25  # IEC 61400 G.6



# bolt sizes----------------------------------------------------------
class BoltLibrary:

    _bolts = {
        "M72": {
            "diameter": 72,
            "pitch": 6,
            "hole_diameter": 78,
            "washer_diameter": 125,
            "nut_height": 65,
        },
        "M80": {
            "diameter": 80,
            "pitch": 6,
            "hole_diameter": 86,
            "washer_diameter": 140,
            "nut_height": 72,
        },
        "M90": {
            "diameter": 90,
            "pitch": 6,
            "hole_diameter": 96,
            "washer_diameter": 157,
            "nut_height": 81,
        }

    }

    @classmethod
    def create(cls, name, bolt_material_grade):
        data = cls._bolts[name]
        return Bolt(name=name, bolt_material_grade=bolt_material_grade, **data
                    )

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
    grade_10_9 = BoltMaterialLibrary.create("10.9")
    m72_bolt = BoltLibrary.create("M72", grade_10_9)



    a=1