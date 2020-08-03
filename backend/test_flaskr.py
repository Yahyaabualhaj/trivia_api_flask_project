import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','asdasdasd','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        # create new question
        self.new_question = {
            'question': 'what is the test quesion ?',
            'answer': 'it is just for test',
            'difficulty': 5,
            'category': 'English',
        }

        # data for quiz.
        self.quiz = {
            'previous_questions': 'what is the test quesion ?',
            'quiz_category': 'English',
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 3)

    def test_get_pageinated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

   
    
    def test_delete_question(self):
        id = Question.query.first().id
        res = self.client().delete(f'questions/{id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==id).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(question,None)
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json= self.new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'],True)
    
    def test_question_search(self):
        res = self.client().post('/questions/search?search_term=why')
        data = json.loads(res.data)

        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_create_new_question(self):
        res = self.client().post('/questions', json= self.quiz)
        data = json.loads(res.data)

        self.assertEqual(data['success'],True)
    


        
        



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()