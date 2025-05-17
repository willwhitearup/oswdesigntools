from collections import defaultdict

from jktdesign.joint import Joint2D


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
        kjt_id = k.split("_")
        if kjt_id[0] == "xjt":
            kjt_no_all = "_".join(kjt_id[:2])
            kdata = "_".join(kjt_id[2:])
            try:
                val = float(v)
            except ValueError:
                val = None
            xjt_geom_data[kjt_no_all][kdata] = val
    return xjt_geom_data


def create_2D_kjoint_data(kjt_geom_data): #, kjt_brace_angles, joint_gap=100):
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
        # create the Joint object and store
        jnt_obj = Joint2D(Dc, tc, d1, t1, d2=d2, t2=t2, d3=d3, t3=t3, jt_name=k)
        jnt_objs.append(jnt_obj)
    return jnt_objs

def create_2D_xjoint_data(xjt_geom_data):
    jnt_objs = []
    for k, v in xjt_geom_data.items():
        Dc = v['can_d']
        tc = v["can_t"]
        d1 = v["stub_d"]
        t1 = v["stub_t"]
        jnt_obj = Joint2D(Dc, tc, d1, t1, d2=d1, t2=t1, jt_name=k)
        jnt_objs.append(jnt_obj)

    return jnt_objs

