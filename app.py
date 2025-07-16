import os
from flask import Flask, render_template, session
from jktdesign.architect import jacket_architect
from jktdesign.jktsections import jacket_sections, jacket_sections_plot
from mto.mto import gen_mto
from routing.routes_home import home
from routing.routes_kjoint import k_joint_route
from routing.routes_xjoint import x_joint_route
from routing.routes_tyjoint import ty_joint_route
from routing.routes_ktjoint import kt_joint_route
from routing.jointdetailing_route import joint_detailing
from gcdesign.gc_route import gc_route

# initialise app variable for Flask obj
app = Flask(__name__, template_folder='templates', static_folder='static')
#app.secret_key = os.environ.get('SECRET_KEY')  # Get the secret key from environment variables
app.secret_key = 'your_secret_key_here'


# register routes
app.add_url_rule('/', 'home', home)
# architect and sections routing
app.add_url_rule('/architect', 'architect', jacket_architect, methods=['GET', 'POST'])
app.add_url_rule('/jktsections', 'jacket_sections', jacket_sections, methods=['GET'])
app.add_url_rule('/jktsections', 'jacket_sections_plot', jacket_sections_plot, methods=['POST'])
# mto routing
app.add_url_rule('/mto', 'gen_mto', gen_mto, methods=['GET', 'POST'])
# scf routing
app.add_url_rule('/k_joint', 'k_joint', k_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/x_joint', 'x_joint', x_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/ty_joint', 'ty_joint', ty_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/kt_joint', 'kt_joint', kt_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/joint_detailing', 'joint_detailing', joint_detailing, methods=['GET', 'POST'])
# gc routing
app.add_url_rule('/gc', 'gc_route', gc_route, methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(debug=True)