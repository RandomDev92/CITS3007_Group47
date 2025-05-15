import imghdr
import os
import time
import statistics
from flask import render_template,  request, redirect, flash, url_for, abort, Blueprint, current_app
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from app.models import User, Question, Difficulty, Tag, Submission, Rating, ProfileShare
from app.sandbox import testCode
from sqlalchemy.sql import func

main = Blueprint('main', __name__,)

@main.route('/')
@main.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")

@main.route('/UploadPage', methods = ['GET', 'POST'])
@login_required
def UploadPage():
    if request.method == 'GET':
        blankform = {"title":"", "short_desc":"", "full_desc":"", "Code":"", "testCode":"", "tags":""}
        return render_template("UploadPage.html", form=blankform)
    if request.method == 'POST':
        uploadedQ = request.form
        print(uploadedQ)
        strCode = uploadedQ["Code"]
        strTest = uploadedQ["testCode"]
        result = testCode(strCode, strTest)
        if result != "All tests passed.":
            flash(result, 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        if None != Question.query.filter_by(title=uploadedQ["title"]).first():
            flash("Title is already taken", 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        question = Question(title=uploadedQ["title"],
                        short_desc=uploadedQ["short_desc"],
                        full_desc=uploadedQ["full_desc"],
                        difficulty=uploadedQ["difficulty"],
                        test_cases=strTest,
                        author_id=current_user.username)
        taglist = uploadedQ["tags"].replace(" ", "").split(',')
        for tag in taglist:
            if Tag.query.filter_by(name=tag).first() != None:
                question.tags.append(Tag.query.filter_by(name=tag).first())
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.LandingUpload'))


@main.route('/LandingUpload')
def LandingUpload():
    return render_template("UploadSuccess.html")


@main.route('/SearchPage', methods=['GET'])
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
    # Add average rating to each question object
    question_ids = [q.id for q in results]
    ratings = (
        db.session.query(Rating.question_id, func.avg(Rating.score))
        .filter(Rating.question_id.in_(question_ids))
        .group_by(Rating.question_id)
        .all()
    )
    rating_map = {qid: round(avg, 1) for qid, avg in ratings}
    for q in results:
        q.avg_rating = rating_map.get(q.id, None)
    
    return render_template("SearchPage.html", questions=results)


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@main.route('/UserPage', methods = ['GET', 'POST'])
@login_required
def UserPage():
    if request.method == 'GET':
        timeArr = []
        attemptsArr = []
        numCompQ = 0
        allQs = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.id).all()
        for Ques in allQs:
            if Ques.passed ==True:
                numCompQ+=1
                timeArr.append(Ques.runtime_sec)
                attemptsArr.append(Ques.attempts)
        startedQ = len(allQs) 
        if numCompQ >= 2:
            stdTime = statistics.stdev(timeArr)
        else:
            stdTime = 0
        if numCompQ >=1:
            AvgTime = statistics.fmean(timeArr)
            AvgAtt = statistics.fmean(attemptsArr)
        else:
            AvgTime = 0
            AvgAtt = 0
        bestQ = Question.query.filter_by(id=current_user.best_question_id).first()
        if bestQ == None:
            bestQid = -1
            bestQtime = 0
            bestQtitle = "No Best Question"
        else:
            bestQid = bestQ.id
            bestQtime = current_user.best_time_sec
            bestQtitle = bestQ.title
        user_stats = {
            "username":current_user.username,
            "average_time":AvgTime, 
            "stdev_time":stdTime, 
            "average_attempts":AvgAtt, 
            "completed_total":numCompQ, 
            "total_started":startedQ,
            "completion_rate":numCompQ/(startedQ if startedQ != 0 else 1)*100,
            "best_question": bestQid,
            "best_question_title": bestQtitle,
            "best_time": bestQtime,
        }
        
        graphingQs = Submission.query.filter_by(user_id=current_user.id).filter(Submission.passed == True).order_by(Submission.id).all()
        submission_data = [
            {"question": s.question.title, "time": s.runtime_sec}
            for s in graphingQs if s.runtime_sec is not None
        ]

        return render_template("UserPage.html", user=user_stats, submission_data=submission_data)
    
    if request.method == 'POST':
        form = request.form
        form_type = form.get("type", "")
        
        if form["type"] == "shareProfileChange":
            user = User.query.get_or_404(current_user.id)
            if form["shareProfile"] == "true":
                user.share_profile = True
            elif form["shareProfile"] == "false":
                user.share_profile = False
            db.session.add(user)
            db.session.commit()
            return ('', 204)
        
        if form["type"] == "Change":
            user = User.query.get_or_404(current_user.id)
            print(user)
            uploaded_file = request.files['newpfp']
            filename = uploaded_file.filename
            print(filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
                    abort(400)
                filepath = current_app.config["UPLOAD_FOLDER"]+current_user.username
                uploaded_file.save(filepath)
                user.avatar_url = current_user.username
                print(user.avatar_url)
            if form["newUsername"].strip() != "":
                user.username = form["newUsername"]
            if form["newPassword"] != "":
                user.password_hash = generate_password_hash(form["newPassword"])
            db.session.add(user)
            db.session.commit()
            flash("Profile Changed.", "success")
            return redirect('/UserPage')
        
        if form["type"] == "addWhitelist":
            username = form.get("whitelist_username").strip()
            target_user = User.query.filter_by(username=username).first()
            if target_user and target_user != current_user:
                from app.models import ProfileShare
                already_shared = ProfileShare.query.filter_by(owner_id=current_user.id, shared_with_id=target_user.id).first()
                if not already_shared:
                    new_entry = ProfileShare(owner_id=current_user.id, shared_with_id=target_user.id)
                    db.session.add(new_entry)
                    db.session.commit()
                    flash(f"{username} has been whitelisted!", "success")
            else:
                flash("User not found or invalid.", "error")
            return redirect('/UserPage')

        if form["type"] == "removeWhitelist":
            from app.models import ProfileShare
            shared_id = int(form.get("whitelist_remove_id"))
            entry = ProfileShare.query.filter_by(owner_id=current_user.id, shared_with_id=shared_id).first()
            if entry:
                db.session.delete(entry)
                db.session.commit()
                flash("User removed from whitelist.", "success")
            return redirect('/UserPage')



@main.route('/SpecificUserPage/<int:userid>')
def SpecificUserPage(userid):
    user = User.query.get_or_404(userid)
    
    #check if user profile is privated
    if user.share_profile == 1:
        #Check to make sure that current user is shared with user they're trying to access
        share = ProfileShare.query.filter_by(owner_id=userid, shared_with_id=current_user.id).first()  
        if not share:
            flash("This user has a private profile.", "error")
            return redirect(request.referrer)

            
    timeArr = []
    attemptsArr = []
    numCompQ = 0
    allQs = Submission.query.filter_by(user_id=user.id).order_by(Submission.id).all()
    for Ques in allQs:
        if Ques.passed ==True:
            numCompQ+=1
            timeArr.append(Ques.runtime_sec)
            attemptsArr.append(Ques.attempts)
    startedQ = len(allQs) 
    if numCompQ >= 2:
        stdTime = statistics.stdev(timeArr)
    else:
        stdTime = 0
    if numCompQ >=1:
        AvgTime = statistics.fmean(timeArr)
        AvgAtt = statistics.fmean(attemptsArr)
    else:
        AvgTime = 0
        AvgAtt = 0
    bestQ = Question.query.filter_by(id=user.best_question_id).first()
    if bestQ == None:
        bestQid = -1
        bestQtime = 0
        bestQtitle = "No Best Question"
    else:
        bestQid = bestQ.id
        bestQtime = user.best_time_sec
        bestQtitle = bestQ.title
    user_stats = {
        "username":user.username,
        "average_time":AvgTime, 
        "stdev_time":stdTime, 
        "average_attempts":AvgAtt, 
        "completed_total":numCompQ, 
        "total_started":startedQ,
        "completion_rate":numCompQ/(startedQ if startedQ != 0 else 1)*100,
        "best_question": bestQid,
        "best_question_title": bestQtitle,
        "best_time": bestQtime,
    }
    graphingQs = Submission.query.filter_by(user_id=user.id).filter(Submission.passed == True).order_by(Submission.id).all()
    submission_data = [
        {"question": s.question.title, "time": s.runtime_sec}
        for s in graphingQs if s.runtime_sec is not None
    ]

    return render_template("SpecificUserPage.html", user=user_stats, submission_data=submission_data)



@main.route('/QuestionDescription')
@login_required
def QuestionDescriptionPage():
    question_id = request.args.get('id', type=int)
    if question_id is None:
        abort(400, description="Missing question ID.")
    question = Question.query.get_or_404(question_id)
    print(question)
    author = User.query.filter_by(username=question.author_id).first_or_404()
    print(author)
    question.author_username = author.username if author else "Unknown"
    avg_rating = db.session.query(func.avg(Rating.score)).filter_by(question_id=question_id).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else None
    return render_template("QuestionDescription.html", question=question, avg_rating=avg_rating, author=author)

@main.route('/QuestionStat', methods = ['GET', 'POST'])
@login_required
def QuestionStatPage():
    question_id = request.args.get('id', type=int)

    # Fetch the question from the database
    question = Question.query.get_or_404(question_id)

    if request.method == "GET":

        # Fetch the most recent submission for the current user and the given question
        submission = Submission.query.filter_by(
            user_id=current_user.id, 
            question_id=question_id
        ).order_by(Submission.id.desc()).first()
        print(str(submission))   
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

        #Code below makes dynamic bins for the range of times submitted by other users to make a histogram of times recorded
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
        # Query all submissions for this question
        submissions = Submission.query.filter_by(question_id=question_id).all()

        # Compute metrics only from passing submissions
        passing_submissions = [s for s in submissions if s.passed]

        if passing_submissions:
            avg_time = round(sum(s.runtime_sec for s in passing_submissions if s.runtime_sec) / len(passing_submissions), 2)
            avg_tests = round(sum(s.tests_run for s in passing_submissions if s.tests_run) / len(passing_submissions), 2)
            best_code_length = min(s.lines_of_code for s in passing_submissions if s.lines_of_code)
            completed_count = len(set(s.user_id for s in passing_submissions))
        else:
            avg_time = avg_tests = best_code_length = completed_count = 0

            # Attach these values to the question object or pass as a separate dict
        question.avg_time = avg_time
        question.avg_tests = avg_tests
        question.best_code_length = best_code_length
        question.completed_count = completed_count
        # Render the template with necessary context
        return render_template(
            "QuestionStat.html",
            question=question,
            user_score=user_score,  # Pass user_score to the template
            bin_labels=bin_labels,
            frequencies=frequencies
        )
    
    if request.method == "POST":
        review = request.form.get('ratingInput', type=int)
        existing = Rating.query.filter_by(user_id=current_user.id, question_id=question_id).first()
        if review is None:
            flash("Have To Select A Star First Before Submitting Review", "error")
        else:
            if existing:
                existing.score = review
                flash("Your review has been updated.", "success")
            else:
                rating = Rating(
                    score=review,
                    user_id=current_user.id, 
                    question_id=question_id
                )
                db.session.add(rating)
                flash("Submitted! Thank You For Your Input", "success")
            db.session.commit()
        
        return redirect(url_for('main.QuestionStatPage', id=question_id))

@main.route('/QuestionAnswer', methods=['GET', 'POST'])
@login_required
def QuestionAnswer():
    print("Entered QuestionAnswer route")
    question_id = request.args.get('id', type=int)

    # Retrieve the question from the database
    question = Question.query.get_or_404(question_id)
    if request.method == 'GET':
        oldsubmission = Submission.query.filter_by(user_id=current_user.id, question_id=question_id).order_by(Submission.id.desc()).first()
        print(oldsubmission)
        if(oldsubmission and oldsubmission.passed == False):
            oldsubmission.attempts+=1
            oldsubmission.start_time = time.time()
            db.session.add(oldsubmission)
        else:
            submission = Submission(
                user_id=current_user.id, 
                question_id=question_id, 
                start_time = time.time(),
                attempts = 0,
                )
            db.session.add(submission)
        db.session.commit()
        return render_template('QuestionAnswer.html', question=question)
    
    if request.method == 'POST':
        print("Form submitting")
        code = request.form.get('Code')
        submission = Submission.query.filter_by(user_id=current_user.id, question_id=question_id).order_by(Submission.id.desc()).first()
        submission.attempts +=1
        
        result = testCode(code, question.test_cases)
        if result != "All tests passed.":
            flash(code, 'code')
            flash(result, 'error')
            return redirect(url_for("main.QuestionAnswer", id=question_id))
        
        submission.end_time = time.time() 
        submission.runtime_sec = submission.end_time - submission.start_time
        submission.lines_of_code = len(code.split("\n"))
        submission.tests_run = len(question.test_cases.split(":")) #this is not needed
        submission.passed = True
        db.session.add(submission)

        if submission.runtime_sec <= current_user.best_time_sec or current_user.best_time_sec == 0:
            cUser = User.query.filter_by(id=current_user.id).first()
            cUser.best_time_sec = submission.runtime_sec
            cUser.best_question_id = question_id
            db.session.add(cUser)

        db.session.commit()

        return redirect(url_for('main.QuestionStatPage', id=question_id))
    
@main.route('/SharedProfilesPage', methods=['GET'])
@login_required
def SharedProfilePage():
    search_query = request.args.get('search', '').strip()

    # Query all users who shared their profile with the current user
    shared_users = db.session.query(User).join(ProfileShare, ProfileShare.owner_id == User.id) \
        .filter(ProfileShare.shared_with_id == current_user.id)

    # Optional search
    if search_query:
        shared_users = shared_users.filter(User.username.ilike(f"%{search_query}%"))

    shared_users = shared_users.all()

    return render_template("SharedProfilePage.html", users=shared_users, search=search_query)