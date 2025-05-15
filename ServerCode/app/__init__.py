from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import *
from app.SetupTags import createTags
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.LoginPage'

def create_app(isTest=False):
   app = Flask(__name__)  
   if isTest:
      app.config.from_object(TestConfig)
   else:
      app.config.from_object(DeploymentConfig)
   db.init_app(app)
   migrate.init_app(app, db, render_as_batch=True)
   login_manager.init_app(app)

   from app.routes import main as main_bp
   app.register_blueprint(main_bp)

   from app.auth import auth as auth_bp
   app.register_blueprint(auth_bp)
   
   if isTest:
      with app.app_context():
         db.create_all()
   return app



'''
run in a virtual env 
to install venv see pinned discord
create venv with `python -m virtualenv venv`
activate venv with `venv\scripts\activate`
adjust as needed depending on OS

run with `flask --app app run` or `flask run`
'''