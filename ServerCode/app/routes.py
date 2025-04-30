from flask import render_template
from flask import request
from app import app
from app.models import User, Question

@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")

@app.route('/LoginPage', methods = ['GET', 'POST'])
def LoginPage():
    if request.method == 'GET':
        return render_template("LoginPage.html")
    if request.method == 'POST':
        data = request.form
        print(data["email"])
        userDB = User.query.filter_by(username=data['email']).first()
        if userDB is None:
            return render_template("UploadPage.html")
        if userDB._password_hash == data["pswd"]:
            return render_template("SignupPage.html") 
        else:
            return render_template("LoginPage.html")



@app.route('/SignupPage')
def SignupPage():
    return render_template("SignupPage.html")

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
def UserPage():
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
