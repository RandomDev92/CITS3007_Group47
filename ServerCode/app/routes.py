from flask import render_template,  request, redirect, flash, url_for
from app import app
from app.models import User, Question, Difficulty, Tag, Submission
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select


from flask_login import current_user, login_required

@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")


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
    question_id = request.args.get('id', type=int)
    if question_id is None:
        abort(400, description="Missing question ID.")
    question = Question.query.get_or_404(question_id)
    return render_template("QuestionDescription.html", question=question)

@app.route('/QuestionStat')
@login_required
def QuestionStatPage():
    question_id = request.args.get('id', type=int)
    
    # Fetch the most recent submission for the current user and question
    submission = Submission.query.filter_by(
        user_id=current_user.id,
        question_id=question_id
    ).order_by(Submission.timestamp.desc()).first()
    
    # Prepare user score data
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

    # Fetch the question
    question = Question.query.get_or_404(question_id)

    # Get all submission times for this question
    submission_times = [s.runtime_sec for s in question.submissions]
    if not submission_times:
        submission_times = [0]

    # Generate dynamic bins for the histogram
    min_time = min(submission_times)
    max_time = max(submission_times)
    bin_count = 10
    bin_size = max(1, (max_time - min_time) // bin_count + 1)
    bins = list(range(min_time, max_time + bin_size, bin_size))

    # Calculate frequency distribution
    import numpy as np
    hist, edges = np.histogram(submission_times, bins=bins)

    # Prepare data for the chart (bin labels and frequency values)
    bin_labels = [f"{edges[i]}–{edges[i+1]}" for i in range(len(edges)-1)]
    frequencies = hist.tolist()

    # Render the template with all necessary context
    return render_template("QuestionResults.html", question=question, user_score=user_score, bin_labels=bin_labels, frequencies=frequencies)




@app.route('/QuestionAnswer', methods=['GET', 'POST'])
@login_required
def QuestionAnswer():
    if request.method == 'POST':
        question_id = request.form.get('question_id', type=int)
        code = request.form.get('code')
        runtime_sec = request.form.get('runtime_sec', type=int)

        # I'll do real evaluations later when I figure out how to get the testing working for now they're just placeholders (except lines of code)
        passed = True  
        tests_run = 3
        lines_of_code = code.count('\n') + 1 if code else 0

        submission = Submission(
            user_id=current_user.id,
            question_id=question_id,
            code=code,
            passed=passed,
            runtime_sec=runtime_sec,
            lines_of_code=lines_of_code,
            tests_run=tests_run
        )
        db.session.add(submission)
        db.session.commit()

        return redirect(url_for('QuestionStatPage.html', id=question_id))
    
    # puts information on the page
    question_id = request.args.get('id', type=int)
    if not question_id:
        return "No question ID provided", 400
    question = Question.query.get_or_404(question_id)
    return render_template("QuestionAnswer.html", question=question)

@app.route('/LandingUpload')
def LandingUpload():
    return render_template("UploadSuccess.html")
