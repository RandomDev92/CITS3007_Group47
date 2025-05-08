from unittest import TestCase
from app import create_app

testapp = create_app(isTest=True)

class BasicTests(TestCase):
    
    def setUp(self):
        