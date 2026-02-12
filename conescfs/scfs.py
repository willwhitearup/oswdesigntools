from typing import Literal
import numpy as np
import math

def calc_cone_scfs_sect3(radius_tubular: float, thickness_tubular: float, thickness_cone: float, alpha: float,
                        junction_type: Literal["small", "large"]):
    """Calculate SCF for tube and cone.

    Parameters:
        radius_tubular (float): Tube radius
        thickness_tubular (float): Tube thickness
        thickness_cone (float): Cone thickness
        alpha (float): Cone angle in radians

    Returns:
        scf_tube (float), scf_cone (float)
    """
    alpha = np.radians(abs(alpha))
    tube_OD = radius_tubular * 2
    numerator = 0.6 * thickness_tubular * math.sqrt(tube_OD * (thickness_tubular + thickness_cone)) * math.tan(alpha)
    scf_tube_1 = 1 + numerator / (thickness_tubular ** 2)
    scf_cone_1 = 1 + numerator / (thickness_cone ** 2)

    scf_tube_2 = 1 - numerator / (thickness_tubular ** 2)
    scf_cone_2 = 1 - numerator / (thickness_cone ** 2)

    # calculate inside and outside SCFs at the small and large diameter cone junctions
    if junction_type == "small":
        scf_tube_in, scf_cone_in = scf_tube_2, scf_cone_2
        scf_tube_out, scf_cone_out = scf_tube_1, scf_cone_1

    elif junction_type == "large":
        scf_tube_in, scf_cone_in = scf_tube_1, scf_cone_1
        scf_tube_out, scf_cone_out = scf_tube_2, scf_cone_2

    # scfs inside and outside (cone- and tube- side)
    return scf_tube_in, scf_cone_in, scf_tube_out, scf_cone_out

### app F DNV eqns to do
def calc_cone_scfs_appf17(radius_tubular: float,  thickness_tubular: float, thickness_cone: float, alpha: float,
                      junction_type: Literal["small", "large"],
                      poisson_ratio: float = 0.3, elastic_modulus: float = 210000000000):
    """Conical SCFs see 2025 DNV-RP-C203 Section Appendix F.17 (see commentary from 3.3.9)

    Args:
        radius_tubular (float): outer radius of tubular [m]
        thickness_tubular (float): thickness of tubular [m]
        thickness_cone (float): thickness of conical [m]
        alpha (float): angle of cone [radians]
        junction_type (str): type of junction ("small" or "large")
        poisson_ratio (float, optional): Poisson's ratio, defaults 0.3
        elastic_modulus (float, optional): Young's modulus, defaults 2.1E11 Pa

    Returns: SCF cone (outer, inner) and SCF tubular (outer, inner)
    """

    alpha = np.radians(abs(alpha))

    r = radius_tubular - thickness_tubular / 2  # centreline radius of tubular

    l_et = (r * thickness_tubular) ** 0.5 / (3 * (1 - poisson_ratio**2)) ** 0.25
    l_ec = (r * thickness_cone) ** 0.5 / (3 * (1 - poisson_ratio**2)) ** 0.25

    k_st = (elastic_modulus * thickness_tubular**3) / (12 * (1 - poisson_ratio**2))
    k_sc = (elastic_modulus * thickness_cone**3) / (12 * (1 - poisson_ratio**2))

    k = (l_et * k_sc) / (l_ec * k_st)

    phi = ((np.sin(alpha) * np.tan(alpha) + np.cos(alpha)) * k * l_et - l_ec) / ((2 * k + 2) * l_ec)

    lambda_ = (0.5 * np.tan(alpha)) + ((poisson_ratio * r * k_st) / (elastic_modulus * l_et**3)) * ((1 / thickness_tubular) - (1 / thickness_cone))

    epsilon = (((l_ec * np.cos(alpha)) / (2 * k * l_et)) + ((l_et * (np.sin(alpha) * np.tan(alpha) + np.cos(alpha)))
            / (2 * l_ec))
        - ((poisson_ratio * r * k_st)
            / (elastic_modulus * thickness_cone * l_et**2 * l_ec)
        ) * np.sin(alpha))

    nu = 0.5 - ((l_ec * np.cos(alpha)) / (2 * k * l_et))

    eta = (phi * lambda_ * (2 * k + 2) - k * epsilon * np.tan(alpha)) / ((2 * k + 2) * (nu * phi - epsilon))

    scf_tube_1 = 1 + ((6 * eta * l_et) / thickness_tubular)
    scf_tube_2 = 1 - ((6 * eta * l_et) / thickness_tubular)

    scf_cone_1 = (((nu * eta - lambda_) / epsilon) * (l_et / l_ec) * np.tan(alpha)
                  + (1 / np.cos(alpha)) * (thickness_tubular / thickness_cone)
                  + ((6 * eta * l_et) / thickness_cone) * (thickness_tubular / thickness_cone))

    scf_cone_2 = (((nu * eta - lambda_) / epsilon) * (l_et / l_ec) * np.tan(alpha)
                  + (1 / np.cos(alpha)) * (thickness_tubular / thickness_cone)
                  - ((6 * eta * l_et) / thickness_cone) * (thickness_tubular / thickness_cone))

    # calculate inside and outside SCFs at the small and large diameter cone junctions
    if junction_type == "small":
        scf_tube_in, scf_cone_in = scf_tube_2, scf_cone_2
        scf_tube_out, scf_cone_out = scf_tube_1, scf_cone_1

    elif junction_type == "large":
        scf_tube_in, scf_cone_in = scf_tube_1, scf_cone_1
        scf_tube_out, scf_cone_out = scf_tube_2, scf_cone_2

    return scf_tube_in, scf_cone_in, scf_tube_out, scf_cone_out