from flask import request, render_template, flash

def home():
    return render_template('home.html')
