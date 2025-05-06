import imghdr
import os
from flask import render_template,  request, redirect, flash, url_for, abort
from app import app
from app.models import User, Question, Difficulty, Tag, Submission
from . import db
from werkzeug.security import generate_password_hash
from app.sandbox import testCode


from flask_login import current_user, login_required

@app.route('/')
@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")

@app.route('/UploadPage', methods = ['GET', 'POST'])
@login_required
def UploadPage():
    if request.method == 'GET':
        blankform = {"title":"", "short_desc":"", "full_desc":"", "Code":"", "testCode":"", "tags":""}
        return render_template("UploadPage.html", form=blankform)
    if request.method == 'POST':
        uploadedQ = request.form
        
        strCode = uploadedQ["Code"]
        strTest = uploadedQ["testCode"]
        result = testCode(strCode, strTest)
        if result != "All tests passed.":
            flash(result)
            return render_template("UploadPage.html", form=uploadedQ)
        
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

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

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
            
            uploaded_file = request.files['newpfp']
            filename = uploaded_file.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
                    abort(400)
                filepath = app.config["UPLOAD_FOLDER"]+current_user.username
                uploaded_file.save(filepath)
                user.avatar_url = current_user.username

            if form["newUsername"].strip() != "":
                user.username = form["newUsername"]
            if form["newPassword"] != "":
                user.password_hash = generate_password_hash(form["newPassword"])
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
    print(type(question.difficulty))
    return render_template("QuestionDescription.html", question=question)

@app.route('/QuestionStat')
@login_required
def QuestionStatPage():
    question_id = request.args.get('id', type=int)

    # Fetch the question from the database
    question = Question.query.get_or_404(question_id)

    # Fetch the most recent submission for the current user and the given question
    submission = Submission.query.filter_by(
        user_id=current_user.username,  # Using username instead of id
        question_id=question_id
    ).order_by(Submission.runtime_sec.desc()).first()

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
    # Fetch all the submission times for the question
    submission_times = [s.runtime_sec for s in question.submissions if s.runtime_sec is not None]

    # If there are no valid submission times, set default values to prevent errors
    if not submission_times:
        submission_times = [0]

    # Ensure min_time, max_time, and bin_size are integers
    min_time = int(min(submission_times))  # Convert min_time to an integer
    max_time = int(max(submission_times))  # Convert max_time to an integer
    bin_count = 10  # Set the number of bins
    bin_size = int(max(1, (max_time - min_time) // bin_count + 1))  # Convert bin_size to an integer

    # Generate the bins
    bins = list(range(min_time, max_time + bin_size, bin_size))  # Ensure min_time, max_time, and bin_size are integers

    # Calculate the frequency distribution for the histogram
    import numpy as np
    hist, edges = np.histogram(submission_times, bins=bins)

    # Prepare the bin labels and frequencies
    bin_labels = [f"{edges[i]}–{edges[i+1]}" for i in range(len(edges)-1)]
    frequencies = hist.tolist()

    # Render the template with necessary context
    return render_template(
        "QuestionStat.html",
        question=question,
        user_score=user_score,  # Pass user_score to the template
        bin_labels=bin_labels,
        frequencies=frequencies
    )



@app.route('/QuestionAnswer', methods=['GET', 'POST'])
@login_required
def QuestionAnswer():
    print("Entered QuestionAnswer route")
    question_id = request.args.get('id', type=int)

    # Retrieve the question from the database
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        print("Form submitting")
        code = request.form.get('code')
        runtime_sec = request.form.get('runtime_sec', type=int)

        # Placeholder values for now, change later when you implement proper evaluation
        passed = True
        tests_run = 3

        # Use current_user.username instead of current_user.id
        submission = Submission(
            user_id=current_user.username,  # Updated to use username
            question_id=question_id,
            code=code,
            passed=passed,
            runtime_sec=runtime_sec,
            lines_of_code=len(code.split("\n")),
            tests_run=tests_run
        )
        try:
            print(submission)
            db.session.add(submission)
            db.session.commit()
            print("Data successfully saved to the database!")
        except Exception as e:
            print("Error saving to the database:", e)
            db.session.rollback()  # Rollback in case of error

        return redirect(url_for('QuestionStatPage', id=question_id))

    else:
        # handle GET
        print("start get")
        question_id = request.args.get('id')
        question = Question.query.get(question_id)
        return render_template('QuestionAnswer.html', question=question)


@app.route('/LandingUpload')
def LandingUpload():
    return render_template("UploadSuccess.html")
