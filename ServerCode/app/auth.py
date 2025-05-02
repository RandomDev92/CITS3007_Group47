from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from app import app
from flask_login import login_user


@app.route('/LoginPage', methods = ['GET', 'POST'])
def LoginPage():
    if request.method == 'GET':
        return render_template("LoginPage.html")
    if request.method == 'POST':
        data = request.form
        print(data)
        userDB = User.query.filter_by(username=data['email']).first()
        if check_password_hash(userDB.password_hash, data["pswd"]):
            login_user(userDB, remember=True)
            return redirect("/UserPage")
        else:
            flash("Login Failed. Double Check Your Details And Try Again.", 'error')
            return redirect("/LoginPage")


@app.route('/SignupPage', methods = ['GET', 'POST'])
def SignupPage():
    if request.method == 'GET':
        return render_template("SignupPage.html")
    if request.method == 'POST':
        data = request.form
        userDB = User.query.filter_by(username=data['email']).first()
        if userDB is not None:
            flash("Email Already In Use", 'success')
            return redirect('/SignupPage')
        else:
            hashedPswd = generate_password_hash(data["pswd"])
            newUser = User(username=data["email"], password_hash=hashedPswd)
            db.session.add(newUser)
            db.session.commit()
            flash("Account Created", 'success')
            return redirect("/LoginPage")
