import numpy as np
import math
from typing import Literal


def calc_scf_thickness_transition(
    diameter_thick_member: float,
    diameter_thin_member: float,
    thickness_thick_member: float,
    thickness_thin_member: float,
    weld_width_inner: float,
    weld_width_outer: float,
    max_misal: float,
    builtin_misal_inner: float,
    builtin_misal_outer: float,
    weld_type: Literal["single", "double"],  # single or double sided weld
    transition: Literal["inside", "outside"],  # transition on inner or outer side of plate
):
    """SCFs for equal plate thickness and at thickness transitions according to DNV-RP-C203 Section 3.3.7.

    Args:
        diameter_thick_member (float): outer diameter of thick member at weld location [m]
        diameter_thin_member (float): outer diameter of thin member at weld location [m]
        thickness_thick_member (float): thickness of thick member at weld location [m]
        thickness_thin_member (float): thickness of thin member at weld location [m]
        weld_width_inner (float): weld width, inner [m]
        weld_width_outer (float): weld width, outer [m]
        max_misal (float): maximum misalignment of the members [m]
        builtin_misal_inner (float): built in misalignment of the members, inner side [m]
        builtin_misal_outer (float): built in misalignment of the members, outer side [m]
        weld_type (str, optional): specification of "single" or "double" sided weld. Defaults to "double".

    Returns:
        SCFMember: SCF outer side, SCF inner side
    """

    # Define centre diameter
    centre_diameter_thick_member = (diameter_thick_member - thickness_thick_member)
    centre_diameter_thin_member = diameter_thin_member - thickness_thin_member

    # Define inner diameter
    # inner_diameter_thick_member = (diameter_thick_member - 2 * thickness_thick_member)
    # inner_diameter_thin_member = (diameter_thin_member - 2 * thickness_thin_member)

    # Transition thickness delta t
    dt = np.abs(0.5 * ((centre_diameter_thick_member) - (centre_diameter_thin_member)))

    if weld_type == "single":
        builtin_misal_inner = 0

    length_inner, length_outer = 999, 999 ### todo weld length L

    if transition == "inside" or transition is None:
        t_scf1 = dt + max_misal - builtin_misal_inner
        t_scf2 = dt - max_misal + builtin_misal_outer
    elif transition == "outside":
        t_scf1 = dt + max_misal - builtin_misal_outer
        t_scf2 = dt - max_misal + builtin_misal_inner

    # calculate constants
    beta = (1.5 - 1 / np.log10(diameter_thin_member / thickness_thin_member) + 3 / (np.log10(diameter_thin_member / thickness_thin_member)) ** 2)
    alpha_inner = (1.82 * length_inner / np.sqrt(diameter_thin_member * thickness_thin_member) / (1 + (thickness_thick_member / thickness_thin_member) ** beta))
    alpha_outer = (1.82 * length_outer / np.sqrt(diameter_thin_member * thickness_thin_member) / (1 + (thickness_thick_member / thickness_thin_member) ** beta))

    # Eq 3.3.5
    scf1_c = (6 * t_scf1 / thickness_thin_member / (1 + (thickness_thick_member / thickness_thin_member) ** beta))
    # Eq 3.3.6
    scf2_c = (6 * t_scf2 / thickness_thin_member / (1 + (thickness_thick_member / thickness_thin_member) ** beta))

    if transition is None:
        SCF_inside = 1 + scf1_c * np.exp(-alpha_inner)
        SCF_outside = 1 + scf1_c * np.exp(-alpha_inner)
    elif transition == "inside":
        SCF_inside = 1 + scf1_c * np.exp(-alpha_inner)
        SCF_outside = 1 - scf2_c * np.exp(-alpha_outer)
    else:
        SCF_inside = 1 - scf2_c * np.exp(-alpha_inner)
        SCF_outside = 1 + scf1_c * np.exp(-alpha_outer)

    return SCF_inside, SCF_outside