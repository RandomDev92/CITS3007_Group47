# import webdriver
import os
import signal
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing
import threading
import time 
import subprocess

from app import db
from app import create_app


class SeleniumTest(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.server_thread = subprocess.Popen('flask --app "app:create_app(isTest=True)" run', creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        options = Options()
        options.add_argument("--no-sandbox")


        self.driver = webdriver.Chrome()
        time.sleep(2)
        
    def tearDown(self):
        db.session.remove()
        self.app_context.pop()
        self.driver.quit()
        os.kill(self.server_thread.pid, signal.CTRL_C_EVENT)
        self.server_thread.terminate()
        self.server_thread.wait()
        pass


    def testSignupAndLogin(self):
        """Test Signup New Account and Login to Account"""
        self.driver.get('http://localhost:5000')
        signupButton = self.driver.find_element(By.ID, "Signup")
        signupButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        signupForm = wait.until(EC.presence_of_element_located((By.ID, 'SignUpForm')))
        self.assertIsNotNone(signupForm, "Signup Form not Found")
        Username = self.driver.find_element(By.ID, "Username")
        Password = self.driver.find_element(By.ID, "pwd")
        confPassword = self.driver.find_element(By.ID, "cnf-pwd")
        submitButton = self.driver.find_element(By.ID, "Submit")
        Username.send_keys("TestUser")
        Password.send_keys("testPassword")
        confPassword.send_keys("testPassword")
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        LoginForm = wait.until(EC.presence_of_element_located((By.ID, 'LoginForm')))
        self.assertIsNotNone(LoginForm, "Login Form not Found")
        Username = self.driver.find_element(By.ID, "Username")
        Password = self.driver.find_element(By.ID, "pwd")
        Username.send_keys("TestUser")
        Password.send_keys("testPassword")
        submitButton = self.driver.find_element(By.ID, "Submit")
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        HomePage = wait.until(EC.title_is("Speed‑Code–Userpage"))
        self.assertIsNotNone(HomePage, "HomePage not Found")

    def testQuesrtion(self):
        """Test Adding New Question For People to Speed Run"""
        self.driver.get('http://localhost:5000/UploadPage')

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cm-editor")))

        title = self.driver.find_element(By.Id, "title")
        short_desc = self.driver.find_element(By.Id, "shortDesc")
        full_desc = self.driver.find_element(By.Id, "fullDesc")
        tag = self.driver.find_element(By.Id, "tag")

        title.send_keys("Return The Parameter * 5")
        short_desc.send_keys("Assume you are given an integer and return the integer * 5")
        full_desc.send_keys("e.g. Input: 3 , Output:15")
        tag.send_keys("Tag1")
        difficulty_medium = self.driver.find_element(By.Id, "medium")
        difficulty_medium.click()

        code_block = self.driver.find_element(By.Id, "codeBlock")
        code_block.click()
        existing_code = self.driver.execute_script("""
            var editor = document.querySelector(".cm-editor").CodeMirror;
            return editor.getDoc().getValue();
        """)
        new_code = existing_code.replace("value", "return param * 5")
        self.driver.execute_script("""
            var editor = document.querySelector(".cm-editor").CodeMirror;
            editor.getDoc().setValue(arguments[0]);
        """, new_code)


        test_block = self.driver.find_element(By.Id, "testBlock")
        test_block.click()
        test_block.send_keys("{(3): 15, (10): 50, (13): 65}")

        submit_button = self.driver.find_element(By.Id, "submitQu")
        submit_button.click()

        WebDriverWait(self.driver, 10).until(EC.url_changes(self.driver.current_url))



        

