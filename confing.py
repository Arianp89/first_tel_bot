import os

db_confing={'host': os.environ.get('db_host'),'user': os.environ.get('db_user'),'password': os.environ.get('password')}
database_name = os.environ.get('db_name')


API_TOKEN = os.environ.get('tel_token')

proxy_1=os.environ.get('proxy_1')
proxy_2=os.environ.get('proxy_2')

ai_token=os.environ.get('ai_Token')