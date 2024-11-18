# calendar_flask_project/calendar_app/error_handlers.py

from flask import render_template

from . import app, db


@app.errorhandler(404)
def page_not_found(error):
    """
    Обработчик ошибки 404 (страница не найдена).

    Parameters:
        error (Exception): Исключение, вызвавшее ошибку.

    Returns:
        response: HTML-страница '404.html' с кодом состояния 404.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Обработчик ошибки 500 (внутренняя ошибка сервера).

    Parameters:
        error (Exception): Исключение, вызвавшее ошибку.

    Returns:
        response: HTML-страница '500.html' с кодом состояния 500.
    """
    db.session.rollback()
    return render_template('500.html'), 500 