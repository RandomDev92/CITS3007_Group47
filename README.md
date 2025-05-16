# CITS3403_Group46
Group 46 Cits3403 Project

## Project Description:

SpeedCode is a website that allows for users to complete user submitted leetcode style questions while timing themselves to see how they fair.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Site Map](#site-map)
- [Setup and Installation](#setup-and-installation)
- [Testing](#Testing)
- [Tech Stack](#tech-stack)
- [Team Members](#team-members)
---

### Overview

**SpeedCode** is a Flask-based web application that helps users practice coding challenges in a timed environment, simulating competitive programming conditions.

With SpeedCode, users can:

- Attempt user-submitted coding problems in a LeetCode-style interface.
    
- Time themselves to track problem-solving speed and accuracy.
    
- View performance metrics like runtime, pass/fail status, and code efficiency.
    
- Submit their own questions to expand the problem bank.

- Share profile statistics with other specific users or shared publicly.

All user data, submissions, and profiles are securely stored and managed, ensuring a private and reliable experience.

---

### Features

- **User Authentication:** Secure registration and login to protect user accounts and submissions
    
- **Problem Dashboard:** Browse and select from a growing collection of coding challenges
    
- **Timed Coding Environment:** Attempt questions while a timer tracks your problem-solving speed
    
- **Code Submission & Evaluation:** Submit code, run tests, and receive instant feedback on correctness
    
- **Performance Tracking:** View details like runtime, test results, and code statistics for every submission

- **Profile Sharing:** Share your profile with just your friends or let the world see your abilities with either whitelists or public profile
    
- **Question Contribution:** Users can create and submit their own coding problems to challenge others
    
- **Secure Code Execution:** Code is executed in a restricted sandbox to ensure safety and isolation
    
- **Profile Management (Optional):** Update account information with your Username and Avatar

---

### Site Map

![SpeedCodeWebsiteLinks](https://github.com/RandomDev92/CITS3403_Group46/blob/main/SpeedCodeWebsiteLinks.png)


---

### Setup and Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/RandomDev92/CITS3403_Group46.git
cd CITS3403_Group46
```

#### 2. Create Virtual Environment

```bash
python -m virtualenv venv
```

#### 3. Activate Virtual Environment

```bash
# On Posix Systems:
source venv/bin/activate

# On Windows Systems:
# venv\Scripts\activate
```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```


#### 5.  Run Application


```bash
flask --app app run
#or just 'flask run'
```

If successful it should host locally at `http://127.0.0.1:5000/`.

---

### Testing

``python run-test.py```

Will run unittests for the sandbox and logic and selenium tests for the website functionality.

---

### Tech Stack
| Category                      | Tools / Libraries                                                 |
| ----------------------------- | ----------------------------------------------------------------- |
| **Frontend**                  | HTML, CSS, Bootstrap, JavaScript, Jinja2                          |
| **Backend**                   | Python, Flask                                                     |
| **Database**                  | Flask-SQLAlchemy                                                  |
| **Authentication & Security** | Flask-Login, Werkzeug, CSRF from flask_wtf, RestrictedPython      |
| **Other**                     | Flask-Migrate for database migrations, Codemirror for text editor |

---

### Team Members

| Name          | Student Number | GithubID     |
| ------------- | -------------- | ------------ |
| Bill Rayner   | 23735293       | RandomDev92  |
| Wesley Conti  | 23499047       | Wetley0      |
| Fanhua Zeng   | 23605914       | FongWongZong |
| Aidin Fenwick | 23800978       | aid-in       |
