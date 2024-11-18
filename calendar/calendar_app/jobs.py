# calendar_flask_project/calendar_app/jobs.py

from datetime import datetime, timedelta, date
from . import db
from .models import Event, Log
from .references import events_log_status

def update_event_status():
    """
    Функция для обновления статуса событий и добавления журнала изменений.

    Находит завершенные события за предыдущий день и обновляет их статус на завершенное (is_completed=1).
    Для каждого события создается запись в журнале изменений с указанием завершенного статуса.

    Parameters:
        None

    Returns:
        None
    """
    datetime_yesterday = datetime.combine(date.today(), datetime.min.time()) - timedelta(days=1)
    events = Event.query.filter(Event.end_date==datetime_yesterday).all()
    
    for event in events:
        event.is_completed = 1
        db.session.add(event)
        db.session.commit()
        
        new_log=Log(
            status=events_log_status['completed'],
            dt = datetime.now(),
            user_name = 'calendar_robot',
            event_id = event.id
        )
        db.session.add(new_log)
        db.session.commit()
        