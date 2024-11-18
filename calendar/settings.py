# calendar_flask_project/settings.py
import os 

from dotenv import load_dotenv
load_dotenv()

class Config(object): 
    SECRET_KEY = os.getenv('MY_SECRET_KEY') #токен CRF для форм FlaskForm
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') #доступ к базе данных
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_ENV = os.getenv('FLASK_ENV')

