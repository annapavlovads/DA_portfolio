# calendar_flask_project/calendar_app/forms.py

from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, BooleanField, DateField, SubmitField, TextAreaField, SelectField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import Select

from .references import rus_week_from_name_to_int, owner_list, restaurant_list, importance_list, promotion_type_list, tag_list, year_list, rus_month_from_int_to_string, rus_month_from_string_to_int

from datetime import date, datetime, timedelta

from flask_login import current_user

this_month = datetime.combine(date.today(), datetime.min.time()).month
this_year = datetime.combine(date.today(), datetime.min.time()).year


class EventForm(FlaskForm):

    name = StringField('Укажите название события (обязательно)',
                        validators=[DataRequired(message='Заполните название события'),
                        Length(1, 128)])

    tag =  SelectMultipleField('Выберите один или несколько тегов', 
                                choices=tag_list, widget=Select(multiple=True), 
                                validators=[DataRequired(message='Выберите тег'),
                                Length(1, 128)])

    importance = SelectField('Выберите важность события', choices=importance_list, 
                            validators=[DataRequired(message='Выберите важность события'),
                                Length(1, 128)])
    begin_date = DateField('Выберите дату начала события', validators=[DataRequired(message='Выберите дату начала')])
    
    end_date = DateField('Выберите дату окончания события', validators=[DataRequired(message='Выберите дату окончания')])
    
    def validate_end_date(form, field):
        if form.begin_date.data and field.data and field.data < form.begin_date.data:
            raise ValidationError('Дата окончания должна быть не раньше даты начала события')


    repeat_event = BooleanField('Создать ряд регулярно повторяющихся аналогичных событий') #, false_values={False, 'false', 'no'})
    repeat_days = SelectMultipleField('Выберите дни недели', choices=rus_week_from_name_to_int.keys(), validators=[])
    end_of_repeat_date = DateField('Выберите дату окончания повторения событий', validators=[Optional()])
    def validate_end_date(form, field):
        if form.end_of_repeat_date.data and field.data and field.data < form.end_date.data:
            raise ValidationError('Дата окончания повторения регулярных событий должна быть не раньше даты основного события')


    owner = SelectField('Выберите владельца события', choices=owner_list) #, 
        #validators=[DataRequired(message='Выберите владельца события'),
        #Length(1, 128)])

    restaurant = SelectMultipleField('Выберите ресторан', choices=restaurant_list, widget=Select(multiple=True), 
                                validators=[DataRequired(message='Выберите один или несколько ресторанов'),
                                Length(1, 128)])
    promotion_type = SelectMultipleField('Выберите тип промо', choices=promotion_type_list, widget=Select(multiple=True), 
                            validators=[])

    brief = StringField('Укажите ссылку на бриф (обязательно)', validators=[DataRequired(message='Бриф - обязательное поле'),
                                Length(1, 256)])
    picture = StringField('Укажите ссылку на макет', validators=[Length(0,256)])
    instruction = StringField('Укажите ссылку на инструкцию', validators=[Length(0,256)])
    comment = TextAreaField('Добавьте комментарий (не обязательно)', validators=[Length(0,256)])
    submit = SubmitField('Добавить')


class ShortEventForm(FlaskForm):

    name = StringField('Укажите название события (обязательно)',
                        validators=[DataRequired(message='Заполните название события'),
                        Length(1, 128)])

    tag =  SelectMultipleField('Выберите один или несколько тегов', 
                                choices=tag_list, widget=Select(multiple=True), 
                                validators=[DataRequired(message='Выберите тег'),
                                Length(1, 128)])

    importance = SelectField('Выберите важность события', choices=importance_list, 
                            validators=[DataRequired(message='Выберите важность события'),
                                Length(1, 128)])
    begin_date = DateField('Выберите дату начала события', validators=[DataRequired(message='Выберите дату начала')])

    def validate_begin_date(form, field):
        min_date = datetime.now() + timedelta(days=14)
        if field.data < min_date.date():
            raise ValidationError('Нельзя добавлять события раньше, чем через 14 дней от текущей даты.')



    end_date = DateField('Выберите дату окончания события', validators=[DataRequired(message='Выберите дату окончания')])

    def validate_event_date(form, field):
        min_date = datetime.now() + timedelta(days=14)
        if form.begin_date.data and field.data and field.data < form.begin_date.data:
            raise ValidationError('Дата окончания должна быть не раньше даты начала события')
    #owner = SelectField('Выберите владельца события', choices=owner_list) #, 
        #validators=[DataRequired(message='Выберите владельца события'),
        #Length(1, 128)])

    
    repeat_event = BooleanField('Создать ряд регулярно повторяющихся аналогичных событий') #, false_values={False, 'false', 'no'})
    repeat_days = SelectMultipleField('Выберите дни недели', choices=rus_week_from_name_to_int.keys(), validators=[])
    end_of_repeat_date = DateField('Выберите дату окончания повторения событий', validators=[Optional()])
    def validate_end_date(form, field):
        if bool(form.repeat_event.data)==True and form.end_of_repeat_date.data and field.data and field.data < form.end_date.data:
            raise ValidationError('Дата окончания повторения регулярных событий должна быть не раньше даты основного события')



    restaurant = SelectMultipleField('Выберите ресторан', choices=restaurant_list, widget=Select(multiple=True), 
                                validators=[DataRequired(message='Выберите один или несколько ресторанов'),
                                Length(1, 128)])
    promotion_type = SelectMultipleField('Выберите тип промо', choices=promotion_type_list, widget=Select(multiple=True), 
                            validators=[])

    brief = StringField('Укажите ссылку на бриф (обязательно)', validators=[DataRequired(message='Бриф - обязательное поле'),
                                Length(1, 256)])
    picture = StringField('Укажите ссылку на макет', validators=[Length(0,256)])
    instruction = StringField('Укажите ссылку на инструкцию', validators=[Length(0,256)])
    comment = TextAreaField('Добавьте комментарий (не обязательно)', validators=[Length(0,256)])
    submit = SubmitField('Добавить')








class SummaryForm(FlaskForm):
    """
    Форма для добавления итога события.

    Attributes:
        summary (TextAreaField): Поле для ввода итога события.
        submit (SubmitField): Кнопка для сохранения введенного итога события.
    """
    summary = TextAreaField('Добавьте итог события', validators=[Length(0, 256)])
    submit = SubmitField('Сохранить') 



class EditEventForm(FlaskForm):
    """
    Форма для редактирования события.

    Attributes:
        name (StringField): Поле для указания названия события.
        tag (SelectMultipleField): Поле для выбора тегов события.
        importance (SelectField): Поле для выбора важности события.
        begin_date (DateField): Поле для выбора даты начала события.
        end_date (DateField): Поле для выбора даты окончания события.
        owner (SelectField): Поле для выбора владельца события.
        restaurant (SelectMultipleField): Поле для выбора ресторанов, связанных с событием.
        promotion_type (SelectMultipleField): Поле для выбора типов промо события.
        brief (StringField): Поле для указания ссылки на бриф.
        picture (StringField): Поле для указания ссылки на макет.
        instruction (StringField): Поле для указания ссылки на инструкцию.
        comment (TextAreaField): Поле для добавления комментария к событию.
        submit (SubmitField): Кнопка для сохранения внесенных изменений.
    """    
    name = StringField('Укажите название события (обязательно)',
                       validators=[DataRequired(message='Обязательное поле'),
                                   Length(1, 128)]
                       )
    tag = SelectMultipleField('Выберите тег', choices=tag_list, widget=Select(multiple=True), validators=[])
    importance = SelectField('Выберите важность события', choices=importance_list, validators=[])
    begin_date = DateField('Выберите дату начала события')

    def validate_begin_date(form, field):
        """
        Валидирует дату начала события.

        Проверяет, что текущий пользователь не является администратором календаря и что дата начала события 
        не превышает 14 дней от текущей даты.

        Args:
            form: Форма, к которой относится поле.
            field: Поле (дата начала события), которое необходимо валидировать.

        Raises:
            ValidationError: Если текущий пользователь не является администратором календаря и дата начала 
            события менее, чем за 14 дней от текущей даты.
        """
        if current_user.user_name != 'calendar_admin':
            min_date = datetime.now() + timedelta(days=14)
            if field.data < min_date.date():
                raise ValidationError('Нельзя редактировать события менее, чем за 14 дней от его начала.')

    end_date = DateField('Выберите дату окончания события')

    def validate_end_date(form, field):
        """
        Валидирует дату окончания события.

        Проверяет, что введенная дата окончания позднее или равна дате начала события.

        Args:
            form: Форма, к которой относится поле.
            field: Поле (дата окончания события), которое необходимо валидировать.

        Raises:
            ValidationError: Если введенная дата окончания раньше даты начала события.
        """
        if form.begin_date.data and field.data and field.data < form.begin_date.data:
            raise ValidationError('Дата окончания должна быть не раньше даты начала события')

    owner = SelectField('Выберите владельца события', choices=owner_list, validators=[])

    restaurant = SelectMultipleField('Выберите ресторан', choices=restaurant_list, widget=Select(multiple=True), validators=[])
    promotion_type = SelectMultipleField('Выберите тип промо', choices=promotion_type_list, widget=Select(multiple=True), validators=[])

    brief = StringField('Укажите ссылку на бриф (обязательно)', validators=[Length(0, 256)])
    picture = StringField('Укажите ссылку на макет', validators=[Length(0, 256)])
    instruction = StringField('Укажите ссылку на инструкцию', validators=[Length(0, 256)])
    comment = TextAreaField('Добавьте комментарий (не обязательно)', validators=[Length(0, 256)])
    submit = SubmitField('Сохранить изменения') 





class SearchEventForm(FlaskForm):
    """
    Форма для поиска событий по различным критериям.

    Attributes:
        name (StringField): Поле для указания названия события или его фрагмента.
        is_completed (BooleanField): Поле для выбора поиска среди завершенных событий.
        owner (SelectMultipleField): Поле для выбора владельцев события.
        period_start_date (DateField): Поле для выбора начальной даты периода событий.
        period_end_date (DateField): Поле для выбора конечной даты периода событий.
        tag (SelectMultipleField): Поле для выбора тегов события.
        tag_selector (BooleanField): Поле для выбора только событий, содержащих все выбранные теги.
        importance (SelectMultipleField): Поле для выбора уровней важности события.
        restaurant (SelectMultipleField): Поле для выбора ресторанов, связанных с событием.
        restaurant_selector (BooleanField): Поле для выбора только событий, актуальных во всех выбранных ресторанах.
        promotion_type (SelectMultipleField): Поле для выбора типов промо события.
        promotion_type_selector (BooleanField): Поле для выбора только событий, использующие все выбранные типы промо.
        submit (SubmitField): Кнопка для запуска поиска событий по указанным критериям.
    """ 
    name = StringField('Укажите название события или его фрагмент',validators=[])
    is_completed = BooleanField('Искать среди завершенных событий')
    owner = SelectMultipleField('Выберите владельцев события', widget=Select(multiple=True), choices=owner_list, validators=[])
    period_start_date = DateField('Выберите дату начала периода')
    period_end_date = DateField('Выберите дату окончания периода')
    tag = SelectMultipleField('Выберите теги', choices=tag_list, widget=Select(multiple=True), validators=[])
    tag_selector = BooleanField('Только события, содержащие все выбранные теги')
    importance = SelectMultipleField('Выберите уровни важности события', widget=Select(multiple=True), choices=importance_list, validators=[])
    restaurant = SelectMultipleField('Выберите рестораны', widget=Select(multiple=True), choices=restaurant_list, validators=[])
    restaurant_selector = BooleanField('Только события, актуальные во всех выбранных ресторанах')
    promotion_type = SelectMultipleField('Выберите типы промо', choices=promotion_type_list, widget=Select(multiple=True), validators=[])
    promotion_type_selector = BooleanField('Только события, использующие все выбранные типы промо')
    submit = SubmitField('Найти события')



class WeekForm(FlaskForm):
    """
    Форма для поиска событий на неделю.

    Attributes:
        week_begin_date (DateField): Поле для выбора даты начала недели.
        owner (SelectMultipleField): Поле для выбора владельцев событий.
        tag (SelectMultipleField): Поле для выбора тегов событий.
        restaurant (SelectMultipleField): Поле для выбора ресторанов, связанных с событиями.
        show_completed (BooleanField): Поле для отображения завершенных событий.
        submit (SubmitField): Кнопка для запуска поиска событий на неделю.
    """
    week_begin_date = DateField('Выберите дату начала недели', validators=[DataRequired(message='Выберите дату начала')])
    owner = SelectMultipleField('Выберите владельца события', choices=owner_list, widget=Select(multiple=True), validators=[])
    tag = SelectMultipleField('Выберите тег', choices=tag_list, widget=Select(multiple=True), validators=[])
    restaurant = SelectMultipleField('Выберите ресторан', widget=Select(multiple=True), choices=restaurant_list, validators=[])
    show_completed = BooleanField('Также показывать завершенные события')
    submit = SubmitField('Найти события')


class LoginForm(FlaskForm): 
    """
    Форма для входа в календарное приложение.

    Attributes:
        user_name (StringField): Поле для ввода логина пользователя.
        user_password (PasswordField): Поле для ввода пароля пользователя.
        submit (SubmitField): Кнопка для входа в календарное приложение.
    """
    user_name = StringField('Введите логин',
                       validators=[DataRequired(message='Обязательное поле'),
                                   Length(1, 32)]
                       )
    user_password=PasswordField('Введите пароль', 
                        validators=[DataRequired(message='Обязательное поле'), 
                                    Length(1,64)])
    submit = SubmitField('Войти в календарь')

class MonthForm(FlaskForm): 
    """
    Форма для поиска событий в определенном месяце.

    Attributes:
        year (SelectField): Поле для выбора года.
        month (SelectField): Поле для выбора месяца.
        only_not_completed (BooleanField): Поле для отображения только незавершенных событий.
        owner (SelectMultipleField): Поле для выбора владельцев событий.
        tag (SelectMultipleField): Поле для выбора тегов событий.
        restaurant (SelectMultipleField): Поле для выбора ресторанов, связанных с событиями.
        submit (SubmitField): Кнопка для запуска поиска событий в выбранном месяце.
    """
    year = SelectField('Выберите год', choices=year_list, validators=[], default=this_year)
    month = SelectField('Выберите месяц', choices=list(rus_month_from_string_to_int.keys()), 
                        validators=[], default=rus_month_from_int_to_string[this_month])
    only_not_completed = BooleanField('Показывать только незавершенные события')
    owner = SelectMultipleField('Выберите владельца события', choices=owner_list, widget=Select(multiple=True), validators=[])
    tag = SelectMultipleField('Выберите тег', choices=tag_list, widget=Select(multiple=True), validators=[])
    restaurant = SelectMultipleField('Выберите ресторан', widget=Select(multiple=True), choices=restaurant_list, validators=[])
    submit = SubmitField('Найти события')