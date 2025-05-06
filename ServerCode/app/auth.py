from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from app import app
from flask_login import login_user, logout_user


@app.route('/LoginPage', methods = ['GET', 'POST'])
def LoginPage():
    if request.method == 'GET':
        return render_template("LoginPage.html")
    if request.method == 'POST':
        data = request.form
        print(data)
        userDB = User.query.filter_by(username=data['Username']).first()
        if userDB == None or check_password_hash(userDB.password_hash, data["pswd"]) == False:
            flash("Login Failed. Double Check Your Details And Try Again.", 'error')
            return redirect("/LoginPage")
        else:
            login_user(userDB, remember=True)
            return redirect("/UserPage")


@app.route('/SignupPage', methods = ['GET', 'POST'])
def SignupPage():
    if request.method == 'GET':
        return render_template("SignupPage.html")
    if request.method == 'POST':
        data = request.form
        userDB = User.query.filter_by(username=data['Username']).first()
        if userDB is not None:
            flash("Username Already In Use", 'success')
            return redirect('/SignupPage')
        else:
            hashedPswd = generate_password_hash(data["pswd"])
            newUser = User(username=data["Username"], password_hash=hashedPswd)
            db.session.add(newUser)
            db.session.commit()
            flash("Account Created", 'success')
            return redirect("/LoginPage")

@app.route('/Logout')
def Logout():
    logout_user()
    return redirect("/HomePage")