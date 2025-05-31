from flask import render_template, Flask

app = Flask(__name__)

@app.route('/mto', methods=['GET', 'POST'])
def gen_mto():
    return render_template('mto.html')