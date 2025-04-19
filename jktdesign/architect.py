import numpy as np

from jktdesign.jacket import Jacket
from jktdesign.plotter import jacket_plotter
from jktdesign.tower import Tower


# water levels---------------------------------------------
lat = 0.
water_depth = 62800  # must be positive
msl = 2200
splash_lower, splash_upper = -6110, 12580

# tower and TP---------------------------------------------
rna_cog = 250000
interface_elev = 42150
tp_btm = 33150
tp_width = 19300
# WTG data for CoA
moment_interface_del = 121587000000  # Nm
shear_interface_del = 1198000 # N
# bool to determine whether to plot (or not) the tower in the figure
show_tower = True

# jacket---------------------------------------------
jacket_footprint = 36000
stickup = 4000
# kjt constraints
tp_btm_k1_voffset = 1000  # todo - slide bar for vertical length at top of jacket to k1
btm_vert_leg_length = 5030  #  todo - slide bar vertical leg length above the stab_in (gripper goes here)
# bays data
bay_heights = [19650, 25000, 18160, 22360]  # todo - slide bar

# batter 1 angles and elevation
batter_1_theta = 86  # degrees todo slider
batter_1_elev = -9700  # todo slider

# end of inputs--------------------------------------------------------------------------------------------------

jkt_obj = Jacket(interface_elev, tp_width, tp_btm, tp_btm_k1_voffset, batter_1_theta, batter_1_elev, jacket_footprint,
                 stickup, bay_heights, btm_vert_leg_length, water_depth)

twr_obj = Tower(rna_cog, interface_elev, moment_interface_del, shear_interface_del)

jacket_plotter(twr_obj, jkt_obj, lat, msl, splash_lower, splash_upper, show_tower)