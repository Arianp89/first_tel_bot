import os,logging

logging.basicConfig(level=logging.INFO, filename='project.log', format="%(asctime)s - %(levelname)s - %(message)s")


db_confing={'host': os.environ.get('db_host'),'user': os.environ.get('db_user'),'password': os.environ.get('password')}
database_name = os.environ.get('db_name')

ADMIN=[60794725]
API_TOKEN = os.environ.get('tel_token')

proxy_1=os.environ.get('proxy_1')
proxy_2=os.environ.get('proxy_2')

ai_token=os.environ.get('ai_Token')