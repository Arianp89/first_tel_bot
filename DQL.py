import mysql.connector
import datetime,time
from confing import db_confing,database_name


def get_customer_data(user_id):
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


def get_all_customer_data():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM CUSTOMER;"
    cur.execute(SQL_Query)
    data = cur.fetchall()    
    cur.close()
    conn.close()
    return data  

def get_sale_id_b_cid(cid):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT ID FROM SALE WHERE CUSTOMER_ID=%s;"
    cur.execute(SQL_Query, (cid,))
    ids = cur.fetchall()
    cur.close()
    conn.close()
    return [row['ID'] for row in ids]

def get_sale_row_data():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM SALE_ROW;"
    cur.execute(SQL_Query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return [row['SALE_ID'] for row in data]


def get_product_id_f_sale_row(sale_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT PRODUCT_ID FROM SALE_ROW WHERE SALE_ID=%s", (sale_id,))
    data = cur.fetchone()
    conn.close()
    cur.close()
    return data


def get_product_data(product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_QUERY = "SELECT * FROM PRODUCT WHERE ID=%s;"
    cur.execute(SQL_QUERY, (product_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


def get_all_token():
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True)
    SQL_Query = "SELECT BOT_TOKEN FROM PRODUCT;"
    cur.execute(SQL_Query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return [row['BOT_TOKEN'] for row in data]


def get_all_register_data():
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
        for key,val in get_all_register_data().items():
            hundred_days_delta = datetime.timedelta(days=get_time(key)-3)
            previous_date = val + hundred_days_delta
            if previous_date==today.strftime('%Y/%m/%d') and  key not in ban_id:
                ban_id.append(key)
                print(key)
                return get_sale_id(key)
        time.sleep(120)

def get_customer_id(sale_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True) 
    SQL_Query = "SELECT CUSTOMER_ID FROM SALE WHERE ID=%s;"
    cur.execute(SQL_Query,(sale_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data['CUSTOMER_ID']

def have_email(email):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor(dictionary=True) 
    SQL_Query = "SELECT * FROM customer  WHERE EMAIL=%s;"
    cur.execute(SQL_Query,(email,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data
