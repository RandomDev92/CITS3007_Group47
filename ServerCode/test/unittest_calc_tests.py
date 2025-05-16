import unittest
from app.routes import calculateUserStats, CalculateSubmission
from app import create_app, db
from app.models import User, Question, Difficulty, Submission
from werkzeug.security import generate_password_hash
import statistics

class testLogic(unittest.TestCase):

    def setUp(self):
        self.app = create_app(isTest=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        return super().setUp()

    def tearDown(self):
        self.app_context.pop()
        return super().tearDown()

    def test_calculateUserStats(self):
        sub1 = Submission(
            user_id=1,
            question_id=1,
            start_time=0,
            end_time=10,
            attempts=1,
            code="temp code",
            passed=True,
            runtime_sec=10,
            lines_of_code=2,
            tests_run=5
        )
        sub2 = Submission(
            user_id=1,
            question_id=1,
            start_time=10,
            end_time=110,
            attempts=4,
            code="temp code",
            passed=True,
            runtime_sec=100,
            lines_of_code=10,
            tests_run=5
        )
        sub3 = Submission(
            user_id=1,
            question_id=1,
            start_time=5,
            end_time=6,
            attempts=100,
            code="temp code",
            passed=False,
            runtime_sec=1,
            lines_of_code=20,
            tests_run=5
        )
        db.session.add(sub1)
        db.session.add(sub2)
        db.session.add(sub3)
        db.session.commit()

        user_stats = calculateUserStats(1)
        self.assertEqual(55, user_stats["average_time"])
        self.assertAlmostEqual(63.639610306789, user_stats["stdev_time"], 4)
        self.assertEqual(2.5, user_stats["average_attempts"])
        self.assertEqual(2, user_stats["completed_total"])
        self.assertEqual(3, user_stats["total_started"])
        self.assertAlmostEqual(66.66666, user_stats["completion_rate"], 4)

    def test_CalculateSubmission(self):
        sub1 = Submission(
            user_id=1,
            question_id=1,
            start_time=0,
            end_time=18,
            attempts=4,
            code="temp code",
            passed=False,
            runtime_sec=18,
            lines_of_code=3,
            tests_run=15
        )
        sub2 = Submission(
            user_id=1,
            question_id=1,
            start_time=50,
            end_time=200,
            attempts=1,
            code="temp code",
            passed=True,
            runtime_sec=150,
            lines_of_code=15,
            tests_run=15
        )
        sub3 = Submission(
            user_id=3,
            question_id=1,
            start_time=5,
            end_time=31,
            attempts=37,
            code="temp code",
            passed=True,
            runtime_sec=26,
            lines_of_code=26,
            tests_run=15
        )
        sub4 = Submission(
            user_id=1,
            question_id=1,
            start_time=20,
            end_time=90,
            attempts=2,
            code="temp code",
            passed=True,
            runtime_sec=70,
            lines_of_code=3,
            tests_run=15
        )
        db.session.add(sub1)
        db.session.add(sub2)
        db.session.add(sub3)
        db.session.add(sub4)
        db.session.commit()

        test_submission = CalculateSubmission(1)
        self.assertEqual(82, test_submission["average time"])
        self.assertEqual(26, test_submission["best time"])
        self.assertAlmostEqual(13.33, test_submission["average attempts"])
        self.assertEqual(3, test_submission["best length"])
        self.assertEqual(2, test_submission["total completed"])
