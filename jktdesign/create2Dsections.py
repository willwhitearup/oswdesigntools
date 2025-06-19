from collections import defaultdict

from jktdesign.joint import Joint2D
from jktdesign.leg import Leg


def get_kjt_geom_form_data(form_data):
    """get the K joint section data from the form data
    """
    kjt_geom_data = defaultdict(lambda: {})
    for k, v in form_data.items():
        kjt_id = k.split("_")
        if kjt_id[0] == "kjt":
            kjt_no_all = "_".join(kjt_id[:2])
            kdata = "_".join(kjt_id[2:])
            try:
                val = float(v)
            except ValueError:
                val = None
            kjt_geom_data[kjt_no_all][kdata] = val
    return kjt_geom_data

def get_xjt_geom_form_data(form_data):
    """get the X joint section data from the form data
    """
    xjt_geom_data = defaultdict(lambda: {})
    for k, v in form_data.items():
        xjt_id = k.split("_")
        if xjt_id[0] == "xjt":
            xjt_no_all = "_".join(xjt_id[:2])
            xdata = "_".join(xjt_id[2:])
            try:
                val = float(v)
            except ValueError:
                val = None
            xjt_geom_data[xjt_no_all][xdata] = val
    return xjt_geom_data

def get_leg_geom_form_data(form_data):
    leg_geom_data = defaultdict(lambda: {})
    for k, v in form_data.items():
        leg_id = k.split("_")
        if leg_id[0] == "leg":
            leg_no_all = "_".join(leg_id[:2])
            legdata = "_".join(leg_id[2:])
            leg_geom_data[leg_no_all][legdata] = float(v)
    return leg_geom_data

def get_brace_geom_form_data(form_data):
    brace_geom_data = defaultdict(lambda: {})
    brace_hz_geom_data = defaultdict(lambda: {})
    for k, v in form_data.items():
        brace_id = k.split("_")
        if brace_id[0] == "bay" and "hz" not in k:
            brace_no_all = "_".join(brace_id[:2])
            bracedata = "_".join(brace_id[2:])
            brace_geom_data[brace_no_all][bracedata] = float(v)

        # get horizontal brace bay data
        elif brace_id[0] == "bay" and "hz" in k:
            bay_no = brace_id[2]
            bracedata = brace_id[-1]
            if len(v) > 0:
                brace_hz_geom_data[f"bay_{bay_no}"][bracedata] = float(v)

    return brace_geom_data, brace_hz_geom_data

def create_2D_kjoint_data(kjt_geom_data, diameter_def="ID"):
    jnt_objs = []
    for k, v in kjt_geom_data.items():
        # extract data from form
        Dc = v['can_d']
        tc = v["can_t"]
        d1 = v["stub_1_d"]
        t1 = v["stub_1_t"]
        d2 = v["stub_2_d"]
        t2 = v["stub_2_t"]
        d3 = v["stub_3_d"]
        t3 = v["stub_3_t"]

        if diameter_def == "ID":
            Dc_OD, d1_OD = Dc + tc, d1+t1,
            d2_OD = d2 + t2 if d2 is not None else None
            d3_OD = d3 + t3 if d3 is not None else None
        else:
            print("todo")
        # create the Joint object and store
        jnt_obj = Joint2D(Dc_OD, tc, # Joint and stubs are defined as D and d as their ODs
                          d1_OD, t1,
                          d2=d2_OD, t2=t2,
                          d3=d3_OD, t3=t3,
                          jt_name=k, jt_type="kjt")
        jnt_objs.append(jnt_obj)
    return jnt_objs

def create_2D_xjoint_data(xjt_geom_data, diameter_def="ID"):
    jnt_objs = []
    for k, v in xjt_geom_data.items():
        Dc = v['can_d']
        tc = v["can_t"]
        d1 = v["stub_d"]
        t1 = v["stub_t"]
        if diameter_def == "ID":
            Dc_OD, d1_OD = Dc + tc, d1+t1
        else:
            print("todo")
        jnt_obj = Joint2D(Dc_OD, tc, d1_OD, t1, d2=d1_OD, t2=t1, jt_name=k, jt_type="xjt")
        jnt_objs.append(jnt_obj)
    return jnt_objs

def create_2D_leg_data(leg_geom_data, kjt_geom_data, diameter_def="ID"):
    """create Leg object from the leg_geom_data and kjt_geom_data (i.e. from app form)
    Args:
        leg_geom_data: dict, see above
        kjt_geom_data: dict, see above

    Returns:
        leg_objs: list, of Leg objects (initialised only)
    """
    leg_objs = []
    last_leg_section = False
    for idx, (k, v) in enumerate(leg_geom_data.items()):
        if idx == len(leg_geom_data) - 1:
            last_leg_section = True  # on last leg section, there is only a Kjt below it (and then pile top)
        leg_no = int(k.split("_")[1])
        thk1 = v["t"]  # leg thickness
        # get leg diameter from the k_jt diameter ABOVE leg section
        for kk, vv in kjt_geom_data.items():
            kjt_no = int(kk.split("_")[1])
            # get kjt data from kjoint above the leg section
            kflag = False
            if kjt_no == leg_no:
                width1 = vv['can_d']
                kflag = True
                break
        # get leg diameter from the k_jt diameter BELO leg section
        if kflag:
            if last_leg_section:  # for the leg section below the bottom k joint (just above top of pile)
                width2 = width1
            else:
                # get kjt data from kjoint above the leg section
                width2 = kjt_geom_data[f"kjt_{kjt_no + 1}"]['can_d']
        # create the object and store
        if diameter_def == "ID":
            leg1_OD, leg2_OD = width1 + thk1, width2 + thk1
        else:
            print("todo")
        leg_obj = Leg(width1=leg1_OD, width2=leg2_OD, thk=thk1, leg_name=k, member_type="LEG")
        leg_objs.append(leg_obj)
    return leg_objs

def create_2D_brace_a_data(brace_geom_data, kjt_geom_data, xjt_geom_data, diameter_def="ID"):
    """create Leg object for an x brace from the leg_geom_data and kjt_geom_data (i.e. from app form)


    brace_a bay braces are in the top half of the x bay. start from a K joint and descend in elevation to the stub of the X joint

    brace a L is left side brace in bay top half
    brace a R is right side brace in bay top half

    Args:
        brace_geom_data: dict, see above
        kjt_geom_data: dict, see above
        xjt_geom_data: dict, see above

    Returns:
        brace_objs: list, of Leg objects (initialised only)
    """
    brace_objs = []
    for bay_name, v in brace_geom_data.items():
        brace_no = int(bay_name.split("_")[1])
        brace_thk = v["t"]
        # get k above
        for ka, va in kjt_geom_data.items():
            kjt_no = int(ka.split("_")[1])  # kjt number
            stub_1_d, stub_2_d, stub_3_d = va['stub_1_d'], va['stub_2_d'], va['stub_3_d']
            # Choose the first non-None value (priority: stub_3_d > stub_2_d > stub_1_d)
            k_stub_d = next(val for val in (stub_3_d, stub_2_d, stub_1_d) if val is not None)
            if kjt_no == brace_no:
                width1_aL = k_stub_d
                break

        # get x below - starting with stubs (go from top left k stub to right to x in construction of bay braces)
        for kb, vb in xjt_geom_data.items():
            xjt_no = int(kb.split("_")[1])  # xjt number
            can_d, stub_d = vb['can_d'], vb['stub_d']
            if xjt_no == brace_no:
                width2_aL, width2_aR = stub_d, can_d
                break

        # create the object and store
        if diameter_def == "ID":
            width1_aR = width1_aL
            brc1L_OD, brc2L_OD = width1_aL + brace_thk, width2_aL + brace_thk
            brc1R_OD, brc2R_OD = width1_aR + brace_thk, width2_aR + brace_thk
        else:
            print("todo")

        brace_obj = Leg(width1=brc1L_OD, width2=brc2L_OD, thk=brace_thk, leg_name=bay_name + "_aL", bay_side="L", member_type="BRC")
        brace_objs.append(brace_obj)

        # for the right side brace a, rename and give it the same width (diameter) as the other side L
        brace_obj = Leg(width1=brc1R_OD, width2=brc2R_OD, thk=brace_thk, leg_name=bay_name + "_aR", bay_side="R", member_type="BRC")
        brace_objs.append(brace_obj)

    return brace_objs


def create_2D_brace_b_data(brace_geom_data, kjt_geom_data, xjt_geom_data, diameter_def="ID"):
    """Create Leg objects for bay braces that descend from X joints to K joint stubs.
    Each bay contains two braces: left (bL) and right (bR).
    """
    brace_objs = []
    for bay_name, v in brace_geom_data.items():
        brace_no = int(bay_name.split("_")[1])
        brace_thk = v["t"]
        # Get geometry from corresponding X-joint
        for kb, vb in xjt_geom_data.items():
            if int(kb.split("_")[1]) == brace_no:
                width1_bL, width1_bR = vb["can_d"], vb["stub_d"]
                break
        # Get geometry from corresponding K-joint (one index below)
        for ka, va in kjt_geom_data.items():
            kjt_no = int(ka.split("_")[1])
            if kjt_no == brace_no + 1:
                # top stub of the corresponding kjt
                k_stub_d = next(val for val in (va.get("stub_1_d"), va.get("stub_2_d"), va.get("stub_2_d")) if val is not None)
                width2_bL = width2_bR = k_stub_d  # Use same thickness for both ends of brace
                break

        # create the object and store
        if diameter_def == "ID":
            brc1L_OD, brc2L_OD = width1_bL + brace_thk, width2_bL + brace_thk
            brc1R_OD, brc2R_OD = width1_bR + brace_thk, width2_bR + brace_thk
        else:
            print("todo")

        # Create left-side brace
        brace_objs.append(Leg(width1=brc1L_OD, width2=brc2L_OD, thk=brace_thk, leg_name=bay_name + "_bL", bay_side="L", member_type="BRC"))
        # Create right-side brace
        brace_objs.append(Leg(width1=brc1R_OD, width2=brc2R_OD, thk=brace_thk, leg_name=bay_name + "_bR", bay_side="R", member_type="BRC"))

    return brace_objs


def create_2D_brace_hz_data(brace_hz_geom_data, kjt_geom_data, diameter_def="ID"):
    """create horizontal brace, which spans between k joints at same level e.g. k1 to k1
    """
    brace_hz_objs = []
    for bay_name, v in brace_hz_geom_data.items():
        bay_no = int(bay_name.split("_")[1])  # get bay number e.g. 1, 2 etc
        hz_t = v["t"]
        # get k below - starting with stubs (go from top left k stub to right to x in construction of bay braces)
        for ka, va in kjt_geom_data.items():
            kjt_no = int(ka.split("_")[1])  # kjt number
            if kjt_no == bay_no + 1:  # e.g. bay 2 horizontal attaches k3 (since k3 is at the bottom of the bay 2)
                stub_2_d = va['stub_2_d']
                break
        # hz braces defined from left to right
        if diameter_def == "ID":
            OD = stub_2_d + hz_t
        else:
            print("todo")

        brace_obj = Leg(width1=OD, width2=OD, thk=hz_t, leg_name=f"{bay_name}_hz", member_type="BRC")
        brace_hz_objs.append(brace_obj)

    return brace_hz_objs
