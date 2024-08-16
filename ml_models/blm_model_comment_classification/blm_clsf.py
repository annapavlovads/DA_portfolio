import pandas as pd
import numpy as np
import glob
import json
import time
import requests
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.simplefilter('ignore')
pd.options.mode.chained_assignment = None

folder_name = 'first_brand' #folder_name = 'second_brand'
file_list = glob.glob(f'{folder_name}/*.csv')
file_container = []
for f in file_list: 
    file_container.append(pd.read_csv(f))
df = pd.concat(file_container, axis=0).drop_duplicates()

ph_rests = json.load(open('first_brand_rests.json'))
hip_rests = json.load(open('second_brand_rests.json'))


if folder_name=='1': 
    brand_name = 'brand_1'
    rest_dict = ph_rests
elif folder_name=='2': 
    brand_name = 'brand_2'
    rest_dict = hip_rests

df['brand_name'] = brand_name
vec_rest_dict = np.vectorize(lambda x: rest_dict[x])
df['restaurant_name'] = vec_rest_dict(df['Ресторан'])
if (df.restaurant_name.isna().sum()!=0): 
    raise ValueError('Найден неизвестный ресторан! Нужно добавить ресторан!')

vec_shorten_comment = np.vectorize(lambda x: x[0:150] if len(x)>10 and isinstance(x, str) else '')
df['Комментарий'] = df['Комментарий'].fillna('')
df['short_comment'] = vec_shorten_comment(df['Комментарий'])
df['order_type'] = df['Тип заказа']
df['created'] = df['Создано']
df['category_food_estimation'] = df['Ответ 1-й'].replace('—', '0').astype(int)
df['category_service_estimation'] = df['Ответ 2-й'].replace('—', '0').astype(int)
df['category_speed_estimation'] = df['Ответ 3-й'].replace('—', '0').astype(int)

respond_list = ['category_food_estimation', 'category_service_estimation', 'category_speed_estimation']
def create_list(row):
    return row.values.tolist()

df['list_of_estims'] = df[respond_list].apply(lambda row: create_list(row), axis=1)

def honest_mean(item): 
    try:
        return (sum(item) / sum(list(map((lambda x: x>0), item))))
    except: 
        return 0

df['mean_estimation'] = df['list_of_estims'].apply(honest_mean)
df['is_positive_comment'] = (df['mean_estimation'] > 8).astype(int)
df['comment_category'] = 'Нет категории'
df['created'] = pd.to_datetime(df['created'].apply(lambda x: x[:10]), format="%d.%m.%Y")

df = df[['ID','brand_name', 'restaurant_name',
         'short_comment', 'order_type','mean_estimation',
         'category_food_estimation', 
         'category_service_estimation', 
         'category_speed_estimation', 'created', 'is_positive_comment']]



def ya_negative_classification(comment_text: str) -> str:
    """
    Классифицирует текст в одну из категорий на негативный отзыв.

    Args:
        comment_text (str): Текст, который необходимо классифицировать.

    Returns:
        str: Главная категория, которой принадлежит текст.
    """

    label_list = ['отравление', 'плохой вкус блюд', 'долго ждать, опоздание', 'невежливость', 'не дозвониться',
                  'бронирование столов', 'неудобно в ресторане', 'грязно', 'недостача заказа', 
                  'плохая работа приложения или сайта', 'другое']

    config = json.load(open('config.json'))
    api_key = config['api_key']
    folder_id = config['folder_id']
    model_uri = f'cls://{folder_id}/yandexgpt/latest'
    task_description = 'Классифицируй текст в одну из категорий, к которой он принадлежит'

    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/fewShotTextClassification'

    data = {
        "modelUri": model_uri,
        "taskDescription": task_description,
        "labels": label_list,
        "text": comment_text
    }

    headers = {
        'Authorization': f'Api-Key {api_key}', 
        'x-folder-id': folder_id
    }

    try: 
        time.sleep(1)
        response = requests.post(url, json=data, headers=headers)
        result = response.json()['predictions']
        conf_list = [(item['label'], item['confidence']) for item in result]
        conf_list.sort(key=lambda x: x[1], reverse=True)
        main_category = conf_list[0][0]
        return main_category
    except: 
        return 'error'
    



def ya_positive_classification(comment_text: str) -> str:
    """
    Классифицирует текст в одну из категорий на позитивный отзыв.

    Args:
        comment_text (str): Текст, который необходимо классифицировать.

    Returns:
        str: Главная категория, которой принадлежит текст.
    """

    label_list = ['вкусно', 'вежливость', 'красиво', 'чисто', 'быстро, вовремя', 'благодарность', 'другое']

    config = json.load(open('config.json'))
    api_key = config['api_key']
    folder_id = config['folder_id']
    model_uri = f'cls://{folder_id}/yandexgpt/latest'
    task_description = 'Классифицируй текст в одну из категорий, к которой он принадлежит'

    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/fewShotTextClassification'

    data = {
        "modelUri": model_uri,
        "taskDescription": task_description,
        "labels": label_list,
        "text": comment_text
    }

    headers = {
        'Authorization': f'Api-Key {api_key}', 
        'x-folder-id': folder_id
    }

    time.sleep(1)
    
    try: 
        time.sleep(1)
        response = requests.post(url, json=data, headers=headers)
        result = response.json()['predictions']
        conf_list = [(item['label'], item['confidence']) for item in result]
        conf_list.sort(key=lambda x: x[1], reverse=True)
        main_category = conf_list[0][0]
        return main_category
    except: 
        return 'error'
    


df.loc[((df['is_positive_comment']==1) & (df['short_comment']!='')
        ), 'comment_category'] = df.loc[(df['is_positive_comment']==1) & (df['short_comment']!='')
                                        ]['short_comment'].apply(ya_positive_classification)
    
df.loc[((df['is_positive_comment']==0) & (df['short_comment']!='')
        ), 'comment_category'] = df.loc[(df['is_positive_comment']==0) & (df['short_comment']!='')
                                        ]['short_comment'].apply(ya_negative_classification)
    


file_name = f'final_comment_classes_{folder_name}.xlsx'
df.to_excel(file_name)