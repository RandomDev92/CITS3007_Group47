from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager



app = Flask(__name__)  
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db, )
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'LoginPage'

if __name__=='__main__': 
   app.run(debug=True) 

from app import routes, models, auth

'''
run in a virtual env 
to install venv see pinned discord
create venv with `python -m virtualenv venv`
activate venv with `venv\scripts\activate`
adjust as needed depending on OS

run with `flask --app app run` or `flask run`
'''