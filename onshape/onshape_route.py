"""Onshape live model viewer route."""

import io
import os

import requests

from flask import (
    abort,
    render_template,
    request,
    send_file,
)

BASE = os.environ.get(
    "ONSHAPE_BASE_URL",
    "https://cad.onshape.com"
)

AUTH = (
    os.environ.get("ONSHAPE_ACCESS_KEY"),
    os.environ.get("ONSHAPE_SECRET_KEY"),
)

# ------------------------------------------------------------------
# Supported CAD models
# ------------------------------------------------------------------

MODELS = {
    "strut": {
        "name": "STRUT",
        "did": "9afde97a2e476db5271e9ff1",
        "wid": "d0f1b93bd2a196643bf1b7f7",
        "eid": "6f8a1698d3b92ecdf31ce063",
    },

    "box1": {
        "name": "BOX_1",
        "did": "c6343cdf51c623039957b389",
        "wid": "90d92f93dfcbe4632267a00a",
        "eid": "8e500fc35b9e07e82a367a82",
    },
    "box2": {
        "name": "BOX_2",
        "did": "49c106ee9b984a0c36811d33",
        "wid": "89561cc03ce942c824124642",
        "eid": "c507d9665b85eaca79e04312",
    },
}

# ------------------------------------------------------------------
# Default slider values
# ------------------------------------------------------------------

DEFAULTS = {
    "leg_offset": 12000,
    "strut_angle": 47,
}

LIMITS = {
    "leg_offset": {
        "min": 2000,
        "max": 20000,
        "step": 100,
    },

    "strut_angle": {
        "min": 20,
        "max": 70,
        "step": 1,
    },
}


# ------------------------------------------------------------------
# Main page
# ------------------------------------------------------------------

def onshape_route():
    """GET /cad_tp_type1"""

    return render_template(
        "onshape/onshape.html",
        defaults=DEFAULTS,
        limits=LIMITS,
        models=MODELS,
        default_model="strut",
    )


# ------------------------------------------------------------------
# GLB endpoint
# ------------------------------------------------------------------

def onshape_model_glb():
    """GET /cad_tp_type1/model.glb?model=strut"""

    model_name = request.args.get(
        "model",
        "strut"
    ).lower()

    model = MODELS.get(model_name)

    if model is None:
        abort(
            404,
            f"Unknown model '{model_name}'"
        )

    if not all([
        AUTH[0],
        AUTH[1],
    ]):
        abort(
            500,
            "Onshape credentials not configured."
        )

    url = (
        f"{BASE}"
        f"/api/partstudios"
        f"/d/{model['did']}"
        f"/w/{model['wid']}"
        f"/e/{model['eid']}"
        f"/gltf"
    )

    response = requests.get(
        url,
        auth=AUTH,
        headers={
            "Accept": "model/gltf-binary"
        },
        timeout=60,
    )

    if response.status_code != 200:
        abort(
            response.status_code,
            response.text[:500]
        )

    return send_file(
        io.BytesIO(response.content),
        mimetype="model/gltf-binary",
        download_name=f"{model_name}.glb",
    )