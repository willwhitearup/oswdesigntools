from flask import request, render_template, flash
import numpy as np

from routing.core import create_plot



def ty_joint_route():
    return render_template('ty_joint.html')