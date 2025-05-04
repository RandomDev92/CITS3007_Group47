from flask import render_template,  request, redirect, flash
from app import app
from app.models import User, Question, db, Submission
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user

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
    return render_template("UserPage.html", current_user=current_user)

@app.route('/QuestionDescription/<int:question_id>')
def QuestionDescriptionPage():
    question_id = request.args.get('id', type=int)
    return render_template("QuestionDescription.html")

@app.route('/QuestionStat')
def QuestionStatPage():
    question_id = request.args.get('id', type=int)
    submission = Submission.query.filter_by(
        user_id=current_user.id,
        question_id=question_id
    ).order_by(Submission.timestamp.desc()).first()
    if submission:
        user_score = {
            'time_taken': submission.runtime_sec,
            'tests_ran': submission.tests_run,
            'code_length': submission.lines_of_code,
            'passed': submission.passed
        }
    else:
        user_score = {
            'time_taken': "N/A",
            'tests_ran': "N/A",
            'code_length': "N/A",
            'passed': "N/A"
        }
    question = Question.query.get_or_404(question_id)
    return render_template("QuestionResults.html", question=question, user_score=user_score)


@app.route('/QuestionAnswer')
def QuestionAnswer():
    return render_template("QuestionAnswer.html")

