import mysql.connector
import logging
import string
import random
from config import db_confing,database_name


def take_random_karakter():
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
    logging.info(f' add new customer by id:{id} and name:{name}')
    return cur.lastrowid


def add_email_password(customer_id,email,password):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET EMAIL=%s,password=%s WHERE ID=%s"
    cur.execute(SQL_Query, (email,password,customer_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"""cusrtomer by id:{customer_id} add
email:{email}
password:{password}
""")


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

def edit_customer_name(name,customer_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET NAME=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (name,customer_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'customer {customer_id} change name to{name}')    


def edit_customer_phone(phone_number,customer_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE CUSTOMER SET PHONE=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (phone_number , customer_id ))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'customer {customer_id} change name to{phone_number}')     




def add_file_project(file_id,product_id):
    conn = mysql.connector.connect(**db_confing, database=database_name)
    cur = conn.cursor()
    SQL_Query = "UPDATE PRODUCT SET PROJECT_FILE_ID=%s WHERE ID=%s;"
    cur.execute(SQL_Query, (file_id,product_id))
    conn.commit()
    cur.close()
    conn.close()
    logging.info('admin add adress file project')



def change_product_status(status,product_id):
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

from mysql.connector import errorcode
from typing import Union

def purge_customer_entirely(customer_id: Union[int, str]) -> bool:
    """
    یک عملیات اتمیک (All-or-Nothing) برای حذف کامل یک مشتری و تمام وابستگی‌های آن.
    مراحل: حذف SALE_ROW -> حذف SALE -> حذف BLACK_LIST -> حذف CUSTOMER
    """
    
    conn = None
    try:
        # ایجاد اتصال
        conn = mysql.connector.connect(**db_confing, database=database_name)
        # غیرفعال کردن Autocommit برای مدیریت دستی تراکنش (بسیار مهم)
        conn.autocommit = False 
        cur = conn.cursor()

        logging.warning(f"⚠️ شروع عملیات پاکسازی کامل برای مشتری: {customer_id}")

        # مرحله 1: حذف تمام جزئیات فاکتورهای این مشتری (SALE_ROW)
        # اول باید بدانیم این مشتری چه فاکتورهایی داشته، سپس ردیف‌های آن فاکتورها را حذف می‌کنیم
        # نکته: اگر در SALE_ROW مستقیماً customer_id نداری، باید از طریق جدول SALE عمل کنی.
        # اینجا فرض می‌کنیم در SALE_ROW ستونی به نام sale_id داریم که به جدول SALE وصل است.
        
        # ابتدا شناسه‌های فروش (Sale IDs) متعلق به این مشتری را می‌گیریم
        cur.execute("SELECT ID FROM SALE WHERE CUSTOMER_ID = %s", (customer_id,))
        sale_ids = [row[0] for row in cur.fetchall()]

        if sale_ids:
            # حذف ردیف‌های مربوط به تمام فاکتورهای این مشتری
            format_strings = ','.join(['%s'] * len(sale_ids))
            query_rows = f"DELETE FROM SALE_ROW WHERE SALE_ID IN ({format_strings})"
            cur.execute(query_rows, tuple(sale_ids))
            logging.info(f"✅ {cur.rowcount} ردیف از SALE_ROW پاکسازی شد.")

        # مرحله 2: حذف خودِ رکورد فاکتورها از جدول SALE
        cur.execute("DELETE FROM SALE WHERE CUSTOMER_ID = %s", (customer_id,))
        logging.info(f"✅ {cur.rowcount} رکورد از SALE پاکسازی شد.")

        # مرحله 3: حذف مشتری از لیست سیاه (BLACK_LIST)
        cur.execute("DELETE FROM BLACK_LIST WHERE CUSTOMER_ID = %s", (customer_id,))
        logging.info(f"✅ ردیف مربوطه از BLACK_LIST پاکسازی شد.")

        # مرحله 4: حذف خودِ مشتری از جدول اصلی CUSTOMER
        cur.execute("DELETE FROM CUSTOMER WHERE ID = %s", (customer_id,))
        
        if cur.rowcount == 0:
            logging.error(f"❌ خطا: مشتری با شناسه {customer_id} یافت نشد. هیچ تغییری اعمال نشد.")
            conn.rollback()
            return False

        # اگر همه مراحل بدون خطا انجام شد، تمام تغییرات را یکجا ذخیره کن
        conn.commit()
        logging.info(f"🔥 عملیات پاکسازی با موفقیت انجام شد. مشتری {customer_id} به طور کامل حذف شد.")
        return True

    except mysql.connector.Error as err:
        # اگر هر خطایی در هر مرحله رخ دهد، تمام تغییرات تا این لحظه کنسل می‌شود (Rollback)
        if conn:
            conn.rollback()
        
        if err.errno == errorcode.ER_LOCK_WAIT_TIMEOUT:
            logging.error("❌ خطای زمان انتظار برای قفل شدن رکورد (Lock Timeout).")
        elif err.errno == errorcode.ER_ROW_IS_REFERENCED_2:
            logging.error("❌ خطا: این مشتری توسط جدول دیگری در حال استفاده است (Constraint Violation).")
        else:
            logging.error(f"❌ خطای دیتابیس: {err}")
        return False

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"❌ خطای سیستمی غیرمنتظره: {e}")
        return False

    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
            logging.info("🔌 اتصال به دیتابیس بسته شد.")
