# calendar_flask_project/calendar_app/__init__.py
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from flask_crontab import Crontab

import locale
locale.setlocale(locale.LC_TIME, 'C')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('MY_SECRET_KEY') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

crontab = Crontab(app)

login_manager = LoginManager()
login_manager.init_app(app)

from . import error_handlers, views, references, models, forms

from .jobs import update_event_status

@crontab.job(minute=0, hour=4)
def scheduled_job():
    '''
    Запускает крон-задачу (функцию) из файла jobs.py
    '''
    update_event_status()
   
