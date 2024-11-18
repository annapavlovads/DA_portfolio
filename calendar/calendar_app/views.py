# calendar_flask_project/calendar_app/views.py

from datetime import date, datetime, timedelta
import calendar
import json

from flask import Flask, redirect, render_template, url_for, flash, abort, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, desc, func, create_engine
from sqlalchemy.dialects.postgresql import array

from . import app, db, bcrypt
from .forms import EventForm, ShortEventForm, SearchEventForm, EditEventForm, MonthForm, WeekForm, SummaryForm, LoginForm
from .models import Holiday, Event, Log, User

from .references import rus_week_from_name_to_int, events_log_status, rus_month, rus_week, user_list, rus_month_from_int_to_string, rus_month_from_string_to_int

from flask_login import login_user, current_user, logout_user

import os 
from dotenv import load_dotenv
load_dotenv()

from .jobs import update_event_status


@app.route('/', methods=['GET', 'POST'])
def welcome_view():
    """
    Отображает страницу для входа на портал (поля для ввода логина и пароля) и содержит обработчик формы входа.

    Методы:
        GET: Отображает страницу приветствия и форму входа.
        POST: Обрабатывает отправленную форму входа.

    Returns:
        response: Редирект на страницу index_view в случае, если пользователь авторизован; 
                  иначе форму входа или страницу с ошибкой.
    """
    if current_user.is_authenticated: 
        return redirect(url_for('index_view'))

    form = LoginForm()

    if form.validate_on_submit(): 

        user = User.query.filter_by(user_name=form.user_name.data).first()

        if user and bcrypt.check_password_hash(user.user_password, form.user_password.data): 
            login_user(user)
            return redirect(url_for('index_view', form=form))
        else: 
            return render_template('100.html')

    return render_template('welcome.html', form=form)

@app.route('/logout')
def logout_view(): 
    """
    Выход из учетной записи пользователя.

    Returns:
        response: Редирект на страницу приветствия welcome_view после успешного выхода из учетной записи.
    """
    logout_user()
    return redirect(url_for('welcome_view'))

@app.route('/search', methods=['GET', 'POST'])
def search_view():
    """
    Отображает страницу поиска событий с возможностью фильтрации по различным критериям.

    Если пользователь не аутентифицирован, перенаправляет на страницу приветствия.
    Производит поиск событий по указанным фильтрам и возвращает результаты.

    Returns:
        response: Страница с перечнем найденных событий. 
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    form = SearchEventForm()

    if request.method=='POST': 
        filters = []
        filter_list = []

        name = form.name.data 
        if name: 
            filters.append(Event.name.ilike(f'%{name}%'))
            filter_list.append(f'Фрагмент имени: {name}')

        is_completed = form.is_completed.data
        if not is_completed: 
            filters.append(Event.is_completed==0)
        condition = 'Да' if is_completed else 'Нет'
        filter_list.append(f'Искать также в завершенных событиях: {condition}')

        owner = form.owner.data
        if owner: 
            or_filters = [Event.owner==o for o in owner]
            filters.append(or_(*or_filters))
            filter_list.append(f'Владельцы события: {" или ".join(owner)}')
        else: 
            filter_list.append('Владелец события любой')


        period_start_date = form.period_start_date.data
        period_end_date = form.period_end_date.data

        if not period_start_date and not period_end_date: 
            filter_list.append('Начало и конец периода не установлены')
        elif period_start_date and not period_end_date: 
            filters.append(Event.end_date >= period_start_date)
            filter_list.append(f'Дата начала периода: {period_start_date.strftime('%d.%m.%Y')}')
        elif not period_start_date and period_end_date: 
            filters.append(Event.begin_date<=period_end_date)
            filter_list.append(f'Дата окончания периода: {period_end_date.strftime('%d.%m.%Y')}')
        elif period_start_date and period_end_date: 
            filters.append(and_(Event.end_date >= period_start_date, Event.begin_date<=period_end_date))
            filter_list.append(f'Дата начала периода: {period_start_date.strftime('%d.%m.%Y')}, Дата окончания периода: {period_end_date.strftime('%d.%m.%Y')}')


        tag = form.tag.data
        tag_selector = form.tag_selector.data
        if tag: 
            tag_filters = [Event.tag.contains([t]) for t in tag]
            if not tag_selector: 
                filters.append(or_(*tag_filters))
                selector_name = ' или '
            if tag_selector: 
                filters.append(and_(*tag_filters))
                selector_name = ' и '
            filter_list.append(f'Теги события: {selector_name.join(tag)}')
        else: 
            filter_list.append('Тег события любой')

        importance = form.importance.data
        if importance: 
            or_filters = [Event.importance==i for i in importance]
            filters.append(or_(*or_filters))
            filter_list.append(f'Важность события: {" или ".join(importance)}')
        else: 
            filter_list.append('Важность события любая')

        restaurant = form.restaurant.data
        restaurant_selector = form.restaurant_selector.data
        if restaurant: 
            restaurant_filters = [Event.restaurant.contains([r]) for r in restaurant]
            if not restaurant_selector: 
                filters.append(or_(*restaurant_filters))
                selector_name = ' или '
            if restaurant_selector: 
                filters.append(and_(*restaurant_filters))
                selector_name = ' и '
            filter_list.append(f'Рестораны события: {selector_name.join(restaurant)}')
        else: 
            filter_list.append('Ресторан события любой')

        promotion_type = form.promotion_type.data
        promotion_type_selector = form.promotion_type_selector.data
        if promotion_type: 
            promotion_type_filters = [Event.promotion_type.contains([pr]) for pr in promotion_type]
            if not promotion_type_selector: 
                filters.append(or_(*promotion_type_filters))
                selector_name = ' или '
            if promotion_type_selector: 
                filters.append(and_(*promotion_type_filters))
                selector_name = ' и '
            filter_list.append(f'Типы промо для события: {selector_name.join(promotion_type)}')
        else: 
            filter_list.append('Тип промо для события любой')
            
        summary_string = ' | '.join(filter_list)

        if filters: 
            events = db.session.query(Event).filter(and_(*filters)).order_by(Event.begin_date).all()
        else: 
            events = db.session.query(Event).order_by(Event.begin_date).all()

        if events:    
            return render_template('event_list.html', events=events, summary_string=summary_string)
        else: 
            return render_template('empty_list.html')
        
    return render_template('search.html', form=form, rus_month=rus_month, rus_week=rus_week)

@app.route('/index')
def index_view():
    """
    Отображает главную страницу приложения.
    Если пользователь аутентифицирован, перенаправляет на страницу входа в проект (личный кабинет).

    Returns:
        response: Страница index.html (личный кабинет, страница входа) со ссылками на различные действия и информацию. 
    """

    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    datetime_today = datetime.combine(date.today(), datetime.min.time())
        
    today_events = Event.query.filter(Event.begin_date<=datetime_today).filter(
                                       Event.end_date>=datetime_today).all()


    holiday_today = Holiday.query.filter(Holiday.dt==datetime_today).first()

    return render_template('index.html' , 
                           datetime_today=datetime_today, 
                           events=today_events, 
                           holiday_today=holiday_today, 
                           rus_month=rus_month, 
                           rus_week=rus_week
                           )

@app.route('/yesterday')
def yesterday_events_view():
    """
    Отображает события, которые завершились вчера.

    Показывает список событий, завершившихся вчера, и информацию о празднике, прошедшем вчера.

    Returns:
        response: Страница yesterday.html с событиями и праздником, прошедшими вчера.
    """

    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

  
    datetime_yesterday = datetime.combine(date.today() - timedelta(days=1), 
                                      datetime.min.time())
        
    yesterday_events = Event.query.filter(Event.end_date==datetime_yesterday).all()

    holiday_yesterday = Holiday.query.filter(Holiday.dt==datetime_yesterday).first()

    return render_template('yesterday.html' , 
                           datetime_today=datetime_yesterday, 
                           events=yesterday_events, 
                           holiday_today=holiday_yesterday, 
                           rus_week=rus_week, 
                           rus_month=rus_month
                           )

@app.route('/tomorrow')
def tomorrow_events_view():
    """
    Отображает события, которые начнутся завтра.

    Показывает список событий, которые начнутся завтра, и информацию о празднике, запланированном на завтра.

    Returns:
        response: Страница tomorrow.html с событиями и праздником, запланированными на завтра.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    datetime_tomorrow = datetime.combine(date.today() + timedelta(days=1), 
                                      datetime.min.time())
        
    tomorrow_events = Event.query.filter(Event.begin_date==datetime_tomorrow).all()

    holiday_tomorrow = Holiday.query.filter(Holiday.dt==datetime_tomorrow).first()

    return render_template('tomorrow.html' , 
                           datetime_today=datetime_tomorrow, 
                           events=tomorrow_events, 
                           holiday_today=holiday_tomorrow, 
                           rus_week=rus_week, 
                           rus_month=rus_month
                           )

@app.route('/eventhistory<int:id>')
def event_history_view(id):
    """
    Отображает историю события.

    Находит и отображает историю события с заданным идентификатором.

    Parameters:
        id (int): Идентификатор события, для которого нужно найти историю.

    Returns:
        response: Страница event_history.html с историей события.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    event_id = id
    event_log = Log.query.filter(Log.event_id==event_id).all()
    
    return render_template('event_history.html', event_log=event_log)

@app.route('/event<int:id>')
def event_view(id):
    """
    Отображает информацию о конкретном событии.

    Находит и отображает информацию о событии с заданным идентификатором.

    Parameters:
        id (int): Идентификатор события, информацию о котором нужно показать.

    Returns:
        response: Страница event.html с информацией о событии.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    event = Event.query.get_or_404(id)

    return render_template('event.html', event=event, rus_week=rus_week, rus_month=rus_month)

@app.route('/edit<int:id>', methods=['GET', 'POST'])
def edit_event_view(id):
    """
    Редактирует событие с указанным идентификатором.

    Находит и редактирует информацию о событии с заданным идентификатором.
    В случае успешного сохранения формы редактирования добавляет запись в журнал изменений.

    Parameters:
        id (int): Идентификатор события, которое требуется отредактировать.

    Returns:
        response: Перенаправление на страницу просмотра отредактированного события после успешного сохранения.
                 Страница редактирования события с формой для редактирования информации о событии.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    event = Event.query.get_or_404(id)

    form = EditEventForm(obj=event)

    
    # Обновляем значения события на основе данных из формы
    #if form.validate_on_submit():
    if request.method=='POST' and form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        #flash('Событие успешно отредактировано!')
        # Перенаправляем пользователя на страницу, где отображается 
        # отредактированное событие
        
        current_moment = datetime.now()
        new_log_string = Log(
            status = events_log_status['edited'], 
            dt = current_moment,
            user_name = current_user.user_name, #'calendar_admin',  #потом добавить текущего юзера
            event_id = event.id #или id
            )
        db.session.add(new_log_string)
        db.session.commit()

        return redirect(url_for('event_view', id=id))

    return render_template('edit.html', form=form, 
                            event=event, rus_week=rus_week, 
                            rus_month=rus_month)

@app.route('/finish_event_view<id>')
def finish_event_view(id): 
    """
    Завершает событие по его идентификатору.

    Если пользователь аутентифицирован, завершает событие с указанным идентификатором.
    Добавляет соответствующую запись в журнал изменений.

    Parameters:
        id (int): Идентификатор события, которое требуется завершить.

    Returns:
        response: Страница event.html с информацией о завершенном событии.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    event = Event.query.get_or_404(id)
    if event.is_completed!=1: 
        event.is_completed = 1
        current_moment = datetime.now()
        new_log=Log(
            status=events_log_status['completed'],
            dt = current_moment,
            user_name = current_user.user_name, #= 'calendar_admin',
            event_id = event.id
            )
        db.session.add(event)
        db.session.add(new_log)
        db.session.commit()

    return render_template('event.html', event=event, rus_week=rus_week, rus_month=rus_month)

@app.route('/summary_event_view<id>', methods=['GET', 'POST'])
def summary_event_view(id): 
    """
    Просмотр и редактирование сводки о событии по его идентификатору.

    Если пользователь аутентифицирован, позволяет просматривать и редактировать сводку о событии с указанным идентификатором.
    Сохраняет изменения и добавляет запись в журнал изменений.

    Parameters:
        id (int): Идентификатор события, для которого нужно просмотреть и отредактировать сводку.

    Returns:
        response: Перенаправление на страницу просмотра события после успешного сохранения изменений.
                 Страница редактирования сводки события с формой для внесения изменений.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    event = Event.query.get_or_404(id)
    form = SummaryForm(obj=event)
    
    if request.method=='POST':
        form.populate_obj(event)
        db.session.commit()
        
        current_moment = datetime.now()
        new_log_string = Log(
            status = events_log_status['summarized'], 
            dt = current_moment,
            user_name = current_user.user_name, #'calendar_admin',  #потом добавить текущего юзера
            event_id = event.id #или id
            )
        db.session.add(new_log_string)
        db.session.commit()

        return redirect(url_for('event_view', id=id))

    return render_template('summary.html', form=form, event=event, rus_week=rus_week, rus_month=rus_month)

@app.route('/resume_event_view<id>')
def resume_event_view(id): 
    """
    Возобновляет событие по его идентификатору.

    Если пользователь аутентифицирован, возобновляет завершенное событие с указанным идентификатором.
    Добавляет соответствующую запись в журнал изменений.

    Parameters:
        id (int): Идентификатор события, которое требуется возобновить.

    Returns:
        response: Страница event.html с информацией о возобновленном событии.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    event = Event.query.get_or_404(id)
    if event.is_completed==1: 
        event.is_completed = 0
        current_moment = datetime.now()
        new_log=Log(
            status=events_log_status['resumed'],
            dt = current_moment,
            user_name = current_user.user_name, #= 'calendar_admin',
            event_id = event.id
            )
        db.session.add(event)
        db.session.add(new_log)
        db.session.commit()

    return render_template('event.html', event=event, rus_week=rus_week, rus_month=rus_month)

@app.route('/no_add')
def no_add_view(): 
    """
    Отображает страницу с сообщением о недоступности добавления.

    Если пользователь не аутентифицирован, перенаправляет на страницу приветствия.

    Returns:
        response: Страница no_add.html с сообщением о недоступности добавления событий.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    return render_template('no_add.html')

@app.route('/user_activity')
def user_activity_view(): 
    """
    Отображает активность пользователей за последние 7 дней.

    Если пользователь аутентифицирован, показывает результаты активности пользователей за последнюю неделю.
    
    Returns:
        response: Страница user_activity.html с информацией об активности пользователей.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    today = datetime.combine(date.today(), datetime.min.time())
    two_days_ago = today - timedelta(days=7)

    log_dict = {}

    for user in user_list: 
        
        logs = db.session.query(Log.status, func.count(Log.event_id)).filter(
            Log.user_name==user, Log.dt >= two_days_ago, Log.dt <= datetime.now()).group_by(
            Log.status).order_by(Log.status).all()

        log_dict[user] = logs

    return render_template('user_activity.html',
                    today=today, 
                    two_days_ago=two_days_ago, 
                    logs=log_dict,
                    rus_week=rus_week, 
                    rus_month=rus_month)

@app.route('/fastsearch', methods=['GET', 'POST'])
def fast_search_view(): 
    """
    Быстрый поиск событий по текстовому запросу.

    Если пользователь аутентифицирован, выполняет поиск событий по словам запроса в имени, ресторанах и тегах.
    Возвращает список событий, удовлетворяющих запросу.

    Returns:
        response: Страница event_list.html с найденными событиями или страница с сообщением об отсутствии результатов.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    t_input = request.args.get('text')
    text= t_input.split( )

    events=[]
    filters=[]
    

    for word in text:
        filters.append(Event.name.ilike(f'%{word}%'))
        filters.append(
            func.array_to_string(Event.restaurant, '').ilike(f'%{word}%')
            )
        filters.append(
            func.array_to_string(Event.tag, '').ilike(f'%{word}%')
            )
    
        
    events = db.session.query(Event).filter(
        or_(*filters)).filter(Event.is_completed==0).all() 

    if events:    
        return render_template('event_list.html', events=events, summary_string=t_input)
    else: 
        return render_template('empty_list.html')

@app.route('/add', methods=['GET', 'POST'])
def add_view():
    """
    Добавляет новое событие в базу данных на основе данных из формы.

    Если текущий пользователь аутентифицирован, позволяет добавить новое событие в базу данных.
    Добавляет запись о создании события в журнал изменений.

    Returns:
        response: Страница add_success.html с информацией об успешном добавлении события или страница добавления события.
    """

    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    if current_user.user_name=='calendar_reader': 
        return render_template('no_add.html') 
    
    if current_user.user_name=='calendar_admin': 
        form = EventForm()
    else: 
        form = ShortEventForm()

    if form.validate_on_submit(): 

        if current_user.user_name!='calendar_admin': 
            real_owner = current_user.user_department 
        else: 
            real_owner = form.owner.data


        new_event = Event(
            name = form.name.data,
            tag = form.tag.data, 
            importance = form.importance.data, 
            begin_date = form.begin_date.data,
            end_date = form.end_date.data,
            owner = real_owner,
            restaurant = form.restaurant.data,
            promotion_type = form.promotion_type.data, 
            brief = form.brief.data, 
            picture = form.picture.data, 
            instruction = form.instruction.data, 
            comment = form.comment.data,
            is_completed = 0
        )

        db.session.add(new_event)
        db.session.commit()

        current_moment = datetime.now() #+ timedelta(hours=3) 

        new_log_string = Log(
            status = events_log_status['created'], 
            dt = current_moment,
            user_name = current_user.user_name,
            event_id = new_event.id
        )

        db.session.add(new_log_string)
        db.session.commit()

        repeat_event = form.repeat_event.data
        if repeat_event: 
            repeat_days = [rus_week_from_name_to_int[x] for x in form.repeat_days.data]

            end_of_repeat_date = form.end_of_repeat_date.data

            this_date = form.end_date.data + timedelta(days=1)

            while this_date <= end_of_repeat_date: 
                if this_date.weekday() in repeat_days: 
                    new_event = Event(
                        name = form.name.data,
                        tag = form.tag.data, 
                        importance = form.importance.data, 
                        begin_date = this_date,
                        end_date = this_date,
                        owner = real_owner,
                        restaurant = form.restaurant.data,
                        promotion_type = form.promotion_type.data, 
                        brief = form.brief.data, 
                        picture = form.picture.data, 
                        instruction = form.instruction.data, 
                        comment = form.comment.data,
                        is_completed = 0
                        )
                    db.session.add(new_event)
                    db.session.commit()

                    new_log_string = Log(
                    status = events_log_status['created'], 
                    dt = current_moment,
                    user_name = current_user.user_name, 
                    event_id = new_event.id)

                    db.session.add(new_log_string)
                    db.session.commit()

                this_date = this_date + timedelta(days=1)             

        return render_template('add_success.html', new_id=new_event.id) 

    return render_template('add.html', form=form, rus_week=rus_week, rus_month=rus_month)

@app.route('/week', methods=['GET', 'POST'])
def week_view():
    """
    Отображает события на текущей неделе с учетом фильтров.

    Если пользователь аутентифицирован, позволяет просматривать события на текущей неделе с возможностью применения фильтров.
    Показывает события каждый день недели и учитывает выбранные фильтры.

    Returns:
        response: Страница this_week.html с событиями на текущей неделе после применения фильтров.
                 Страница empty_list.html, если результаты по фильтрам отсутствуют.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    form = WeekForm()

    if request.method=='POST': 

        filters = []
        filter_list = []
        filters_moving_dict = {}

        week_begin_date = form.week_begin_date.data
        if not week_begin_date: 
            week_begin_date = datetime.combine(date.today(), datetime.min.time())

        week_dates = [week_begin_date + timedelta(days=i) for i in range(7)]

        owner = form.owner.data
        if owner: 
            filters_moving_dict['owner'] = owner
            or_filters = [Event.owner==o for o in owner]
            filters.append(or_(*or_filters))
            filter_list.append(f'Владельцы события: {", ".join(owner)}')
        else: 
            filter_list.append('Владелец события любой')

        tag = form.tag.data
        if tag: 
            filters_moving_dict['tag'] = tag
            or_filters = [Event.tag.contains([t]) for t in tag]
            filters.append(or_(*or_filters))
            filter_list.append(f'Теги события: {", ".join(tag)}')
        else: 
            filter_list.append('Тег события любой')

        restaurant = form.restaurant.data
        if restaurant: 
            filters_moving_dict['restaurant'] = restaurant
            or_filters = [Event.restaurant.contains([r]) for r in restaurant]
            filters.append(or_(*or_filters))
            filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
        else:
            filter_list.append('Ресторан события любой')

        show_completed = form.show_completed.data
        filters_moving_dict['show_completed'] = show_completed
        if not show_completed: 
            filters.append(Event.is_completed==0)
        condition = 'Да' if show_completed else 'Нет'
        filter_list.append(f'Также включать завершенные события: {condition}')
        
        filters_json_string = json.dumps(filters_moving_dict)
        summary_string = ' | '.join(filter_list)


        week_events = []
        
        for d in week_dates: 

            events = db.session.query(Event).filter(
                and_(*filters)).filter(Event.begin_date<=d
                ).filter(Event.end_date>=d).order_by(desc(
                    Event.begin_date)).all()
                    
            week_events.append(events)
            
        week_begin_date = week_begin_date.strftime('%d.%m.%Y')

        if week_events:
            return render_template('this_week.html', 
                                    week_dates=week_dates, 
                                    week_events=week_events, 
                                    rus_week=rus_week, 
                                    rus_month=rus_month,
                                    summary_string=summary_string, 
                                    week_begin_date=week_begin_date, 
                                    filters_json_string=filters_json_string)
        else: 
            return render_template('empty_list.html')
    
    return render_template('week.html', 
                           form=form, 
                           rus_week=rus_week, 
                           rus_month=rus_month)

@app.route('/next_week_view/<week_begin_date>/<filters_json_string>')
def next_week_view(week_begin_date, filters_json_string): 
    
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    filters_json_dict = json.loads(filters_json_string)
    
    owner = filters_json_dict.get('owner')
    tag = filters_json_dict.get('tag')
    restaurant = filters_json_dict.get('restaurant')
    show_completed = filters_json_dict.get('show_completed')
    
    week_begin_date = datetime.strptime(week_begin_date, "%d.%m.%Y")
    
    week_begin_date = week_begin_date + timedelta(days=7)
    
    week_dates = [week_begin_date + timedelta(days=i) for i in range(7)]
    
    filters = []
    filter_list = []
    
    if owner: 
        or_filters = [Event.owner==o for o in owner]
        filters.append(or_(*or_filters))
        filter_list.append(f'Владельцы события: {", ".join(owner)}')
    else: 
        filter_list.append('Владелец события любой')

    
    if tag: 
        or_filters = [Event.tag.contains([t]) for t in tag]
        filters.append(or_(*or_filters))
        filter_list.append(f'Теги события: {", ".join(tag)}')
    else: 
        filter_list.append('Тег события любой')
        
    
    if restaurant: 
        or_filters = [Event.restaurant.contains([r]) for r in restaurant]
        filters.append(or_(*or_filters))
        filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
    else:
        filter_list.append('Ресторан события любой')

    if not show_completed: 
        filters.append(Event.is_completed==0)
    condition = 'Да' if show_completed else 'Нет'
    filter_list.append(f'Также включать завершенные события: {condition}')
        
    summary_string = ' | '.join(filter_list)

    week_events = []

    for d in week_dates: 
        events = db.session.query(Event).filter(
                and_(*filters)).filter(Event.begin_date<=d
                ).filter(Event.end_date>=d).order_by(desc(
                    Event.begin_date)).all()
                    
        week_events.append(events)
        
    week_begin_date = week_begin_date.strftime('%d.%m.%Y')

    if week_events:
        return render_template('this_week.html', 
                                    week_dates=week_dates, 
                                    week_events=week_events, 
                                    rus_week=rus_week, 
                                    rus_month=rus_month,
                                    summary_string=summary_string, 
                                    week_begin_date=week_begin_date, 
                                    filters_json_string=filters_json_string)
    else: 
        return render_template('empty_list.html')


@app.route('/prev_week_view/<week_begin_date>/<filters_json_string>')
def prev_week_view(week_begin_date, filters_json_string): 
    """
    Отображает события на предыдущей неделе с учетом фильтров.

    Если пользователь аутентифицирован, позволяет просматривать события на текущей неделе с возможностью применения фильтров.
    Показывает события каждый день недели и учитывает выбранные фильтры.

    Returns:
        response: Страница prev_week.html с событиями на текущей неделе после применения фильтров.
                 Страница empty_list.html, если результаты по фильтрам отсутствуют.
    """    
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    filters_json_dict = json.loads(filters_json_string)
    
    owner = filters_json_dict.get('owner')
    tag = filters_json_dict.get('tag')
    restaurant = filters_json_dict.get('restaurant')
    show_completed = filters_json_dict.get('show_completed')
    
    week_begin_date = datetime.strptime(week_begin_date, "%d.%m.%Y")
    
    week_begin_date = week_begin_date - timedelta(days=7)
    
    week_dates = [week_begin_date + timedelta(days=i) for i in range(7)]
    
    filters = []
    filter_list = []
    
    if owner: 
        or_filters = [Event.owner==o for o in owner]
        filters.append(or_(*or_filters))
        filter_list.append(f'Владельцы события: {", ".join(owner)}')
    else: 
        filter_list.append('Владелец события любой')

    
    if tag: 
        or_filters = [Event.tag.contains([t]) for t in tag]
        filters.append(or_(*or_filters))
        filter_list.append(f'Теги события: {", ".join(tag)}')
    else: 
        filter_list.append('Тег события любой')
        
    
    if restaurant: 
        or_filters = [Event.restaurant.contains([r]) for r in restaurant]
        filters.append(or_(*or_filters))
        filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
    else:
        filter_list.append('Ресторан события любой')

    if not show_completed: 
        filters.append(Event.is_completed==0)
    condition = 'Да' if show_completed else 'Нет'
    filter_list.append(f'Также включать завершенные события: {condition}')
        
    summary_string = ' | '.join(filter_list)

    week_events = []

    for d in week_dates: 
        events = db.session.query(Event).filter(
                and_(*filters)).filter(Event.begin_date<=d
                ).filter(Event.end_date>=d).order_by(desc(
                    Event.begin_date)).all()
                    
        week_events.append(events)
        
    week_begin_date = week_begin_date.strftime('%d.%m.%Y')

    if week_events:
        return render_template('this_week.html', 
                                    week_dates=week_dates, 
                                    week_events=week_events, 
                                    rus_week=rus_week, 
                                    rus_month=rus_month,
                                    summary_string=summary_string, 
                                    week_begin_date=week_begin_date, 
                                    filters_json_string=filters_json_string)
    else: 
        return render_template('empty_list.html')


@app.route('/thisweek')
def this_week_view():
    """
    Отображает события на текущей неделе без фильтров.

    Если пользователь аутентифицирован, показывает события на текущей неделе без применения фильтров.
    Показывает события каждый день недели без учета фильтров.

    Returns:
        response: Страница this_week_only.html с событиями на текущей неделе без фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    datetime_today = datetime.combine(date.today(), datetime.min.time())
    start_of_week = datetime_today - timedelta(days=datetime_today.weekday())
    
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    week_events = []

    for d in week_dates: 
        events = Event.query.filter(Event.begin_date<=d).filter(
                                       Event.end_date>=d).order_by(Event.importance).all()
        week_events.append(events)


    return render_template('this_week_only.html', week_dates=week_dates, week_events=week_events, rus_week=rus_week, rus_month=rus_month)

@app.route('/my_thisweek')
def my_this_week_view():
    """
    Отображает события для авторизованного пользователя на текущей неделе.

    Если пользователь аутентифицирован, показывает события пользователя на текущей неделе.
    Показывает события пользователя каждый день недели с сортировкой по важности.

    Returns:
        response: Страница my_this_week.html с событиями пользователя на текущей неделе.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    datetime_today = datetime.combine(date.today(), datetime.min.time())
    start_of_week = datetime_today - timedelta(days=datetime_today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    week_events = []

    for d in week_dates: 
        events = Event.query.filter(
            Event.begin_date<=d).filter(
                Event.end_date>=d).order_by(
                    Event.importance).all()
        week_events.append(events)


    return render_template('my_this_week.html', week_dates=week_dates, 
            week_events=week_events, rus_week=rus_week, rus_month=rus_month)

@app.route('/month', methods=['GET', 'POST'])
def month_view():
    """
    Отображает события в выбранном месяце с учетом фильтров.

    Если пользователь аутентифицирован, позволяет просматривать события в выбранном месяце с возможностью применения фильтров.
    Показывает события каждый день месяца и учитывает выбранные фильтры.

    Returns:
        response: Страница month.html с событиями в выбранном месяце после применения фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    form = MonthForm()

    if request.method=='POST': 

        filters = []
        filter_list = []
        filters_moving_dict = {}

        datetime_today = datetime.combine(date.today(), datetime.min.time())

        year = int(form.year.data)
        if not year: 
            year = datetime_today.year
        filter_list.append(f'Год: {year}')

        month = int(rus_month_from_string_to_int[form.month.data])
        if not month: 
            month = datetime_today.month
        filter_list.append(f'Месяц: {rus_month_from_int_to_string[month]}')

        first_month_date=datetime(year, month, 1)
        last_month_date = first_month_date.replace(
        day=calendar.monthrange(
            year, 
            month
            )[1]
            )

        owner = form.owner.data
        if owner: 
            filters_moving_dict['owner'] = owner
            or_filters = [Event.owner==o for o in owner]
            filters.append(or_(*or_filters))
            filter_list.append(f'Владельцы события: {", ".join(owner)}')
        else: 
            filter_list.append('Владелец события любой')

        tag = form.tag.data
        if tag: 
            filters_moving_dict['tag'] = tag
            or_filters = [Event.tag.contains([t]) for t in tag]
            filters.append(or_(*or_filters))
            filter_list.append(f'Теги события: {", ".join(tag)}')
        else: 
            filter_list.append('Тег события любой')

        restaurant = form.restaurant.data
        if restaurant: 
            filters_moving_dict['restaurant'] = restaurant
            or_filters = [Event.restaurant.contains([r]) for r in restaurant]
            filters.append(or_(*or_filters))
            filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
        else:
            filter_list.append('Ресторан события любой')

        only_not_completed = form.only_not_completed.data
        if only_not_completed: 
            filters_moving_dict['only_not_completed'] = only_not_completed
            filters.append(Event.is_completed==0)
        else: 
            only_not_completed = ''
        condition = 'Да' if only_not_completed else 'Нет'
        filter_list.append(f'Только незавершенные события: {condition}')

        filters_json_string = json.dumps(filters_moving_dict)
        summary_string = ' | '.join(filter_list)

        current_month_events = []

        current_month = calendar.monthcalendar(year, month)

        for week in current_month: 
            this_week_events=[]
            for d in week: 
                if d >= 1: 
                    needed_date_dt = datetime(year, month, d)
                    date_events = db.session.query(Event).filter(
                    Event.begin_date<=needed_date_dt).filter(
                        Event.end_date>=needed_date_dt).filter(
                        and_(*filters)).order_by(
                            Event.importance).all()
                    this_week_events.append((needed_date_dt, date_events))
                else: 
                    this_week_events.append(('', ''))

            current_month_events.append(this_week_events)
  
        if current_month_events:
            return render_template('this_month.html', 
                            rus_week=rus_week, 
                            rus_month=rus_month, 
                            first_month_date=first_month_date, 
                            last_month_date=last_month_date, 
                            this_year=year, 
                            datetime_today=datetime_today,
                            this_month=month, 
                            events=current_month_events, 
                            rus_month_from_int_to_string=rus_month_from_int_to_string, 
                            rus_month_from_string_to_int=rus_month_from_string_to_int, 
                            summary_string=summary_string,
                            filters_json_string=filters_json_string)
        else: 
            return render_template('empty_list.html')
    
    return render_template('month.html', form=form, rus_week=rus_week, rus_month=rus_month)

@app.route('/thismonth')
def this_month_view():
    """
    Отображает события текущего месяца без применения фильтров.

    Если пользователь аутентифицирован, показывает события текущего месяца без применения фильтров.
    Показывает события каждый день текущего месяца.

    Returns:
        response: Страница this_month_only.html с событиями текущего месяца без применения фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    datetime_today = datetime.combine(date.today(), datetime.min.time())
    this_year = datetime_today.year
    this_month = datetime_today.month

    first_month_date = datetime_today.replace(day=1)
    last_month_date = first_month_date.replace(
        day=calendar.monthrange(
            datetime_today.year, 
            datetime_today.month
            )[1]
            )

    current_month = calendar.monthcalendar(this_year, this_month)

    current_month_events = []

    for week in current_month: 
        this_week_events=[]
        for d in week: 
            if d >= 1: 
                needed_date_dt = datetime(this_year, this_month, d)
                date_events = Event.query.filter(
                    Event.begin_date<=needed_date_dt).filter(
                        Event.end_date>=needed_date_dt).order_by(
                            Event.importance).all()
                this_week_events.append((needed_date_dt, date_events))
            else: 
                this_week_events.append(('', ''))
        current_month_events. append(this_week_events)

    return render_template('this_month_only.html', 
                            rus_week=rus_week, 
                            rus_month=rus_month, 
                            datetime_today=datetime_today, 
                            first_month_date=first_month_date, 
                            last_month_date=last_month_date, 
                            this_year=this_year, 
                            this_month=this_month, 
                            events=current_month_events, 
                            rus_month_from_int_to_string=rus_month_from_int_to_string, 
                            rus_month_from_string_to_int=rus_month_from_string_to_int)

@app.route('/get_all_next_month_events/<this_year>/<this_month>/<filters_json_string>')
def get_all_next_month_events(this_year, this_month, filters_json_string): 
    """
    Получает все события следующего месяца с учетом заданных фильтров.

    Если пользователь аутентифицирован, возвращает все события следующего месяца с применением выбранных фильтров.
    Учитывает фильтры по владельцам событий, тегам, ресторанам и состоянию завершенности.

    Parameters:
        this_year (str): Год следующего месяца.
        this_month (str): Месяц следующего месяца.
        filters_json_string (str): JSON-строка с фильтрами.

    Returns:
        response: Страница this_month.html с событиями следующего месяца после применения фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    filters_json_dict = json.loads(filters_json_string)
   
    only_not_completed = filters_json_dict.get('only_not_completed')
    owner = filters_json_dict.get('owner')
    tag= filters_json_dict.get('tag')
    restaurant = filters_json_dict.get('restaurant')

    filters=[]
    filter_list = []
    
    this_month = int(this_month)
    this_year = int(this_year)
    
    if this_month<=11: 
        this_month+=1
    else: 
        this_month=1
        this_year= int(this_year) + 1

    first_month_date = datetime(this_year,this_month,1)
    last_month_date = first_month_date.replace(
        day=calendar.monthrange(
            this_year, 
            this_month
            )[1]
            )
    
    if owner: 
        or_filters = [Event.owner==o for o in owner]
        filters.append(or_(*or_filters))
        filter_list.append(f'Владельцы события: {", ".join(owner)}')
    else: 
        filter_list.append('Владелец события любой')

    if tag:
        or_filters = [Event.tag.contains([t]) for t in tag]
        filters.append(or_(*or_filters))
        filter_list.append(f'Теги события: {", ".join(tag)}')
    else: 
        filter_list.append('Тег события любой')

    if restaurant: 
        or_filters = [Event.restaurant.contains([r]) for r in restaurant]
        filters.append(or_(*or_filters))
        filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
    else:
        filter_list.append('Ресторан события любой')

    if only_not_completed and only_not_completed!=0: 
        filters.append(Event.is_completed==0)
    condition = 'Да' if (only_not_completed and only_not_completed!=0) else 'Нет'
    filter_list.append(f'Только незавершенные события: {condition}')

    summary_string = ' | '.join(filter_list)
        
    current_month = calendar.monthcalendar(this_year, this_month)

    current_month_events = []

    for week in current_month: 
        this_week_events=[]
        for d in week: 
            if d >= 1: 
                needed_date_dt = datetime(this_year, this_month, d)
                date_events = db.session.query(Event).filter(
                    Event.begin_date<=needed_date_dt).filter(
                        Event.end_date>=needed_date_dt).filter(
                        and_(*filters)).order_by(
                            Event.importance).all()
                this_week_events.append((needed_date_dt, date_events))
            else: 
                this_week_events.append(('', ''))
        current_month_events.append(this_week_events)

    return render_template('this_month.html', 
                            rus_week=rus_week, 
                            rus_month=rus_month, 
                            first_month_date=first_month_date, 
                            last_month_date=last_month_date, 
                            this_year=this_year, 
                            this_month=this_month, 
                            events=current_month_events, 
                            rus_month_from_int_to_string=rus_month_from_int_to_string, 
                            rus_month_from_string_to_int=rus_month_from_string_to_int, 
                            filters_json_string=filters_json_string, 
                            summary_string=summary_string
                            )

@app.route('/get_all_prev_month_events/<int:this_year>/<int:this_month>/<filters_json_string>')
def get_all_prev_month_events(this_year,this_month, filters_json_string):
    """
    Получает все события предыдущего месяца с учетом заданных фильтров.

    Если пользователь аутентифицирован, возвращает все события предыдущего месяца с применением выбранных фильтров.
    Учитывает фильтры по владельцам событий, тегам, ресторанам и состоянию завершенности.

    Parameters:
        this_year (int): Год предыдущего месяца.
        this_month (int): Месяц предыдущего месяца.
        filtersjsonstring (str): JSON-строка с фильтрами.

    Returns:
        response: Страница this_month.html с событиями предыдущего месяца после применения фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    filters_json_dict = json.loads(filters_json_string)
   
    only_not_completed = filters_json_dict.get('only_not_completed')
    owner = filters_json_dict.get('owner')
    tag= filters_json_dict.get('tag')
    restaurant = filters_json_dict.get('restaurant')

    filters=[]
    filter_list = []

    this_month = int(this_month)
    this_year = int(this_year)
    
    if this_month==1: 
        this_month = 12
        this_year = this_year - 1
    else: 
        this_month = this_month - 1


    first_month_date = datetime(this_year,this_month,1)
    last_month_date = first_month_date.replace(
        day=calendar.monthrange(
            this_year, 
            this_month
            )[1]
            )
    
    if owner: 
        or_filters = [Event.owner==o for o in owner]
        filters.append(or_(*or_filters))
        filter_list.append(f'Владельцы события: {", ".join(owner)}')
    else: 
        filter_list.append('Владелец события любой')

    if tag:
        or_filters = [Event.tag.contains([t]) for t in tag]
        filters.append(or_(*or_filters))
        filter_list.append(f'Теги события: {", ".join(tag)}')
    else: 
        filter_list.append('Тег события любой')

    if restaurant: 
        or_filters = [Event.restaurant.contains([r]) for r in restaurant]
        filters.append(or_(*or_filters))
        filter_list.append(f'Рестораны события: {", ".join(restaurant)}')
    else:
        filter_list.append('Ресторан события любой')

    if only_not_completed and only_not_completed!=0: 
        filters.append(Event.is_completed==0)
    condition = 'Да' if (only_not_completed and only_not_completed!=0) else 'Нет'
    filter_list.append(f'Только незавершенные события: {condition}')

    summary_string = ' | '.join(filter_list)
        
    current_month = calendar.monthcalendar(this_year, this_month)

    current_month_events = []

    for week in current_month: 
        this_week_events=[]
        for d in week: 
            if d >= 1: 
                needed_date_dt = datetime(this_year, this_month, d)
                date_events = db.session.query(Event).filter(
                    Event.begin_date<=needed_date_dt).filter(
                        Event.end_date>=needed_date_dt).filter(
                        and_(*filters)).order_by(
                            Event.importance).all()
                this_week_events.append((needed_date_dt, date_events))
            else: 
                this_week_events.append(('', ''))
        current_month_events.append(this_week_events)

    return render_template('this_month.html', 
                            rus_week=rus_week, rus_month=rus_month, 
                            first_month_date=first_month_date, 
                            last_month_date=last_month_date, 
                            this_year=this_year, 
                            this_month=this_month, 
                            events=current_month_events, 
                            rus_month_from_int_to_string=rus_month_from_int_to_string, 
                            rus_month_from_string_to_int=rus_month_from_string_to_int, 
                            filters_json_string=filters_json_string, 
                            summary_string=summary_string
                            )

@app.route('/mythismonth')
def my_this_month_view():
    """
    Отображает события текущего месяца пользователя без применения фильтров.

    Если пользователь аутентифицирован, показывает события пользователя на текущий месяц без применения фильтров.
    Показывает события пользователя каждый день текущего месяца.

    Returns:
        response: Страница this_month_only.html с событиями текущего месяца пользователя без применения фильтров.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    datetime_today = datetime.combine(date.today(), datetime.min.time())

    first_month_date = datetime_today.replace(day=1)
    last_month_date = first_month_date.replace(
        day=calendar.monthrange(
            datetime_today.year, 
            datetime_today.month
            )[1]
            )

    this_year = datetime_today.year
    this_month = datetime_today.month

    current_month = calendar.monthcalendar(this_year, this_month)

    current_month_events = []

    for week in current_month: 
        this_week_events=[]
        for d in week: 
            if d >= 1: 
                needed_date_dt = datetime(this_year, this_month, d)
                date_events = Event.query.filter(
                    Event.owner==current_user.user_department).filter(
                    Event.begin_date<=needed_date_dt).filter(
                        Event.end_date>=needed_date_dt).order_by(
                            Event.importance).all()
                this_week_events.append((needed_date_dt, date_events))
            else: 
                this_week_events.append(('', ''))
        current_month_events. append(this_week_events)


    return render_template('this_month_only.html', 
                            rus_week=rus_week, rus_month=rus_month, 
                            datetime_today=datetime_today, 
                            first_month_date=first_month_date, 
                            last_month_date=last_month_date, 
                            this_year=this_year, 
                            this_month=this_month, 
                            events=current_month_events, 
                            rus_month_from_int_to_string=rus_month_from_int_to_string, 
                            rus_month_from_string_to_int=rus_month_from_string_to_int)

@app.route('/events_for_date<needed_date_str>')
def events_for_date_view(needed_date_str):

    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    needed_date_dt = datetime.strptime(needed_date_str, "%d.%m.%Y")

    date_events = Event.query.filter(Event.begin_date<=needed_date_dt).filter(
                                       Event.end_date>=needed_date_dt).order_by(
                                           Event.importance).all()
    
    holiday_today = Holiday.query.filter(Holiday.dt==needed_date_dt).first()


    return render_template('events_for_date.html', 
                           events=date_events, 
                           date=needed_date_dt, 
                           holiday_today=holiday_today, 
                           rus_week=rus_week, 
                           rus_month=rus_month)

@app.route('/my_events_for_date<needed_date_str>')
def my_events_for_date_view(needed_date_str):
    """
    Отображает события для выбранной даты.

    Если пользователь аутентифицирован, показывает события для выбранной даты с учетом их важности.
    Проверяет также, является ли выбранная дата праздничным днем.

    Parameters:
        needed_date_str (str): Строка, представляющая выбранную дату в формате "%d.%m.%Y".

    Returns:
        response: Страница events_for_date.html с событиями для выбранной даты и информацией о праздничном дне, если таковой имеется.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 

    needed_date_dt = datetime.strptime(needed_date_str, "%d.%m.%Y")

    date_events = Event.query.filter(Event.begin_date<=needed_date_dt).filter(
                                       Event.end_date>=needed_date_dt).order_by(
                                           Event.importance).all()
    
    holiday_today = Holiday.query.filter(Holiday.dt==needed_date_dt).first()


    return render_template('my_events_for_date.html', 
                           events=date_events, 
                           date=needed_date_dt, 
                           holiday_today=holiday_today, 
                           rus_week=rus_week, 
                           rus_month=rus_month)

@app.route('/imprtance_reference')
def importance_reference_view():
    """
    Отображает страницу справочника значений важности событий.

    Если пользователь аутентифицирован, показывает страницу со справочной информацией о значениях важности событий.

    Returns:
        response: Страница importance_reference.html со справочной информацией о значениях важности событий.
    """
    if not current_user.is_authenticated or not current_user: 
        return redirect(url_for('welcome_view')) 
    
    return render_template('importance_reference.html')