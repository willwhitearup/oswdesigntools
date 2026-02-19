import numpy as np

from boltedconn.boltdata import BoltLibrary, BoltMaterialLibrary
from boltedconn.flange import BoltedFlange
from boltedconn.steel import SteelMaterial
from boltedconn.tensionerdata import BoltTensionerLibrary

# Inputs =======================================================
# bolt inputs
bolt_material_grade = "10.9"
flange_steel_grade = "355"
foundation_steel_grade = "355"
bolt = "M90"


# foundation geometry
outer_diameter = 7500
wall_thickness = 100
flange_height = 200  # in z
flange_length = 400  # radial length

# loading
ULS_axial_force = 17.305e6 # N above the flange
ULS_bending_moment = 557e9 # Nmm


# process =======================================================
# get bolt constants
grade_10_9 = BoltMaterialLibrary.create(bolt_material_grade)
bolt_obj = BoltLibrary.create(bolt, grade_10_9)
bolt_obj.calculate_yielding_bolt_force()  # for F_tR
print("Bolt preload currently set using 0.7 x ultimate bolt strength... could be wrong and maybe use yield instead??")
bolt_tensioner_tool = BoltTensionerLibrary.create(bolt)

# material data
foundation_steel = SteelMaterial(foundation_steel_grade, wall_thickness)
flange_steel = SteelMaterial(flange_steel_grade, flange_height)

# flange geometry and bolt data
flange_obj = BoltedFlange(outer_diameter, wall_thickness, flange_height, flange_length, bolt_tensioner_tool, ULS_bending_moment, ULS_axial_force)
flange_obj.geometry_validity_check()

print("no. of bolts", flange_obj.n_bolts)
print("design preload", bolt_obj.design_preload)
print("bolt section force ULS", flange_obj.bolt_sector_force)
print("a/b ratio", flange_obj.a / flange_obj.b)
# geom checks
print("a", flange_obj.a)
print("a'",flange_obj.a)








