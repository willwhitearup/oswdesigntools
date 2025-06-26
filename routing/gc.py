from flask import request, render_template, flash

def gc_route():
    return render_template('gc.html')

def joint_detailing():
    return render_template('joint_detailing.html')