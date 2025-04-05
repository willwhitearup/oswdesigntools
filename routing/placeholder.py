from flask import request, render_template, flash

def placeholder_route():
    return render_template('placeholder.html')

def kt_joint_route():
    return render_template('kt_joint.html')

def butt_weld_mps_route():
    return render_template('butt_weld_mps.html')