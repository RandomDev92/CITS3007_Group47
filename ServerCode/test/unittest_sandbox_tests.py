import unittest
from app.sandbox import testCode

class testSandbox(unittest.TestCase):
    def test_sandbox_test_input(self):
        """Test the Testing Parameters for the User Code"""
        codeOneParam = """def return10(N):
    return 10"""
        testOneParam = r"{(123):10, (1.23):10, ([1]):10, ([1, 2, 3]):10, ('string'):10, ((1, 0)):10}"
        self.assertEqual("All tests passed.", testCode(codeOneParam, testOneParam))

        tesTwoParam = r"{(123, 123):10, (1.23, 1.23):10, ([1], [2]):10, ([1, 2, 3], [1, 2, 3]):10, ('string', 'string2'):10, ((1, 0), (1, 2)):10, (123, 'string'):10}"
        self.assertEqual("An Error has Occured in the Code Block. return10() takes 1 positional argument but 2 were given", testCode(codeOneParam, tesTwoParam))
        codeTwoParam = """def return10(N, B):
    return 10"""
        self.assertEqual("All tests passed.", testCode(codeTwoParam, tesTwoParam))
    

    def test_sandbox_code(self):
        """Test the Testing UserCode Functionality"""
        codeInplace = """def return10(N):
    b = 2
    b +=1
    return 10"""
        testOneParam = r"{(123):10, (1.23):10, ([1]):10, ([1, 2, 3]):10, ('string'):10, ((1, 0)):10}"
        self.assertEqual("All tests passed.", testCode(codeInplace, testOneParam))
        codeManuallyAllowedFunc = """def return10(N):
    sum([1,2,3])
    type(1)
    d = dict()
    s = set()
    return 10"""
        self.assertEqual("All tests passed.", testCode(codeManuallyAllowedFunc, testOneParam))
        codeIter = """def return10(N):
    S = 0
    for i in range(10):
        S+=1
    n = 0
    while(n < S):
        n+=1
    return S"""
        self.assertEqual("All tests passed.", testCode(codeIter, testOneParam))


    def test_sandbox_security(self):
        """Testing the security of the Sandbox"""
        codeImport = """def return10(N):
    import math
    import collections
    import itertools
    return 10"""
        testOneParam = r"{(123):10, (1.23):10, ([1]):10, ([1, 2, 3]):10, ('string'):10, ((1, 0)):10}"
        self.assertEqual("All tests passed.", testCode(codeImport, testOneParam))
        codeIllegalImport = """def return10(N):
    import os
    import sys
    return 10"""
        self.assertEqual("An Error has Occured in the Code Block. 'os' is not a supported import", testCode(codeIllegalImport, testOneParam))
        #user_code here is a local var in sandbox that should not be accessable
        codeAccessGlob = """def return10(N):
    return user_code"""
        self.assertEqual("An Error has Occured in the Code Block. name 'user_code' is not defined", testCode(codeAccessGlob, testOneParam))
        #testing that RestrictedPython catches calls to dangerous functions
        codeFunctions = """def return10(N):
    exec("maliciouscode")
    return user_code"""
        self.assertEqual("An Error has Occured in the Code Block. ('Line 2: Exec calls are not allowed.',)", testCode(codeFunctions, testOneParam))


if __name__ == "__main__":
    unittest.main(verbosity=2)