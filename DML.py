import mysql.connector
import logging
import string
import random
from confing import db_confing,database_name


def take_random_karckter():
    requence=string.ascii_lowercase + string.ascii_uppercase + string.digits
    return str(''.join(random.choices(requence,k=6)))

def add_customer(id,name,phone):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET NAME=%s,PHONE=%s where ID=%s;"
    cur.execute(SQL_Query, (name,phone,id ))
    conn.commit()
    cur.close()
    conn.close()
    print(f'customer {id} add ')
    logging.info(f' add new customer by id:{id}')
    return cur.lastrowid


def add_email_password(cid,email,password):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET EMAIL=%s,password=%s where ID=%s"
    cur.execute(SQL_Query, (email,password,cid))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'the customer change name to(cid)')


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


def add_new_project(customer_id,EMAIL,PASSWORD,BOT_TOKEN,TIME_GIVE,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER=None):
    project_id=add_new_product(None,EMAIL,PASSWORD,BOT_TOKEN,TIME_GIVE ,BOT_SPECE_SOUND_ID,TOTAL_COST,FEE_PAID,RAN_IN_SERSER)
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



def add_customer_black_list(customer_id,time,stage=1,don='no'):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    cur.execute("SELECT * FROM BLACK_LIST WHERE CUSTOMER_ID=%s", (customer_id,))
    user = cur.fetchone()
    if user==None:
        SQL_Query ="INSERT INTO BLACK_LIST (customer_id,STATUS,STAGE,DON,TIME) VALUES (%s,%s,%s,%s,%s);"
        cur.execute(SQL_Query, (customer_id,'yes',stage,don,time))
        conn.commit()
    else:
        SQL_Query = "UPDATE BLACK_LIST SET STATUS=%s,STAGE=%s,DON=%s,TIME=%s WHERE CUSTOMER_ID=%s;"
        cur.execute(SQL_Query, ('yes',stage,don,time,customer_id))
        conn.commit()
    cur.close()
    conn.close()

def came_customer_black_list(customer_id,stage):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE BLACK_LIST SET STATUS=%s,STAGE=%s,DON=%s WHERE CUSTOMER_ID=%s;"
    cur.execute(SQL_Query, ('no',stage,'yes',customer_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'customer {customer_id} came from the black list')
    print('came')


def register_user(cid,name):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    cur.execute("SELECT * FROM CUSTOMER WHERE ID=%s", (cid,))
    user = cur.fetchone()
    if user==None:
        cur.execute("INSERT INTO CUSTOMER (ID,NAME) VALUES (%s,%s)", (cid,name))
        conn.commit()
    cur.close()
    conn.close()


def delete_customer(cid):
    conn = mysql.connector.connect(
        **db_confing,
        database=database_name
    )
    cur = conn.cursor()

    try:
        # حذف مشتری از لیست سیاه (در صورت وجود)
        cur.execute(
            "DELETE FROM BLACK_LIST WHERE CUSTOMER_ID = %s",
            (cid,)
        )

        # حذف تمام خریدهای مشتری
        cur.execute(
            "DELETE FROM SALE WHERE CUSTOMER_ID = %s",
            (cid,)
        )

        # حذف خود مشتری
        cur.execute(
            "DELETE FROM CUSTOMER WHERE ID = %s",
            (cid,)
        )

        conn.commit()

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"خطای پایگاه داده: {err}")

    finally:
        cur.close()
        conn.close()
register_user(1,'aaaaaaaaaa')
add_customer(1,'ali',9339798695)
add_new_product(1,'token',14,111111,50000000,1,STATUS='no')
add_sale('aaa',1)
add_sale_row('aaa',1)
delete_customer(1)
