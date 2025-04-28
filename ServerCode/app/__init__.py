from flask import Flask
from flash_migrate import Migrate
from flash_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)  
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

if __name__=='__main__': 
   app.run(debug=True) 

from app import routes, models
'''
run in a virtual env 
to install venv see pinned discord
create venv with `python -m virtualenv venv`
activate venv with `venv\scripts\activate`
adjust as needed depending on OS

run with `flask --app app run` or `flask run`
'''