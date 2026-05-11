import mysql.connector
import logging
import string
import random
from confing import db_confing,database_name


def take_random_karckter():
    requence=string.ascii_lowercase + string.ascii_uppercase + string.digits
    return str(''.join(random.choices(requence,k=6)))

def add_customer( id ,name , phone ):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "INSERT INTO CUSTOMER (ID,NAME, PHONE) VALUES (%s , %s , %s);"
    cur.execute(SQL_Query, (id , name, phone ))
    conn.commit()
    cur.close()
    conn.close()
    print(f'customer {name} data ')
    logging.info(f' add new customer by id:{id},name{name}')
    return cur.lastrowid

def add_new_product(ID,BOT_TOKEN,TIME_GIVE,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER=None,STATUS=None):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "INSERT INTO PRODUCT (ID,BOT_TOKEN,TIME_GIVE,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER,STATUS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
    cur.execute(SQL_Query, (ID,BOT_TOKEN,TIME_GIVE,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER,STATUS))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'add new project by id:{cur.lastrowid}')
    return  cur.lastrowid


def add_sale(id,customer_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "INSERT INTO SALE (ID,CUSTOMER_ID) VALUES (%s,%s);"
    cur.execute(SQL_Query, (id,customer_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'add new sale by id:{cur.lastrowid}')
    return  cur.lastrowid


def add_sale_row(sale_id,product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "INSERT INTO SALE_ROW (SALE_ID,PRODUCT_ID) VALUES (%s,%s);"
    cur.execute(SQL_Query, (sale_id,product_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'add new sale row by id:{cur.lastrowid}')

def edit_customer_name(name,cid):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET NAME=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (name,cid))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'the customer change name to{name}')    


def edit_customer_phone(phone_number,cid):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET PHONE=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (phone_number,cid))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'the customer change name to{phone_number}')     




def add_file_project(file_id,product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE PRODUCT SET PROJECT_FILE_ID=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (file_id,product_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info('admin add file project')


def add_new_project(customer_id,BOT_TOKEN,BOT_SPECE_TEXT,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER=None):
    project_id=add_new_product(None,BOT_TOKEN,BOT_SPECE_TEXT,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER)
    random=take_random_karckter()
    add_sale(random,customer_id)
    add_sale_row(random,project_id)
    return random

def chenge_status_product(status,product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE PRODUCT SET STATUS=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (status,product_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info('admin add file project')