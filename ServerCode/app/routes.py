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
    #establish list for tags for popup
    taglist = ""
    for tag in Tag.query.all():
        taglist = taglist + tag.name + ", "
    
    if request.method == 'GET':
        blankform = {"title":"", "short_desc":"", "full_desc":"", "Code":"", "testCode":"", "tags":""}
        return render_template("UploadPage.html", form=blankform, taglist=taglist)
    
    if request.method == 'POST':
        uploadedQ = request.form
        strCode = uploadedQ["Code"]
        strTest = uploadedQ["testCode"]
        
        #test the user's code in the sandbox
        result = testCode(strCode, strTest)

        #failed tests
        if result != "All tests passed.":
            flash(result, 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        
        #title taken
        if None != Question.query.filter_by(title=uploadedQ["title"]).first():
            flash("Title is already taken", 'error')
            return render_template("UploadPage.html", form=uploadedQ)
        
        #establish question and tags into db before returning success 
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
    #establish list for tags for popup
    taglist = ""
    for tag in Tag.query.all():
        taglist = taglist + tag.name + ", "
    
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
    
    return render_template("SearchPage.html", questions=results, taglist=taglist)

#function for validating if a file is an image from https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def calculateUserStats(Userid):
    #for a given user calculate the stats to display
    user = User.query.filter_by(id=Userid).first()
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
    return user_stats

@main.route('/UserPage', methods = ['GET', 'POST'])
@login_required
def UserPage():
    if request.method == 'GET':
        user_stats = calculateUserStats(current_user.id)
        
        #Get the graphing data
        graphingQs = Submission.query.filter_by(user_id=current_user.id).filter(Submission.passed == True).order_by(Submission.id).all()
        submission_data = [
            {"question": s.question.title, "time": s.runtime_sec}
            for s in graphingQs if s.runtime_sec is not None
        ]

        return render_template("UserPage.html", user=user_stats, submission_data=submission_data)
    
    if request.method == 'POST':
        form = request.form
        #determine the type of post from this page, sharing page, or changing profile
        if form["type"] == "shareProfileChange":
            #this is to share with everyone
            user = User.query.get_or_404(current_user.id)
            if form["shareProfile"] == "true":
                user.share_profile = True
            elif form["shareProfile"] == "false":
                user.share_profile = False
            db.session.add(user)
            db.session.commit()
            return ('', 204)
        
        if form["type"] == "Change":
            #change any data of the account
            user = User.query.get_or_404(current_user.id)
            uploaded_file = request.files['newpfp']
            filename = uploaded_file.filename
            #test username first as it needs to be unique
            if form["newUsername"].strip() != "":
                nUsername = form["newUsername"]
                if User.query.filter_by(username=nUsername).first() == None:
                    flash("UsernameTaken", "error")
                    return redirect('/UserPage')
                user.username =  nUsername
            #if there is a change in image create the file in the static, and validate it 
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
                    abort(400)
                filepath = current_app.config["UPLOAD_FOLDER"]+current_user.username
                uploaded_file.save(filepath)
                user.avatar_url = current_user.username
            #otherwise if the password
            if form["newPassword"] != "":
                user.password_hash = generate_password_hash(form["newPassword"])
            db.session.add(user)
            db.session.commit()
            flash("Profile Changed.", "success")
            return redirect('/UserPage')
        
        if form["type"] == "addWhitelist":
            #whitelist a specific user to view your share page
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
            #unshare from your whitelist 
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
    
    #check if user profile is privated if so then redirect back
    if user.share_profile == False:
        #Check to make sure that current user is shared with user they're trying to access
        share = ProfileShare.query.filter_by(owner_id=userid, shared_with_id=current_user.id).first()  
        if not share:
            flash("This user has a private profile.", "error")
            return redirect(request.referrer)

    user_stats = calculateUserStats(userid)
    graphingQs = Submission.query.filter_by(user_id=user.id).filter(Submission.passed == True).order_by(Submission.id).all()
    submission_data = [
        {"question": s.question.title, "time": s.runtime_sec}
        for s in graphingQs if s.runtime_sec is not None
    ]

    return render_template("SpecificUserPage.html", user=user_stats, submission_data=submission_data)



@main.route('/QuestionDescription')
@login_required
def QuestionDescriptionPage():
    #display the questions description
    question_id = request.args.get('id', type=int)
    if question_id is None:
        abort(400, description="Missing question ID.")
    question = Question.query.get_or_404(question_id)
    author = User.query.filter_by(username=question.author_id).first()
    question.author_username = author.username if author else "Unknown"
    #if the author is unknown set authorid to invalid
    if author == None:
        author = {"id":-1}

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
        # Prepare user score data
        if submission:
            user_score = {
                'time_taken': submission.runtime_sec,
                'attempts': submission.attempts,
                'code_length': submission.lines_of_code,
                'passed': submission.passed
            }
        else:
            user_score = {
                'time_taken': "N/A",
                'attempts': "N/A",
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
            avg_attempts = round(sum(s.attempts for s in passing_submissions if s.attempts) / len(passing_submissions), 2)
            best_time = min(s.runtime_sec for s in passing_submissions if s.runtime_sec)
            best_code_length = min(s.lines_of_code for s in passing_submissions if s.lines_of_code)
            completed_count = len(set(s.user_id for s in passing_submissions))
        else:
            avg_time = avg_attempts = best_code_length = completed_count = 0

            # Attach these values to the question object or pass as a separate dict
        question.avg_time = avg_time
        question.avg_attempts = avg_attempts
        question.best_time = best_time
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
        #submit a review trhough the 5 star ratings
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


def CalculateSubmission(questionID):
    #calculate the graphing 
    question = Question.query.filter_by(id=questionID).first()

    all_subs = Submission.query.filter_by(question_id=question.id).order_by(Submission.id).all()

    passing_subs = [s for s in all_subs if s.passed]

    time_arr = [s.runtime_sec for s in passing_subs if s.runtime_sec]
    att_arr = [s.attempts for s in passing_subs if s.attempts]
    best_code_length = min(s.lines_of_code for s in passing_subs if s.lines_of_code)
    completed_count = len(set(s.user_id for s in passing_subs))

    avg_time = round(statistics.fmean(time_arr), 2) if time_arr else 0
    avg_att = round(statistics.fmean(att_arr), 2) if att_arr else 0
    best_time = min(time_arr) if time_arr else 0
    best_code_length = best_code_length if best_code_length else 0
    sub_stats = {
        "average time": avg_time,
        "average attempts": avg_att,
        "best time": best_time,
        "best length": best_code_length,
        "total completed": completed_count
    }
    return sub_stats

@main.route('/QuestionAnswer', methods=['GET', 'POST'])
@login_required
def QuestionAnswer():
    print("Entered QuestionAnswer route")
    question_id = request.args.get('id', type=int)

    # Retrieve the question from the database
    question = Question.query.get_or_404(question_id)
    if request.method == 'GET':
        #if they have an older submission they didnt complete and its been less than a day use that submission and its start time
        #otherwise make a new submission with now as the start time
        oldsubmission = Submission.query.filter_by(user_id=current_user.id, question_id=question_id).order_by(Submission.id.desc()).first()
        start_time = 0 
        if(oldsubmission and oldsubmission.passed == False):
            diff = time.time() - oldsubmission.start_time
            if diff > 86400:
                oldsubmission.start_time = time.time()
            oldsubmission.attempts+=1
            db.session.add(oldsubmission)
            start_time = oldsubmission.start_time
        else:
            submission = Submission(
                user_id=current_user.id, 
                question_id=question_id, 
                start_time = time.time(),
                attempts = 0,
                )
            db.session.add(submission)
        db.session.commit()
        flash(start_time, "time")
        return render_template('QuestionAnswer.html', question=question)
    
    if request.method == 'POST':
        #user has submitted code for testign as an attempt 
        code = request.form.get('Code')
        submission = Submission.query.filter_by(user_id=current_user.id, question_id=question_id).order_by(Submission.id.desc()).first()
        submission.attempts +=1
        
        #test code if they failed then display why 
        result = testCode(code, question.test_cases)
        if result != "All tests passed.":
            flash(submission.start_time, "time")
            flash(code, 'code')
            flash(result, 'error')
            return redirect(url_for("main.QuestionAnswer", id=question_id))
        
        #if they passed add the results to submission and check if its their best time
        submission.end_time = time.time() 
        submission.runtime_sec = round(submission.end_time - submission.start_time, 2)
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
    #a feed page for all users who have explicity shared their page with you.
    search_query = request.args.get('search', '').strip()

    # Query all users who shared their profile with the current user
    shared_users = db.session.query(User).join(ProfileShare, ProfileShare.owner_id == User.id) \
        .filter(ProfileShare.shared_with_id == current_user.id)

    # Optional search
    if search_query:
        shared_users = shared_users.filter(User.username.ilike(f"%{search_query}%"))

    shared_users = shared_users.all()

    return render_template("SharedProfilePage.html", users=shared_users, search=search_query)