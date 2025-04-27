from flask import Flask     
app = Flask(__name__)  

if __name__=='__main__': 
   app.run(debug=True) 

from app import routes
'''
run in a virtual env 
to install venv see pinned discord
create venv with `python -m virtualenv venv`
activate venv with `venv\scripts\activate`
adjust as needed depending on OS

run with `flask --app app run` or `flask run`
'''