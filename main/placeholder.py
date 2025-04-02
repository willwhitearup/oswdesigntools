from flask import request, render_template, flash

def placeholder_route():
    return render_template('placeholder.html')