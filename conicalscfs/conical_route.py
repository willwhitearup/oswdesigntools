from flask import Flask, render_template, flash, jsonify, request, session


app = Flask(__name__)

@app.route('/gc', methods=['GET', 'POST'])
def conical_route():
    return render_template('conicalscfs.html')