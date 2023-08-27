import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import telegram
import pandahouse
from datetime import date, datetime
import io
import sys
import os
import warnings
warnings.filterwarnings("ignore")
sns.set(rc={'figure.figsize': (18,12)})
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

CHAT_ID = 278936023   
MY_BOT_TOKEN = '6504583850:AAEQYH3Jl_LMZzwOpWK4QsRWCAqTNrpFLvE'

default_args = {
    'owner': 'an-pavlova', 
    'depends_on_past': False, 
    'retries': 2, 
    'retry_delay': timedelta(minutes=3), 
    'start_date': datetime(2023,8,16)
}

####################### ОДИН РАЗ В ЧАС
#schedule_interval = timedelta(minutes=15)
schedule_interval = '0 * * * *'

@dag(default_args=default_args, catchup=False, schedule_interval=schedule_interval)
def simple_bot_alert(): 
    
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
        #chat_id = CHAT_ID
        #bot = telegram.Bot(token=MY_BOT_TOKEN)
        connection = {
        'host': 'https://clickhouse.lab.karpov.courses', 
        'password': 'dpo_python_2020', 
        'user': 'student', 
        'database': 'simulator_20230720'}

        q = """
        select toStartOfFifteenMinutes(time) as time_chunk, 
        toDate(time) as date, 
        formatDateTime(toStartOfFifteenMinutes(time), '%R') as hour_minutes, 
        uniqExact(user_id) as users, 
        countIf(action='view') as views, 
        countIf(action='like') as likes
        from simulator_20230720.feed_actions
        where time >= today() - 1 and time < toStartOfFifteenMinutes(now())
        group by time_chunk, date, hour_minutes
        order by time_chunk
        """

        df = pandahouse.read_clickhouse(q, connection=connection)

        metrics = ['users', 'views', 'likes']

        for metric in metrics: 
            #print(metric)
            df_chunk = df[['time_chunk', 'date', 'hour_minutes', metric]]
            alert_flag, df_chunk = check_anomaly(df_chunk, metric)

            if alert_flag: # or True:   
                current_value = df_chunk[metric].iloc[-1]
                last_value = df_chunk[metric].iloc[-2]
                diff_value = 1 - current_value/last_value

                text = f"""{datetime.now().strftime('%Y-%m-%d (%H:%m)')} Метрика '{metric}': текущее значение {current_value:.2f}, отклонение от предыдущего значения ({last_value:.2f}): {diff_value:+.2%}"""

                plt.tight_layout()
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk['upper'], label='upper border')
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk['lower'], label='lower border')
                ax = sns.lineplot(x=df_chunk['time_chunk'], y=df_chunk[metric], label=metric)
                ax.set(xlabel='time')
                ax.set(ylabel=metric)
                ax.set_title(f"Metric '{metric}' and normal borders")

                plot_object = io.BytesIO()
                ax.figure.savefig(plot_object)
                plot_object.seek(0)
                plot_object.name = f'{metric}.png'
                plt.close()

                bot.sendMessage(chat_id=CHAT_ID, text=text)
                bot.sendPhoto(chat_id=CHAT_ID, photo=plot_object)

simple_bot_alert = simple_bot_alert()