from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import *
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.LoginPage'
#WTFforms through flask not available for codemirror 6 just codemirror 5 so doing CSRF by adding it as hidden to post 
csrf = CSRFProtect()

#using isTest as a bool because using the config object could not be resolved on cmd line
def create_app(isTest=False):
   app = Flask(__name__)  
   if isTest:
      app.config.from_object(TestConfig)
   else:
      app.config.from_object(DeploymentConfig)
   
   db.init_app(app)  
   csrf.init_app(app)
   migrate.init_app(app, db, render_as_batch=True)
   login_manager.init_app(app)

   from app.routes import main as main_bp
   app.register_blueprint(main_bp)

   from app.auth import auth as auth_bp
   app.register_blueprint(auth_bp)
   
   #for testing configuration, set up db and add testing values
   if isTest:
      with app.app_context():
         from app.models import User, Question, Difficulty
         db.create_all()
         db.session.add(User(
            username="TestUser",
            password_hash=generate_password_hash("Password")
         ))
         db.session.add(Question(
            title="TestQuestion Return Factorial",
            short_desc= "Return the factorial of N",
            full_desc= "Create a function that takes integer N and returns N! or N factorial.",
            difficulty= Difficulty.EASY,
            test_cases= r"{(0):1, (3):6, (1):1, (10):3628800}",
            author_id=0,
         ))
         db.session.commit()
   return app
