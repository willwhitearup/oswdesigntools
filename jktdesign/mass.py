from dataclasses import dataclass
from typing import Optional
from jktdesign.jacket import Jacket
import numpy as np
import pandas as pd
from dataclasses import asdict
import re

class JacketMassCalculator:

    rho = 7.85e-9  # steel density in tonnes/mm³

    def __init__(self, jacket: Jacket):
        self.jacket = jacket

        # get the different section types from the jacket obj
        self.joint_objs = self.jacket.joint_objs
        self.leg_objs = self.jacket.leg_objs
        self.brace_a_objs = self.jacket.brace_a_objs
        self.brace_b_objs = self.jacket.brace_b_objs
        self.brace_hz_objs = self.jacket.brace_hz_objs

        ### calculate and store the masses
        # leg sections (incl. kjt Cans)
        self.k_joint_can_mass_objs = []
        self.leg_section_mass_objs = []  # leg masses
        # bay braces (includes, kjt stubs, brace sections and the xjts)
        self.x_brace_section_mass_objs = []  # x brace masses
        self.x_joint_can_mass_objs = []  # x jt Cans
        self.x_joint_stub_mass_objs = []  # x jt stubs
        self.k_joint_stub_mass_objs = []  # k jt stubs
        self.hz_brace_mass_objs = []  # hz braces

        # call the methods
        self._compute_k_joint_can_masses()
        self.compute_leg_section_masses()
        # x bay braces
        self._compute_bay_brace_masses()
        self._compute_x_joint_masses()
        self._compute_k_joint_stub_masses()
        self._compute_hz_brace_masses()


        self.leg_mass_objs = (
                self.k_joint_can_mass_objs +
                self.leg_section_mass_objs)


        self.bay_mass_objs =  (self.x_brace_section_mass_objs +
                self.x_joint_can_mass_objs +
                self.x_joint_stub_mass_objs +
                self.k_joint_stub_mass_objs +
                self.hz_brace_mass_objs)

        # store in convenient df
        self.df = None
        self._create_df_masses()

        # todo testing
        # k jts
        # for obj in self.joint_can_mass_objs:
        #     print(obj.name, obj.mass)
        # leg sections
        # for obj in self.leg_section_masses:
        #     print(obj.name, obj.mass)
        # for obj in self.x_brace_section_masses:
        #     print(obj.name, obj.mass)
        # for obj in self.x_joint_can_mass_objs:
        #     print(obj.name, obj.mass)

    def _compute_k_joint_can_masses(self):
        for joint in self.joint_objs:
            if joint.mirror or joint.jt_type != "kjt":
                continue  # only k jts on 1 of the legs required for mto
            Dc, thk = joint.Dc, joint.tc
            if not joint.kinked_can:  # hollow straight tubular volume
                vol = JacketMassCalculator.hollow_frustum_volume(Dc, joint.can_length, thk)
                chs_mass_obj = MassSection(name=f"{joint.jt_name}", mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=Dc, thickness=thk, length=joint.can_length, od_bottom=None)
                self.k_joint_can_mass_objs.append(chs_mass_obj)
            else:
                pt_kink = joint.pt_kink  # kinked tubular volume
                [vol1, vol2] = JacketMassCalculator.kinked_pipe_volume(joint.can_pt_top, pt_kink, joint.can_pt_btm, Dc, thk)
                for idx, vol in enumerate([vol1, vol2]):
                    pt1 = joint.can_pt_top if idx == 0 else joint.can_pt_btm
                    can_length = np.linalg.norm(np.array(pt1) - np.array(pt_kink))
                    chs_mass_obj = MassSection(name=f"{joint.jt_name}_section_{idx + 1}", mass=vol * JacketMassCalculator.rho,
                                                outer_diameter=Dc, thickness=thk, length=can_length, od_bottom=None)

                    self.k_joint_can_mass_objs.append(chs_mass_obj)

    def compute_leg_section_masses(self):

        for leg_obj in self.leg_objs:
            if leg_obj.mirror or leg_obj.member_type != "LEG":
                continue  # skip mirror sections
            # section properties
            thk, width1, width2 = leg_obj.thk, leg_obj.width1, leg_obj.width2
            if leg_obj.is_cone:
                cone_length = leg_obj.cone_length
                chs_mass_obj = JacketMassCalculator.make_mass_section(f"{leg_obj.leg_name}_cone", width1, cone_length, thk, d2=width2)
                self.leg_section_mass_objs.append(chs_mass_obj)

            # now get leg_a and leg_b volumes and associated lengths
            vols_a, lengths_a = JacketMassCalculator.calculate_leg_volume(leg_obj.leg_a, width1, thk)
            vols_b, lengths_b = JacketMassCalculator.calculate_leg_volume(leg_obj.leg_b, width2, thk)

            for aidx, vol in enumerate(vols_a):
                chs_mass_obj = MassSection(name=f"{leg_obj.leg_name}_section_{aidx + 1}", mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=width1, thickness=thk, length=lengths_a[aidx], od_bottom=None)
                self.leg_section_mass_objs.append(chs_mass_obj)

            for bidx, vol in enumerate(vols_b):
                chs_mass_obj = MassSection(name=f"{leg_obj.leg_name}_section_{bidx + aidx + 2}", mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=width2, thickness=thk, length=lengths_b[bidx], od_bottom=None)
                self.leg_section_mass_objs.append(chs_mass_obj)

    def _compute_bay_brace_masses(self):
        brace_a_section_masses = JacketMassCalculator.bay_brace_mass_calculator(self.brace_a_objs, bay_brace_loc="top")
        brace_b_section_masses = JacketMassCalculator.bay_brace_mass_calculator(self.brace_b_objs, bay_brace_loc="btm")
        self.x_brace_section_mass_objs.extend(brace_a_section_masses)
        self.x_brace_section_mass_objs.extend(brace_b_section_masses)

    def _compute_x_joint_masses(self):
        """calculate xjt Can and stub masses
        """
        # x joints
        for joint in self.joint_objs:
            if joint.jt_type != "xjt":
                continue  # only k jts on 1 of the legs required for mto
            Dc, thk = joint.Dc, joint.tc  # joint Can diameter and thickness
            vol = JacketMassCalculator.hollow_frustum_volume(Dc, joint.can_length, thk)
            chs_mass_obj = MassSection(name=f"{joint.jt_name}", mass=vol * JacketMassCalculator.rho,
                                       outer_diameter=Dc, thickness=thk, length=joint.can_length, od_bottom=None)
            self.x_joint_can_mass_objs.append(chs_mass_obj)
            d1, t1 = joint.d1, joint.t1  # joint stub diameter and thickness
            d2, t2 = joint.d2, joint.t2  # joint stub diameter and thickness  # not used currently
            for idx, (k, v) in enumerate(joint.stub_end_pts.items()):
                start_pts = joint.stub_start_pts[k]
                distance = np.linalg.norm(np.array(v) - np.array(start_pts))
                vol = JacketMassCalculator.hollow_frustum_volume(d1, distance, t1)
                stub_name = f"{joint.jt_name}_stub_{idx+1}"
                chs_mass_obj = MassSection(name=stub_name, mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=d1, thickness=t1, length=distance, od_bottom=None)
                self.x_joint_stub_mass_objs.append(chs_mass_obj)

    def _compute_k_joint_stub_masses(self):
        """calculate kjt stub masses
        """
        for joint in self.joint_objs:
            if joint.mirror or joint.jt_type != "kjt":
                continue  # only k jts on 1 of the legs required for mto
            # we need the stubs from BOTH leg kjts, as here we are calculating the mass of the bay braces
            ds_ts = [(joint.d1, joint.t1), (joint.d2, joint.t2), (joint.d3, joint.t3)]
            for idx, (k, v) in enumerate(joint.stub_end_pts.items()):
                start_pts = joint.stub_start_pts[k]
                distance = np.linalg.norm(np.array(v) - np.array(start_pts))
                d, t = ds_ts[idx]
                vol = JacketMassCalculator.hollow_frustum_volume(d, distance, t)
                # create names
                stub_name_a = f"{joint.jt_name}_stub_{idx+1}_leg_a"
                stub_name_b = f"{joint.jt_name}_stub_{idx+1}_leg_b"
                # create mass objs for stubs on either side of the bay (i.e. attached to each leg)
                chs_mass_obj_a = MassSection(name=stub_name_a, mass=vol*JacketMassCalculator.rho,
                                           outer_diameter=d, thickness=t, length=distance, od_bottom=None)
                chs_mass_obj_b = MassSection(name=stub_name_b, mass=vol*JacketMassCalculator.rho,
                                           outer_diameter=d, thickness=t, length=distance, od_bottom=None)
                # store the mass objs
                self.k_joint_stub_mass_objs.append(chs_mass_obj_a)
                self.k_joint_stub_mass_objs.append(chs_mass_obj_b)

    def _compute_hz_brace_masses(self):
        """calculate hz_brace_masses
        """
        for brace_hz_obj in self.brace_hz_objs:
            # section properties
            thk, width1, width2 = brace_hz_obj.thk, brace_hz_obj.width1, brace_hz_obj.width2
            # now get leg_a and leg_b volumes and associated lengths
            distance = np.linalg.norm(np.array(brace_hz_obj.pts[1]) - np.array(brace_hz_obj.pts[0]))
            vol = JacketMassCalculator.hollow_frustum_volume(width1, distance, thk)
            chs_mass_obj = MassSection(name=f"{brace_hz_obj.leg_name}_hz", mass=vol * JacketMassCalculator.rho,
                                       outer_diameter=width1, thickness=thk, length=distance, od_bottom=None)
            self.hz_brace_mass_objs.append(chs_mass_obj)

    @staticmethod
    def bay_brace_mass_calculator(brace_objs, bay_brace_loc="top"):
        """brace a sections go in descending order from k- down to x-joints. e.g. bay 1 brace a sections go from
        k1 to x1

            "_aL" is lhs brace at top of bay going to x stub.
            _aR" is rhs at top of bay going to x Can.
        """
        x_brace_section_masses = []
        for brace_obj in brace_objs:
            brace_name = brace_obj.leg_name
            bay_no = "_".join(brace_name.split("_")[:2])
            side = "left" if "L" in brace_name else "right"
            easy_name = f"{bay_no}_{bay_brace_loc}_{side}"

            thk, width1, width2 = brace_obj.thk, brace_obj.width1, brace_obj.width2

            if brace_obj.is_cone:
                cone_length = brace_obj.cone_length
                chs_mass_obj = JacketMassCalculator.make_mass_section(f"{brace_obj.leg_name}_cone", width1, cone_length, thk, d2=width2)
                x_brace_section_masses.append(chs_mass_obj)

            vols_a, lengths_a = JacketMassCalculator.calculate_leg_volume(brace_obj.leg_a, width1, thk)
            vols_b, lengths_b = JacketMassCalculator.calculate_leg_volume(brace_obj.leg_b, width2, thk)

            for aidx, vol in enumerate(vols_a):
                chs_mass_obj = MassSection(name=f"{easy_name}_section_{aidx + 1}", mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=width1, thickness=thk, length=lengths_a[aidx], od_bottom=None)
                x_brace_section_masses.append(chs_mass_obj)

            for bidx, vol in enumerate(vols_b):
                chs_mass_obj = MassSection(name=f"{easy_name}_section_{bidx + aidx + 2}", mass=vol * JacketMassCalculator.rho,
                                           outer_diameter=width2, thickness=thk, length=lengths_b[bidx], od_bottom=None)
                x_brace_section_masses.append(chs_mass_obj)
        return x_brace_section_masses

    @staticmethod
    def calculate_leg_volume(leg_pts, width, thk):
        vol_list, lengths_list = [], []
        if leg_pts:
            if len(leg_pts) == 3:
                pt1, pt2, pt3 = leg_pts
                p1, p2, p3 = map(np.array, (pt1, pt2, pt3))
                v1, v2 = p2 - p1, p3 - p2
                L1, L2 = np.linalg.norm(v1), np.linalg.norm(v2)
                vols = JacketMassCalculator.kinked_pipe_volume(pt1, pt2, pt3, width, thk)
                vol_list.extend(vols)
                lengths_list.extend([L1, L2])
            elif len(leg_pts) == 2:
                pt1, pt2 = leg_pts
                p1, p2 = map(np.array, (pt1, pt2))
                L1 = np.linalg.norm(p2 - p1)
                vol = JacketMassCalculator.hollow_frustum_volume(width, L1, thk)
                vol_list.append(vol)
                lengths_list.append(L1)

        return vol_list, lengths_list

    @staticmethod
    def make_mass_section(name, od, length, thk, d2=None):
        vol = JacketMassCalculator.hollow_frustum_volume(od, length, thk, d2=d2)
        return MassSection(name=name, mass=vol * JacketMassCalculator.rho, outer_diameter=od, thickness=thk, length=length, od_bottom=d2)

    @staticmethod
    def hollow_frustum_volume(d1: float, length: float, tw: float, d2: float = None) -> float:
        """Calculate the volume of a hollow conical frustum or cylindrical shell.

        Parameters:
            d1 (float): Outer diameter at one end.
            length (float): Axial or slant height of the frustum.
            tw (float): Constant wall thickness.
            d2 (float, optional): Outer diameter at the other end. Defaults to d1 (cylinder).

        Returns: Volume of the hollow frustum.
        """
        d2 = d1 if d2 is None else d2
        R1, R2 = d1 / 2, d2 / 2
        r1, r2 = R1 - tw, R2 - tw
        if r1 <= 0 or r2 <= 0:
            raise ValueError("Wall thickness too large.")
        vol = (np.pi * length / 3) * (R1 ** 2 + R1 * R2 + R2 ** 2 - r1 ** 2 - r1 * r2 - r2 ** 2)
        return vol

    @staticmethod
    def kinked_pipe_volume(pt1, pt2, pt3, outer_diameter, thk):
        """calculate volume of a kinked pipe with constant OD and thickness. Includes volume of the mitered joint
        pt1 and pt3 are the end points
        pt2 is the intermediate point where the kink angle exists
        """
        p1, p2, p3 = map(np.array, (pt1, pt2, pt3))
        v1, v2 = p2 - p1, p3 - p2
        L1, L2 = np.linalg.norm(v1), np.linalg.norm(v2)
        v1u, v2u = v1 / L1, v2 / L2
        theta = np.arccos(np.clip(np.dot(v1u, v2u), -1.0, 1.0))
        r1, r2 = outer_diameter / 2, outer_diameter / 2 - thk
        A = np.pi * (r1 ** 2 - r2 ** 2)
        r_mean = (r1 + r2) / 2
        V_miter = A * r_mean * np.tan(theta / 2)
        vol1, vol2 = A * L1 - 0.5 * V_miter, A * L2 - 0.5 * V_miter
        return [vol1, vol2]

    def _create_df_masses(self):
        # Add section_str column data for legs
        section_str_leg = [m.section_str() for m in self.leg_mass_objs]
        self.df_leg = pd.DataFrame([asdict(m) for m in self.leg_mass_objs])
        self.df_leg["section"] = section_str_leg
        self.df_leg["location"] = "LEG"

        # Add section_str column data for bays
        section_str_bay = [m.section_str() for m in self.bay_mass_objs]
        self.df_bay = pd.DataFrame([asdict(m) for m in self.bay_mass_objs])
        self.df_bay["section"] = section_str_bay
        self.df_bay["location"] = self.df_bay["name"].apply(
            lambda name: ((m := re.search(r"_\d+", name)) and f"BAY{m.group()}") or "UNKNOWN"
        )
        self.df_bay = self.df_bay.sort_values(by="location").reset_index(drop=True)

        # Combine and reorder columns
        self.df = pd.concat([self.df_leg, self.df_bay], ignore_index=True)
        cols = [col for col in self.df.columns if col not in ("location", "mass")]
        self.df = self.df[["location"] + cols + ["mass"]]

        self.df = self.df.rename(columns={"mass": "unit mass [t]",
                                          "length": "length [mm]",
                                          "outer_diameter": "od_top [mm]",
                                          "thickness": "thickness [mm]",
                                          "od_bottom": "od_bottom [mm]"
                                          })

        # round
        self.df[["length [mm]", "unit mass [t]"]] = self.df[["length [mm]", "unit mass [t]"]].round(3)

        # Export to CSV without index
        # self.df.to_csv(r"C:\Users\Will.White\Python\website\test.csv", index=False, encoding="utf-8-sig")

#
def calculate_jkt_mto(jkt_obj: Jacket):
    jm_obj = JacketMassCalculator(jkt_obj)
    df_mto = jm_obj.df
    return df_mto





@dataclass
class MassSection:
    name: str
    mass: float        # in tonnes
    outer_diameter: float  # OD or top OD in mm
    thickness: float   # wall thickness in mm
    length: float      # in mm
    od_bottom: Optional[float] = None  # bottom OD for conical, None if CHS

    def __post_init__(self):
        if self.od_bottom is None:
            self.od_bottom = self.outer_diameter

    def section_str(self) -> str:
        if self.od_bottom != self.outer_diameter:
            return f"ConicalCHS({self.outer_diameter:.0f}→{self.od_bottom:.0f}, {self.thickness:.0f})"
        return f"CHS({self.outer_diameter:.0f}, {self.thickness:.0f})"

