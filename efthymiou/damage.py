""" standardised Damage class object
"""
# imports -----------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import copy
from collections import OrderedDict
from .constants import SNCURVES, SNcurve

# constants ---------------------------------------------------------------------------------------
HISTOGRAM_COLUMNS = ['cycles', 'range', 'mean']

# class objects -----------------------------------------------------------------------------------
class Damage(object):
    """ defines a Damage class object with methods for calculating fatigue damage from histogram
    
        Note that the damage value is updated automatically whenever a dependent attribute
        is updated by the user.
        
        Attributes:
            histogram, pandas Dataframe defining histogram or markov matrix, columns headings are
                    either ['cycles', 'range', 'mean', 'damage'], or ['cycles', 'range', 'damage']
                    depending on user input
            sncurve, string or namedtuple, SN curve name, see efthymiou.SNCURVES for available
                    curves, or an efthymiou.constants.SNcurve namedtuple user defined SN curve
            damage, float, defining total fatigue damage (note that damages are also added to the
                    stored histogram)
            angle, float or None, defines angle to calculate fatigue damage at, None if not
                    relevant to SN curve else 0.0 default
            
    """
    def __init__(self, histogram, sncurve, thickness, scf=1.0, angle=None):
        """ initialise 
        
            Args:
                histogram, pandas Dataframe defining histogram or markov matrix, or numpy array of
                            shape (bins, 2 or 3) where dimension 2 is HISTOGRAM_COLUMNS
                sncurve, string, SN curve name, see efthymiou.SNCURVES for available curves
                thickness, float, defines the thickness to use in the damage assessment
                scf, float, defines the scf to use in the damage assessment, default 1.0
                angle, float, defines angle to calculate fatigue damage at, None if not relevant
                        to SN curve else 0.0 default
        """
        # check histogram
        _histogram = self.__check_histogram(histogram)
        # check sncurve
        _sncurve = self.__check_sncurve(sncurve)
        # store sncurve
        self._sncurve = _sncurve
        # check thickness
        _thickness = self.__check_thickness(thickness)
        # store thickness
        self._thickness = thickness
        # check scf
        _scf = self.__check_scf(scf)
        # store scf
        self._scf = scf
        # check angle
        _angle = self.__check_angle(angle)
        # store angle
        self._angle = angle
        # get curve
        _curve = self.getcurve(_sncurve, angle)
        # calculate damage
        _damages = self._getdamage(_histogram.values.T, _curve, self._thickness, self._scf)
        # update DataFrame with damage
        _histogram['damage'] = _damages
        # store histogram
        self._histogram = _histogram
    
    @property
    def histogram(self):
        """ get histogram property """
        return self._histogram
    
    @histogram.setter
    def histogram(self, value):
        """ set histogram property """
        # check value
        _histogram = self.__check_histogram(value)
        # update curve
        _curve = self.getcurve(self._sncurve, self._angle)
        # recalculate damage
        _damages = self._getdamage(_histogram.values.T, _curve, self._thickness, self._scf)
        # update DataFrame with damage
        self._histogram['damage'] = _damages
    
    def __check_histogram(self, value):
        """ check a histogram input """
        # check if histogram is a pandas.Dataframe
        try:
            assert isinstance(value, pd.DataFrame)
            _histogram = value #copy.deepcopy(value)
        except:
            # convert to numpy matrix
            try:
                _histogram = np.array(value).astype(np.float64)
            except:
                raise DamageError('Cannot convert {} into numpy float64 array, please provide a compatible sequence'.format(value))
            # check dimensions
            try:
                assert(_histogram.shape[1] > 1 and _histogram.shape[1] < 4)
            except:
                raise DamageError('Expected histogram to have second dimension == 2 or == 3 not {}'.format(_histogram.shape[1]))
            # convert to Dataframe
            _histogram = pd.DataFrame(_histogram, columns=HISTOGRAM_COLUMNS[:_histogram.shape[1]])
        # check column names
        try:
            assert set(_histogram.columns.values.tolist()) == set(HISTOGRAM_COLUMNS[:len(_histogram.columns)])
        except:
            raise DamageError('Histogram must have columns {} or {} not {}'.format(HISTOGRAM_COLUMNS, HISTOGRAM_COLUMNS[:2], _histogram.columns))
        # return histogram
        return _histogram
        
    @property
    def sncurve(self):
        """ get sncurve property """
        return self._sncurve
    
    @sncurve.setter
    def sncurve(self, value):
        """ set sncurve property """
        # check sncurve value
        _sncurve = self.__check_sncurve(value)
        # store sncurve as property to help with checking angle
        self._sncurve = _sncurve
        # check angle is still compatible
        _angle = self.__check_angle(self._angle)
        # update curve
        _curve = self.getcurve(_sncurve, _angle)
        # recalculate damage
        _damages = self._getdamage(self._histogram.values.T, _curve, self._thickness, self._scf)
        # store angle as property
        self._angle = _angle
        # update DataFrame with damage
        self._histogram['damage'] = _damages
        
    def __check_sncurve(self, value):
        """ check an sncurve input """
        # check if sncurve is user defined or just a string
        if isinstance(value, str):
            try:
                _sncurve = SNCURVES[str(value).upper()]
            except KeyError:
                raise DamageError('SN curve {} not found'.format(value))
        elif isinstance(value, SNcurve):   
            # store as is
            _sncurve = value
        else:
            # raise error
            raise DamageError('SN curve {} is not in a compatible format, please choose from: {}'.format(value, SNCURVES.keys()))
        # return sncurve
        return _sncurve
        
    @property
    def angle(self):
        """ get angle property """
        return self._angle
    
    @angle.setter
    def angle(self, value):
        """ set angle property """
        # check angle value
        _angle = self.__check_angle(value)
        # update curve
        _curve = self.getcurve(self._sncurve, _angle)
        # recalculate damage
        _damages = self._getdamage(self._histogram.values.T, _curve, self._thickness, self._scf)
        # store angle as property
        self._angle = _angle
        # update DataFrame with damage
        self._histogram['damage'] = _damages
        
    def __check_angle(self, value):
        """ check an angle input """
        # check if sncurve is relevant
        if isinstance(self._sncurve, SNcurve):
            # then angle is not relevant
            _angle = None
        else:
            # use value or set to 0.0
            if value is None:
                _angle = 0.0
            else:
                _angle = float(value)
        # return angle
        return _angle
        
    @property
    def scf(self):
        """ get scf property """
        return self._scf
    
    @scf.setter
    def scf(self, value):
        """ set scf property """
        # check angle value
        _scf = self.__check_scf(value)
        # update curve
        _curve = self.getcurve(self._sncurve, self._angle)
        # recalculate damage
        _damages = self._getdamage(self._histogram.values.T, _curve, self._thickness, _scf)
        # store scf as property
        self._scf = _scf
        # update DataFrame with damage
        self._histogram['damage'] = _damages
        
    def __check_scf(self, value):
        """ check an scf input """
        # check if scf can be converted to float
        try:
            _scf = float(value)
        except TypeError:
            raise DamageError('scf {} cannot be converted to float'.format(value))
        # return angle
        return _scf
    
    @property
    def thickness(self):
        """ get thickness property """
        return self._thickness
    
    @thickness.setter
    def thickness(self, value):
        """ set thickness property """
        # check angle value
        _thickness = self.__check_thickness(value)
        # update curve
        _curve = self.getcurve(self._sncurve, self._angle)
        # recalculate damage
        _damages = self._getdamage(self._histogram.values.T, _curve, _thickness, self._scf)
        # store thickness as property
        self._thickness = _thickness
        # update DataFrame with damage
        self._histogram['damage'] = _damages
        
    def __check_thickness(self, value):
        """ check an thickness input """
        # check if thickness can be converted to float
        try:
            _thickness = float(value)
        except TypeError:
            raise DamageError('thickness {} cannot be converted to float'.format(value))
        # return angle
        return _thickness
    
    @staticmethod
    def getcurve(sncurve, angle):
        """ method to get the sncurve used for calculating damage
            
            this is important to help keep a consistent damage calculation if planar or normal
            sn curves are used
        """
        # check if critical plane approach requested
        if angle != None and not isinstance(sncurve, SNcurve):
            # check what sn-curve sector the plane angle sits in and get parameters
            for sector, _sncurve in sncurve.items():
                if sector[0] <= angle and angle <= sector[1]: 
                    break
        else:
            _sncurve = sncurve
        # return SNcurve to use in damage calculation
        return _sncurve
        
    @property
    def damage(self):
        """ get damage property """
        return np.sum(self._histogram['damage'])
        
    def dem(self, m=None, N=None):
        """ calculate damage equivalent moment, dem includes scaling of stresses by scf
        
            Args:
                m, float, sncurve gradient to use in calculation, if None then uses 
                    self.sncurve.m1, default is None
                N, float, number of cycles to use in DEM calculation, if None then
                    self.sncurve.Nlimit is used, default is None
        """
        # pick m value
        if m is None:
            _curve = self.getcurve(self._sncurve, self._angle)
            m = float(_curve.m1)
        else:
            m = float(m)
        # pick N value
        if N is None:
            _curve = self.getcurve(self._sncurve, self._angle)
            N = float(_curve.Nlimit)
        else:
            N = float(N)
        # calculate dem from damage including scf
        dem = (self.damage / N) ** (1 / m)
        print(N, m, self.damage, dem)
        return dem
    
    @staticmethod
    def _getdamage(histogram, sncurve, thickness, scf, dem=None, m=None, N=None):
        """ private method for calculating fatigue damage from histogram or DEM and sncurve
        
            Args:
                histogram, 2D numpy array of shape [2, :] where:
                    [0,:] = cycles
                    [1,:] = ranges
                sncurve, efthymiou.constants.SNcurve object to use damage calculation
                thickness, float, thickness to use in damage calculation
                scf, float, multiplier on stress range and dem used in damage assessment
                dem, float, if not None then used in damage assessment instead of histogram, note
                    that dem value is multiplied by scf, default is None
                m, float, sncurve gradient to use in calculation, if None then uses sncurve.m1,
                    default is None
                N, float, number of cycles to use in DEM calculation, if None then
                    self.sncurve.Nlimit is used, default is None
                
            Returns
                if dem is None returns 1D array of floats defining damage per cycle/range pair
                    shape is (histogram.shape[1],)
                else returns float of damage
        
        """
        # thickness adjustment
        tovertref = thickness / float(sncurve.tref)
        if thickness < sncurve.tref:
            tovertref = 1.0
        # check if dem is provided
        if dem is None:
            # calculate damage for the different portions of the curve
            # implemented in numpy
            nci1 = np.power(10, sncurve.log10a1 - sncurve.m1 * np.log10(histogram[1,:] * float(scf) * np.power((tovertref), sncurve.k)))
            nci2 = np.power(10, sncurve.log10a2 - sncurve.m2 * np.log10(histogram[1,:] * float(scf) * np.power((tovertref), sncurve.k)))
            # mask for determining whether nci1 or nci2 should be used
            mask = nci1 > float(sncurve.Nlimit)
            nci = nci1 * np.invert(mask) + nci2 * mask
            # calculate damage
            damages = histogram[0,:] / nci
            # replace inf and nan values with zero (when deltasig is zero because of np.log10 above)
            damages[np.isnan(damages)] = 0.0
            damages[np.absolute(damages) == np.inf] = 0.0
            return damages
        else:
            # calculate damage from dem
            # pick m value
            if m is None:
                m = float(sncurve.m1)
            else:
                m = float(m)
            # pick N value
            if N is None:
                N = float(sncurve.Nlimit)
            else:
                N = float(N)
            # calculate damage
            _damage = ((float(dem) * float(scf)) ** m) * N
            return _damage
    
    @property
    def __dict__(self):
        """ updates __dict__ method to convert data to float values for pickling """
        odict = OrderedDict()
        odict['histogram'] = OrderedDict((colname, self.histogram[colname].values.tolist()) for colname in self.histogram.columns)
        if isinstance(self._sncurve, SNcurve):
            odict['sncurve'] = self._sncurve._asdict()
        else:
            odict['sncurve'] = {k: v._asdict() for k, v in self._sncurve.items()}
        odict['damage'] = self.damage
        odict['thickness'] = self._thickness
        odict['scf'] = self._scf
        return odict
        
    def __getstate__(self):
        """ returns dict property for serialization during pickling """
        return self.__dict__

    def __setstate__(self, state):
        """ populates private attributes from serialized object during unpickling """
        # populate attributes
        self._thickness = state['thickness']
        self._scf = state['scf']
        # convert histogram dictionary to pandas DataFrame
        self._histogram = pd.DataFrame.from_dict(state['histogram'])
        # unpack SN curve into namedtuple
        self._sncurve = SNcurve(**state['sncurve'])
    
class DamageError(Exception):
    """ Damage error handler """
    pass