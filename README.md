# Data Analytics Portfolio 
(Under Construction till 01 Jan 2024)

## Automatic alert (TG-bot) / Алерт в Телеграм-бот при значительном изменении метрик 
`Python` `Clickhouse` `Gitlab ci\cd` `Telegram-bot` `Docker` `Seaborn` `Apache Airflow` `SQL`<br><br>
[Airflow DAG Python script](https://github.com/annapavlovads/DA_portfolio/blob/main/airflow_dag_etl_tg_bot_reports/an_pavlova_15_min_bot_alert.py) || [Report example](https://drive.google.com/file/d/1j-aiejRbDkbRsspF-a7qtYXs7fUWMQCm/view?usp=share_link)<br><br>
Задача: Система должна с периодичностью 15 минут проверять ключевые метрики, такие как активные пользователи в ленте / мессенджере, просмотры, лайки, CTR, количество отправленных сообщений. В случае обнаружения аномального значения, в чат должен отправиться алерт - сообщение со следующей информацией: метрика, ее значение, величина отклонения, а также график, ссылка на дашборд/чарт в BI системе. <br>
<br>
Task: The system checks the key metrics every 15 minutes. The key metrics are: active users in the feed / messenger, views, likes, CTR, the number of messages sent. If any abnormal value is detected, an alert message is to be sent to the chat. The message contains: the metric, its value, the deviation value, graph, a link to the dashboard / chart in the BI system. <br>

## Exploratory Data Analysis
`Python` `Pandas` `Plotly` `Matplotlib` `Numpy` `Seaborn` <br><br>
[IPYNB-file](https://github.com/annapavlovads/DA_portfolio/) <br><br>
Задача: <br><br>
Task: <br><br>

## Time Series Data Analysis
`python` `pandas` `plotly` `seaborn` `matplotlib` `numpy` `orbit` 

## ETL-pipeline
`Apache Airflow` `Clickhouse` `Telegram-bot` `Seaborn` `Python` `SQL`<br><br>
[Airflow DAG Python script](https://github.com/annapavlovads/DA_portfolio/blob/4e762b085ed0b88933d80835c3ee9334fa1756e1/ETL_pipeline_DAG.py)<br><br>
Задача: создание ETL-пайплайна, ежедневно выгружающего данные из clickhouse, преобразующего их с помощью python-скрипта и загружающего таблицу в базу данных с помощью автоматизации DAG в Apache Airflow <br><br>
Task: ETL-pipeline daily exctracting data from clickhouse database, transforming with python-script and loading result to database with Apache Airflow DAG <br>

## Superset Dashboards (ClickHouse)
[SQL requests]() ---- [Dashboards]() <br>
Task: 
Задача: 
`superset` `clickhouse` `sql` 

## Automatic reports (TG-bot) / Автоматический отчет в Телеграм-бот 
`Apache Airflow` `Clickhouse` `Telegram-bot` `Seaborn` `Python` `SQL`<br><br>
[Airflow DAG Python script](https://github.com/annapavlovads/DA_portfolio/blob/main/airflow_dag_etl_tg_bot_reports/dag_an_pavlova_report_full.py)<br><br>
Задача: создание автоматической отчетности, поступающей в Телеграм-бот по расписанию (ежедневно) <br><br>
Task: to create an automatic daily report from the database to the Telegram bot. <br>

## AB-tests
[IPYNB file - AB tests]() <br>
`python` `numpy` `scipy stats` 

## Tableau dashboard 
[Tableau portfolio page]() <br> 
`tableau`

