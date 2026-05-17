import logging
import mysql.connector
from confing import *




def create_database(database_name):
    conn=mysql.connector.connect(**db_confing)
    cur=conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {database_name};")
    cur.execute(f"CREATE database {database_name} ;")
    conn.commit()
    cur.close()
    conn.close()
    print(f'database {database_name} created successfully')
    logging.info(f'database {database_name} created successfully')


def create_table_customer(database_name):
    conn=mysql.connector.connection.MySQLConnection(**db_confing, database=database_name)
    cur=conn.cursor()
    SQL_Query="""
    CREATE TABLE CUSTOMER(
    `ID`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `NAME`              VARCHAR(20) ,
    `PHONE`             VARCHAR(11) ,
    `EMAIL`             VARCHAR(50) ,
    `PASSWORD`          VARCHAR(50) ,
    `BLACK_LIST`        VARCHAR(5)  ,
    `REGISTER_DATE`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `LAST_UPDATE`       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    cur.execute(SQL_Query)
    conn.commit()
    cur.close()
    conn.close()
    print(f'table customer created successfully')
    logging.info(f'table customer created successfully')


def create_table_product(database_name):
    conn=mysql.connector.connect(**db_confing, database=database_name)
    cur=conn.cursor()
    SQL_Query="""
    CREATE TABLE PRODUCT(
    `ID`                    INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `BOT_TOKEN`             TEXT NOT NULL,
    `PROJECT_FILE_ID`       VARCHAR(50) ,
    `TIME_GIVE`             INT NOT NULL,
    `BOT_SPECE_SOUND_ID`    BIGINT NOT NULL ,
    `TOTAL_COST`            INT NOT NULL,
    `FEE_PAID`              INT NOT NULL,
    `RAN_IN_SERSER`         VARCHAR(4),
    `STATUS`                TEXT,
    `REGISTER_DATE`         DATETIME DEFAULT CURRENT_TIMESTAMP,
    `LAST_UPDATE`           DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );"""
    cur.execute(SQL_Query)
    conn.commit()
    cur.close()
    conn.close()
    print('table product created successfully')
    logging.info('table product created successfully')


def create_table_sale(database_name):
    conn=mysql.connector.connection.MySQLConnection(**db_confing , database=database_name)
    cur=conn.cursor()
    SQL_Query="""
    CREATE TABLE SALE(
    `ID`                VARCHAR(6) NOT NULL  PRIMARY KEY ,
    `CUSTOMER_ID`       BIGINT UNSIGNED NOT NULL,
    `REGEITER_DATE`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `LAST_UPDATE`       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER(ID)
    );
    """
    cur.execute(SQL_Query)
    conn.commit()
    cur.close()
    conn.close()
    print(f'table sale created successfully')
    logging.info(f'table sale created successfully')



def create_table_sale_row(database_name):
    conn=mysql.connector.connection.MySQLConnection(**db_confing , database=database_name)
    cur=conn.cursor()
    SQL_Query="""
    CREATE TABLE SALE_ROW(
    `SALE_ID`                   VARCHAR(6) NOT NULL ,
    `PRODUCT_ID`                INT UNSIGNED NOT NULL  ,
    `REGISTER_DATE`             DATETIME DEFAULT CURRENT_TIMESTAMP,
    `LAST_UPDATE`               DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (SALE_ID)       REFERENCES SALE(ID),
    FOREIGN KEY (PRODUCT_ID)    REFERENCES PRODUCT(ID)
    );
    """
    cur.execute(SQL_Query)
    conn.commit()
    cur.close()
    conn.close()
    print(f'table sale_row created successfully')
    logging.info(f'table sale_row created successfully') 


if __name__ == '__main__':
    create_database(database_name)
    create_table_customer(database_name)
    create_table_product(database_name)
    create_table_sale(database_name)
    create_table_sale_row(database_name)
    print('end the project')