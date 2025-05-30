# import webdriver
import multiprocessing.process
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
from selenium import webdriver
import multiprocessing
import threading
import time 
import subprocess
from app import create_app


class SeleniumTest(unittest.TestCase):
    def _run_app(self):
        self.app.run()

    def setUp(self):
        self.app = create_app(isTest=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        if os.name == 'posix':
            #multiprocessing.set_start_method("fork")
            #self.server_thread = multiprocessing.Process(target=self._run_app, args=(), daemon=True)
            ctx = multiprocessing.get_context("fork")
            self.server_thread = ctx.Process(target=self._run_app, daemon=True)
            self.server_thread.start()
        if os.name == 'nt':
            self.server_thread = subprocess.Popen('flask --app "app:create_app(isTest=True)" run', creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        options = Options()
        options.add_argument("allow-running-insecure-content")


        self.driver = webdriver.Chrome(options=options)
        time.sleep(2)
        
    def tearDown(self):
        self.app_context.pop()
        self.driver.quit()
        if os.name == 'nt':
            os.kill(self.server_thread.pid, signal.CTRL_C_EVENT)
            self.server_thread.terminate()
            self.server_thread.wait()
        if os.name == 'posix':
            self.server_thread.kill()
        pass


    def testSignupAndLogin(self):
        """Test Signup New Account and Login to Account"""
        self.driver.get("http://127.0.0.1:5000")
        signupButton = self.driver.find_element(By.ID, "Signup")
        signupButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        signupForm = wait.until(EC.presence_of_element_located((By.ID, 'SignUpForm')), "Signup Form not Found")
        Username = self.driver.find_element(By.ID, "Username")
        Password = self.driver.find_element(By.ID, "pwd")
        confPassword = self.driver.find_element(By.ID, "cnf-pwd")
        submitButton = self.driver.find_element(By.ID, "Submit")
        Username.send_keys("SeleniumUser")
        Password.send_keys("testPassword")
        confPassword.send_keys("testPassword")
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        LoginForm = wait.until(EC.presence_of_element_located((By.ID, 'LoginForm')), "Login Form not Found")
        Username = self.driver.find_element(By.ID, "Username")
        Password = self.driver.find_element(By.ID, "pwd")
        Username.send_keys("SeleniumUser")
        Password.send_keys("testPassword")
        submitButton = self.driver.find_element(By.ID, "Submit")
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        UserPage = wait.until(EC.title_is("Speed‑Code–Userpage"), "UserPage not Found")
        time.sleep(0.5)

    def loginTestUser(self):
        #login chunk
        self.driver.get("http://127.0.0.1:5000/LoginPage")
        wait = WebDriverWait(self.driver, timeout=2)
        LoginForm = wait.until(EC.presence_of_element_located((By.ID, 'LoginForm')), "Login Form not Found")
        Username = self.driver.find_element(By.ID, "Username")
        Password = self.driver.find_element(By.ID, "pwd")
        Username.send_keys("TestUser")
        Password.send_keys("Password")
        submitButton = self.driver.find_element(By.ID, "Submit")
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        UserPage = wait.until(EC.title_is("Speed‑Code–Userpage"), "UserPage not Found")      
   
    def testUpload(self):
        """Test Adding New Question For People to Speed Run"""
        self.loginTestUser()

        self.driver.get("http://127.0.0.1:5000/UploadPage")
        
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cm-editor")))

        title = self.driver.find_element(By.ID, "title")
        short_desc = self.driver.find_element(By.ID, "shortDesc")
        full_desc = self.driver.find_element(By.ID, "fullDesc")
        tag = self.driver.find_element(By.ID, "tag")

        title.send_keys("Return The Parameter * 5")
        short_desc.send_keys("Assume you are given an integer and return the integer * 5")
        full_desc.send_keys("e.g. Input: 3 , Output:15")
        tag.send_keys("Math")
        
        
        difficulty_medium = self.driver.find_element(By.ID, "medium")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", difficulty_medium)
        time.sleep(2)
        self.driver.execute_script("arguments[0].click();", difficulty_medium)


        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cm-editor"))
        )
        time.sleep(1)
        
        cm_content_element = self.driver.find_element(By.CLASS_NAME, "cm-content")
        code_block = "def func(param):\n    return param * 5"
        self.driver.execute_script("""
            const element = arguments[0];
            const newText = arguments[1];
            const cm = element?.cmView?.rootView?.view;
            if (!cm) throw new Error("CodeMirror view not found");
            cm.dispatch({
                changes: {
                    from: 0,
                    to: cm.state.doc.length,
                    insert: newText
                }
            });
        """, cm_content_element, code_block)

        test_block = self.driver.find_element(By.ID, "testBlock")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", test_block)
        time.sleep(0.2)
        test_block.click()
        #self.driver.execute_script("arguments[0].click()", test_block)
        
        test_block.send_keys("{(3): 15, (10): 50, (13): 65}")
        
        submit_button = self.driver.find_element(By.ID, "submitQu")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.2)
        submit_button.click()
        wait = WebDriverWait(self.driver, timeout=2)
        LandingPage = wait.until(EC.title_is("Landing Page"), "LandingPage not Found")
        time.sleep(0.5)
        # WebDriverWait(self.driver, 10).until(EC.url_changes(self.driver.current_url))        

    def testAnswering(self):
        """Test Answering a Question"""
        self.loginTestUser()

        #get to search page
        self.driver.get("http://127.0.0.1:5000/SearchPage")
        wait = WebDriverWait(self.driver, timeout=2)
        QuestionCard = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'question-card')), "Question Card not Found")
        time.sleep(0.3)
        QuestionCard.click()

        #open question
        wait = WebDriverWait(self.driver, timeout=2)
        DescPage = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'desc-card')), "Description Page not Found")
        time.sleep(0.3)
        startButton = self.driver.find_element(By.ID, "StartQ")
        startButton.click()

        #begin question answering 
        wait = WebDriverWait(self.driver, timeout=2)
        infoCard = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'info-card')), "Answer page Page not Found")
        cm_content_element = self.driver.find_element(By.CLASS_NAME, "cm-content")
        code_block = """def func(N):
    S = 1
    for i in range(1, N+1):
        S *= i
    return S"""
        self.driver.execute_script("""
            const element = arguments[0];
            const newText = arguments[1];
            const cm = element?.cmView?.rootView?.view;
            if (!cm) throw new Error("CodeMirror view not found");
            cm.dispatch({
                changes: {
                    from: 0,
                    to: cm.state.doc.length,
                    insert: newText
                }
            });
        """, cm_content_element, code_block)

        SubmitButton = self.driver.find_element(By.ID, "TestSubmit")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", SubmitButton)
        time.sleep(0.5)
        SubmitButton.click()
        
        #confirm answer is submitted
        wait = WebDriverWait(self.driver, timeout=2)
        StatCard = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stat-card')),  "Stats page Page not Found")
        time.sleep(0.5)
        
    def testRatings(self):
        self.testAnswering()
        star5 = self.driver.find_element(By.CSS_SELECTOR, '[data-value="5"]')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", star5)
        time.sleep(0.5)
        star5.click()
        submitButton = self.driver.find_element(By.ID, 'SubmitReview')
        submitButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        alertFound = wait.until(EC.presence_of_element_located((By.ID, 'alert')), "Review Not Submitted")
        time.sleep(0.5)

    def testSharing(self):
        self.testSignupAndLogin()
        whitelist = self.driver.find_element(By.ID, 'WriteUser')
        addButton = self.driver.find_element(By.ID, 'AddUser')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", addButton)
        time.sleep(0.5)
        whitelist.send_keys("TestUser")
        addButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        whitelistAllert = wait.until(EC.presence_of_element_located((By.ID, 'successAlert')), "Whitelist not Submitted")
        time.sleep(0.3)
        LogoutButton = self.driver.find_element(By.ID, 'Logout')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", LogoutButton)
        time.sleep(0.5)
        LogoutButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        HomePage = wait.until(EC.title_is("Home"), "HomePage not Found")

        self.loginTestUser()
        SharedPagesButton = self.driver.find_element(By.ID, 'SharedPages')
        SharedPagesButton.click()
        wait = WebDriverWait(self.driver, timeout=2)
        SharedUser = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'user-card')), "SharePage not Found")
        time.sleep(0.3)
        SharedUser.click()
        wait = WebDriverWait(self.driver, timeout=2)
        UserPage = wait.until(EC.title_is("SeleniumUser's Page"), "UserPage not Found")
        time.sleep(0.3)

