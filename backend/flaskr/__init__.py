import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
SECRET_KEY='dev'
QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def pagenate_questions(request,objs):
    page = request.args.get('page',1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = page*QUESTIONS_PER_PAGE
    return [obj.format() for obj in objs][start:end]


  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
        
    questions = None    
    try:
      page = request.args.get('page',1, type=int)
      categories = Category.query.order_by(Category.id).all()
      current_category = Category.query.order_by(Category.id).first()
      selection_query = Question.query.filter(Category.id==current_category.id).all()
      questions = pagenate_questions(request, selection_query)
  
    except:
      abort(422)

    if len(questions) == 0:
      abort(404)

    data={
      'success': True, 
      'questions':questions,
      'total_questions':len(questions),
      'categories':[category.type for  category in categories ],
      'current_category':current_category.format(),
    }
    return jsonify(data)

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)
    
    data={
      'success': True, 
      'categories':[category.type for category in categories]
    }
    return jsonify(data)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
        
    question_delete = Question.query.filter(Question.id==question_id).one_or_none()
    if question_delete is None:
          print('I am inside it')
          abort(404)    

    try:
      question_delete.delete()
    except:
      abort(422)
    
    data = {'success': True}
    return jsonify(data)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question',None)
    answer = body.get('answer',None) 
    difficulty = body.get('difficulty',None)
    category_id = body.get('category',None)
  
    category_obj = Category.query.get(category_id)
    try:
      new_question = Question(question, answer,  difficulty)
      category_obj._append(new_question)
      

    except Exception as ex:
      abort(422)

    return jsonify({'success': True})
  
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def retrieve_questions_by_category(category_id):
        
    questions=None
    try:
      page = request.args.get('page',1, type=int)
      current_category = Category.query.get(category_id)
      selection_query = Question.query.filter(Question.category==category_id).all()
      questions = pagenate_questions(request, selection_query)

    except:
      abort(422)

    if len(questions) == 0:
            abort(404)

    data={
      'success': True, 
      'questions':questions,
      'total_questions':len(questions),
      'current_category':current_category.format(),
    }
    return jsonify(data)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def question_search():

    data = None
    try:

      search_term = request.args.get('search_term','',type=str)
      results = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
      categories =  Category.query.order_by(Category.id).all()
      

      data={
          'success': True,
          'questions':[ question.format() for question in  results],
          'total_questions':len(results),
          'categories':[category.type for  category in categories ],
          'current_category':results[0].category if results else '',
      }
    except:

      abort(422)
    
    return jsonify(data)
  
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def random_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions',None)
    quiz_category = body.get('quiz_category',None)

    questions = None
    
    if quiz_category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter(Question.category == int(quiz_category['id'])+1).all()
    
   
    current_question = ''
    questions_count = len(questions)
    search_conut = 0
    if questions_count > 0:
      
      while True:
        index = random.randrange(questions_count)
        current_question = questions[index]
        search_conut +=1

        if current_question.id not in previous_questions:
              break
          
        if len(previous_questions) == questions_count or search_conut == questions_count:
              current_question=''
              break
    

    return jsonify({
      'success': True, 
      'question': current_question.format() if current_question else None
    })
    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "bad request"
      }), 400

  return app

    