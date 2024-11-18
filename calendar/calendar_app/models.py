# calendar_flask_project/calendar_app/models.py

from datetime import datetime, date, timedelta
from . import db, login_manager
from sqlalchemy.dialects.postgresql import ARRAY
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id): 
    """
    Функция для загрузки пользователя по его идентификатору.

    Parameters:
        id (int): Идентификатор пользователя.

    Returns:
        User: Объект пользователя, соответствующий переданному идентификатору.
    """
    return User.query.get(int(id))


class Holiday(db.Model):
    """
    Модель для хранения информации о праздничных днях.
    Таблица: holidays.

    Attributes:
        id (int): Идентификатор праздничного дня.
        dt (datetime): Дата праздничного дня.
        name (str): Наименование праздничного дня.
    """
    __tablename__ = 'holidays' 
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, index=True, nullable=False, unique=False)
    name = db.Column(db.String(128), nullable=False)





class Event(db.Model):
    """
    Модель для хранения информации о событиях в календарном приложении.
    Таблица: events 

    Attributes:
        id (int): Идентификатор события.
        name (str): Наименование события.
        tag (list): Теги, связанные с событием.
        importance (str): Важность события.
        begin_date (datetime): Начальная дата события.
        end_date (datetime): Конечная дата события.
        owner (str): Владелец события.
        restaurant (list): Рестораны, связанные с событием.
        promotion_type (list): Типы промо-мероприятий.
        brief (str): Краткое описание события.
        picture (str): Путь к изображению.
        instruction (str): Инструкция по событию.
        comment (str): Комментарий к событию.
        is_completed (int): Флаг завершения события.
        summary (str): Сводка о событии.
    """

    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False, index=True, unique=False) 

    tag = db.Column(ARRAY(db.String(128)), nullable=False, unique=False)

    importance = db.Column(db.String(32), nullable=False, unique=False)
    begin_date = db.Column(db.DateTime, index=True, nullable=True, unique=False) 
    end_date = db.Column(db.DateTime, index=True, nullable=True, unique=False)
    owner = db.Column(db.String(64), nullable=False, unique=False)

    restaurant = db.Column(ARRAY(db.String(128)))
    promotion_type = db.Column(ARRAY(db.String(128)))

    brief = db.Column(db.String(256), unique=False, nullable=False)
    picture = db.Column(db.String(256), unique=False, nullable=True)
    instruction = db.Column(db.Text, unique=False, nullable=True)
    comment = db.Column(db.Text, unique=False, nullable=True)
    is_completed = db.Column(db.Integer, nullable=True, unique=False)
    summary = db.Column(db.Text, unique=False, nullable = True)
    #event_dates = db.Column(ARRAY(db.DateTime), index=True, nullable=True, unique=False)




class Log(db.Model):
    """
    Модель для хранения журнала изменений событий.
    Таблица: log
    Attributes:
        id (int): Идентификатор записи в журнале.
        status (str): Статус изменения (создание, редактирование и т.д.).
        dt (datetime): Метка времени изменения.
        user_name (str): Имя пользователя, выполнившего изменение.
        event_id (int): Идентификатор связанного события.
        event (Event): Связь с моделью Event.
    """
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32))
    dt = db.Column(db.DateTime, index=True, nullable=True, unique=False)
    user_name = db.Column(db.String(64))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id')) 

    event = db.relationship('Event', backref='Log') 




class User(db.Model, UserMixin): 
    """
    Модель для хранения информации о пользователях.

    Attributes:
        id (int): Идентификатор пользователя.
        user_name (str): Имя пользователя.
        user_password (str): Пароль пользователя.
        rights (str): Права пользователя.
        user_department (str): Департамент пользователя.
        user_description (str): Описание пользователя.
    """
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32), unique=True, nullable=False)
    user_password = db.Column(db.String(64), unique=False, nullable=False)

    rights = db.Column(db.String(32))  

    user_department = db.Column(db.String(64))
    user_description = db.Column(db.String(128))







