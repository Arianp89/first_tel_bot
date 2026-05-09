import mysql.connector
import datetime,time
from confing import db_confing,database_name


def get_user_data(user_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM CUSTOMER WHERE ID=%s;"
    cur.execute(SQL_Query, (user_id,))
    data = cur.fetchone()    
    cur.close()
    conn.close()
    if data==None:
        return None
    return { 'id':data['ID'],'name':data['NAME'],'phone':data['PHONE']}

def get_bot_data(cid):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT ID FROM SALE WHERE CUSTOMER_ID=%s;"
    cur.execute(SQL_Query, (cid,))
    ids = cur.fetchall()
    cur.close()
    conn.close()
    return [row['ID'] for row in ids]

def get_file_id_data():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM PRODUCT WHERE PROJECT_FILE_ID=%s;"
    cur.execute(SQL_Query, (1,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return [row['ID'] for row in data]   


def get_product_data_A(sale_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT PRODUCT_ID FROM SALE_ROW WHERE SALE_ID=%s", (sale_id,))
    data = cur.fetchone()['PRODUCT_ID']
    conn.close()
    cur.close()
    return data


def get_product_data_B(product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_QUERY = "SELECT * FROM PRODUCT WHERE ID=%s;"
    cur.execute(SQL_QUERY, (product_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


def get_product_token():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT BOT_TOKEN FROM PRODUCT;"
    cur.execute(SQL_Query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return [row['BOT_TOKEN'] for row in data]


def get_produt_register_data():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True) 
    SQL_Query = "SELECT * FROM PRODUCT;"
    cur.execute(SQL_Query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return{char['ID']: char['REGISTER_DATE'] for char in data}


def get_sale_id(product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True) 
    SQL_Query = "SELECT SALE_ID FROM SALE_ROW WHERE PRODUCT_ID=%s;"
    cur.execute(SQL_Query,(product_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


def get_time(product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True) 
    SQL_Query = "SELECT TIME_GIVE FROM PRODUCT WHERE ID=%s;"
    cur.execute(SQL_Query,(product_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def check_time():
    ban_id=[]
    while True:
        today = datetime.datetime.now()
        for key,val in get_produt_register_data().items():
            hundred_days_delta = datetime.timedelta(days=get_time(key)-3)
            previous_date = val + hundred_days_delta
            if previous_date==today.strftime('%Y/%m/%d') and  key not in ban_id:
                ban_id.append(key)
                print(key)
                return get_sale_id(key)
        time.sleep(120)



print(get_file_id_data())