from flask import render_template,  request, redirect, flash, url_for
from app import app
from app.models import User, Question, Difficulty, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select


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
        #print(uploadedQ)
        question = Question(title=uploadedQ["title"],
                        short_desc=uploadedQ["short_desc"],
                        full_desc=uploadedQ["full_desc"],
                        difficulty=uploadedQ["difficulty"],
                        author_username=current_user.username)
        db.session.add(question)
        db.session.commit()

        return redirect("/SearchPage")


@app.route('/SearchPage')
def SearchPage():
    return render_template("SearchPage.html")

@app.route('/UserPage')
@login_required
def UserPage():
    return render_template("UserPage.html", current_user=current_user)

@app.route('/QuestionDescription')
def QuestionDescriptionPage():
    return render_template("QuestionDescription.html")

@app.route('/QuestionStat')
def QuestionStatPage():
    return render_template("QuestionStat.html")

@app.route('/QuestionAnswer')
def QuestionAnswer():
    return render_template("QuestionAnswer.html")

