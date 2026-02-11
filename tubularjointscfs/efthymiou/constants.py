""" module containing all constants
"""
# imports -----------------------------------------------------------------------------------------
from collections import namedtuple

# constants ---------------------------------------------------------------------------------------
# define SNCURVE namedtuple
SNcurve = namedtuple('SNcurve', ['name', 'log10a1', 'm1', 'log10a2', 'm2', 'k', 'tref', 'Nlimit'])

# sn-curve data is: name, log10a1, m1, log10a2, m2, k, tref, Nlimit
# all names and keys are uppercase
SNCURVES = {'B1AIR': SNcurve('B1AIR',15.117,4.0,17.146,5.0,0.00,25.0,1.0E+07),
            'B2AIR': SNcurve('B2AIR',14.885,4.0,16.856,5.0,0.00,25.0,1.0E+07),
            'CAIR': SNcurve('CAIR',12.592,3.0,16.320,5.0,0.05,25.0,1.0E+07),
            'C1AIR': SNcurve('C1AIR',12.449,3.0,16.081,5.0,0.10,25.0,1.0E+07),
            'C2AIR': SNcurve('C2AIR',12.301,3.0,15.835,5.0,0.15,25.0,1.0E+07),
            'DAIR': SNcurve('DAIR',12.164,3.0,15.606,5.0,0.20,25.0,1.0E+07),
            'EAIR': SNcurve('EAIR',12.010,3.0,15.350,5.0,0.20,25.0,1.0E+07),
            'FAIR': SNcurve('FAIR',11.855,3.0,15.091,5.0,0.25,25.0,1.0E+07),
            'F1AIR': SNcurve('F1AIR',11.699,3.0,14.832,5.0,0.25,25.0,1.0E+07),
            'F3AIR': SNcurve('F3AIR',11.546,3.0,14.576,5.0,0.25,25.0,1.0E+07),
            'GAIR': SNcurve('GAIR',11.398,3.0,14.330,5.0,0.25,25.0,1.0E+07),
            'TAIR': SNcurve('TAIR',12.480,3.0,16.130,5.0,0.25,16.0,1.0E+07),
            'W1AIR': SNcurve('W1AIR',11.261,3.0,14.101,5.0,0.25,25.0,1.0E+07),
            'W2AIR': SNcurve('W2AIR',11.107,3.0,13.845,5.0,0.25,25.0,1.0E+07),
            'W3AIR': SNcurve('W3AIR',10.970,3.0,13.617,5.0,0.25,25.0,1.0E+07),
            'B1CP': SNcurve('B1CP',14.917,4.0,17.146,5.0,0.00,25.0,1.0E+06),
            'B2CP': SNcurve('B2CP',14.685,4.0,16.856,5.0,0.00,25.0,1.0E+06),
            'CCP': SNcurve('CCP',12.192,3.0,16.320,5.0,0.05,25.0,1.0E+06),
            'C1CP': SNcurve('C1CP',12.049,3.0,16.081,5.0,0.10,25.0,1.0E+06),
            'C2CP': SNcurve('C2CP',11.901,3.0,15.835,5.0,0.15,25.0,1.0E+06),
            'DCP': SNcurve('DCP',11.764,3.0,15.606,5.0,0.20,25.0,1.0E+06),
            'ECP': SNcurve('ECP',11.610,3.0,15.350,5.0,0.20,25.0,1.0E+06),
            'FCP': SNcurve('FCP',11.455,3.0,15.091,5.0,0.25,25.0,1.0E+06),
            'F1CP': SNcurve('F1CP',11.299,3.0,14.832,5.0,0.25,25.0,1.0E+06),
            'F3CP': SNcurve('F3CP',11.146,3.0,14.576,5.0,0.25,25.0,1.0E+06),
            'GCP': SNcurve('GCP',10.998,3.0,14.330,5.0,0.25,25.0,1.0E+06),
            'TCP': SNcurve('TCP',12.180,3.0,16.130,5.0,0.25,16.0,1.8E+06),
            'W1CP': SNcurve('W1CP',10.861,3.0,14.101,5.0,0.25,25.0,1.0E+06),
            'W2CP': SNcurve('W2CP',10.707,3.0,13.845,5.0,0.25,25.0,1.0E+06),
            'W3CP': SNcurve('W3CP',10.570,3.0,13.617,5.0,0.25,25.0,1.0E+06),
            'B1FC': SNcurve('B1FC',12.436,3.0,12.436,3.0,0.00,25.0,1.0E+20),
            'B2FC': SNcurve('B2FC',12.262,3.0,12.262,3.0,0.00,25.0,1.0E+20),
            'CFC': SNcurve('CFC',12.115,3.0,12.115,3.0,0.15,25.0,1.0E+20),
            'C1FC': SNcurve('C1FC',11.972,3.0,11.972,3.0,0.15,25.0,1.0E+20),
            'C2FC': SNcurve('C2FC',11.824,3.0,11.824,3.0,0.15,25.0,1.0E+20),
            'DFC': SNcurve('DFC',11.687,3.0,11.687,3.0,0.20,25.0,1.0E+20),
            'EFC': SNcurve('EFC',11.533,3.0,11.533,3.0,0.20,25.0,1.0E+20),
            'FFC': SNcurve('FFC',11.378,3.0,11.378,3.0,0.25,25.0,1.0E+20),
            'F1FC': SNcurve('F1FC',11.222,3.0,11.222,3.0,0.25,25.0,1.0E+20),
            'F3FC': SNcurve('F3FC',11.068,3.0,11.068,3.0,0.25,25.0,1.0E+20),
            'GFC': SNcurve('GFC',10.921,3.0,10.921,3.0,0.25,25.0,1.0E+20),
            'TFC': SNcurve('TFC',12.030,3.0,12.030,3.0,0.25,16.0,1.8E+06),
            'W1FC': SNcurve('W1FC',10.784,3.0,10.784,3.0,0.25,25.0,1.0E+20),
            'W2FC': SNcurve('W2FC',10.630,3.0,10.630,3.0,0.25,25.0,1.0E+20),
            'W3FC': SNcurve('W3FC',10.493,3.0,10.493,3.0,0.25,25.0,1.0E+20),
}
            
# angle dependent sn-curves
SNCURVES['PLANE-TUB-AIR'] = {(-90.0, -30.001): SNCURVES['C2AIR'],
                                 (-30.0, 30.0): SNCURVES['TAIR'],
                                 (30.001, 90.0): SNCURVES['C2AIR']}
SNCURVES['PLANE-TUB-CP'] = {(-90.0, -30.001): SNCURVES['C2CP'],
                                 (-30.0, 30.0): SNCURVES['TCP'],
                                 (30.001, 90.0): SNCURVES['C2CP']}                                 
SNCURVES['PLANE-TUB-FC'] = {(-90.0, -30.001): SNCURVES['C2FC'],
                                 (-30.0, 30.0): SNCURVES['TFC'],
                                 (30.001, 90.0): SNCURVES['C2FC']}
                                 
SNCURVES['PLANE-TUB-ROOT-AIR'] = {(-90.0, -75.001): SNCURVES['DAIR'],
                                 (-75.0, -60.001): SNCURVES['EAIR'],
                                 (-60.0, -45.001): SNCURVES['FAIR'],
                                 (-45.0, -30.001): SNCURVES['F1AIR'],
                                 (-30.0, 30.0): SNCURVES['F3AIR'],
                                 (30.001, 45.0): SNCURVES['F1AIR'],
                                 (45.001, 60.0): SNCURVES['FAIR'],
                                 (60.001, 75.0): SNCURVES['EAIR'],
                                 (75.001, 90.0): SNCURVES['DAIR']}
SNCURVES['PLANE-TUB-ROOT-CP'] = {(-90.0, -75.001): SNCURVES['DCP'],
                                 (-75.0, -60.001): SNCURVES['ECP'],
                                 (-60.0, -45.001): SNCURVES['FCP'],
                                 (-45.0, -30.001): SNCURVES['F1CP'],
                                 (-30.0, 30.0): SNCURVES['F3CP'],
                                 (30.001, 45.0): SNCURVES['F1CP'],
                                 (45.001, 60.0): SNCURVES['FCP'],
                                 (60.001, 75.0): SNCURVES['ECP'],
                                 (75.001, 90.0): SNCURVES['DCP']}                                
SNCURVES['PLANE-TUB-ROOT-FC'] = {(-90.0, -75.001): SNCURVES['DFC'],
                                 (-75.0, -60.001): SNCURVES['EFC'],
                                 (-60.0, -45.001): SNCURVES['FFC'],
                                 (-45.0, -30.001): SNCURVES['F1FC'],
                                 (-30.0, 30.0): SNCURVES['F3FC'],
                                 (30.001, 45.0): SNCURVES['F1FC'],
                                 (45.001, 60.0): SNCURVES['FFC'],
                                 (60.001, 75.0): SNCURVES['EFC'],
                                 (75.001, 90.0): SNCURVES['DFC']}

SNCURVES['PLANE-PLAT-c-AIR'] = {(-90.0, -30.001): SNCURVES['C2AIR'],
                                 (-30.0, 30.0): SNCURVES['DAIR'],
                                 (30.001, 90.0): SNCURVES['C2AIR']}
SNCURVES['PLANE-PLAT-c-CP'] = {(-90.0, -30.001): SNCURVES['C2CP'],
                                 (-30.0, 30.0): SNCURVES['DCP'],
                                 (30.001, 90.0): SNCURVES['C2CP']}                                 
SNCURVES['PLANE-PLAT-c-FC'] = {(-90.0, -30.001): SNCURVES['C2FC'],
                                 (-30.0, 30.0): SNCURVES['DFC'],
                                 (30.001, 90.0): SNCURVES['C2FC']}