""" implementation of stress root reduction factors
    
    Table F-6 from DNV-RP-C203, January 2020
    
"""
# imports -----------------------------------------------------------------------------------------
import numpy as np


# functions ---------------------------------------------------------------------------------------
def kaxial(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-3, K-Joint Axial Load
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    zeta = g / d1
    
    # calculate rf
    rf = 2.6 * (0.203 + 1.66 * beta - 1.3 * (beta ** 2)) * \
        (0.47 + 0.024 * gamma - 0.00054 * (gamma ** 2)) * \
        (((0.187 * tau) / (((tau ** 2) + (0.52 ** 2)) ** 2)) + 0.39) * \
        (1.64 - (0.005 ** (0.0012 / zeta))) * \
        (0.808 + 1.053 * theta - 1.029 * (theta ** 2))
    
    # return rf
    return rf


def kbip(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-4, K-Joint Balanced in-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    tau = thk2 / thk1
    zeta = g / d1
    
    # calculate rf
    rf = 3.04 * (((0.31 * beta) / (((beta ** 2) + (0.77 ** 2)) ** 2)) + 0.37) * \
        (((0.44 * tau) / (((tau ** 2) + (0.67 ** 2)) ** 2)) + 0.13) * \
        (1.97 - (zeta ** -0.13)) * \
        (6.22 + 10.6 * theta - 5.034 * (theta ** 2))
    
    # return rf
    return rf


def kbop(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-5, K-Joint Balanced out-of-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    zeta = g / d1
    
    # calculate rf
    rf = 4.82 * (1.04 - 1.17 * beta + 0.7 * (beta ** 2)) * (gamma ** -0.175) * \
        (((0.28 * tau) / (((tau ** 2) + (0.57 ** 2)) ** 2)) + 0.17) * \
        ((zeta ** -0.017) - 0.45) * (1.56 - 0.663 * theta)
    
    # return rf
    return rf    


def taxial(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-6, T- and Y-Joint Axial Load
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.35 * (-1.802 * (beta ** 2) + 1.557 * beta + 0.318) * \
         (-0.556 * tau + 0.85) * (0.007 * gamma + 0.5) * \
         (-0.246 * (theta ** 2) + 0.679 * theta + 0.540)     
    
    # return rf
    return rf


def tbip(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-7, T- and Y-Joint Balanced in-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.55 * (0.334 * beta + 0.419) * \
         (-0.648 * (tau ** 2) + 0.252 * tau + 0.611) * \
         (0.0002 * (gamma ** 2) - 0.002 * gamma + 0.578) * \
         (2.314 * (theta ** 2) - 5.536 * theta + 3.985)
      
    # return rf
    return rf 


def tbop(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-6, T- and Y-Joint Balanced out-of-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.4 * (-1.051 * (beta ** 2) + 0.856 * beta + 0.469) * \
         (-0.6 * tau + 0.856) * \
         (-0.0002 * (gamma ** 2) + 0.014 * gamma + 0.456) * \
         (0.117 * (theta ** 2) - 0.454 * theta + 1.426)    
    
    # return rf
    return rf


def xaxial(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-9, X-Joint Axial Load
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.25 * (-1.734 * (beta ** 2) + 1.565 * beta + 0.326) * \
         (2.687 * (tau ** 3) - 5.117 * (tau ** 2) + 2.496 * tau + 0.297) * \
         (0.0065 * gamma + 0.53)
    
    # return rf
    return rf


def xbip(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-10, X-Joint Balanced in-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.5 * (0.25 * beta + 0.548) * \
         (3.772 * (tau ** 3) - 7.478 * (tau ** 2) + 4.136 * tau - 0.073) * \
         (0.008 * gamma + 0.472)
    
    # return rf
    return rf


def xbop(d1, d2, thk1, thk2, length, theta, g):
    """ Table F-6, Eqn F.10-11, X-Joint Balanced out-of-plane bending
        
        Reduction factors for calculation of stress at root area of single sided
        welds in tubular joints
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2, numpy array of floats defining diameter "d"
            thk1, numpy array of floats defining chord thickness "T"
            thk2, numpy array of floats defining thickness "t"
            length, numpy array of floats defining chord length "L"
            theta, numpy array of floats defining angle (in radians) "theta"
            g, numpy array of floats defining gap between two braces, "g"
        
        Returns numpy array of rf values
    """
    # calculate parameters
    beta = d2 / d1
    gamma = d1 / (2 * thk1)
    tau = thk2 / thk1
    
    # calculate rf
    rf = 2.4 * (-1.188 * (beta ** 2) + 0.981 * beta + 0.453) * \
         (3.414 * (tau ** 3) - 6.33 * (tau ** 2) + 3.101 * tau + 0.194) * \
         (-0.0002 * (gamma ** 2) + 0.014 * gamma + 0.46)
    
    # return rf
    return rf
