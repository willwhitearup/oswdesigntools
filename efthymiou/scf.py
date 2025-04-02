""" Module containing Efthymiou joint SCF functions implemented using numpy
    
    See ./refs/Efthymiou_1988.pdf
    
    Ref:
        Development of SCF Formulae and Generalised Influence Functions for use in
        Fatigue Analysis, M/ Efthymiou, Shell Internationale Petroleum Maatachappij B.V.,
        OTH'88 Recent Developments in Tubular Joints Technology, 4-5 October 1988
"""
# imports -----------------------------------------------------------------------------------------
import numpy as np


# functions ---------------------------------------------------------------------------------------
def f1(d1, d2, thk1, length):
    """ Table 1 - parametric equations for SCF in T/Y-joints, short chord correction factor eqn F1

        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            length, numpy array of floats defining chord length "L"

        Returns:
            numpy array of short chord correction factors
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    alpha = 2 * length / d1

    # Evaluates to 1, unless alpha < 12 is true. alpha < 12 is used because 'if' doesn't handle element-wise operation.
    correction_factor = 1 - (alpha < 12) * (0.83 * beta - 0.56 * (beta ** 2) - 0.02) * (gamma ** 0.23) * \
                        np.exp(-0.21 * (gamma ** -1.16) * (alpha ** 2.5))

    return correction_factor


def f2(d1, d2, thk1, length):
    """ Table 1 - parametric equations for SCF in T/Y-joints, short chord correction factor eqn F2

        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            length, numpy array of floats defining chord length "L"

        Returns:
            numpy array of short chord correction factors
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    alpha = 2 * length / d1

    # Evaluates to 1, unless alpha < 12 is true. alpha < 12 is used because 'if' doesn't handle element-wise operation.
    correction_factor = 1 - (alpha < 12) * (1.43 * beta - 0.97 * (beta ** 2) - 0.03) * (gamma ** 0.04) * \
                        np.exp(-0.71 * (gamma ** -1.38) * (alpha ** 2.5))

    return correction_factor


def f3(d1, d2, thk1, length):
    """ Table 1 - parametric equations for SCF in T/Y-joints, short chord correction factor eqn F3

        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            length, numpy array of floats defining chord length "L"

        Returns:
            numpy array of short chord correction factors
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    alpha = 2 * length / d1

    # Evaluates to 1, unless alpha < 12 is true. alpha < 12 is used because 'if' doesn't handle element-wise operation.
    correction_factor = 1 - (alpha < 12) * 0.55 * (beta ** 1.8) * (gamma ** 0.16) * np.exp(-0.49 * (gamma ** -0.89)
                                                                                           * (alpha ** 1.8))

    return correction_factor


def f4(d1, d2, thk1, length):
    """ Table 3 - Table 3 - equations for SCF in gap / overlap K-joints,, short chord correction factor eqn F4

        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            length, numpy array of floats defining chord length "L"

        Returns:
            numpy array of short chord correction factors
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    alpha = 2 * length / d1

    # Evaluates to 1, unless alpha < 12 is true. alpha < 12 is used because 'if' doesn't handle element-wise operation.
    correction_factor = 1 - (alpha < 12) * 1.07 * (beta ** 1.88) * np.exp(-0.16 * (gamma ** -1.06) * (alpha ** 2.4))

    return correction_factor


def t1(d1, d2, thk1, thk2, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = gamma * (tau ** 1.1) * (1.11 - 3 * (beta - 0.52) ** 2) * np.sin(theta) ** 1.6

    return scf


def t2(d1, d2, thk1, thk2, length, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    alpha = 2 * length / d1

    scf = (gamma ** 0.2) * tau * (2.65 + 5 * (beta - 0.65) ** 2) + tau * \
          beta * (0.25 * alpha - 3) * np.sin(theta)

    return scf


def t3(d1, d2, thk1, thk2, length, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    alpha = 2 * length / d1

    scf = 1.3 + gamma * (tau ** 0.52) * (alpha ** 0.1) * (0.187 - 1.25 * (beta ** 1.1) * (beta - 0.96)) * \
          np.sin(theta) ** (2.7 - 0.01 * alpha)

    return scf


def t4(d1, d2, thk1, thk2, length):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    alpha = 2 * length / d1

    scf = 3 + (gamma ** 1.2) * (0.12 * np.exp(-4 * beta) + 0.011 * (beta ** 2) - 0.045) + \
          beta * tau * (0.1 * alpha - 1.2)

    return scf


def t5(d1, d2, thk1, thk2, length, theta, c):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T5
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    tau = thk2 / thk1
    alpha = 2 * length / d1
    c1 = 2 * (c - 0.5)

    # calculate t1 SCF
    scf = t1(d1, d2, thk1, thk2, theta)

    scf = scf + c1 * (0.8 * alpha - 6) * tau * (beta ** 2) * ((1 - (beta ** 2)) ** 0.5) * \
          np.sin(2 * theta) ** 2

    return scf


def t6(d1, d2, thk1, thk2, length, theta, c):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T6
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    alpha = 2 * length / d1
    c2 = c / 2

    scf = (gamma ** 0.2) * tau * (2.65 + 5 * (beta - 0.65) ** 2) + tau * beta * \
          (c2 * alpha - 3) * np.sin(theta)

    return scf


def t7(d1, d2, thk1, thk2, length, c):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T7
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    alpha = 2 * length / d1
    c3 = c / 5

    scf = 3 + (gamma ** 1.2) * (0.12 * np.exp(-4 * beta) + 0.011 * (beta ** 2) - 0.045) + \
          beta * tau * (c3 * alpha - 1.2)

    return scf


def t8(d1, d2, thk1, thk2, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T8
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = 1.45 * beta * (tau ** 0.85) * (gamma ** (1 - 0.68 * beta)) * (np.sin(theta) ** 0.7)

    return scf


def t9(d1, d2, thk1, thk2, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T9
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = 1 + 0.65 * beta * (tau ** 0.4) * (gamma ** (1.09 - 0.77 * beta)) * \
          (np.sin(theta) ** (0.06 * gamma - 1.16))

    return scf


def t10(d1, d2, thk1, thk2, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T10
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = gamma * tau * beta * (1.7 - 1.05 * (beta ** 3)) * (np.sin(theta) ** 1.6)

    return scf


def t11(d1, d2, thk1, thk2, theta):
    """ Table 1 - parametric equations for SCF in T/Y-joints, Eqn. T11
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    # calculate SCF of T10
    scf = t10(d1, d2, thk1, thk2, theta)

    scf = (tau ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta + 0.08 * (beta ** 4)) * scf

    return scf


def x1(d1, d2, thk1, thk2, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = 3.87 * gamma * tau * beta * (1.1 - (beta ** 1.8)) * (np.sin(theta) ** 1.7)

    return scf


def x2(d1, d2, thk1, thk2, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = (gamma ** 0.2) * tau * (2.65 + 5 * ((beta - 0.65) ** 2)) - 3 * tau * beta * np.sin(theta)

    return scf


def x3(d1, d2, thk1, thk2, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = 1 + 1.9 * gamma * (tau ** 0.5) * (beta ** 0.9) * (1.09 - (beta ** 1.7)) * \
          (np.sin(theta) ** 2.5)

    return scf


def x4(d1, d2, thk1):
    """ Table 2 - equations for SCF in X-joints, Eqn. X4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)

    scf = 3 + (gamma ** 1.2) * (0.12 * np.exp(-4 * beta) + 0.011 * (beta ** 2) - 0.045)

    return scf


def x5(d1, d2, thk1, thk2, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X5
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = gamma * tau * beta * (1.56 - 1.34 * (beta ** 4)) * (np.sin(theta) ** 1.6)

    return scf


def x6(d1, d2, thk1, thk2, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X6
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = x5(d1, d2, thk1, thk2, theta)
    scf = (tau ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta + 0.08 * (beta ** 4)) * scf

    return scf


def x7(d1, d2, thk1, thk2, length, theta, c):
    """ Table 2 - equations for SCF in X-joints, Eqn. X7
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1

    scf = t5(d1, d2, thk1, thk2, length, theta, c)
    scf = scf * (1 - 0.26 * (beta ** 3))

    return scf


def x8(d1, d2, thk1, thk2, length, theta):
    """ Table 2 - equations for SCF in X-joints, Eqn. X8
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
        
        Returns:
            numpy array of SCF values
    """
    # calculate parameters
    beta = d2 / d1

    # calculate scf for T3
    scf = t3(d1, d2, thk1, thk2, length, theta)

    scf = scf * (1 - 0.26 * (beta ** 3))

    return scf


def k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab,
       d2_c=None, thk2_c=None, theta_c=None, g_bc=None):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"

            If 3rd brace is present (KT balanced axial case), brace C args:
                d2_c, numpy array of floats defining brace diameter "dc"
                thk2_c, numpy array of floats defining brace thickness "tc"
                theta_c, numpy array of floats defining angle (in radians) "thetaC"
                g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
        
        Returns:
            numpy array of chord A SCF values,
            numpy array of chord B SCF values,
            numpy array of chord C SCF values (or np.nan if no brace C)
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    tau_a = thk2_a / thk1
    tau_b = thk2_b / thk1
    zeta_ab = g_ab / d1

    beta_max = np.maximum(beta_a, beta_b)
    beta_min = np.minimum(beta_a, beta_b)
    # We need max angle in range 0-90deg - angles >90deg need to be mirrored about 90deg, e.g. 110deg -> 70deg
    # This only matters for equations where maximum of 2 angles is required, because all other equations just use
    # the sin of the angles directly, and sin 70deg = sin 110deg anyway
    theta_a = np.minimum(theta_a, np.pi - theta_a)
    theta_b = np.minimum(theta_b, np.pi - theta_b)
    theta_max = np.maximum(theta_a, theta_b)
    theta_min = np.minimum(theta_a, theta_b)

    has_three_braces = True
    if d2_c is None or thk2_c is None or theta_c is None or g_bc is None:
        has_three_braces = False

    if has_three_braces:
        beta_c = d2_c / d1
        tau_c = thk2_c / thk1
        zeta_bc = g_bc / d1
        zeta_a = zeta_c = zeta_ab + zeta_bc + beta_b
        zeta_b = np.maximum(zeta_ab, zeta_bc)

        beta_max = np.maximum(beta_c, beta_max)
        beta_min = np.minimum(beta_c, beta_min)
        # See note above regarding max angle
        theta_c = np.minimum(theta_c, np.pi - theta_c)
        theta_max = np.maximum(theta_c, theta_max)
        theta_min = np.minimum(theta_c, theta_min)

        scf_c = (tau_c ** 0.9) * (gamma ** 0.5) * (0.67 - (beta_c ** 2) + 1.16 * beta_c) * \
                np.sin(theta_c) * ((np.sin(theta_max) / np.sin(theta_min)) ** 0.3) * \
                ((beta_max / beta_min) ** 0.3) * (1.64 + 0.29 * (beta_c ** -0.38) * np.arctan(8 * zeta_c))
    else:
        zeta_a = zeta_b = zeta_ab
        scf_c = np.nan

    # calculate SCF for A, B and C
    scf_a = (tau_a ** 0.9) * (gamma ** 0.5) * (0.67 - (beta_a ** 2) + 1.16 * beta_a) * \
            np.sin(theta_a) * ((np.sin(theta_max) / np.sin(theta_min)) ** 0.3) * \
            ((beta_max / beta_min) ** 0.3) * (1.64 + 0.29 * (beta_a ** -0.38) * np.arctan(8 * zeta_a))

    scf_b = (tau_b ** 0.9) * (gamma ** 0.5) * (0.67 - (beta_b ** 2) + 1.16 * beta_b) * \
            np.sin(theta_b) * ((np.sin(theta_max) / np.sin(theta_min)) ** 0.3) * \
            ((beta_max / beta_min) ** 0.3) * (1.64 + 0.29 * (beta_b ** -0.38) * np.arctan(8 * zeta_b))

    return scf_a, scf_b, scf_c


def k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab, brace_ab=None,
       d2_c=None, thk2_c=None, theta_c=None, g_bc=None, brace_bc=None):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K2

    !!! WW edited to allow only k joints with gaps !!!
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            brace_ab, number identifying which brace A or B is a through brace (1 = A, 2 = B)

            If 3rd brace is present (KT balanced axial case), brace C args:
                d2_c, numpy array of floats defining brace diameter "dc"
                thk2_c, numpy array of floats defining brace thickness "tc"
                theta_c, numpy array of floats defining angle (in radians) "thetaC"
                g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
                brace_bc, string identifying which brace B or C is a through brace (2 = B, 3 = C)
        
        Returns:
            numpy array of brace A SCF values,
            numpy array of brace B SCF values,
            numpy array of brace C SCF values (or np.nan if no brace C)
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    tau_a = thk2_a / thk1
    tau_b = thk2_b / thk1
    zeta_ab = g_ab / d1

    # We need max angle in range 0-90deg - angles >90deg need to be mirrored about 90deg, e.g. 110deg -> 70deg
    # This only matters for equations where maximum of 2 angles is required, because all other equations just use
    # the sin of the angles directly, and sin 70deg = sin 110deg anyway
    theta_a = np.minimum(theta_a, np.pi - theta_a)
    theta_b = np.minimum(theta_b, np.pi - theta_b)
    theta_max = np.maximum(theta_a, theta_b)
    theta_min = np.minimum(theta_a, theta_b)

    if brace_ab is not None:
        raise Exception("Calculations currently only assume there is a gap i.e. no overlaps...")
    else:
        c_a = (g_ab <= 0) * ((brace_ab == 1) * 1 + (brace_ab == 2) * 0.5)
        c_b = (g_ab <= 0) * ((brace_ab == 1) * 0.5 + (brace_ab == 2) * 1)

    # calculate scf for A and B using K1
    scf_a, scf_b, scf_c = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab,
                             d2_c, thk2_c, theta_c, g_bc)

    three_braces = True
    if d2_c is None or thk2_c is None or theta_c is None or g_bc is None:
        three_braces = False

    if three_braces:
        beta_c = d2_c / d1
        tau_c = thk2_c / thk1
        zeta_bc = g_bc / d1
        zeta_a = zeta_c = zeta_ab + zeta_bc + beta_b
        zeta_b = np.maximum(zeta_ab, zeta_bc)

        # See note above regarding max angle
        theta_c = np.minimum(theta_c, np.pi - theta_c)
        theta_max = np.maximum(theta_c, theta_max)
        theta_min = np.minimum(theta_c, theta_min)

        # Unclear whether c_b should be relative to brace a or c - therefore, worst of both (maximum) taken here
        c_b = np.maximum(c_b, (g_bc <= 0) * ((brace_bc == 2) * 1 + (brace_bc == 3) * 0.5))
        c_c = (g_bc <= 0) * ((brace_bc == 2) * 0.5 + (brace_bc == 3) * 1)

        scf_c = 1 + scf_c * (1.97 - 1.57 * (beta_c ** 0.25)) * (tau_c ** -0.14) * \
                (np.sin(theta_c) ** 0.7) + c_c * (beta_c ** 1.5) * (gamma ** 0.5) * (tau_c ** -1.22) * \
                (np.sin(theta_max + theta_min) ** 1.8) * (0.131 - 0.084 * np.arctan(14 * zeta_c + 4.2 * beta_c))
    else:
        zeta_a = zeta_b = zeta_ab
        scf_c = np.nan

    # calculate scf for A, B and C
    # WW edited!!!!
    scf_a = 1 + scf_a * (1.97 - 1.57 * (beta_a ** 0.25)) * (tau_a ** -0.14) * \
            (np.sin(theta_a) ** 0.7)# + c_a * (beta_a ** 1.5) * (gamma ** 0.5) * (tau_a ** -1.22) * \
            #(np.sin(theta_max + theta_min) ** 1.8) * (0.131 - 0.084 * np.arctan(14 * zeta_a + 4.2 * beta_a))

    scf_b = 1 + scf_b * (1.97 - 1.57 * (beta_b ** 0.25)) * (tau_b ** -0.14) * \
            (np.sin(theta_b) ** 0.7)# + c_b * (beta_b ** 1.5) * (gamma ** 0.5) * (tau_b ** -1.22) * \
            #(np.sin(theta_max + theta_min) ** 1.8) * (0.131 - 0.084 * np.arctan(14 * zeta_b + 4.2 * beta_b))

    return scf_a, scf_b, scf_c


def k3(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g_ab):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g_ab, numpy array of floats defining gap between two braces, "g"
        
        Returns:
            numpy array of brace A SCF values
            numpy array of brace B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1

    # calculate scf for A and B using t9
    scf_a = t9(d1, d2_a, thk1, thk2_a, theta_a)
    scf_b = t9(d1, d2_b, thk1, thk2_b, theta_b)

    # calculate scf for A and B
    scf_a = scf_a * (0.9 + 0.4 * beta_a)
    scf_b = scf_b * (0.9 + 0.4 * beta_b)

    # Turn invalid (non-overlap) values to np.nan to remove them
    scf_a = np.where(g_ab < 0, scf_a, np.nan)
    scf_b = np.where(g_ab < 0, scf_b, np.nan)

    return scf_a, scf_b


def k4(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns:
            numpy array of chord A SCF values
            numpy array of chord B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    zeta = g / d1
    beta_max = np.maximum(beta_a, beta_b)
    x_a = 1 + (zeta * np.sin(theta_a) / beta_a)
    x_b = 1 + (zeta * np.sin(theta_b) / beta_b)

    # calculate scf for A and B using T10
    t10a = t10(d1, d2_a, thk1, thk2_a, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, theta_b)

    # calculate scf for A and B
    scf_a = t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_a)) + \
            t10b * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_a)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_a))

    scf_b = t10b * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_b)) + \
            t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_b)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_b))

    return scf_a, scf_b




def k5(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K5
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns:
            numpy array of brace A SCF values
            numpy array of brace B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    tau_a = thk2_a / thk1
    tau_b = thk2_b / thk1

    # calculate SCF for A and B using T10
    scf_a, scf_b = k4(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g)

    # calculate SCF for A and B
    scf_a = (tau_a ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta_a + 0.08 * (beta_a ** 4)) * scf_a
    scf_b = (tau_b ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta_b + 0.08 * (beta_b ** 4)) * scf_b

    return scf_a, scf_b


def k6(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K6
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns:
            numpy array of chord A SCF values
            numpy array of chord B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    zeta = g / d1
    x_a = 1 + (zeta * np.sin(theta_a) / beta_a)
    x_b = 1 + (zeta * np.sin(theta_b) / beta_b)

    # calculate SCF for A and B using T10
    t10a = t10(d1, d2_a, thk1, thk2_a, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, theta_b)

    # calculate SCF for A and B
    scf_a = t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_a))
    scf_b = t10b * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_b))

    return scf_a, scf_b


def k7(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g):
    """ Table 3 - equations for SCF in gap / overlap K-joints, Eqn. K7
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining brace diameter "dA"
            d2_b, numpy array of floats defining brace diameter "dB"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining brace thickness "ta"
            thk2_b, numpy array of floats defining brace thickness "tb"
            theta_a, numpy array of floats defining angle (in radians) "thetaA"
            theta_b, numpy array of floats defining angle (in radians) "thetaB"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns:
            numpy array of brace A SCF values
            numpy array of brace B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    tau_a = thk2_a / thk1
    tau_b = thk2_b / thk1

    # calculate SCF for A and B using eqn 25
    scf_a, scf_b = k6(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, theta_a, theta_b, g)

    # calculate SCF for A and B
    scf_a = (tau_a ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta_a + 0.08 * (beta_a ** 4)) * scf_a
    scf_b = (tau_b ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta_b + 0.08 * (beta_b ** 4)) * scf_b

    return scf_a, scf_b


def kt1(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, theta_a, theta_b, theta_c, g_ab, g_bc):
    """ Table 4 - Equations for SCF in KT-joints, Eqn. KT1
        
        SCF FOR C NEEDS TO BE CHECKED!!!!
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining first brace diameter "dA"
            d2_b, numpy array of floats defining second (central) brace diameter "dB"
            d2_c, numpy array of floats defining third brace diameter "dC"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining first brace thickness "ta"
            thk2_b, numpy array of floats defining second (central) brace thickness "tb"
            thk2_c, numpy array of floats defining third brace thickness "tc"
            theta_a, numpy array of floats defining first brace angle (in radians) "thetaA"
            theta_b, numpy array of floats defining second (central) brace angle (in radians) "thetaB"
            theta_c, numpy array of floats defining third brace angle (in radians) "thetaC"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            
        Returns:
            numpy array of chord A SCF values
            numpy array of chord C SCF values,
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_a) / beta_a)
    x_ac = 1 + ((zeta_ab + zeta_bc + beta_b) * np.sin(theta_a) / beta_a)
    x_bc = 1 + (zeta_bc * np.sin(theta_c) / beta_c)
    x_ca = 1 + ((zeta_ab + zeta_bc + beta_b) * np.sin(theta_c) / beta_c)
    # np.maximum only takes 2 inputs, so using np.maximum.reduce (repeatedly applies function to a list of values)
    # note that np.max does not do element-wise maximum, but rather returns a single value for all data entered
    beta_max = np.maximum.reduce([beta_a, beta_b, beta_c])

    # calculate SCF for A, B and C using T10
    t10a = t10(d1, d2_a, thk1, thk2_a, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, theta_b)
    t10c = t10(d1, d2_c, thk1, thk2_c, theta_c)

    # calculate SCF for A and C
    scf_a = t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_ac)) + \
            t10b * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ab)) + \
            t10c * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ac)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ac))

    scf_c = t10c * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) * \
            (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ca)) + \
            t10b * (1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_bc)) + \
            t10a * (1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_ca)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ca))

    return scf_a, scf_c


def kt2(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, theta_a, theta_b, theta_c, g_ab, g_bc):
    """ Table 4 - Equations for SCF in KT-joints, Eqn. KT2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining first brace diameter "dA"
            d2_b, numpy array of floats defining second (central) brace diameter "dB"
            d2_c, numpy array of floats defining third brace diameter "dC"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining first brace thickness "ta"
            thk2_b, numpy array of floats defining second (central) brace thickness "tb"
            thk2_c, numpy array of floats defining third brace thickness "tc"
            theta_a, numpy array of floats defining first brace angle (in radians) "thetaA"
            theta_b, numpy array of floats defining second (central) brace angle (in radians) "thetaB"
            theta_c, numpy array of floats defining third brace angle (in radians) "thetaC"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            
        Returns:
            numpy array of chord B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_b) / beta_b)
    x_bc = 1 + (zeta_bc * np.sin(theta_b) / beta_b)
    # np.maximum only takes 2 inputs, so using np.maximum.reduce (repeatedly applies function to a list of values)
    # note that np.max does not do element-wise maximum, but rather returns a single value for all data entered
    beta_max = np.maximum.reduce([beta_a, beta_b, beta_c])

    # calculate SCF for A, B and C using T10
    t10a = t10(d1, d2_a, thk1, thk2_a, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, theta_b)
    t10c = t10(d1, d2_c, thk1, thk2_c, theta_c)

    # calculate SCF for B
    scf = t10b * ((1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) ** ((beta_a / beta_b) ** 2)) * \
          ((1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) ** ((beta_c / beta_b) ** 2)) + \
          t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
          (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ab)) + \
          t10c * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) * \
          (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_bc))

    return scf


def opb_brace(d1, d2, thk1, thk2, scf):
    """ Table 4 - Equations for SCF in KT-joints, new eqn: OPB Brace
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining brace diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining brace thickness "t"
            scf, numpy array of chord SCF values
            
        Returns:
            numpy array of brace SCF values
    """

    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1

    scf = (tau ** -0.54) * (gamma ** -0.05) * (0.99 - 0.47 * beta + 0.08 * (beta ** 4)) * scf

    return scf


def kt3(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_c, theta_a, theta_c, g_ab, g_bc):
    """ Table 4 - Equations for SCF in KT-joints, Eqn. KT3

        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining first brace diameter "dA"
            d2_b, numpy array of floats defining second (central) brace diameter "dB"
            d2_c, numpy array of floats defining third brace diameter "dC"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining first brace thickness "ta"
            thk2_c, numpy array of floats defining third brace thickness "tc"
            theta_a, numpy array of floats defining first brace angle (in radians) "thetaA"
            theta_c, numpy array of floats defining third brace angle (in radians) "thetaC"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            
        Returns:
            numpy array of chord A SCF values
            numpy array of chord C SCF values,
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_a) / beta_a)
    x_ac = 1 + ((zeta_ab + zeta_bc + beta_b) * np.sin(theta_a) / beta_a)
    x_bc = 1 + (zeta_bc * np.sin(theta_c) / beta_c)
    x_ca = 1 + ((zeta_ab + zeta_bc + beta_b) * np.sin(theta_c) / beta_c)

    # calculate SCF for A and C using T10
    t10a = t10(d1, d2_a, thk1, thk2_a, theta_a)
    t10c = t10(d1, d2_c, thk1, thk2_c, theta_c)

    # calculate SCF for A and C
    scf_a = t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_ac))

    scf_c = t10c * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) * \
            (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ca))

    return scf_a, scf_c


def kt4(d1, d2_a, d2_b, d2_c, thk1, thk2_b, theta_b, g_ab, g_bc):
    """ Table 4 - Equations for SCF in KT-joints, Eqn. KT4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining first brace diameter "dA"
            d2_b, numpy array of floats defining second (central) brace diameter "dB"
            d2_c, numpy array of floats defining third brace diameter "dC"
            thk1, numpy array of floats defining chord thickness "T"
            thk2_b, numpy array of floats defining second (central) brace thickness "tb"
            theta_b, numpy array of floats defining second (central) brace angle (in radians) "thetaB"
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            
        Returns:
            numpy array of chord B SCF values
    """
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_b) / beta_b)
    x_bc = 1 + (zeta_bc * np.sin(theta_b) / beta_b)

    # calculate SCF for A, B and C using T10
    t10b = t10(d1, d2_b, thk1, thk2_b, theta_b)

    # calculate SCF for B
    scf = t10b * ((1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) ** ((beta_a / beta_b) ** 2)) * \
          ((1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) ** ((beta_c / beta_b) ** 2))

    return scf
