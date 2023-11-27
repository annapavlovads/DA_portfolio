# Data Analytics Portfolio 
(Under Construction till 01 Jan 2024)
## Содержание

[Исследовательский анализ данных | Exploratory Data Analysis](https://github.com/annapavlovads/DA_portfolio/tree/main#exploratory-data-analysis)<br>
[Система дашбордов для ресторана в Superset | Superset Dashboards](https://github.com/annapavlovads/DA_portfolio/tree/main#superset-dashboards-clickhouse)<br>
[Tableau дашборд | Tableau Dashboards]()<br>
[AB-тесты | AB-tests]()<br>
[ETL-pipeline](https://github.com/annapavlovads/DA_portfolio/tree/main#etl-pipeline)<br>
[Автоматический отчет в Телеграм-бот | Automatic reports (TG-bot)](https://github.com/annapavlovads/DA_portfolio/tree/main#automatic-reports-tg-bot--%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9-%D0%BE%D1%82%D1%87%D0%B5%D1%82-%D0%B2-%D1%82%D0%B5%D0%BB%D0%B5%D0%B3%D1%80%D0%B0%D0%BC-%D0%B1%D0%BE%D1%82)<br>
[Алерт в Телеграм-бот при изменении метрик| Automatic alert ](https://github.com/annapavlovads/DA_portfolio/tree/main#automatic-alert-tg-bot--%D0%B0%D0%BB%D0%B5%D1%80%D1%82-%D0%B2-%D1%82%D0%B5%D0%BB%D0%B5%D0%B3%D1%80%D0%B0%D0%BC-%D0%B1%D0%BE%D1%82-%D0%BF%D1%80%D0%B8-%D0%B7%D0%BD%D0%B0%D1%87%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D0%BC-%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D0%B5%D0%BD%D0%B8%D0%B8-%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA)<br>

<br>
<br>
<br>

## Automatic alert (TG-bot) / Алерт в Телеграм-бот при значительном изменении метрик 
`Python` `Clickhouse` `Gitlab ci\cd` `Telegram-bot` `Docker` `Seaborn` `Apache Airflow` `SQL`<br><br>
[Airflow DAG Python script](https://github.com/annapavlovads/DA_portfolio/blob/main/airflow_dag_etl_tg_bot_reports/an_pavlova_15_min_bot_alert.py) | [Report example](https://drive.google.com/file/d/1j-aiejRbDkbRsspF-a7qtYXs7fUWMQCm/view?usp=share_link)<br><br>
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

## Система дашбордов для ресторанов в Superset | Superset Dashboards 
`superset` `clickhouse` `sql` <br>
Task: <br>
Задача: <br><br>
[Дашборд: продажи в ресторане](https://github.com/annapavlovads/DA_portfolio/blob/main/pl_dashboards/pl_sales_dashboard/%D0%94%D0%B0%D1%88%D0%B1%D0%BE%D1%80%D0%B4_%D0%9F%D0%9B_%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6%D0%B8_%D0%B2_%D1%80%D0%B5%D1%81%D1%82%D0%BE%D1%80%D0%B0%D0%BD%D0%B5.jpg) | [Документация](https://github.com/annapavlovads/DA_portfolio/blob/main/pl_dashboards/pl_sales_dashboard/%D0%94%D0%B0%D1%88%D0%B1%D0%BE%D1%80%D0%B4%20%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B0%20%D0%BB%D0%BE%D1%8F%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6%D0%B8%20%D1%80%D0%B5%D1%81%D1%82%D0%BE%D1%80%D0%B0%D0%BD%D0%B0%20(%D0%B0%D0%BB%D1%8F%D0%BA%D0%B0%D1%80%D1%82%20%2B%20%D0%B4%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B0%20%D1%81%D0%B0%D0%BC%D0%BE%D0%B2%D1%8B%D0%B2%D0%BE%D0%B7).pdf) | [SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/pl_dashboards/pl_sales_dashboard/dataset_request.txt.txt)<br>
[Дашборд: гостевая база ресторана]()<br>
[Дашборд: базовые метрики]()<br>


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

