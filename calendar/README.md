## Маркетинговый событийный календарь | `Event`-календарь

`Python` `Flask` `PostgreSQL` `SQLAlchemy` `Jinja` `HTML` `CSS`

#### Описание проекта
###### Мотивация к созданию 
- большое количество неорганизованных файлов о мероприятиях, проводимых в ресторанах (концерты, мастер-классы, банкеты под закрытие и т.д.), потеря информации при передаче из одной службы в другую
- нецелесообразность добавления всех участников на централизованный корпоративный портал УК, необходимость быстро и просто предоставлять информацию о мероприятиях всем причастным сотрудникам ресторана  
###### Цели
- облегчить управление событиями (ивенты, концерты, мероприятия и т.д.) для различных служб УК ресторанного бизнеса 
- избежать потерю информации 
- избежать заполнения и пересылки множества различных файлов и таблиц 
###### Функционал
- позволяет эффективно вести расписание мероприятий, координировать действия служб и обеспечивать прозрачность в планировании и проведении событий
- единый минималистичный интерфейс для всех служб, с возможностью вносить, редактировать и просматривать свои события, а также осуществлять поиск информации по заданным критериям
- расширенный функционал для администратора календаря-бизнес-заказчика (Отдел маркетинга и рекламы, Директор по маркетингу)
###### Реализация  
- реализован с использованием `Flask`-фреймворка на `Python`. 
- для хранения и управления данными событий используется `Postgresql` 
- функционал поиска и фильтрации обеспечивается с помощью запросов к базе данных
- реализован механизм авторизации пользователя по логину и паролю, а также различные права для различных пользователей 
- проект запущен на виртуальной машине с `Ubuntu 22.04 LTS` на момент релиза проекта
- доступ осуществляется через веб-браузер по ссылке 

#### Установка и настройка
1. Создать ВМ / зайти на ВМ, установить `docker`, `python3-venv`, `python3-pip` и т.д. 
2. Создать среду, установить зависимости из `requirements.txt`
3. Запустить контейнер с `PostgreSL`: 
```bash
docker run -d -p 5432:5432 -v /database/ps_files:/var/lib/postgresql/data --name postgresql-container -e POSTGRES_PASSWORD=passwd postgres:13
```
4. Подключиться к `PostgreSQL`, создать пользователя, базу, таблицы (файл `ddl.sql`)
5. Проверяем открытые порты, при необходимости добавляем. 
6. Проверяем работу проекта 
```bash
flask run --host=0.0.0.0 --port=5000
```
7. Запускаем проект на постоянной основе:
- Копируем файл `myflaskapp.service` в директорию `/etc/systemd/system/`
- Запускаем службу: `sudo systemctl start myflaskapp`
- Активируем службы при старте системы: `sudo systemctl enable myflaskapp`
- Проверяем статус службы: `systemctl status myflaskapp`

#### Структура проекта

```bash
├── calendar_app
│   ├── __init__.py
│   ├── error_handlers.py
│   ├── forms.py
│   ├── jobs.py
│   ├── models.py
│   ├── references.py
│   ├── static
│   ├── templates
│   └── views.py
├── ddl.sql
├── myflaskapp.service
├── requirements.txt
└── settings.py
```

#### Документация
   - Содержится в `docstring` форм и функций
   - `Пользовательская инструкция`

#### Скриншоты 
[Страница входа](https://drive.google.com/file/d/1OraBixYzT61Fp-BUcZU8br6OGzhWYkOR/view?usp=drive_link) | 
[Главная страница](https://drive.google.com/file/d/121y-yIZS0_QzLPlb_4ArFgP-uCqnAZhD/view?usp=drive_link) | 
[Найдено быстрым поиском](https://drive.google.com/file/d/1HKYU8EusT5dshtzW6eiamhBS95j7pqea/view?usp=drive_link) <br>
[Поиск](https://drive.google.com/file/d/14hwrygHrnBkBdkWHSBhq9zAa7GYOroaI/view?usp=sharing) | 
[Добавить событие](https://drive.google.com/file/d/1XIcNRp4jQ_9BS5zp570gbkziRY0_So0F/view?usp=drive_link) | 
[Месяц](https://drive.google.com/file/d/1QX9Ah4ijQpn9j3DTMbj72Bey0Z8119pW/view?usp=drive_link) | 
[Неделя](https://drive.google.com/file/d/1SySYUyuyBvYqNS0xI1dlVzX1i5qN-CTR/view?usp=sharing) | 
[Событие](https://drive.google.com/file/d/1xIrpzBLLO69aG-BGGOy-4lVth0jOo7cA/view?usp=drive_link) 

