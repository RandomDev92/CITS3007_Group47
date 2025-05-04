from flask import render_template,  request, redirect, flash, url_for
from app import app
from app.models import User, Question, Difficulty
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select


from flask_login import current_user, login_required
from flask_login import current_user, login_required

@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")

@app.route('/UploadPage', methods = ['GET', 'POST'])
def UploadPage():
    if request.method == 'GET':
        blankform = {"title":"", "short_desc":"", "full_desc":"", "Code":"", "testCode":"",}
        return render_template("UploadPage.html", form=blankform)
    if request.method == 'POST':
        uploadedQ = request.form
        print(uploadedQ)
        if None != Question.query.filter_by(title=uploadedQ["title"]).first():
            flash("Title is already taken", 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        question = Question(title=uploadedQ["title"],
                        short_desc=uploadedQ["short_desc"],
                        full_desc=uploadedQ["full_desc"],
                        difficulty=uploadedQ["difficulty"],
                        author_username=current_user.username)
        print("added to db", flush=True)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('LandingUpload'))


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

@app.route('/LandingUpload')
def LandingUpload():
    return render_template("UploadSuccess.html")
