'''implements RRF calcs as per DNV RP C203

for X braces, where beta limit of 0.85 is exceeded, KMethod have developed their own
methodology to determine RRFs. This is selected as the default approach to determine
RRFs in this way.
'''

import numpy as np


#------------------------------------------------------------------------------
# X brace joint RRFS___________________________________________________________
def axialrrf_x(beta, gamma, tau, method="KMethod"):
    '''defines axial rrf for x brace
    args:
        beta, gamma, tau: floats, define geometrical parameter of joint
    returns:
        rrf, float, root reduction factor
    '''
    if beta <= 0.85:
        rrf = 2.25*(-1.734*beta**2 + 1.565*beta + 0.326)*(2.687*tau**3 - 5.117*tau**2 + 2.496*tau + 0.297)*(0.0065*gamma + 0.53)
    # dnv method
    elif (beta > 0.85 and beta <= 1.0) and method=="DNV":
        '''see notes section of Table F-6 in DNV-RP-C203, appx F.
        '''
        beta_85, beta_1 = 0.85, 1
        rrf_beta_85 = 2.25*(-1.734*beta_85**2 + 1.565*beta_85 + 0.326)*(2.687*tau**3 - 5.117*tau**2 + 2.496*tau + 0.297)*(0.0065*gamma + 0.53)
        rrf_beta_1 = 0.85
        rrf = np.interp(beta, [beta_85, beta_1], [rrf_beta_85, rrf_beta_1])
    # KMethod method
    elif (beta > 0.85 and beta <= 1.0) and method=="KMethod":
        betavals = np.arange(0.4, 0.85+0.01, 0.05)
        rrf_betavals = 2.25*(-1.734*betavals**2 + 1.565*betavals + 0.326)*(2.687*tau**3 - 5.117*tau**2 + 2.496*tau + 0.297)*(0.0065*gamma + 0.53)
        rrf = max(rrf_betavals)
    else:
        raise Exception(f"beta value of {beta} outside validity ranges")
    return rrf

def ipbrrf_x(beta, gamma, tau):
    '''defines ipb rrf for x brace. Only DNV method is used here for when beta>0.85
    '''
    if beta <= 0.85:
        rrf = 2.5*(0.25*beta+0.548)*(3.772*tau**3-7.478*tau**2+4.136*tau-0.073)*(0.008*gamma+0.472)
    # dnv method only (note, no "KMethod" method exists for ipb rrf)
    elif (beta > 0.85 and beta <= 1.0):
        beta_85, beta_1 = 0.85, 1
        rrf_beta_85 = 2.5*(0.25*beta_85+0.548)*(3.772*tau**3-7.478*tau**2+4.136*tau-0.073)*(0.008*gamma+0.472)
        rrf_beta_1 = 0.85
        rrf = np.interp(beta, [beta_85, beta_1], [rrf_beta_85, rrf_beta_1])
    return rrf

def opbrrf_x(beta, gamma, tau, method="KMethod"):
    if beta <= 0.85:
        rrf = 2.4*(-1.188*beta**2+0.981*beta+0.453)*(3.414*tau**3-6.33*tau**2+3.101*tau+0.194)*(-0.0002*gamma**2+0.014*gamma+0.46)
    # dnv method
    elif (beta > 0.85 and beta <= 1.0) and method=="DNV":
        beta_85, beta_1 = 0.85, 1
        rrf_beta_85 = 2.4*(-1.188*beta_85**2+0.981*beta_85+0.453)*(3.414*tau**3-6.33*tau**2+3.101*tau+0.194)*(-0.0002*gamma**2+0.014*gamma+0.46)
        rrf_beta_1 = 0.85
        rrf = np.interp(beta, [beta_85, beta_1], [rrf_beta_85, rrf_beta_1])
    # KMethod method
    elif (beta > 0.85 and beta <= 1.0) and method=="KMethod":
        betavals = np.arange(0.4, 0.85 + 0.01, 0.05)
        rrf_betavals = 2.4*(-1.188*betavals**2+0.981*betavals+0.453)*(3.414*tau**3-6.33*tau**2+3.101*tau+0.194)*(-0.0002*gamma**2+0.014*gamma+0.46)
        rrf = max(rrf_betavals)
    return rrf
#------------------------------------------------------------------------------
# end of X brace joint RRFS____________________________________________________


#------------------------------------------------------------------------------
# YT joints RRFS_______________________________________________________________
def axialrrf_yt(beta, gamma, tau, theta):
    if beta <= 0.85:
        rrf = 2.35*(-1.802*beta**2+1.557*beta+0.318)*(-0.556*tau+0.85)*(0.007*gamma+0.5)*(-0.246*np.radians(theta)**2+0.679*np.radians(theta)+0.54)
    return rrf

def ipbrrf_yt(beta, gamma, tau, theta):
    rrf = 2.55*(0.334*beta+0.419)*(-0.648*tau**2+0.252*tau+0.611)*(0.0002*gamma**2-0.002*gamma+0.578)*(2.314*np.radians(theta)**2-5.536*np.radians(theta)+3.985)
    return rrf

def opbrrf_yt(beta, gamma, tau, theta):
    rrf = 2.4*(-1.051*beta**2+0.856*beta+0.469)*(-0.6*tau+0.856)*(-0.0002*gamma**2+0.014*gamma+0.456)*(0.117*np.radians(theta)**2-0.454*np.radians(theta)+1.426)
    return rrf
#------------------------------------------------------------------------------
# end of YT joints RRFS________________________________________________________


#------------------------------------------------------------------------------
# K joints RRFS________________________________________________________________
def axialrrf_k(beta, gamma, tau, theta, zeta):
    try:
        rrf = 2.6*(0.203+1.66*beta-1.3*beta**2)*(0.47+0.024*gamma-0.00054*gamma**2)*((0.187*tau/(tau**2+0.52**2)**2)+0.39)*(1.64-0.005**(0.0012/zeta))*(0.808+1.053*np.radians(theta)-1.029*np.radians(theta)**2)
    except ZeroDivisionError:
        rrf = 0.0
    return rrf

def ipbrrf_k(beta, gamma, tau, theta, zeta):
    rrf = 3.04*(0.31*beta/(beta**2+0.77**2)**2+0.37)*(0.44*tau/(tau**2+0.67**2)**2+0.13)*(1.97-zeta**(-0.13))*(6.22-10.6*np.radians(theta)+5.034*np.radians(theta)**2)
    return rrf

def opbrrf_k(beta, gamma, tau, theta, zeta):
    rrf = 4.82*(1.04-1.17*beta+0.7*beta**2)*gamma**(-0.175)*(0.28*tau/(tau**2+0.57**2)**2+0.17)*(zeta**(-0.017)-0.45)*(1.56-0.663*np.radians(theta))
    return rrf
#------------------------------------------------------------------------------
# end of K joints RRFS_________________________________________________________
#