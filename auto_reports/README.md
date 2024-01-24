## Ежедневный автоматический отчет в Телеграм-бот 
`Apache Airflow` `Clickhouse` `Telegram-bot` `Seaborn` `Python` `SQL`<br><br>
[Airflow DAG - Python](https://github.com/annapavlovads/DA_portfolio/blob/main/auto_reports/dag_an_pavlova_report_full.py)<br><br>
**Задача**: создание автоматической отчетности, поступающей в Телеграм-бот по расписанию (ежедневно) <br>
**Решение**: создан DAG для `Apache Airflow` <br>
**Как работает**: Создается отчетность по данным с сайта, используя информацию из базы данных `ClickHouse` (активность пользователей, сообщения, лайки и просмотры). 
Данные собираются ежедневно в 11 утра по расписанию.<br>

## Автоматический мониторинг аномалий в метриках с отправкой отчета в Телеграм-бот 
`Apache Airflow` `Clickhouse` `Telegram-bot` `Seaborn` `Python` `SQL`<br><br>
[Airflow DAG - Python](https://github.com/annapavlovads/DA_portfolio/blob/main/auto_reports/an_pavlova_15_min_bot_alert.py) | 
[Screenshot уведомления](https://drive.google.com/file/d/1j-aiejRbDkbRsspF-a7qtYXs7fUWMQCm/view?usp=drive_link) | 
[Пример чарта для уведомления](https://drive.google.com/file/d/19myesfBdOirk7HbFie64WtMWew_BZwxo/view?usp=drive_link)
<br><br>
**Задача**: создание автоматического мониторинга метрик и отправки уведомлений в `Telegram-бот` о возможных аномалиях в данных.<br>
**Решение**: создан DAG для `Apache Airflow` <br>
**Как работает**: таск запускается каждые 15 минут для анализа метрик за последний день (по данным с сайта, используя информацию из базы данных `ClickHouse` - активность пользователей, сообщения, лайки и просмотры) и отправки уведомлений в `Telegram-бот` случае обнаружения аномалий, внутри таски используется операция по сглаживанию границ и определению аномалий.

## Автоматический ежедневный ETL-пайплайн (Clickhouse)
`Apache Airflow` `Clickhouse` `Telegram-bot` `Seaborn` `Python` `SQL`<br><br>
[Airflow DAG Python script](https://github.com/annapavlovads/DA_portfolio/blob/main/airflow_dag_etl_tg_bot_reports/dag_an_pavlova_report_full.py)<br><br>
**Задача**: создание автоматического ETL-пайплайна, который агрегирует данные из базы данных ClickHouse за предыдущий день.<br>
**Решение**: создан DAG для `Apache Airflow` <br>
**Как работает**: таск запускается ежедневно в 11 часов, агрегирует данные из базы данных `ClickHouse` и записывает их в другую базy `ClickHouse`. 
