import os
from flask import Flask
from main.routes_home import home
from main.routes_kjoint import k_joint_route
from main.routes_xjoint import x_joint_route
from main.placeholder import placeholder_route

# initialise app variable for Flask obj
app = Flask(__name__, template_folder='templates', static_folder='static')
#app.secret_key = os.environ.get('SECRET_KEY')  # Get the secret key from environment variables
app.secret_key = 'your_secret_key_here'

# register routes
app.add_url_rule('/', 'home', home)
app.add_url_rule('/k_joint', 'k_joint', k_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/x_joint', 'x_joint', x_joint_route, methods=['GET', 'POST'])
app.add_url_rule('/placeholder', 'placeholder', placeholder_route)


if __name__ == '__main__':
    app.run(debug=True)