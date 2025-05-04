from flask import render_template,  request, redirect, flash, url_for
from app import app
from app.models import User, Question, Difficulty, Tag
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
        blankform = {"title":"", "short_desc":"", "full_desc":"", "Code":"", "testCode":"", "tags":""}
        return render_template("UploadPage.html", form=blankform)
    if request.method == 'POST':
        uploadedQ = request.form
        if None != Question.query.filter_by(title=uploadedQ["title"]).first():
            flash("Title is already taken", 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        question = Question(title=uploadedQ["title"],
                        short_desc=uploadedQ["short_desc"],
                        full_desc=uploadedQ["full_desc"],
                        difficulty=uploadedQ["difficulty"],
                        author_username=current_user.username)
        taglist = uploadedQ["tags"].replace(" ", "").split(',')
        for tag in taglist:
            if Tag.query.filter_by(name=tag).first() != None:
                question.tags.append(Tag.query.filter_by(name=tag).first())
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('LandingUpload'))


@app.route('/SearchPage', methods=['GET'])
@login_required
def SearchPage():
    title_query = request.args.get('title', '').strip()
    difficulty_query = request.args.get('difficulty', '').strip()
    tag_query = request.args.get('tag', '').strip()

    query = Question.query

    if title_query:
        query = query.filter(Question.title.ilike(f"%{title_query}%"))

    if difficulty_query:
        try:
            enum_val = Difficulty[difficulty_query.upper()]
            query = query.filter(Question.difficulty == enum_val)
        except KeyError:
            pass

    if tag_query:
        query = query.join(Question.tags).filter(Tag.name.ilike(f"%{tag_query}%"))

    results = query.distinct().all()
    return render_template("SearchPage.html", questions=results)

@app.route('/UserPage', methods = ['GET', 'POST'])
@login_required
def UserPage():
    if request.method == 'GET':
        return render_template("UserPage.html", user=current_user)
    if request.method == 'POST':
        form = request.form
        if form["username"] != current_user.username:
            return ('', 204)
        if form["type"] == "shareProfileChange":
            user = User.query.get_or_404(current_user.username)
            if form["shareProfile"] == "true":
                user.share_profile = True
            elif form["shareProfile"] == "false":
                user.share_profile = False
            db.session.add(user)
            db.session.commit()
            return ('', 204)
        if form["type"] == "Change":
            user = User.query.get_or_404(current_user.username)
            user.username = form["newUsername"]
            #more changes if needed e.g. password or so on
            db.session.add(user)
            db.session.commit()
            flash("Profile Changed.", "success")
            return redirect('/UserPage')


@app.route('/UserPage/<userid>')
def SpecificUserPage(userid):
    userDB = User.query.filter_by(username=userid).first()
    if userDB == None or userDB.share_profile == False or userDB == current_user:
        flash("User Either Doesn't Exist Or Has Share Disabled.", "error")
        return redirect('/UserPage')
    return render_template("UserPage.html", user=userDB)

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
