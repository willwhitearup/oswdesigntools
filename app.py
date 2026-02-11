import os
from flask import Flask, render_template, session
from jktdesign.architect import jacket_architect
from jktdesign.jktsections import jacket_sections, jacket_sections_plot
from mto.mto import gen_mto
from tubularjointscfs.routes_home import home
from tubularjointscfs.routes_kjoint import k_joint_route
from tubularjointscfs.routes_xjoint import x_joint_route
from tubularjointscfs.routes_tyjoint import ty_joint_route
from tubularjointscfs.routes_ktjoint import kt_joint_route
from tubularjointscfs.jointdetailing_route import joint_detailing
from gcdesign.gc_route import gc_route
from kitesurf.kitesurf_route import kitesurf_route
from conicalscfs.conical_route import conical_route


# initialise app variable for Flask obj
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key_here'


# register routes
app.add_url_rule('/', 'home', home)
# architect and sections tubularjointscfs
app.add_url_rule('/architect', 'architect', jacket_architect, methods=['GET', 'POST'])
app.add_url_rule('/jktsections', 'jacket_sections', jacket_sections, methods=['GET'])
app.add_url_rule('/jktsections', 'jacket_sections_plot', jacket_sections_plot, methods=['POST'])
# mto tubularjointscfs
app.add_url_rule('/mto', 'gen_mto', gen_mto, methods=['GET', 'POST'])
# scf tubularjointscfs
app.add_url_rule('/k_joint', 'k_joint', k_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/x_joint', 'x_joint', x_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/ty_joint', 'ty_joint', ty_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/kt_joint', 'kt_joint', kt_joint_route, methods=['GET', 'POST'])
# conicals TODO
app.add_url_rule('/conicalscfs', 'conical_route', conical_route, methods=['GET', 'POST'])

app.add_url_rule('/joint_detailing', 'joint_detailing', joint_detailing, methods=['GET', 'POST'])
# gc tubularjointscfs
app.add_url_rule('/gc', 'gc_route', gc_route, methods=['GET', 'POST'])
# kitesurf
app.add_url_rule('/kitesurf', 'kitesurf_route', kitesurf_route, methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(debug=True)
