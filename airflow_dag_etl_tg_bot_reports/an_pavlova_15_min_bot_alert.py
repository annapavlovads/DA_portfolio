"""
Данный DAG реализует операции для мониторинга метрик и отправки уведомлений в Telegram о возможных аномалиях в данных.

Таски:
- run_alerts: функция, которая запускает процесс мониторинга и анализа метрик. 
Внутри таски используется операция по сглаживанию границ и определению аномалий.

Примечания:
- Функция check_anomaly используется для определения аномалий в данных на основе 
квартилей и интерквартильного размаха.
- Таск run_alerts запускается каждые 15 минут для анализа метрик за последний день 
и отправки уведомлений в случае обнаружения аномалий.
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import telegram
import pandahouse
from datetime import date, datetime, timedelta
import io
import sys
import os

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

default_args = {
    'owner': 'an-pavlova', 
    'depends_on_past': False, 
    'retries': 2, 
    'retry_delay': timedelta(minutes=3), 
    'start_date': datetime(2023,8,16)
}

schedule_interval = timedelta(minutes=15)
        
connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020', 
    'user': 'student', 
    'database': 'simulator_20230720'
}

CHAT_ID = 278936023
MY_BOT_TOKEN = '6504583850:AAEQYH3Jl_LMZzwOpWK4QsRWCAqTNrpFLvE'
bot = telegram.Bot(token=MY_BOT_TOKEN)

tg_responsible_user = '@AnnaPavlovaDS'
        
chart_links = {
    'ctr': 'http://superset.lab.karpov.courses/r/4265', 
    'users_feed': 'http://superset.lab.karpov.courses/r/4273', 
    'likes_feed': 'http://superset.lab.karpov.courses/r/4269', 
    'views_feed': 'http://superset.lab.karpov.courses/r/4271', 
    'users_messenger': 'http://superset.lab.karpov.courses/r/4279', 
    'messages':'http://superset.lab.karpov.courses/r/4281'}
        
dashboard_link = 'http://superset.lab.karpov.courses/r/4319'
        

@dag(default_args=default_args, catchup=False, schedule_interval=schedule_interval)
def an_pavlova_15_min_bot_alert(): 
    
    def check_anomaly(df, metric, coef_a=3, coef_n=5): 
        
        df['q25'] = df[metric].shift(1).rolling(coef_n).quantile(0.25) #сдвигаем окно на 1 период назад, 
        #чтобы на значения для текущей 15-минутки не повлиять значением самой этой 15-минутки
        df['q75'] = df[metric].shift(1).rolling(coef_n).quantile(0.75)
        df['iqr'] = df['q75'] - df['q25']
        df['upper'] = df['q75'] + coef_a * df['iqr']
        df['lower'] = df['q25'] - coef_a * df['iqr']
        #сгладим границы, иначе на графике они получаются слишком рваные и нестабильные 
        df['upper'] = df['upper'].rolling(coef_n, center=True, min_periods=1).mean()
        df['lower'] = df['lower'].rolling(coef_n, center=True, min_periods=1).mean()
        recent_chunk = df[metric].iloc[-1]
        
        alert_flag = 0
        
        if recent_chunk < df['lower'].iloc[-1] or recent_chunk > df['upper'].iloc[-1]: 
            alert_flag = 1
            
        return alert_flag, df
    
    
    
    @task()    
    def run_alerts(): 
        
        today = date.today().strftime('%Y-%m-%d')
        yesterday = (date.today() - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
        week_ago = (date.today() - pd.DateOffset(days=7)).strftime('%Y-%m-%d')
        
        metrics = ['ctr', 'users_feed', 'likes_feed', 'views_feed', 'users_messenger', 'messages']
        
        q = """
        select * from 
        (select toStartOfFifteenMinutes(time) as time_chunk, toDate(time) as day, 
        formatDateTime(toStartOfFifteenMinutes(time), '%R') as hours_minutes, 
        uniqExact(user_id) as users_feed, 
        countIf(action='view') as views_feed, 
        countIf(action='like') as likes_feed, 
        countIf(action='like')/countIf(action='view') as ctr
        from simulator_20230720.feed_actions
        where time >= today() - 1 and time < toStartOfFifteenMinutes(now())
        group by time_chunk, day, hours_minutes) f
        inner join
        (select toStartOfFifteenMinutes(time) as time_chunk, 
        toDate(time) as day, 
        formatDateTime(toStartOfFifteenMinutes(time), '%R') as hours_minutes, 
        uniqExact(user_id) as users_messenger,  
        count(user_id) as messages 
        from simulator_20230720.message_actions
        where time >= today() - 1 and time < toStartOfFifteenMinutes(now())
        group by time_chunk, day, hours_minutes
        ) m
        using (time_chunk, day, hours_minutes)

        """

        df = pandahouse.read_clickhouse(q, connection=connection)
        
        for metric in metrics: 
            
            df_chunk = df[['time_chunk', 'day', 'hours_minutes', metric]]
            alert_flag, df_chunk = check_anomaly(df_chunk, metric)

            if alert_flag: #or True:  
                
                current_value = df_chunk[metric].iloc[-1]
                last_value = df_chunk[metric].iloc[-2]
                
                if current_value < last_value: 
                    diff_value = (last_value - current_value)/last_value
                else: 
                    diff_value = (current_value - last_value)/last_value
                
                #create alert text
                text = f"""{datetime.now().strftime('%Y-%m-%d (%H:%m)')} 
                Metric name: '{metric}', current value: {current_value:.2f}, 
                difference with the previous value: ({last_value:.2f}): {diff_value:+.2%}
                Online chart link: {chart_links[metric]}
                Dashboard link: {dashboard_link}
                Attention to: {tg_responsible_user}
                """
                
                #create alert picture
                sns.set(rc={'figure.figsize': (24,16)})
                sns.set(font_scale=2)
                sns.set_style('white')
                plt.tight_layout()
                
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk['upper'], label='upper border')
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk['lower'], label='lower border')
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk[metric], label=metric)
                
                for index, label in enumerate(ax.get_xticklabels()): 
                    if index % 3 == 0: 
                        label.set_visible(True)
                    else: 
                        label.set_visible(False)
            
                ax.set(xlabel='time')
                ax.set(ylabel=metric)
                
                ax.set_title(f"Metric '{metric}' and normal borders")

                plot_object = io.BytesIO()
                ax.figure.savefig(plot_object)
                plot_object.seek(0)
                plot_object.name = f'{metric}.png'
                plt.close()
                
                #sending messages
                bot.sendMessage(chat_id=CHAT_ID, text=text)
                bot.sendPhoto(chat_id=CHAT_ID, photo=plot_object)
                
    run_alerts()

an_pavlova_15_min_bot_alert = an_pavlova_15_min_bot_alert()