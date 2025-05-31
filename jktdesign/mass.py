from jktdesign.jacket import Jacket


class JointMassCalculator:

    rho = 7.85e-9  # steel density in tonnes/mm³

    def __init__(self, jacket: Jacket):
        self.jacket = jacket

    def compute_joint_masses(self):
        for joint in self.jacket.joints:
            joint.mass = self.estimate_mass(joint)

    def estimate_mass(self, joint):
        # Placeholder logic — in mm³
        estimated_volume = self.estimate_joint_volume(joint)
        return estimated_volume * self.rho  # tonnes

    def estimate_joint_volume(self, joint):
        # Placeholder: 100,000 mm³ = 0.0001 m³ ~ a small node
        # Later you can improve this based on joint type, connected members, etc.
        return 100_000