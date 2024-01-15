"""
Этот DAG определяет ETL-пайплайн, который агрегирует данные из базы данных ClickHouse за предыдущий день.

Задачи в DAG:
- load_likes_and_views - Извлекает данные о лайках и просмотрах из таблицы feed_actions, агрегируя данные 
по event_date, user, gender, age и OS.
- load_messages - Извлекает данные о сообщениях из таблицы message_actions, включая отправленные и полученные 
сообщения, а также количество уникальных пользователей, участвующих в переписке, агрегируя данные по event_date и user.
- merge_datasets - Объединяет наборы данных, полученные из задач 'load_likes_and_views' и 'load_messages', используя 
user и event_date в качестве ключей.
- gender_dimension - Создает измерение по полу из объединенного набора данных, делая сводку по полю 'gender' и агрегируя другие метрики.
- age_dimension - Создает измерение по возрасту аналогично 'gender_dimension', но сводит метрику по полю 'age'.

Результирующие измерения для пола и возраста включают сумму просмотров, лайков, отправленных и полученных сообщений, 
а также количество уникальных пользователей, отправляющих и получающих сообщения.

Примечание: Фактический ETL-процесс, хоть и указан, не полностью реализован в этом фрагменте DAG. 
Определение задач должно быть дополнено вызовом каждой задачи и логикой обработки результатов.

Аргументы по умолчанию:
- владелец: 'an-pavlova'
- depends_on_past: False
- количество попыток повторения: 2
- задержка между попытками повторения: 3 минуты
- дата начала: 21 августа 2023 года

Расписание: DAG запланирован на выполнение ежедневно в 11:00 утра.

Подключения: DAG взаимодействует с двумя базами данных ClickHouse, а именно основной базой данных 'simulator_20230720' 
для извлечения ETL-данных и 'test' для неуказанных операций.
"""

#create DAG
import pandahouse
import pandas as pd
import numpy as np

from datetime import timedelta, datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context


default_args = {
    'owner': 'an-pavlova', 
    'depends_on_past': False, 
    'retries': 2, 
    'retry_delay': timedelta(minutes=3), 
    'start_date': datetime(2023,8,21)
}

schedule_interval = '0 11 * * *'

connection = {
    'host': 'https://clickhouse.lab.karpov.courses', 
    'password': 'dpo_python_2020', 
    'user': 'student', 
    'database': 'simulator_20230720'}

connection_test = {
    'host': 'https://clickhouse.lab.karpov.courses', 
    'password': '656e2b0c9c', 
    'user': 'student-rw', 
    'database': 'test'}


@dag(default_args=default_args, catchup=False, schedule_interval=schedule_interval)
def ETL_pipeline_DAG(): 
    #create task: load likes and views 
    @task()
    def load_likes_and_views():
        q = f"""
            select 
            toDate(time) event_date, 
            user_id as user, 
            gender, 
            age, 
            os, 
            countIf(action='view') as views, 
            countIf(action='like') as likes
            from simulator_20230720.feed_actions
            where toDate(time)=today()-1
            group by event_date, user, gender, age, os
            """
        likes_and_views = pandahouse.read_clickhouse(q, connection=connection)
        return likes_and_views
    
    #create task: messages 
    @task()
    def load_messages(): 
        q = f"""
                select event_date, user, messages_sent, messages_received, users_sent, users_received
                from 
                (
                select toDate(time) as event_date, 
                user_id as user, 
                count() as messages_sent, 
                uniq(reciever_id) as users_sent
                from simulator_20230720.message_actions
                where toDate(time)=today()-1
                group by event_date, user
                )
                as s
                full outer join 
                (
                select toDate(time) as event_date, reciever_id as user, count() as messages_received, uniq(user_id) as users_received
                from simulator_20230720.message_actions
                where toDate(time)=today()-1
                group by event_date, user
                ) as r 
                using user
                """
        messages = pandahouse.read_clickhouse(q, connection=connection)
        return messages
    
    #create task: merge loaded tables 
    @task()
    def merge_datasets(likes_and_views, messages): 
        df = likes_and_views.merge(messages, how='outer', on=['user', 'event_date'])#.dropna()
        return df
    
    #create task: dimension gender
    @task()
    def gender_dimension(df):     
        gender_dimension = df.pivot_table(
            index=['gender'], values=['views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent'], 
            aggfunc='sum').reset_index()
        gender_dimension['dimension'] = 'gender'
        gender_dimension['dimension_value'] = gender_dimension['gender']
        gender_dimension_df = gender_dimension[['dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return gender_dimension_df
    
    #create task: dimension age
    @task()
    def age_dimension(df):     
        age_dimension = df.pivot_table(
            index=['age'], 
            values=['views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent'],
            aggfunc='sum').reset_index()
        age_dimension['dimension'] = 'age'
        age_dimension['dimension_value'] = age_dimension['age']
        age_dimension_df = age_dimension[['dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return age_dimension
    
    #create task: dimension os 
    @task()
    def os_dimension(df):     
        os_dimension = df.pivot_table(
            index=['os'], 
            values=['views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent'], 
            aggfunc='sum').reset_index()
        os_dimension['dimension'] = 'os'
        os_dimension['dimension_value'] = os_dimension['os']
        os_dimension_df = os_dimension[['dimension','dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return os_dimension_df 
    
    
    #create final dataset (of all dimensions)
    @task
    def final_concat(likes_and_views, os_dimension_df, age_dimension_df, gender_dimension_df):
        
        final_df = pd.concat([os_dimension_df, age_dimension_df, gender_dimension_df], axis=0)
        final_df['event_date'] = likes_and_views.iloc[0].event_date
        final_df = final_df[['event_date', 'dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        final_df = final_df.astype({'likes': 'int', 'views': 'int', 'messages_received': 'int', 'messages_sent': 'int', 'users_received': 'int', 'users_sent': 'int'})
        return final_df
    
    #create task: load final table to "an-pavlova_etl" table
    @task
    def load_table(final_df): 
        #q_load = """
        #CREATE TABLE test.an_pavlova_etl
        #(
        #event_date Date, 
        #dimension String, 
        #dimension_value String, 
        #views UInt64, 
        #likes UInt64, 
        #messages_received UInt64,
        #messages_sent UInt64, 
        #users_received UInt64, 
        #users_sent UInt64
        #)
        #ENGINE = MergeTree()
        #ORDER BY event_date
        #"""
        
        connection_test = {
            'host': 'https://clickhouse.lab.karpov.courses', 
            'password': '656e2b0c9c', 
            'user': 'student-rw', 
            'database': 'test'}
        
        #pandahouse.execute(q_load, connection=connection_test)
        
        pandahouse.to_clickhouse(
            final_df, 
            'an_pavlova_etl', 
            index=False, 
            connection=connection_test)
        
    
    likes_and_views = load_likes_and_views()
    messages = load_messages()
    df = merge_datasets(likes_and_views, messages)
    age_dimension_df = age_dimension(df)
    gender_dimension_df = gender_dimension(df)
    os_dimension_df = os_dimension(df)
    final_df = final_concat(likes_and_views, os_dimension_df, age_dimension_df, gender_dimension_df)
    load_table(final_df)
    
ETL_pipeline_DAG = ETL_pipeline_DAG()  