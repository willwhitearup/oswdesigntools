import numpy as np

######## CHATGPT ~~~~~~~~~~~~
def compute_brace_mass_with_saddle_cut(P1_brace, P2_brace, D_b, t_b, P1_chord, P2_chord, D_c, rho=7850):
    """
    Calculate mass of a brace after saddle cut from intersecting chord.

    Parameters:
        P1_brace, P2_brace: Endpoints of brace (3D points)
        D_b: Outer diameter of brace (m)
        t_b: Thickness of brace (m)
        P1_chord, P2_chord: Endpoints of chord (3D points)
        D_c: Outer diameter of chord (m)
        rho: Material density (default 7850 kg/m³ for steel)

    Returns:
        mass: Mass of the trimmed brace (kg)
        L_remaining: Remaining length of the brace (m)
    """

    def unit_vector(v):
        return v / np.linalg.norm(v)

    # Convert to NumPy arrays
    P1_b, P2_b = np.array(P1_brace), np.array(P2_brace)
    P1_c, P2_c = np.array(P1_chord), np.array(P2_chord)

    # Vectors
    vec_brace = P2_b - P1_b
    vec_chord = P2_c - P1_c
    L_brace_total = np.linalg.norm(vec_brace)

    # Unit vectors
    u_brace = unit_vector(vec_brace)
    u_chord = unit_vector(vec_chord)

    # Angle between brace and chord
    cos_theta = np.clip(np.dot(u_brace, u_chord), -1.0, 1.0)
    theta = np.arccos(cos_theta)  # in radians

    # Determine which end of brace is closer to chord axis
    def point_to_line_distance(P, A, B):
        AP = P - A
        AB = B - A
        t = np.dot(AP, AB) / np.dot(AB, AB)
        closest = A + t * AB
        return np.linalg.norm(P - closest)

    d1 = point_to_line_distance(P1_b, P1_c, P2_c)
    d2 = point_to_line_distance(P2_b, P1_c, P2_c)

    # Effective penetration length of chord into brace (approximate saddle length)
    # Based on chord radius projected along brace axis
    R_c = D_c / 2
    R_b = D_b / 2
    R_b_in = R_b - t_b
    A_cross = np.pi * (R_b ** 2 - R_b_in ** 2)  # cross-sectional area of brace wall

    if np.sin(theta) < 1e-6:
        # Nearly parallel -> no meaningful intersection (edge case)
        L_cut = 0
    else:
        L_cut = R_c / np.sin(theta)  # length to trim from brace

    L_remaining = max(L_brace_total - L_cut, 0)
    V_remaining = A_cross * L_remaining  # volume of truncated brace
    mass = V_remaining * rho

    return mass, L_remaining





######## CLAUDE ~~~~~~~~~~~~


class TubularJointCalculator:
    def __init__(self, P1_brace, P2_brace, D_b, t_b,
                 P1_chord, P2_chord, D_c,
                 rho=7850):
        """
        Initialize the tubular joint calculator.

        Parameters:
        - P1_brace, P2_brace: 3D points defining brace centerline (numpy arrays)
        - D_b: Brace outer diameter (mm)
        - t_b: Brace wall thickness (mm)
        - P1_chord, P2_chord: 3D points defining chord centerline (numpy arrays)
        - D_c: Chord outer diameter (mm)
        - rho: Steel density (kg/m³)
        """
        self.brace_p1 = np.array(P1_brace)
        self.brace_p2 = np.array(P2_brace)
        self.brace_od = D_b
        self.brace_thickness = t_b
        self.chord_p1 = np.array(P1_chord)
        self.chord_p2 = np.array(P2_chord)
        self.chord_od = D_c
        self.steel_density = rho

        # Calculate centerline vectors
        self.chord_vector = self.chord_p2 - self.chord_p1
        self.brace_vector = self.brace_p2 - self.brace_p1

        # Normalize vectors
        self.chord_unit = self.chord_vector / np.linalg.norm(self.chord_vector)
        self.brace_unit = self.brace_vector / np.linalg.norm(self.brace_vector)

    def find_intersection_point(self):
        """Find the intersection point of chord and brace centerlines."""
        # Solve for intersection using parametric line equations
        # Chord: P1 + t1 * (P2 - P1)
        # Brace: P3 + t2 * (P4 - P3)

        # Set up system of equations for closest approach
        A = np.array([self.chord_vector, -self.brace_vector]).T
        b = self.brace_p1 - self.chord_p1

        try:
            params = np.linalg.lstsq(A, b, rcond=None)[0]
            t1, t2 = params

            # Calculate intersection points on each line
            chord_point = self.chord_p1 + t1 * self.chord_vector
            brace_point = self.brace_p1 + t2 * self.brace_vector

            # Use midpoint as intersection
            intersection = (chord_point + brace_point) / 2
            return intersection, t2
        except:
            # If lines are parallel or other issues, use perpendicular projection
            return self.chord_p1, 0

    def calculate_saddle_cut_length(self, intersection_point, t_intersection):
        """
        Calculate the length of brace that needs to be cut due to saddle intersection.
        This uses the exact geometry of cylinder-cylinder intersection.
        """
        # Distance from brace centerline to intersection point
        brace_point_at_intersection = self.brace_p1 + t_intersection * self.brace_vector

        # Calculate the angle between chord and brace
        cos_angle = np.dot(self.chord_unit, self.brace_unit)
        angle = np.arccos(np.clip(abs(cos_angle), 0, 1))

        # For cylinder-cylinder intersection, the cut length depends on:
        # 1. Angle between cylinders
        # 2. Ratio of diameters
        # 3. Wall thickness

        # Simplified formula for saddle cut length (conservative estimate)
        # This accounts for the elliptical nature of the intersection
        R_chord = self.chord_od / 2
        R_brace = self.brace_od / 2

        # Effective cut length considering the saddle shape
        if angle > np.pi / 2:
            angle = np.pi - angle

        # Calculate the penetration depth
        penetration_factor = min(1.0, R_brace / R_chord)

        # Saddle cut length formula (empirical, widely used in offshore industry)
        cut_length = (R_chord / np.sin(angle)) * (1 + penetration_factor) * 1.1  # 10% safety factor

        return cut_length

    def calculate_brace_mass(self):
        """
        Calculate the mass of the brace accounting for saddle cut.
        """
        # Find intersection point
        intersection_point, t_intersection = self.find_intersection_point()

        # Calculate total brace length
        total_brace_length = np.linalg.norm(self.brace_vector)

        # Calculate saddle cut length
        cut_length = self.calculate_saddle_cut_length(intersection_point, t_intersection)

        # Effective brace length (excluding the part inside the chord)
        effective_length = total_brace_length - cut_length
        effective_length = max(0, effective_length)  # Ensure non-negative

        # Calculate cross-sectional area of brace (hollow cylinder)
        outer_radius = self.brace_od / 2
        inner_radius = outer_radius - self.brace_thickness
        cross_sectional_area = np.pi * (outer_radius ** 2 - inner_radius ** 2)  # mm²

        # Convert to m² for mass calculation
        cross_sectional_area_m2 = cross_sectional_area / 1e6
        effective_length_m = effective_length / 1000  # Convert mm to m

        # Calculate volume and mass
        volume = cross_sectional_area_m2 * effective_length_m  # m³
        mass = volume * self.steel_density  # kg

        return {
            'total_brace_length': total_brace_length,
            'cut_length': cut_length,
            'effective_length': effective_length,
            'cross_sectional_area': cross_sectional_area,
            'volume': volume,
            'mass': mass,
            'intersection_point': intersection_point,
            'angle_degrees': np.degrees(np.arccos(np.clip(abs(np.dot(self.chord_unit, self.brace_unit)), 0, 1)))
        }


# Example usage
if __name__ == "__main__":
    # Example coordinates (in mm)
    P1_brace = [2000, 0, 1000]  # Brace starting above chord
    P2_brace = [2000, 0, -1000]  # Brace ending below chord
    D_b = 508  # 20" brace outer diameter
    t_b = 25  # 25mm wall thickness
    P1_chord = [0, 0, 0]
    P2_chord = [5000, 0, 0]  # 5m chord
    D_c = 914  # 36" chord outer diameter

    # Create calculator instance
    calc = TubularJointCalculator(
        P1_brace, P2_brace, D_b, t_b,
        P1_chord, P2_chord, D_c
    )

    # Calculate mass
    results = calc.calculate_brace_mass()

    # Display results
    print("Tubular Joint Brace Mass Calculation Results:")
    print("=" * 50)
    print(f"Total brace length: {results['total_brace_length']:.1f} mm")
    print(f"Saddle cut length: {results['cut_length']:.1f} mm")
    print(f"Effective brace length: {results['effective_length']:.1f} mm")
    print(f"Cross-sectional area: {results['cross_sectional_area']:.1f} mm²")
    print(f"Brace volume: {results['volume']:.6f} m³")
    print(f"Brace mass: {results['mass']:.2f} kg")
    print(f"Intersection angle: {results['angle_degrees']:.1f}°")
    print(f"Intersection point: [{results['intersection_point'][0]:.1f}, "
          f"{results['intersection_point'][1]:.1f}, {results['intersection_point'][2]:.1f}] mm")

    # Additional validation
    print("\nValidation:")
    print(f"Chord OD: {D_c} mm")
    print(f"Brace OD: {D_b} mm")
    print(f"Brace thickness: {t_b} mm")
    print(f"Steel density: {calc.steel_density} kg/m³")

    # Mass per unit length check
    unit_mass = (results['mass'] / (results['effective_length'] / 1000))
    print(f"Mass per meter: {unit_mass:.2f} kg/m")


# Example usage
if __name__ == "__main__":
    # Test with your exact inputs
    P1_brace = [2.0, 0, 1.0]
    P2_brace = [2.0, 0, -1.0]
    D_b = 0.508  # 20" = 0.508m
    t_b = 0.025  # 25mm = 0.025m
    P1_chord = [0, 0, 0]
    P2_chord = [5.0, 0, 0]
    D_c = 0.914  # 36" = 0.914m

    # Create calculator instance
    calc = TubularJointCalculator(
        P1_brace, P2_brace, D_b, t_b,
        P1_chord, P2_chord, D_c
    )

    # Calculate mass
    results = calc.calculate_brace_mass()

    # Display results
    print("Tubular Joint Brace Mass Calculation Results:")
    print("=" * 50)
    print(f"Total brace length: {results['total_brace_length']:.1f} mm")
    print(f"Saddle cut length: {results['cut_length']:.1f} mm")
    print(f"Effective brace length: {results['effective_length']:.1f} mm")
    print(f"Cross-sectional area: {results['cross_sectional_area']:.1f} mm²")
    print(f"Brace volume: {results['volume']:.6f} m³")
    print(f"Brace mass: {results['mass']:.2f} kg")
    print(f"Intersection angle: {results['angle_degrees']:.1f}°")
    print(f"Intersection point: [{results['intersection_point'][0]:.1f}, "
          f"{results['intersection_point'][1]:.1f}, {results['intersection_point'][2]:.1f}] mm")

    # Additional validation
    print("\nValidation:")
    print(f"Chord OD: {D_c} mm")
    print(f"Brace OD: {D_b} mm")
    print(f"Brace thickness: {t_b} mm")
    print(f"Steel density: {calc.steel_density} kg/m³")

    # Mass per unit length check
    unit_mass = (results['mass'] / (results['effective_length'] / 1000))
    print(f"Mass per meter: {unit_mass:.2f} kg/m")


    mass, L_remaining = compute_brace_mass_with_saddle_cut(
        P1_brace,
        P2_brace,
        D_b,
        t_b,
        P1_chord,
        P2_chord,
        D_c
    )

    print("******* CHAT GPT *******************")
    print(f"Brace Mass (kg): {mass:.2f}")
    print(f"Remaining Length (m): {L_remaining:.3f}")