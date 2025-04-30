from flask import render_template,  request, redirect, flash
from app import app
from app.models import User, Question, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import *

@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")

@app.route('/UploadPage', methods = ['GET', 'POST'])
def UploadPage():
    if request.method == 'GET':
        return render_template("UploadPage.html")
    if request.method == 'POST':
        uploadedQ = request.form
        print(uploadedQ)
        newQ = Question(title=uploadedQ["Title"])
        return render_template("UploadPage.html")
    

@app.route('/SearchPage')
def SearchPage():
    return render_template("SearchPage.html")

@app.route('/UserPage')
@login_required
def UserPage():
    print(current_user.avg_time_sec)
    return render_template("UserPage.html")

@app.route('/QuestionDescription')
def QuestionDescriptionPage():
    return render_template("QuestionDescription.html")

@app.route('/QuestionStat')
def QuestionStatPage():
    return render_template("QuestionStat.html")

@app.route('/QuestionAnswer')
def QuestionAnswer():
    return render_template("QuestionAnswer.html")

@app.route('/testing')
def testing():
    user = Users.query.all()
    return render_template("dbtest.html", user=user)
