import numpy as np
from typing import Literal


def calc_scf_thickness_transition(
    diameter_thick_member: float,
    diameter_thin_member: float,
    thickness_thick_member: float,
    thickness_thin_member: float,
    weld_width: float,
    delta_m: float,
    delta_0: float,
    taper_ratio: float, # e.g. 4 is in 1 in 4
    weld_type: Literal["single", "double"],  # single or double sided weld
    transition: Literal["inside", "outside"],  # transition on inner or outer side of plate
):
    """SCFs for equal plate thickness and at thickness transitions according to DNV-RP-C203 Section 3.3.7.

    Args:
        diameter_thick_member (float): outer diameter of thick member at weld location [m]
        diameter_thin_member (float): outer diameter of thin member at weld location [m]
        thickness_thick_member (float): thickness of thick member at weld location [m]
        thickness_thin_member (float): thickness of thin member at weld location [m]
        weld_width (float): weld width [m]
        delta_m (float): maximum misalignment of the members [m]
        builtin_misal_inner (float): built in misalignment of the members, inner side [m]
        builtin_misal_outer (float): built in misalignment of the members, outer side [m]
        weld_type (str, optional): specification of "single" or "double" sided weld. Defaults to "double".

    Returns:
        SCFMember: SCF outer side, SCF inner side
    """

    # calculate centre line diameters
    centre_diameter_thick_member = diameter_thick_member - thickness_thick_member
    centre_diameter_thin_member = diameter_thin_member - thickness_thin_member

    # Transition thickness delta t
    dt = np.abs(0.5 * (centre_diameter_thick_member - centre_diameter_thin_member))
    if weld_type == "single_sided":
        delta_0 = 0.
        print("delta_0 set to 0 as single sided weld")  # todo check this

    # determine whether weld width is either 1) the weld width or 2) the length of the tapered region
    thickness_transition = thickness_thick_member - thickness_thin_member
    length = taper_ratio * (thickness_transition) if taper_ratio is not None and thickness_transition != 0 else weld_width
    # print(f"length {length}, taper ratio {taper_ratio}")

    t_scf1 = dt + delta_m - delta_0
    t_scf2 = dt - delta_m + delta_0

    # calculate constants
    beta = (1.5 - 1 / np.log10(diameter_thin_member / thickness_thin_member) + 3 / (np.log10(diameter_thin_member / thickness_thin_member)) ** 2)
    alpha = (1.82 * length / np.sqrt(diameter_thin_member * thickness_thin_member) / (1 + (thickness_thick_member / thickness_thin_member) ** beta))

    # Eq 3.10
    scf1_c = (6 * t_scf1 / thickness_thin_member / (1 + (thickness_thick_member / thickness_thin_member) ** beta))
    # Eq 3.11
    scf2_c = (6 * t_scf2 / thickness_thin_member / (1 + (thickness_thick_member / thickness_thin_member) ** beta))

    if transition is None:
        scf_inside = 1 + scf1_c * np.exp(-alpha) # Eq 3.10
        scf_outside = 1 + scf1_c * np.exp(-alpha) # Eq 3.10
    elif transition == "inside":
        scf_inside = 1 + scf1_c * np.exp(-alpha) # Eq 3.10
        scf_outside = 1 - scf2_c * np.exp(-alpha) # Eq 3.11
    elif transition == "outside":
        scf_inside = 1 - scf2_c * np.exp(-alpha)  # Eq 3.11
        scf_outside = 1 + scf1_c * np.exp(-alpha)  # Eq 3.10

    # SCF for butt welds between members with equal thickness, 3.3.7.2 in DNV RP C203 2025
    if np.isclose(thickness_transition, 0.):
        print("SCF calculated for butt welds between members with equal thickness, 3.3.7.2 in DNV RP C203 2025. Taper ratio is ignored.")
        alpha = 0.91 * weld_width / np.sqrt(diameter_thin_member * thickness_thin_member)
        if weld_type == "single_sided":
            # weld root (inside for single sided) SCF can be put to 1.0 as per text in C203 above fig 3-8
            scf_inside = 1 #  - 3 * (delta_m - delta_0) * np.exp(-alpha) / thickness_thin_member
            scf_outside = 1 + 3 * (delta_m - delta_0) * np.exp(-alpha) / thickness_thin_member
        elif weld_type == "double_sided":
            scf_inside = 1 + 3 * (delta_m - delta_0) * np.exp(-alpha) / thickness_thin_member
            scf_outside = 1 + 3 * (delta_m - delta_0) * np.exp(-alpha) / thickness_thin_member



    return scf_inside, scf_outside
