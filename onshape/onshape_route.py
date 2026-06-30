"""Onshape live model viewer route — TP type 1."""

import io
import os
import requests
from flask import render_template, send_file, abort

BASE = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")
DID  = os.environ.get("ONSHAPE_DID")
WID  = os.environ.get("ONSHAPE_WID")
EID  = os.environ.get("ONSHAPE_EID")
AUTH = (os.environ.get("ONSHAPE_ACCESS_KEY"), os.environ.get("ONSHAPE_SECRET_KEY"))

DEFAULTS = {"leg_offset": 12000, "strut_angle": 47}
LIMITS = {
    "leg_offset":  {"min": 2000, "max": 20000, "step": 100},
    "strut_angle": {"min": 20,   "max": 70,    "step": 1},
}


def onshape_route():
    """GET /cad_tp_type1 — render the configurator page."""
    return render_template(
        "onshape/onshape.html",
        defaults=DEFAULTS,
        limits=LIMITS,
        doc_id=DID, wid=WID, eid=EID,
    )


def onshape_model_glb():
    """GET /cad_tp_type1/model.glb — default model thumbnail."""
    if not all([DID, WID, EID, AUTH[0], AUTH[1]]):
        abort(500, "Onshape env vars not set.")
    url = f"{BASE}/api/partstudios/d/{DID}/w/{WID}/e/{EID}/gltf"
    r = requests.get(url, auth=AUTH, headers={"Accept": "model/gltf-binary"})
    if r.status_code != 200:
        abort(r.status_code, r.text[:300])
    return send_file(
        io.BytesIO(r.content),
        mimetype="model/gltf-binary",
        download_name="model.glb",
    )