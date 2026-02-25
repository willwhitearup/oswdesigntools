import numpy as np
import os
from contextlib import redirect_stdout
from pprint import pprint
# local
from boltedconn.boltdata import BoltLibrary, BoltMaterialLibrary
from boltedconn.flange import BoltedFlange
from boltedconn.steel import SteelMaterial
from boltedconn.tensionerdata import BoltTensionerLibrary


def bolt_connection_uls_strength_check(outer_diameter, wall_thickness,
                                       bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                       ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                                       flange_height, flange_length, bolt_size, n_bolts, b_star):
    # process =======================================================
    # get bolt constants

    # steel materials
    bolt_steel = BoltMaterialLibrary.create(bolt_steel_grade)
    flange_steel = SteelMaterial(flange_steel_grade, flange_height)
    tower_wall_steel = SteelMaterial(tower_steel_grade, wall_thickness)

    bolt_obj = BoltLibrary.create(bolt_size, bolt_steel)
    bolt_obj.calculate_yielding_bolt_force()  # for F_tR
    # print("Bolt preload currently set using 0.7 x ultimate bolt strength... could be wrong and maybe use yield instead??")
    bolt_tensioner_tool = BoltTensionerLibrary.create(bolt_size)

    # flange geometry and bolt data
    flange_obj = BoltedFlange(outer_diameter, wall_thickness, flange_height, flange_length, bolt_tensioner_tool, bolt_obj, flange_steel, tower_wall_steel,
                              ULS_bending_moment, ULS_axial_force, n_bolts, b_star)
    flange_obj.geometry_validity_check(maintain_a_b_ratio_1_25)

    if not flange_obj.valid_geom: # penalises the geometry
        #print("invalid geom")
        return flange_obj

    flange_obj.calc_flange_plastic_hinge_resistance()
    if not flange_obj.Fu_convergence:
        #print("non convergence")
        return flange_obj

    flange_obj.calc_bolted_connection_failure_modes()
    flange_obj.calc_util()
    util = flange_obj.util
    #print("Util: ", util)
    return flange_obj

def flange_searching_geometry(outer_diameter, wall_thickness, bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                              ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                              target_util,
                              flange_height_min, flange_height_max,
                              flange_length_min, flange_length_max, incrs
                              ):

    # searching....
    print("==================================================")
    print("==============Optimising==========================")
    print("==================================================")
    bolt_sizes = list(BoltLibrary._bolts.keys())
    bolt_sizes.sort(key=lambda x: int(x[1:]))  # removes 'M' prefix
    print("Finding optimal geometry for the following bolt sizes: ", bolt_sizes)
    geom_acceptable = {}
    for bolt_size in bolt_sizes:
        print(f"Searching for flange geometries for bolt size: {bolt_size}...")
        geom_acceptable[bolt_size] = {}
        counter = 0  # new counter for each bolt size
        for flange_height in np.arange(flange_height_min, flange_height_max, incrs):
            for flange_length in np.arange(flange_length_min, flange_length_max, incrs):

                # call the strength check func and suppress all prints temporarily
                with open(os.devnull, "w") as fnull:
                    with redirect_stdout(fnull):
                        flange_obj = bolt_connection_uls_strength_check(outer_diameter, wall_thickness,
                                       bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                       ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                                       flange_height, flange_length, bolt_size
                                                                  )

                        util = flange_obj.util


                if util <= target_util:
                    geom_dict = {"flange_area": flange_height * flange_length, "flange_height": flange_height,
                        "flange_length": flange_length, "util": round(util, 3)
                    }
                    geom_acceptable[bolt_size][f"{bolt_size}_geom_{counter}"] = geom_dict
                    counter += 1

        # If we found at least one feasible geometry for this bolt, stop checking larger bolts
        if geom_acceptable[bolt_size]:
            print(f"Feasible geometries found for bolt {bolt_size}, skipping larger bolts.")
            break

    # Optional: sort geometries by area and keep top N
    optimal_res = {}
    for bolt_size, geoms in geom_acceptable.items():
        if geoms:
            # sort by area
            sorted_geoms = dict(sorted(geoms.items(), key=lambda item: item[1]["flange_area"]))
            top_geoms = dict(list(sorted_geoms.items())[:5])  # keep top 5
            optimal_res[bolt_size] = top_geoms

    if optimal_res:
        print(f"Optimal geometries for smallest feasible bolt {bolt_size}:")
        pprint(optimal_res[bolt_size])
    else:
        print("Flange design for the given inputs can not be found! Exiting!")

    return optimal_res




if __name__ == "__main__":
    # Inputs =======================================================
    # foundation geometry
    outer_diameter = 7500
    wall_thickness = 100
    bolt_steel_grade = "10.9"
    flange_steel_grade = "355"
    tower_steel_grade = "355"
    # loading
    ULS_axial_force = 17.305e6 # N above the flange
    ULS_bending_moment = 557e9 # Nmm

    # Inputs to optimise =======================================================
    # design inputs to optimise
    bolt_size = "M90"  # options ["M72", "M80", "M90"] M72 is optimal compared to M90
    flange_height = 200  # in z
    flange_length = 400  # radial length
    maintain_a_b_ratio_1_25 = True # keep to stricter geom

    flange_obj = bolt_connection_uls_strength_check(outer_diameter, wall_thickness,
                                       bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                       ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                                       flange_height, flange_length, bolt_size)

    # user inputs for optimising
    incrs = 5  # search every 5mm increment size
    flange_height_min, flange_height_max = 50, 500
    flange_length_min, flange_length_max = wall_thickness + 10, 1500
    target_util = 0.95

    flange_searching_geometry(outer_diameter, wall_thickness, bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                              ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                              target_util,
                              flange_height_min, flange_height_max,
                              flange_length_min, flange_length_max, incrs
                              )





