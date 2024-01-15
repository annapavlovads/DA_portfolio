"""
Этот DAG предназначен для создания отчетности по данным с сайта, используя информацию из базы данных ClickHouse. 
Он анализирует активность пользователей, сообщения, лайки и просмотры, происходящие на платформе.

Основные этапы включают в себя:
1. Извлечение основных метрик (users, posts, likes, views, ctr) за последние 10 дней из таблицы feed_actions 
и группировка данных по датам, операционной системе и источнику.
2. Извлечение данных о сообщениях (users, messages, mess_per_user), агрегированных по датам за последние 10 дней 
из таблицы message_actions.
3. Выявление уникальных пользователей по операционным системам (users, android_users, ios_users) на общее количество 
и количество уникальных пользователей, использующих Android и iOS, совершивших действия в приложении.
4. Подсчет новых пользователей (users, organic_users, ads_users), включая разделение на органических пользователей 
и пришедших из рекламы, с минимальными датами первого визита в приложение за последние 100 дней.

Конфигурация задачи:
- Владелец: 'an-pavlova'
- Не зависит от предыдущих запусков: False
- Попытки повторения в случае неудачи: 2
- Задержка между повторными попытками: 3 минуты
- Дата начала выполнения: 21 августа 2023 года

Данные собираются ежедневно в 11 утра по расписанию.
"""

import pandahouse

import pandas as pd
import numpy as np

from datetime import timedelta, datetime
import telegram

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import io

import os 
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()


default_args = {
    'owner': 'an-pavlova', 
    'depends_on_past': False, 
    'retries': 2, 
    'retry_delay': timedelta(minutes=3), 
    'start_date': datetime(2023,8,21)
}

schedule_interval = '0 11 * * *'


@dag(default_args=default_args, catchup=False, schedule_interval=schedule_interval)
def dag_an_pavlova_report_full():

    connection = {
        'host': 'https://clickhouse.lab.karpov.courses', 
        'password': 'dpo_python_2020', 
        'user': 'student', 
        'database': 'simulator_20230720'}
        
        
    q_df = """
        select toDate(time) as date, 
        os as os, 
        source as source, 
        uniqExact (user_id) as users, 
        uniqExact(post_id) as posts, 
        countIf(user_id, action='like') as likes, 
        countIf(user_id, action='view') as views, 
        100 * likes/views as ctr
        from simulator_20230720.feed_actions
        where toDate(time) between today()-10 and today()-1
        group by date, os, source
        order by date DESC
        """
    df = pandahouse.read_clickhouse(q_df, connection=connection)
        

    q_df_mess = """
        select toDate(time) as date,
        uniqExact (user_id) as users, 
        count(*) as messages, 
        messages/users as mess_per_user
        from simulator_20230720.message_actions
        where toDate(time) between today()-10 and today()-1
        group by date
        order by date DESC

        """
    df_mess = pandahouse.read_clickhouse(q_df_mess, connection=connection)
        
        
    q_df_unique_os = """
        select date, 
        uniqExact (user_id) as users, 
        uniqExactIf(user_id, os='Android') as android_users, 
        uniqExactIf(user_id, os='iOS') as ios_users
        from 
        (
        select distinct toDate(time) as date, 
        user_id as user_id, 
        os as os
        from simulator_20230720.feed_actions 
        where toDate(time) between today()-10 and today()-1
        union all
        select distinct toDate(time) as date, 
        user_id as user_id, 
        os as os
        from simulator_20230720.message_actions
        where toDate(time) between today()-10 and today()-1
        ) as temporary_table
        group by date
        order by date
        """        
    df_unique_os = pandahouse.read_clickhouse(q_df_unique_os, connection=connection)
        
        
    q_new_users_df = """
        select first_visit, 
        uniqExact(user_id) as users, 
        uniqExactIf(user_id, source='organic') as organic_users, 
        uniqExactIf(user_id, source='ads') as ads_users
        from
        (select 
        user_id, 
        source, 
        min(start_date) as first_visit
        from 
        (
        select 
        user_id as user_id, 
        source as source, 
        min(toDate(time)) as start_date
        from simulator_20230720.feed_actions 
        where toDate(time) between today()-100 and today()-1
        group by user_id, source
        union all
        select user_id as user_id, 
        source as source, 
        min(toDate(time)) as start_date
        from simulator_20230720.message_actions
        where toDate(time) between today()-100 and today()-1
        group by user_id, source) as temporary_table
        group by user_id, source) as temp_table
        group by first_visit
        having first_visit between today()-8 and today()-1
        
        """        
        
    new_users_df = pandahouse.read_clickhouse(q_new_users_df, connection=connection)
        
   
    @task()    
    def get_text(df, df_unique_os, new_users_df, df_mess): 
        
        #prepairing datasets
        df = df.astype({'users': int, 'likes': int, 'views': int, 'posts': int})
        df_unique_os = df_unique_os.astype({'users': int, 'android_users': int, 'ios_users': int})
        df_mess = df_mess.astype({'users': int, 'messages': int})
        new_users_df = new_users_df.astype({'users': int, 'organic_users': int, 'ads_users': int})
        
        today_date = (datetime.now() - timedelta(days=1)).date()
        yesterday_date = (today_date - timedelta(days=1))
        week_ago_date = (today_date - timedelta(days=7))
        
        users_per_os = df.pivot_table(
            index=['date', 'os'], 
            values=['users'], aggfunc='sum'
        ).sort_values(
            by='date', ascending=False
        ).reset_index()

        #creating metrics
        all_events = df_mess.messages.sum() + df.views.sum() + df.likes.sum() 
        report_date = (df.iloc[0].date).strftime('%Y-%m-%d')
    
        #Newsline DAU
        nl_users_today = df.loc[df['date'].dt.date==today_date].users.sum()
        nl_users_day_ago = nl_users_today / df.loc[df['date'].dt.date==yesterday_date].users.sum()
        nl_users_week_ago = nl_users_today / df.loc[df['date'].dt.date==week_ago_date].users.sum()  
        
        #Messenger DAU 
        mess_users_today = df_mess.iloc[0].users
        mess_users_day_ago = mess_users_today / df_mess.iloc[0].users/df_mess.iloc[1].users
        mess_users_week_ago = mess_users_today / df_mess.iloc[0].users/df_mess.iloc[7].users
        
        #Total DAU
        all_users_today = df_unique_os.loc[df_unique_os['date'].dt.date == today_date].users.values[0]
        all_users_day_ago = all_users_today / df_unique_os.loc[df_unique_os['date'].dt.date == yesterday_date].users.values[0]
        all_users_week_ago = all_users_today / df_unique_os.loc[df_unique_os['date'].dt.date == week_ago_date].users.values[0]
        
        #Total DAU Android-iOS
        total_users_ios_today = df_unique_os.loc[df_unique_os['date'].dt.date == today_date].ios_users.values[0]
        total_users_android_today = df_unique_os.loc[df_unique_os['date'].dt.date == today_date].android_users.values[0]
        
        total_users_ios_day_ago = total_users_ios_today / df_unique_os.loc[df_unique_os['date'].dt.date == yesterday_date].ios_users.values[0]
        total_users_android_day_ago = total_users_android_today / df_unique_os.loc[df_unique_os['date'].dt.date == yesterday_date].android_users.values[0] 
        
        total_users_ios_week_ago = total_users_ios_today / df_unique_os.loc[df_unique_os['date'].dt.date == week_ago_date].ios_users.values[0]
        total_users_android_week_ago = total_users_android_today / df_unique_os.loc[df_unique_os['date'].dt.date == week_ago_date].android_users.values[0]       
        
        #NL DAU Android
        all_users_android_today = users_per_os.loc[((users_per_os['date']).dt.date==today_date) & (users_per_os['os']=='Android')].users.values[0]
        all_users_android_day_ago = all_users_android_today / users_per_os.loc[((users_per_os['date']).dt.date==yesterday_date) & (users_per_os['os']=='Android')].users.values[0]
        all_users_android_week_ago = all_users_android_today / users_per_os.loc[((users_per_os['date']).dt.date==week_ago_date) & (users_per_os['os']=='Android')].users.values[0]
        
        #NL DAU iOS 
        all_users_ios_today = users_per_os.loc[((users_per_os['date']).dt.date==today_date) & (users_per_os['os']=='iOS')].users.values[0]
        all_users_ios_day_ago = all_users_ios_today / users_per_os.loc[((users_per_os['date']).dt.date==yesterday_date) & (users_per_os['os']=='iOS')].users.values[0]
        all_users_ios_week_ago = all_users_ios_today / users_per_os.loc[((users_per_os['date']).dt.date==week_ago_date) & (users_per_os['os']=='iOS')].users.values[0]
        
        #New users

        new_users_today = new_users_df.loc[new_users_df['first_visit'].dt.date==today_date].users.values[0]
        new_users_day_ago = new_users_today / new_users_df.loc[new_users_df['first_visit'].dt.date==yesterday_date].users.values[0]
        new_users_week_ago = new_users_today / new_users_df.loc[new_users_df['first_visit'].dt.date==week_ago_date].users.values[0]
        
        new_users_organic_today = new_users_df.loc[new_users_df['first_visit'].dt.date==today_date].organic_users.values[0]
        new_users_organic_day_ago = new_users_organic_today / new_users_df.loc[new_users_df['first_visit'].dt.date==yesterday_date].organic_users.values[0]
        new_users_organic_week_ago = new_users_organic_today / new_users_df.loc[new_users_df['first_visit'].dt.date==week_ago_date].organic_users.values[0]
        
        new_users_ads_today = new_users_df.loc[new_users_df['first_visit'].dt.date==today_date].ads_users.values[0]
        new_users_ads_day_ago = new_users_ads_today / new_users_df.loc[new_users_df['first_visit'].dt.date==yesterday_date].ads_users.values[0]
        new_users_ads_week_ago = new_users_ads_today / new_users_df.loc[new_users_df['first_visit'].dt.date==week_ago_date].ads_users.values[0]
        
        #Views
        views_today = df.loc[(df['date']).dt.date==today_date].views.sum()
        views_day_ago = views_today / df.loc[(df['date']).dt.date==yesterday_date].views.sum()
        views_week_ago = views_today / df.loc[(df['date']).dt.date==week_ago_date].views.sum()
        
        #Likes
        likes_today = df.loc[(df['date']).dt.date==today_date].likes.sum()
        likes_day_ago = likes_today / df.loc[(df['date']).dt.date==yesterday_date].likes.sum()
        likes_week_ago = likes_today / df.loc[(df['date']).dt.date==week_ago_date].likes.sum()
    
        ctr_today = round((100*likes_today / views_today),2)
        ctr_day_ago = ctr_today / round((100*likes_day_ago / views_day_ago),2)
        ctr_week_ago = ctr_today / round((100*likes_week_ago / views_week_ago),2)

        #count likes per user 
        likes_per_user_today = round((likes_today / nl_users_today),2)
        likes_per_user_day_ago = round((likes_day_ago / nl_users_day_ago),2)
        likes_per_user_week_ago = round((likes_week_ago / nl_users_week_ago),2)
    
        #count active posts 
        posts_today = df.loc[(df['date']).dt.date==today_date].posts.sum()
        posts_day_ago = posts_today / df.loc[(df['date']).dt.date==yesterday_date].posts.sum()
        posts_week_ago = posts_today / df.loc[(df['date']).dt.date==week_ago_date].posts.sum()
    
        #count messages 
        messages_today = df_mess.iloc[0].messages
        messages_day_ago = messages_today / df_mess.iloc[0].messages/df_mess.iloc[1].messages
        messages_week_ago = messages_today / df_mess.iloc[0].messages/df_mess.iloc[7].messages      
        
        #count messages per user
        mess_per_user_today = df_mess.iloc[0].mess_per_user
        mess_per_user_day_ago = mess_per_user_today / df_mess.iloc[0].mess_per_user/df_mess.iloc[1].mess_per_user
        mess_per_user_week_ago = mess_per_user_today / df_mess.iloc[0].mess_per_user/df_mess.iloc[7].mess_per_user
        
        #creating text 
        text = f"""
        Application report ({report_date}):
        -------------------------------------
        All events: {all_events}
        App DAU: {all_users_today} ({all_users_day_ago:+.2%} to a day ago, {all_users_week_ago:+.2%} to a week ago)
        -- App DAU Android: {total_users_android_today} ({total_users_android_day_ago:+.2%} to a day ago, {total_users_android_week_ago:+.2%} to a week ago)
        -- App DAU iOS: {total_users_ios_today} ({total_users_ios_day_ago:+.2%} to a day ago, {total_users_ios_week_ago:+.2%} to a week ago)
        New users: {new_users_today} ({new_users_day_ago:+.2%} to a day ago, {new_users_week_ago:+.2%} to a week ago)
        -- new users (organic): {new_users_organic_today} ({new_users_organic_day_ago:+.2%} to a day ago, {new_users_organic_week_ago:+.2%} to a week ago)
        -- new users (ads): {new_users_ads_today} ({new_users_ads_day_ago:+.2%} to a day ago, {new_users_ads_week_ago:+.2%} to a week ago)
        -------------------------------------
        Newsline metrics: 
        - DAU: {nl_users_today} ({nl_users_day_ago:+.2%} to a day ago, {nl_users_week_ago:+.2%} to a week ago)
        -- Android DAU: {all_users_android_today} ({all_users_android_day_ago:+.2%} to a day ago, {all_users_android_week_ago:+.2%} to a week ago)
        -- iOS DAU: {all_users_ios_today} ({all_users_ios_day_ago:+.2%} to a day ago, {all_users_ios_week_ago:+.2%} to a week ago)
        - Views: {views_today} ({views_day_ago:+.2%} to a day ago, {views_week_ago:+.2%} to a week ago)
        - Likes: {likes_today} ({likes_day_ago:+.2%} to a day ago, {likes_week_ago:+.2%} to a week ago)
        - CTR: {ctr_today:.2f}% ({ctr_day_ago:+.2%} to a day ago, {ctr_week_ago:+.2%} to a week ago)
        - Likes per user: {likes_per_user_today:.2f} ({likes_per_user_day_ago:+.2%} to a day ago, {likes_per_user_week_ago:+.2%} to a week ago)
        - Active posts: {posts_today} ({posts_day_ago:+.2%} to a day ago, {posts_week_ago:+.2%} to a week ago)
        -------------------------------------
        Messenger metrics: 
        - DAU: {mess_users_today} ({mess_users_day_ago:+.2%} to a day ago, {mess_users_week_ago:+.2%} to a week ago)
        - Messages: {messages_today} ({messages_day_ago:+.2%} to a day ago, {messages_week_ago:+.2%} to a week ago)
        - Messages per user: {mess_per_user_today:.2f} ({mess_per_user_day_ago:+.2%} to a day ago, {mess_per_user_week_ago:+.2%} to a week ago)
        """
            
        return text
    
    @task()
    def get_lineplot(df, df_unique_os, new_users_df, df_mess): 
        
        df_users_pivot = df.pivot_table(index='date', values='users', aggfunc='sum').reset_index()
        df_ctr_pivot = df.pivot_table(index='date', values=['views', 'likes'], aggfunc='sum').reset_index()
        df_ctr_pivot['day_ctr'] = round(100 * df_ctr_pivot['likes'] / df_ctr_pivot['views'], 2)
        org_ads = new_users_df[['first_visit', 'organic_users', 'ads_users']].melt(
            id_vars=['first_visit'], value_vars=['organic_users', 'ads_users'])
        df_users = df.pivot_table(index=['date', 'os'])['users'].reset_index()


        fig, axes = plt.subplots(3,2,figsize=(30,30))

        fig.suptitle('Application KPI lineplots')

        sns.lineplot(ax=axes[0,0], data=df_unique_os, x='date', y='users')
        axes[0,0].set_title('Application DAU (Android, iOS)')
        axes[0,0].set_xlabel(None)
        axes[0,0].set_ylabel(None)

        sns.lineplot(ax=axes[0,1], data=org_ads, x='first_visit', y='value', hue='variable')
        axes[0,1].set_title('Application New Users (organic, ads)')
        axes[0,1].set_xlabel(None)
        axes[0,1].set_ylabel(None)

        sns.lineplot(ax=axes[1,0], data=df_users, x='date', y='users', hue='os')
        axes[1,0].set_title('DAU (Newsline)')
        axes[1,0].set_xlabel(None)
        axes[1,0].set_ylabel(None)

        sns.lineplot(ax=axes[1,1], data=df_mess, x='date', y='users')    
        axes[1,1].set_title('DAU (Messenger)')
        axes[1,1].set_xlabel(None)
        axes[1,1].set_ylabel(None)

        sns.lineplot(ax=axes[2,0], data=df_ctr_pivot, x='date', y='day_ctr')    
        axes[2,0].set_title('CTR (Newsline)')
        axes[2,0].set_xlabel(None)
        axes[2,0].set_ylabel(None)

        sns.lineplot(ax=axes[2,1], data=df_mess, x='date', y='mess_per_user')    
        axes[2,1].set_title('Messages per user')
        axes[2,1].set_xlabel(None)
        axes[2,1].set_ylabel(None)
        
        plot_object = io.BytesIO()    
        plt.savefig(plot_object)
        plot_object.name = 'app_report_plot.png'
        plot_object.seek(0)        
        plt.close()          
        
        return plot_object

    
    @task()
    def report_to_bot(text, plot_object):
        chat_id = -927780322   
        my_bot_token = '6504583850:AAEQYH3Jl_LMZzwOpWK4QsRWCAqTNrpFLvE'
        bot = telegram.Bot(token=my_bot_token)
        bot.sendMessage(chat_id=chat_id, text=text)
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)     


    text = get_text(df, df_unique_os, new_users_df, df_mess)    
    plot_object = get_lineplot(df, df_unique_os, new_users_df, df_mess)
    report_to_bot(text, plot_object)
    
dag_an_pavlova_report_full = dag_an_pavlova_report_full()    