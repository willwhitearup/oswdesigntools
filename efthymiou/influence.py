""" Module containing Efthymiou joint Influence functions implemented using numpy
    
    See .\refs\Efthymiou_1988.pdf
    
    Ref:
        Development of SCF Formulae and Generalised Influence Functions for use in
        Fatigue Analysis, M/ Efthymiou, Shell Internationale Petroleum Maatachappij B.V.,
        OTH'88 Recent Developments in Tubular Joints Technology, 4-5 October 1988
"""
# imports -----------------------------------------------------------------------------------------
import numpy as np
from collections import OrderedDict
from efthymiou.scf import *
from efthymiou.reduction import *

# functions ---------------------------------------------------------------------------------------
def ix1_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b, c):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"      
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for chord A
    """     
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using x1 and x7 eqn respectively
    x1a = max(SCFMIN, x1(d1, d2_a, thk1, thk2_a, L, theta_a))
    x7a = max(SCFMIN, x7(d1, d2_a, thk1, thk2_a, L, theta_a, c))
    
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (x1a - x7a)

    return infunc_a           

def ix2_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b, c):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"      
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using x2 and t6 eqn respectively
    x2a = max(SCFMIN, x2(d1, d2_a, thk1, thk2_a, L, theta_a))
    t6a = max(SCFMIN, t6(d1, d2_a, thk1, thk2_a, L, theta_a, c))

    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (x2a - t6a)

    return infunc_a 
    
def ix3_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b, c):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"      
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using x3 and x8 eqn respectively
    x3a = max(SCFMIN, x3(d1, d2_a, thk1, thk2_a, L, theta_a))
    x8a = max(SCFMIN, x8(d1, d2_a, thk1, thk2_a, L, theta_a))

    # calculate influence function for A and B
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (x3a - x8a)

    return infunc_a   
    
def ix4_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b, c):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"      
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using x4 and t7 eqn respectively
    x4a = max(SCFMIN, x4(d1, d2_a, thk1, thk2_a, L, theta_a))
    t7a = max(SCFMIN, t7(d1, d2_a, thk1, thk2_a, L, theta_a, c))
    
    # calculate influence function for A 
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (x4a - t7a)

    return infunc_a 

def ix5_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX5
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"  
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    secMod_a =  np.pi * ((d2_a ** 4) - ((d2_a - thk2_a * 2) ** 4)) / (32 * d2_a)
    secMod_b =  np.pi * ((d2_b ** 4) - ((d2_b - thk2_b * 2) ** 4)) / (32 * d2_b)    
    
    # calculate scf for A using x5 and t10 eqn respectively
    x5a = max(SCFMIN, x5(d1, d2_a, thk1, thk2_a, L, theta_a))
    t10a = max(SCFMIN, t10(d1, d2_a, thk1, thk2_a, L, theta_a))
    
    # calculate influence function for A
    infunc_a = sigma_b * ((secMod_b * np.sin(theta_b)) / (secMod_a * np.sin(theta_a))) * \
            (x5a - t10a)

    return infunc_a    
    
def ix6_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, sigma_b):
    """ Table 5 - Influence functions for X-joints under axial load and opb, Eqn. IX6
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"  
        
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    secMod_a =  np.pi * ((d2_a ** 4) - ((d2_a - thk2_a * 2) ** 4)) / (32 * d2_a)
    secMod_b =  np.pi * ((d2_b ** 4) - ((d2_b - thk2_b * 2) ** 4)) / (32 * d2_b)    
    
    # calculate scf for A using x6 and t11 eqn respectively
    x6a = max(SCFMIN, x6(d1, d2_a, thk1, thk2_a, L, theta_a))
    t11a = max(SCFMIN, t11(d1, d2_a, thk1, thk2_a, L, theta_a))
    
    # calculate influence function for A
    infunc_a = sigma_b * ((secMod_b * np.sin(theta_b)) / (secMod_a * np.sin(theta_a))) * \
            (x6a - t11a)

    return infunc_a

def ik1_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, c, sigma_b):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using t5 and k1 eqn respectively
    t5a = max(SCFMIN, t5(d1, d2_a, thk1, thk2_a, L, theta_a, c) * f2(d1, d2_a, thk1, thk2_a, L))
    k1a, k1b, k1c = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k1a = max(SCFMIN, k1a)
    k1b = max(SCFMIN, k1b)
    k1c = max(SCFMIN, k1c)
        
    # calculate influence function for A and B
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (t5a - k1a)

    return infunc_a

def ik2_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, c, sigma_b):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            c, numpy array of floats defining chord-end fixity parameter "C"
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using t6 and k1 eqn respectively
    t6a = max(SCFMIN, t6(d1, d2_a, thk1, thk2_a, L, theta_a, c))
    k1a, k1b, k1c = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k1a = max(SCFMIN, k1a)
    k1b = max(SCFMIN, k1b)
    k1c = max(SCFMIN, k1c)    
        
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (t6a - k1a)

    return infunc_a

def ik3_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, sigma_b, brace_1):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            brace_1, string identifying which brace A or B is a through brace
            
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using t3 and k2 eqn respectively
    t3a = max(SCFMIN, t3(d1, d2_a, thk1, thk2_a, L, theta_a) * f2(d1, d2_a, thk1, thk2_a, L))
    k2a, k2b, k2c = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, brace_1)
    k2a = max(SCFMIN, k2a)
    k2b = max(SCFMIN, k2b)
    k2c = max(SCFMIN, k2c)
    
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (t3a - k2a)

    return infunc_a

def ik4_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, sigma_b, brace_1):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            brace_1, string identifying which brace A or B is a through brace        
            
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    
    # calculate scf for A using t7 and k2 eqn respectively
    t7a = max(SCFMIN, t7(d1, d2_a, thk1, thk2_a, L, theta_a, c))
    k2a, k2b, k2c = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, brace_1)
    k2a = max(SCFMIN, k2a)
    k2b = max(SCFMIN, k2b)
    k2c = max(SCFMIN, k2c)
    
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * \
            (t7a - k2a)

    return infunc_a

def ik5_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, sigma_b):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK5
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
        
        Returns numpy array of influence function for chord A
    """    
    # calculate scf for A and B using k4 and k6 eqn respectively
    k4a, k4b = k4(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k6a, k6b = k6(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k4a = max(SCFMIN, k4a)
    k4b = max(SCFMIN, k4b)
    k6a = max(SCFMIN, k6a)
    k6b = max(SCFMIN, k6b)
    
    # calculate influence function for A
    infunc_a = sigma_b * (k4a - k6a)

    return infunc_a

def ik6_a(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, sigma_b):
    """ Table 6 - Influence functions for K-joints under axial load and opb, Eqn. IK6
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            sigma_b, numpy array of floats defining stress "sigma B"        
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
        
        Returns numpy array of influence function for brace A
    """    
    # calculate scf for A and B using k4 and k6 eqn respectively
    k5a, k5b = k5(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k7a, k7b = k7(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k5a = max(SCFMIN, k5a)
    k5b = max(SCFMIN, k5b)
    k7a = max(SCFMIN, k7a)
    k7b = max(SCFMIN, k7b)
    
    # calculate influence function for A
    infunc_a = sigma_b * (k5a - k7a)

    return infunc_a

def ikt1_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 7 - Influence functions for KT-joints under axial load, Eqn. IKT1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    area_c = np.pi * (d2_c / 2) ** 2 - np.pi * (d2_c / 2 - thk2_c) ** 2  
    
    # calculate scf for A using t5 and k1 eqn respectively
    t5a = t5(d1, d2_a, thk1, thk2_a, L, theta_a, c) * f2(d1, d2_a, thk1, thk2_a, L)
    k1ab, k1ba, k1c = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k1ac, k1ca, k1c = k1(d1, d2_a, d2_c, thk1, thk2_a, thk2_c, L, theta_a, theta_c, g_ab + d2_b + g_bc)

    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * (t5a - k1ab) + \
            sigma_c * ((area_c * np.sin(theta_c)) / (area_a * np.sin(theta_a))) * (t5a - k1ac)

    return infunc_a

def ikt2_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 7 - Influence functions for KT-joints under axial load, Eqn. IKT2
        
         Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
        
        Returns numpy array of influence function for chord A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    area_c = np.pi * (d2_c / 2) ** 2 - np.pi * (d2_c / 2 - thk2_c) ** 2  
    
    # calculate scf for A using t5 and k1 eqn respectively
    t6a = t6(d1, d2_a, thk1, thk2_a, L, theta_a, c)
    k1ab, k1ba, k1c = k1(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab)
    k1ac, k1ca, k1c = k1(d1, d2_a, d2_c, thk1, thk2_a, thk2_c, L, theta_a, theta_c, g_ab + g_bc)
        
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * (t6a - k1ab) + \
            sigma_c * ((area_c * np.sin(theta_c)) / (area_a * np.sin(theta_a))) * (t6a - k1ac)

    return infunc_a

def ikt3_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 7 - Influence functions for KT-joints under axial load, Eqn. IKT3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
                    
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    area_c = np.pi * (d2_c / 2) ** 2 - np.pi * (d2_c / 2 - thk2_c) ** 2  
    
    # calculate scf for A using t5 and k1 eqn respectively
    t3a = t3(d1, d2_a, thk1, thk2_a, L, theta_a) * f2(d1, d2_a, thk1, thk2_a, L)
    k2ab, k2ba, k2c = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, brace_1)
    k2ac, k2ca, k2c = k2(d1, d2_a, d2_c, thk1, thk2_a, thk2_c, L, theta_a, theta_c, g_ab + g_bc, brace_2)
        
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * (t3a - k2ab) + \
            sigma_c * ((area_c * np.sin(theta_c)) / (area_a * np.sin(theta_a))) * (t3a - k2ac)

    return infunc_a

def ikt4_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 7 - Influence functions for KT-joints under axial load, Eqn. IKT4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
            
        Returns numpy array of influence function for brace A
    """ 
    # calculate parameters
    area_a = np.pi * (d2_a / 2) ** 2 - np.pi * (d2_a / 2 - thk2_a) ** 2  
    area_b = np.pi * (d2_b / 2) ** 2 - np.pi * (d2_b / 2 - thk2_b) ** 2  
    area_c = np.pi * (d2_c / 2) ** 2 - np.pi * (d2_c / 2 - thk2_c) ** 2  
    
    # calculate scf for A using t7 and k2 eqn respectively
    t7a = t7(d1, d2_a, thk1, thk2_a, L, theta_a, c)
    k2ab, k2ba, k2c = k2(d1, d2_a, d2_b, thk1, thk2_a, thk2_b, L, theta_a, theta_b, g_ab, brace_1)
    k2ac, k2ca, k2c = k2(d1, d2_a, d2_c, thk1, thk2_a, thk2_c, L, theta_a, theta_c, g_ab + g_bc, brace_2)
        
    # calculate influence function for A
    infunc_a = sigma_b * ((area_b * np.sin(theta_b)) / (area_a * np.sin(theta_a))) * (t7a - k2ab) + \
            sigma_c * ((area_c * np.sin(theta_c)) / (area_a * np.sin(theta_a))) * (t7a - k2ac)

    return infunc_a

def hss1_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 8 - Hot spot stresses in KT-joints under OPB, Eqn. HSS1
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
            
        Returns numpy array of hot spot stresses for chord A
    """ 
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    beta_max = np.maximum(beta_a, beta_b, beta_c)
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_a) / beta_a)
    x_ac = 1 + ((zeta_ab + zeta_bc + beta_b) * np.sin(theta_a) / beta_a)
    
    # calculate scf for A, B and C using t10
    t10a = t10(d1, d2_a, thk1, thk2_a, L, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, L, theta_b)
    t10c = t10(d1, d2_b, thk1, thk2_b, L, theta_c) 
        
    # calculate hot spot stresses for A
    hss_a = sigma_a * t10a * (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_ac)) + \
            sigma_b * t10b * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ab)) + \
            sigma_c * t10c * (1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ac)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ac))
            
    return hss_a

def hss2_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
          phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 8 - Hot spot stresses in KT-joints under OPB, Eqn. HSS2
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
            
        Returns numpy array of hot spot stresses for brace A
    """ 
    # calculate parameters
    beta_a = d2_a / d1
    gamma = d1 / (2 * thk1)
    tau_a = thk2_a / thk1
   
    # calculate hot spot stresses for a and c using HSS1
    hss1 = hss1_a(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
                   phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c)
        
    # calculate hot spot stresses for A
    hss_a = (tau_a ** -0.54) * (gamma ** -0.05) * \
            (0.99 - 0.47 * beta_a + 0.08 * (beta_a ** 4)) * hss1
            
    return hss_a

def hss3(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
         phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 8 - Hot spot stresses in KT-joints under OPB, Eqn. HSS3
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
            
        Returns numpy array of hot spot stresses for chord B
    """ 
    # calculate parameters
    beta_a = d2_a / d1
    beta_b = d2_b / d1
    beta_c = d2_c / d1
    beta_max = np.maximum(beta_a, beta_b, beta_c)
    gamma = d1 / (2 * thk1)
    zeta_ab = g_ab / d1
    zeta_bc = g_bc / d1
    x_ab = 1 + (zeta_ab * np.sin(theta_b) / beta_b)
    x_bc = 1 + (zeta_bc * np.sin(theta_b) / beta_b)
    
    # calculate scf for A, B and C using t10
    t10a = t10(d1, d2_a, thk1, thk2_a, L, theta_a)
    t10b = t10(d1, d2_b, thk1, thk2_b, L, theta_b)
    t10c = t10(d1, d2_b, thk1, thk2_b, L, theta_c) 
        
    # calculate hot spot stresses for B
    hss_b = sigma_b * t10b * \
            ((1 - 0.08 * ((beta_a * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) ** ((beta_a / beta_b) ** 2)) * \
            ((1 - 0.08 * ((beta_c * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) ** ((beta_c / beta_b) ** 2)) + \
            sigma_a * t10a * \
            (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_ab)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_ab)) + \
            sigma_c * t10c * \
            (1 - 0.08 * ((beta_b * gamma) ** 0.5) * np.exp(-0.8 * x_bc)) * \
            (2.05 * (beta_max ** 0.5) * np.exp(-1.3 * x_bc))
            
    return hss_b

def hss4(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
         phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c):
    """ Table 8 - Hot spot stresses in KT-joints under OPB, Eqn. HSS4
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_a, numpy array of floats defining diameter "dA"
            d2_b, numpy array of floats defining diameter "dB"            
            d2_c, numpy array of floats defining diameter "dC" 
            thk1, numpy array of floats defining chord thickness "T"
            thk2_a, numpy array of floats defining thickness "tA"
            thk2_b, numpy array of floats defining thickness "tB"
            thk2_c, numpy array of floats defining thickness "tC"
            length, numpy array of floats defining length "L"
            theta_a, numpy array of floats defining angle (in radians) "theta" for a
            theta_b, numpy array of floats defining angle (in radians) "theta" for b
            theta_c, numpy array of floats defining angle (in radians) "theta" for c
            sigma_a, numpy array of floats defining stress "sigma A"
            sigma_b, numpy array of floats defining stress "sigma B"
            sigma_c, numpy array of floats defining stress "sigma C" 
            phi_b, numpy array of floats defining angle (in radians) "phi" for b
            phi_c, numpy array of floats defining angle (in radians) "phi" for c          
            g_ab, numpy array of floats defining gap between two braces A and B, "gAB"
            g_bc, numpy array of floats defining gap between two braces B and C, "gBC"
            c, numpy array of floats defining chord-end fixity parameter "C"
            brace_1, string identifying which brace A or B is a through brace
            brace_2, string identifying which brace A or C is a through brace
            brace_3, string identifying which brace B or C is a through brace
            
        Returns numpy array of hot spot stresses for brace B
    """ 
    # calculate parameters
    beta_b = d2_b / d1
    gamma = d1 / (2 * thk1)
    tau_b = thk2_b / thk1
   
    # calculate hot spot stresses for b using HSS3
    hss3_b = hss3(d1, d2_a, d2_b, d2_c, thk1, thk2_a, thk2_b, thk2_c, L, theta_a, theta_b, theta_c, \
                  phi_b, phi_c, g_ab, g_bc, c, brace_1, brace_2, brace_3, sigma_a, sigma_b, sigma_c)
        
    # calculate hot spot stresses for A and C
    hss_b = (tau_b ** -0.54) * (gamma ** -0.05) * \
            (0.99 - 0.47 * beta_b + 0.08 * (beta_b ** 4)) * hss3_b
            
    return hss_b

def im1(d1, d2_i, d2_j, thk1, thk2_i, thk2_j, L, theta_i, theta_j, phi_j, c, sigma_j):
    """ Table 9 - Influence functions for non-planar braces, Eqn. IM1
        
        ** i refers to the reference brace, j refers to braces that are not in-plane with i
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_i, numpy array of floats defining diameter "di" 
            d2_j, numpy nd array of floats defining diameter "dj"                        
            thk1, numpy array of floats defining chord thickness "T"
            thk2_i, numpy array of floats defining thickness "ti"
            thk2_j, numpy nd array of floats defining thickness "tj"         
            length, numpy array of floats defining length "L"
            theta_i, numpy array of floats defining angle (in radians) "theta" for i
            theta_j, numpy array of floats defining angle (in radians) "theta" for j
            phi_j, numpy array of floats defining angle (in radians) "phi" for j           
            sigma_j, numpy array of floats defining stress "sigma j"         
            c, numpy array of floats defining chord-end fixity parameter "C"
            
        Returns numpy array of influence function for reference chord i
    """ 
    # calculate parameters
    area_i = np.pi * (d2_i / 2) ** 2 - np.pi * (d2_i / 2 - thk2_i) ** 2  
    area_j = np.pi * (d2_j / 2) ** 2 - np.pi * (d2_j / 2 - thk2_j) ** 2  
    arrSize = d2_j.shape[2]
    p2 = np.zeros((d2_j.shape[0],d2_j.shape[1]))
    
    for ite in range(arrSize):
        p2 = p2 + sigma_j[:, :, ite] * area_j[:, :, ite] * np.cos(2 * phi_j[:, :, ite]) * \
             np.sin(theta_j[:,:,ite])    
             
    # calculate scf for i using x1 and t5 eqn respectively
    x1i = max(SCFMIN, x1(d1, d2_i, thk1, thk2_i, L, theta_i))
    t5i = max(SCFMIN, t5(d1, d2_i, thk1, thk2_i, L, theta_i, c) * f2(d1, d2_i, thk1, thk2_i, L))
    
    # calculate influence function for i
    infunc = (p2 / (area_i * np.sin(theta_i))) * (x1i - t5i)

    return infunc

def im2(d1, d2_i, d2_j, thk1, thk2_i, thk2_j, L, theta_i, theta_j, phi_j, c, sigma_j):
    """ Table 9 - Influence functions for non-planar braces, Eqn. IM2
        
        ** i refers to the reference brace, j refers to braces that are not in-plane with i
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_i, numpy array of floats defining diameter "di" 
            d2_j, numpy nd array of floats defining diameter "dj"                        
            thk1, numpy array of floats defining chord thickness "T"
            thk2_i, numpy array of floats defining thickness "ti"
            thk2_j, numpy nd array of floats defining thickness "tj"         
            length, numpy array of floats defining length "L"
            theta_i, numpy array of floats defining angle (in radians) "theta" for i
            theta_j, numpy array of floats defining angle (in radians) "theta" for j
            phi_j, numpy array of floats defining angle (in radians) "phi" for j           
            sigma_j, numpy array of floats defining stress "sigma j"         
            c, numpy array of floats defining chord-end fixity parameter "C"
            
        Returns numpy array of influence function for reference chord i
    """ 
    # calculate parameters
    beta_i = d2_i / d1
    alpha = 2 * L / d1 
    tau_i = thk2_i / thk1    
    area_i = np.pi * (d2_i / 2) ** 2 - np.pi * (d2_i / 2 - thk2_i) ** 2  
    area_j = np.pi * (d2_j / 2) ** 2 - np.pi * (d2_j / 2 - thk2_j) ** 2  
    arrSize = d2_j.shape[2]
    p1 = np.zeros((d2_j.shape[0],d2_j.shape[1]))
    
    for ite in range(arrSize):
        p1 = p1 + sigma_j[:, :, ite] * area_j[:, :, ite] * np.cos(phi_j[:, :, ite]) * \
             np.sin(theta_j[:,:,ite])  

    # calculate influence function for i
    infunc = (p1 / area_i) * ((c / 2) * alpha * beta_i * tau_i)

    return infunc

def im3(d1, d2_i, d2_j, thk1, thk2_i, thk2_j, L, theta_i, theta_j, phi_j, c, sigma_j):
    """ Table 9 - Influence functions for non-planar braces, Eqn. IM3
        
        ** i refers to the reference brace, j refers to braces that are not in-plane with i,
           k refers to an arbitary brace (mainly for completeness, does not exist)
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_i, numpy array of floats defining diameter "di" 
            d2_j, numpy nd array of floats defining diameter "dj"                        
            thk1, numpy array of floats defining chord thickness "T"
            thk2_i, numpy array of floats defining thickness "ti"
            thk2_j, numpy nd array of floats defining thickness "tj"         
            length, numpy array of floats defining length "L"
            theta_i, numpy array of floats defining angle (in radians) "theta" for i
            theta_j, numpy array of floats defining angle (in radians) "theta" for j
            phi_j, numpy array of floats defining angle (in radians) "phi" for j           
            sigma_j, numpy array of floats defining stress "sigma j"         
            c, numpy array of floats defining chord-end fixity parameter "C"
            
        Returns numpy array of influence function for reference chord i
    """ 
    # calculate parameters
    area_i = np.pi * (d2_i / 2) ** 2 - np.pi * (d2_i / 2 - thk2_i) ** 2  
    area_j = np.pi * (d2_j / 2) ** 2 - np.pi * (d2_j / 2 - thk2_j) ** 2  
    arrSize = d2_j.shape[2]
    p2 = np.zeros((d2_j.shape[0],d2_j.shape[1]))
    
    for ite in range(arrSize):
        p2 = p2 + sigma_j[:, :, ite] * area_j[:, :, ite] * np.cos(2 * phi_j[:, :, ite]) * \
             np.sin(theta_j[:,:,ite])    
             
    # calculate scf for i using x3 and t3 eqn respectively
    x3i = max(SCFMIN, x3(d1, d2_i, thk1, thk2_i, L, theta_i))
    t3i = max(SCFMIN, t3(d1, d2_i, thk1, thk2_i, L, theta_i) * f2(d1, d2_i, thk1, thk2_i, L))
    
    # calculate influence function for i
    infunc = (p2 / (area_i * np.sin(theta_i))) * (x3i - t3i)

    return infunc

def im4(d1, d2_i, d2_j, thk1, thk2_i, thk2_j, L, theta_i, theta_j, phi_j, c, sigma_j):
    """ Table 9 - Influence functions for non-planar braces, Eqn. IM4
        
        ** i refers to the reference brace, j refers to braces that are not in-plane with i,
           k refers to an arbitary brace (mainly for completeness, does not exist)
        
        Args:
            d1, numpy array of floats defining chord diameter "D"
            d2_i, numpy array of floats defining diameter "di" 
            d2_j, numpy nd array of floats defining diameter "dj"                        
            thk1, numpy array of floats defining chord thickness "T"
            thk2_i, numpy array of floats defining thickness "ti"
            thk2_j, numpy nd array of floats defining thickness "tj"         
            length, numpy array of floats defining length "L"
            theta_i, numpy array of floats defining angle (in radians) "theta" for i
            theta_j, numpy array of floats defining angle (in radians) "theta" for j
            phi_j, numpy array of floats defining angle (in radians) "phi" for j           
            sigma_j, numpy array of floats defining stress "sigma j"         
            c, numpy array of floats defining chord-end fixity parameter "C"
            
        Returns numpy array of influence function for reference chord i
    """ 
    # calculate parameters
    beta_i = d2_i / d1
    alpha = 2 * L / d1 
    tau_i = thk2_i / thk1    
    area_i = np.pi * (d2_i / 2) ** 2 - np.pi * (d2_i / 2 - thk2_i) ** 2  
    area_j = np.pi * (d2_j / 2) ** 2 - np.pi * (d2_j / 2 - thk2_j) ** 2  
    arrSize = d2_j.shape[2]
    p1 = np.zeros((d2_j.shape[0],d2_j.shape[1]))
    
    for ite in range(arrSize):
        p1 = p1 + sigma_j[:, :, ite] * area_j[:, :, ite] * np.cos(phi_j[:, :, ite]) * \
             np.sin(theta_j[:,:,ite])  

    # calculate influence function for i
    infunc = (p1 / area_i) * ((c / 5) * alpha * beta_i * tau_i)

    return infunc   
    
######## list of equations not coded / need to test #############
# brace saddle for axial load - general fixity conditions table 1 = T3 * F2
# chord crown for in plane bending table 2 = T8 
# brace crown for in plane bending table 2 = T9
# chord crown for axial load on one brace only table 2 = T6
# brace crown for axial load on one brace only table 2 = T7 * F1 or * F2
# chord saddle for out of plane bending on one brace only table 2 = T10 
# brace saddle for out of plane bending on one brace only table 2 = T11 * F3	
# chord crown for unbalanced IPB table 3 = T8 / T8 * 1.2
# gap joint-brace crown for unbalanced IPB table 3 = T9
# chord saddle for axial load on one brace only table 3 = T5 * F1
# chord crown for axial load on one brace only table 3 = T6
# brace saddle for axial load on one brace only table 3 = T3 * F1
# brace crown for axial load on one brace only table 3 = T7
# chord crown for IPB on one brace only table 3 = T8
# brace crown for IPB on one brace only table 3 = T9
# chord for balanced axial laod table 4 = K1
# brace for balanced axial laod table 4 = K2
# chord for in plane bending table 4 = T8
# brace for in plane bending table 4 = T9
# OPB Brace table 4  - using KT1 or KT2
# chord saddle for axial load on one brace only table 4 = T5
# chord crown for axial load on one brace only table 4 = T6
# brace saddle for axial load on one brace only table 4 = T3
# brace crown for axial load on one brace only table 4 = T7
# OPB Brace table 4  - using KT3 or KT4