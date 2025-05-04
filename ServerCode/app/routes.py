from flask import render_template,  request, redirect, flash
from app import app
from app.models import User, Question, db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user, login_required

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
@login_required
def SearchPage():
    return render_template("SearchPage.html")

@app.route('/UserPage')
@login_required
def UserPage():
    return render_template("UserPage.html", current_user=current_user)

@app.route('/QuestionDescription')
@login_required
def QuestionDescriptionPage():
    return render_template("QuestionDescription.html")

@app.route('/QuestionStat')
@login_required
def QuestionStatPage():
    return render_template("QuestionStat.html")

@app.route('/QuestionAnswer')
@login_required
def QuestionAnswer():
    return render_template("QuestionAnswer.html")

