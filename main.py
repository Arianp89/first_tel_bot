from config import ai_token, proxy_2, proxy_1, API_TOKEN, ADMIN
from DQL import *
from DML import *
# from requests_forwarder import setup_proxy
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from Text import texts
from openai import OpenAI
import telebot 
import logging
import time
import requests
import os
import threading
import datetime

# setup_proxy(proxy_1)
# setup_proxy(proxy_2)

# telebot.apihelper.API_URL = 'http://tapi.bale.ai/bot{0}/{1}'
bot = telebot.TeleBot(API_TOKEN)

# Initialize application global state dictionaries
user_step_ai = dict()
contact_us_data = dict()
creat_bot_data = dict()
user_step_profile = dict()
user_step_creat_bot = dict()
user_step_contact_us = dict()
user_step_profile_mid = dict()
admin_send_location_data = dict()
creat_bot_data_total_cost = dict()
admin_step_send_location_file = dict()
admin_send_message_to_customer = dict()
admin_send_message_to_customer_data = dict()

# Initialize AI Client Configuration
def ai(message):
    client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=ai_token)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


# Safe send message wrapper with automated fallback logs
def send_message(*args, **kwargs):
    try:
        return bot.send_message(*args, **kwargs)
    except Exception as e:
        logging.error(f'send message error:{e}')


# Markups Configuration
def customer_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['create_bot'])
    markup.add(texts['profile'])
    markup.add(texts['about_us'], texts['contact_us'])
    return markup


def admin_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['check_customer'], texts['check_project'])
    markup.add(texts['send_location_file'], texts['send_message_to_customer'])
    markup.add(texts['ai_for_admin'])
    return markup


def back_meno():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['go_home'])
    return markup


# Token verification routing check
def check_token(token):
    url = f"http://tapi.bale.ai/bot{token}/getMe"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            return [True, data['result']['username']]
        else:
            print("The token is invalid!")
            return False
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False
    


def download_voice(cid , file_id,file_name):
    save_path = os.path.join('Data', 'voice', str(cid))
    os.makedirs(save_path, exist_ok=True)
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    content = bot.download_file(file_path)
    with open(os.path.join(save_path, str(file_name) + '.mp3'), 'wb') as f:
        f.write(content)


def send_voice(cid,customer_id ,text , product_id):
    save_path = os.path.join('Data', 'voice', str(customer_id))
    print(save_path)
    file_name = get_voice_id(product_id)
    print(file_name)
    with open(os.path.join(save_path, str(file_name) + '.mp3') , 'rb') as f:
        bot.send_voice(cid , f , caption=text)


# Anti-Spam Control monitoring functionality
find_spam_data = dict()     # {cid:[len,time],...}
def find_spam(cid, maximum_time=1, maximum_watch=5):  
    global find_spam_data
    now = time.time()
    if cid not in find_spam_data:
        find_spam_data[cid] = [0, time.time()]
    if now - find_spam_data[cid][1] < maximum_time:
        find_spam_data[cid][0] += 1
    if find_spam_data[cid][0] % maximum_watch == 0:
        data = get_customer_black(cid)

        if cid not in get_black_list_list():
            add_customer_black_list(cid, time.time())
            text = texts['spam_ban_15'].format(name=get_customer_data(cid)['name'])
            bot.send_message(cid, text)
            logging.warning(f"User {cid} blocked for 15 minutes due to spam activity.")
        elif data['STAGE'] == 1 and data['DON'] == 'true':
            text = texts['spam_ban_60'].format(name=get_customer_data(cid)['name'])
            add_customer_black_list(cid, time.time(), 2)
            bot.send_message(cid, text)
            logging.warning(f"User {cid} blocked for 60 minutes due to structural Stage 1 spam.")
        elif data['STAGE'] == 2 and data['DON'] == 'true':
            add_customer_black_list(cid, time.time(), 3)
            logging.warning(f"User {cid} blacklisted permanently under Stage 3 restriction rules.")
    find_spam_data[cid][1] = time.time()


# Main Global Chat Update Listener Routine
def listener(messages):
    for m in messages:
        find_spam( m.chat.id)
        if m.content_type == 'text':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: {m.text}")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: {m.text}")
        elif m.content_type == 'photo':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New photo received")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New photo received")
        elif m.content_type == 'document':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New document received")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New document received")
        elif m.content_type == 'voice':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New voice received")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New voice received")
        if check_black_list(m.chat.id) == False:
            print('it not in black list')
bot.set_update_listener(listener)  


# Start command implementation logic
@bot.message_handler(commands=['start'])
def message_start_handler(message):
    cid = message.chat.id
    register_user(cid, message.chat.first_name)
    if check_black_list(cid) == False:
        if cid in ADMIN:
            send_message(cid, texts['admin_welcome'], reply_markup=admin_markup())
        else:
            bot.send_message(cid, texts['user_welcome'], reply_markup=customer_markup())


# Navigation back processing menu
@bot.message_handler(func=lambda message: message.text == texts['go_home'])
def back_to_home_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in user_step_creat_bot:
            user_step_creat_bot.pop(cid)
        if cid in user_step_profile:
            user_step_profile.pop(cid)
        bot.send_message(cid, texts['choose_from_menu'], reply_markup=customer_markup())





#________________________________________ ADMIN BUTTON __________________________________________

# Customer data checking metrics monitor setup
@bot.message_handler(func=lambda message: message.text == texts['check_customer'])
def check_customer_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        customer_num = 0
        in_black_list = 0
        notin_black_list = 0
        for i in get_all_customer_data():
            customer_num += 1
            if get_customer_black(i['ID']) !=None:
                if get_customer_black(i['ID'])['STATUS'] == 'true':
                    in_black_list += 1
                else:
                    notin_black_list += 1
            else:
                notin_black_list += 1
        text = texts['customer_stats_admin'].format(customer_num=customer_num, yes_black_list=in_black_list, no_black_list=notin_black_list)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['btn_view_customers'], callback_data='customer_data'))
        bot.send_message(cid, text, reply_markup=markup)     



# Project metrics analytical dashboard inside internal Admin panel 
@bot.message_handler(func=lambda message: message.text == texts['check_project'])
def check_project_handler_admin(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in ADMIN:
            if get_all_product_data()!=[]:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(texts['active_projects'], callback_data='check-projects_false'))
                markup.add(InlineKeyboardButton(texts['finished_projects'], callback_data='check-projects_true'))
                markup.add(InlineKeyboardButton(texts['btn_not_paid_projects'] , callback_data=f'check-projects_not pay'))
                all_project = 0
                on_project = 0
                off_project = 0
                for project in get_all_product_data():
                    all_project += 1
                    if project['STATUS'] == 'false':
                        on_project += 1
                    else:
                        off_project += 1
                text = texts['project_stats_admin'].format(all_project=all_project, on_project=on_project, off_project=off_project)
                bot.send_message(cid, text, reply_markup=markup)
            else:
                bot.send_message(cid,texts['no_active_projects'])
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())




# Broadcasting execution strategy configuration 
@bot.message_handler(func=lambda message: message.text == texts['send_message_to_customer'])
def admin_send_file_to_customer_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['send_to_all'], callback_data='send file_all'))
        markup.add(InlineKeyboardButton(texts['send_to_one'], callback_data="send file_one"))
        bot.send_message(cid, texts['admin_choose_menu'], reply_markup=markup)
    

@bot.message_handler(func=lambda message: admin_send_message_to_customer.get(message.chat.id) in ['A', 'B'])
def admin_send_message_to_customer_handler_A_B(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        step = admin_send_message_to_customer.get(cid)
        if step == 'A':
            number = 0
            unsuccessful = 0
            successful = 0
            for i in get_all_customer_data():
                number += 1
                if number % 20 == 0: time.sleep(2)
                try:
                    bot.send_message(i['ID'], message.text)
                    successful += 1
                except:
                    unsuccessful += 1
            text = texts['broadcast_finished'].format(successful=successful, unsuccessful=unsuccessful)
            bot.send_message(cid, text)
        elif step == 'B':
            customer_id = admin_send_message_to_customer_data[cid]
            try:
                bot.send_message(customer_id, message.text)
                bot.send_message(cid, texts['message_sent_success'])
            except:
                bot.send_message(cid , texts['msg_send_failed'])
        admin_send_message_to_customer.pop(cid) 



@bot.message_handler(func=lambda message: message.text == texts['send_location_file'])
def send_location_file_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in ADMIN:
            false = 0
            for i in get_all_product_data():
                if i['STATUS'] == 'false':
                    false += 1
            if false != 0:
                markup = InlineKeyboardMarkup()
                for i in get_sale_row_data():
                    product_id = get_product_id_f_sale_row(i)
                    product_data = get_product_data(product_id['PRODUCT_ID'])
                    if product_data != None:
                        if product_data['STATUS'] == 'false':
                            markup.add(InlineKeyboardButton(f"{i}", callback_data=f"send-lcn-file_{i}"))
                bot.send_message(cid, texts['missing_file_projects'], reply_markup=markup)
            else:
                bot.send_message(cid, texts['no_active_projects'])
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())


@bot.message_handler(func=lambda message: admin_step_send_location_file.get(message.chat.id) == 'A')
def send_location_file_handler_A(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        try:
            sale_id = admin_send_location_data[cid]
            github_id = message.text
            add_file_project(github_id, get_product_id_f_sale_row(sale_id)['PRODUCT_ID'])
            customer_id = get_customer_id(sale_id)
            product_data = get_product_data(get_product_id_f_sale_row(sale_id)['PRODUCT_ID'])
            user_step_creat_bot[customer_id]='G'
            text=texts['end_admin_approved_pay'].format(amount = product_data['TOTAL_COST']-product_data['FEE_PAID']  , sale_id = sale_id)
            bot.send_message(int(customer_id), text , reply_markup=customer_markup())
            bot.send_message(cid, texts['file_link_saved'])
        except Exception as e:
            bot.send_message(cid, texts['file_send_error'])
            logging.error(f'error in send location file: {e}')
        admin_step_send_location_file.pop(cid)



# Admin AI workspace route entry point
@bot.message_handler(func=lambda message: message.text == texts['ai_for_admin'])
def ai_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in ADMIN:
            bot.send_message(cid, texts['enter_ai_prompt'])
            user_step_ai[cid] = 'A'
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())


@bot.message_handler(func=lambda message: user_step_ai.get(message.chat.id) == 'A')
def ai_handler_A(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        bot.send_chat_action(cid, 'typing', timeout=5)
        text = ai(message.text)
        bot.send_message(cid, text)
        user_step_ai.pop(cid)




#_______________________________ CUSTOMER BUTTON ________________________________

# Support contact routing pipeline
@bot.message_handler(func=lambda message: message.text == texts['contact_us'])
def message_contact_us_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['yes'], callback_data='contact us_true'),
                   InlineKeyboardButton(texts['no'], callback_data='contact us_false'))
        bot.send_message(cid, texts['ask_send_message'], reply_markup=markup)


@bot.message_handler(func=lambda message: user_step_contact_us.get(message.chat.id) == 'A')
def message_contact_us_handler_A(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        customer_message = message
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['btn_reply_user'], callback_data=f'response contact_{cid}'))
        msg_content = customer_message.text if customer_message.content_type == 'text' else texts['non_text_message']
        text = texts['admin_forward_contact'].format(name=get_customer_data(cid)['name'], message=msg_content)
        for ad in ADMIN:
            bot.send_message(ad, text, reply_markup=markup)
            break
        user_step_contact_us.pop(cid)
        send_message(cid, texts['msg_sent_to_admin_success'])


@bot.message_handler(func=lambda message: user_step_contact_us.get(message.chat.id) == 'B')
def B_contact_us_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        message_text = message.text
        customer_id = contact_us_data.get(cid)
        if customer_id != None:
            bot.send_message(customer_id, texts['support_reply_header'].format(message=message_text))
            send_message(cid, texts['msg_sent_to_user_success'], reply_markup=admin_markup())
        user_step_contact_us.pop(cid)


# About Us layout distribution logic
@bot.message_handler(func=lambda message: message.text == texts['about_us'])
def about_us_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        number = 0
        for token in get_all_token():
            number += 1
        if number >= 5:
            number = 0
            text = texts['bot_list_header']
            for token in get_all_token():
                number += 1
                try:
                    check_res = check_token(token)
                except:
                    logging.error('have error to check token in adout_us button')
                if check_res:
                    text += f"{number}: @{check_res[1]}\n"
            send_message(cid, text)
        else:
            bot.send_message(cid,texts['about_us_disabled'])





# Registration order setup wizard workflow 
@bot.message_handler(func=lambda message: message.text == texts['create_bot'])
def creat_bot_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        creat_bot_data[cid] = {'name': None, 'bot_token': None, 'total_cost': None, 'time_give': None , 'voice_file_id': None, 'photo_file_id': None, 'email': None, 'password': None}
        if get_customer_data(cid)['phone'] == None:
            send_message(cid, texts['enter_name'])
            user_step_creat_bot[cid] = 'A'
        else:
            if have_email(cid) != None:
                text=texts['enter_bot_details_no_server']
            else:
                text=texts['enter_bot_details_server']
            bot.send_message(cid , text , reply_markup=back_meno())
            user_step_creat_bot[cid] = 'C'

@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'A')
def create_bot_handler_A(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if len(message.text) > 20:
            bot.send_message(cid , texts['error_send_low_caracter'])
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(texts['send_contact_btn'], request_contact=True))
        send_message(cid, texts['enter_phone'], reply_markup=markup)
        user_step_creat_bot[cid] = 'B'
        creat_bot_data[cid]["name"] = message.text


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'B', content_types=['contact'])
def create_bot_handler_B_contact(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        phone = message.contact.phone_number
        if get_customer_data(cid)['phone'] == None:
            if cid == message.contact.user_id:
                if phone.startswith('98'):
                    phone = phone[2:] 
            add_customer(cid, creat_bot_data[cid]['name'], int(phone))
            if have_email(cid) != None:
                text=texts['enter_bot_details_no_server']
            else:
                text=texts['enter_bot_details_server']
            bot.send_message(cid , text , reply_markup=back_meno())
        user_step_creat_bot[cid]='C'


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'B')
def create_bot_handler_B_text(message):
    cid = message.chat.id
    phone = message.text
    if check_black_list(cid) == False:
        if get_customer_data(cid)['phone'] == None:
            if phone[:2] == '98':
                phone = phone[2:]
            elif phone[:1] == '0':
                phone = phone[1:]
            add_customer(cid, creat_bot_data[cid]['name'], int(phone))
            if have_email(cid) != None:
                text=texts['enter_bot_details_no_server']
            else:
                text=texts['enter_bot_details_server']
            bot.send_message(cid , text)
        user_step_creat_bot[cid]='C'


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'C')
def creat_bot_hadler_C(message):
    cid = message.chat.id
    data=message.text
    def check_integer(text):
        try:
            int(text)
            return True
        except:
            return False
                
    if check_black_list(cid) == False:
        if have_email(cid) != None:
            try:
                token, total_cost, time_give = data.split()
            except Exception as e:
                try:
                    token, total_cost, time_give =data.split('\n')
                except Exception as e:
                    text=texts['error_enter_bot_details_no_server']
                    bot.send_message(cid , text)
                    return
            if check_integer(time_give)==False and check_integer(total_cost)==False:
                bot.send_message(cid , texts['send_integer'])
                return
            elif check_integer(total_cost)==False:
                bot.send_message(cid , texts['integer_cost'])
                return
            elif check_integer(time_give)==False:
                bot.send_message(cid , texts['integer_time-give'])
                return
            creat_bot_data[cid]['token'] = token
            creat_bot_data[cid]['total_cost'] = int(total_cost)
            creat_bot_data[cid]['time_give'] = int(time_give)
            creat_bot_data[cid]['FEE_PAID'] = int(total_cost) / 2
            bot.send_message(cid, texts['send_voice_features'], reply_markup=back_meno())
            user_step_creat_bot[cid] = 'D'
        elif have_email(cid) == None:
            try:
                email, password, token, total_cost, time_give = data.split()
            except Exception as e:
                try:
                    email, password, token, total_cost, time_give= data.split('\n')
                except Exception as e:
                    text=texts['error_enter_bot_details_server']
                    bot.send_message(cid , text)
                    return
            if check_integer(time_give)==False and check_integer(total_cost)==False:
                bot.send_message(cid , texts['send_integer'])
                return
            elif check_integer(total_cost)==False:
                bot.send_message(cid , texts['integer_cost'])
                return
            elif check_integer(time_give)==False:
                bot.send_message(cid , texts['integer_time-give'])
                return
            creat_bot_data[cid]['email'] = email
            creat_bot_data[cid]['password'] = password
            creat_bot_data[cid]['token'] = token
            creat_bot_data[cid]['total_cost'] = int(total_cost)
            creat_bot_data[cid]['time_give'] = int(time_give)
            creat_bot_data[cid]['FEE_PAID'] = int(total_cost) / 2
            add_email_password(cid, email, password) 
            bot.send_message(cid, texts['send_voice_features'], reply_markup=back_meno())
            user_step_creat_bot[cid] = 'D'
        else:
            bot.send_message(cid, texts['invalid_token_retry'])
            user_step_creat_bot[cid] = 'B'


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'D', content_types=['voice', 'document'])
def create_bot_handler_D(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        send_message(cid, texts['data_sent_to_admin'])
        file_id = message.voice.file_id
        creat_bot_data[cid]['voice_file_id'] = file_id
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['confirm'], callback_data=f'check-project-request_true_{cid}'),
                   InlineKeyboardButton(texts['cancel'], callback_data=f'check-project-request_false_{cid}'))
        for ad in ADMIN:
            text = texts['admin_new_order'].format(
                name=get_customer_data(cid)['name'],
                cost=creat_bot_data[cid]['total_cost'],
                time=creat_bot_data[cid]['time_give'],
                token=creat_bot_data[cid]['token']
            )
            bot.send_voice(ad, file_id, text, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'E', content_types=['photo'])
def user_step_create_bot_handler_E(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        file_id = message.photo[-1].file_id
        creat_bot_data[cid]['photo_file_id'] = file_id
        bot.send_message(cid, texts['photo_sent_to_admin'])
        for ad in ADMIN:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['confirm'], callback_data=f'check-deposit_true_{cid}'),
                       InlineKeyboardButton(texts['cancel'], callback_data=f'check-deposit_false_{cid}'))
            text = texts['admin_payment_received'].format(name=get_customer_data(cid)['name'], amount=creat_bot_data[cid]['total_cost'] / 2)
            bot.send_photo(ad, file_id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'F')
def user_step_create_bot_handler_F(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        customer_id = int(creat_bot_data[cid])
        file_name = str(time.time()).replace('.', '')
        project_id = add_new_product(None,
                                        creat_bot_data[customer_id]['token'],
                                        int(creat_bot_data[customer_id]['time_give']),
                                        int(file_name), 
                                        creat_bot_data[customer_id]['total_cost'],
                                        int(message.text),
                                        'false')
        sale_id = take_random_karakter()
        add_sale(sale_id, customer_id)
        add_sale_row(sale_id, project_id)
        # download_voice(customer_id ,creat_bot_data[customer_id]['voice_file_id'] , str(file_name))
        user_step_creat_bot.pop(customer_id, None)
        creat_bot_data.pop(customer_id, None)
        bot.send_message(customer_id, texts['order_registered'].format(id=sale_id), reply_markup=customer_markup())



@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id) == 'G',
                     content_types=['photo'])
def user_step_creat_bot_handler_G(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        file_id = message.photo[-1].file_id
        creat_bot_data[cid] = file_id
        bot.send_message(cid, texts['photo_sent_to_admin'])
        sale_id = admin_send_location_data[ADMIN[0]]
        customer_id = get_customer_id(sale_id)
        product_id = get_product_data_f_sale_row(sale_id)["PRODUCT_ID"]
        product_data=get_product_data(product_id)
        for ad in ADMIN:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['confirm'], callback_data=f'check-lcn_true_{sale_id}'),
                       InlineKeyboardButton(texts['cancel'], callback_data=f'check-lcn_false_{sale_id}'))
            text = texts['admin_payment_received'].format(name=get_customer_data(cid)['name'], amount=product_data['TOTAL_COST']-product_data['FEE_PAID'])
            bot.send_photo(ad, file_id, text, reply_markup=markup)
        admin_send_location_data.pop(ADMIN[0] , None)
        user_step_creat_bot.pop(customer_id , None )


# Profile execution and handling management
@bot.message_handler(func=lambda message: message.text == texts['profile'])
def profile_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        markup = InlineKeyboardMarkup()
        if get_customer_data(cid)['phone'] == None:
            name = texts['not_registered']
            phone = texts['not_registered']
            markup.add(InlineKeyboardButton(texts['btn_enter_info'], callback_data='send_info'))
        else:
            name = get_customer_data(cid)['name']
            phone = get_customer_data(cid)['phone']
            markup.add(InlineKeyboardButton(texts['edit_bot'], callback_data='change_information'))
            markup.add(InlineKeyboardButton(texts['my_bots'], callback_data='my_bots'))
        text = texts['profile_info'].format(name=name, phone=phone)
        msg = send_message(cid, text, reply_markup=markup, parse_mode='HTML')
        user_step_profile_mid[cid] = msg
        



@bot.message_handler(func=lambda message: user_step_profile.get(message.chat.id) == 'A')
def user_step_profile_A(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if len(message.text) >= 20:
            bot.send_message(cid , texts['error_send_low_caracter'])
            return
        if get_customer_data(cid)['phone'] != None:
            name=message.text
            edit_customer_name(name, cid)
            text=texts['name_changed']
            bot.send_message(cid,text)
            user_step_profile.pop(cid)
        else:
            edit_customer_name(message.text,cid)
            user_step_profile[cid] = 'B'
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton(texts['btn_send_phone'], request_contact=True))
            bot.send_message(cid, texts['ask_send_phone'], reply_markup=markup)


@bot.message_handler(func=lambda message: user_step_profile.get(message.chat.id) == 'B', content_types=['contact'])
def user_step_profile_B(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        phone_number = message.contact.phone_number
        if get_customer_data(cid)['phone'] != None:
            if message.contact.user_id == cid:
                if phone_number.startswith('98'):
                    phone_number = phone_number[2:]
                elif phone_number.startswith('0'):
                    phone_number = phone_number[1:]
                edit_customer_phone(phone_number, cid)
                user_step_profile.pop(cid)
            text =texts['phone_changed']
            bot.send_message(cid,text, parse_mode='HTML')
            user_step_profile.pop(cid)
        else:
            if message.contact.user_id == cid:
                if phone_number.startswith('98'):
                    phone_number = phone_number[2:]
                elif phone_number.startswith('0'):
                    phone_number = phone_number[1:]
                edit_customer_phone(phone_number, cid)
                user_step_profile.pop(cid)
                bot.send_message(cid, texts['info_saved_success'], reply_markup=customer_markup())


@bot.message_handler(func=lambda message: user_step_profile.get(message.chat.id) == 'B')
def user_step_profile_B_text(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        phone=message.text
        if phone.startswith('0'):
            phone = phone[1:]
        try:
            int(phone)
        except:
            bot.send_message(cid , texts['er_send_to_number'] )
            return

        if get_customer_data(cid)['phone'] != None and len(phone) == 10:
            edit_customer_phone(message.text, cid)
            text =texts['phone_changed']
            bot.send_message( cid , text )
            user_step_profile.pop(cid)
        elif len(phone) == 10:
            edit_customer_phone(phone, cid)
            user_step_profile.pop(cid)
            bot.send_message(cid, texts['info_saved_success'], reply_markup=customer_markup())
        else:
             bot.send_message(cid , texts['send_again'])



# Project metrics analytical dashboard inside internal Admin panel 
@bot.message_handler(func=lambda message: message.text == texts['check_project'])
def check_project_handler_admin(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in ADMIN:
            if get_all_product_data()!=[]:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(texts['active_projects'], callback_data='check-projects_false'))
                markup.add(InlineKeyboardButton(texts['finished_projects'], callback_data='check-projects_true'))
                all_project = 0
                on_project = 0
                off_project = 0
                for project in get_all_product_data():
                    all_project += 1
                    if project['STATUS'] == 'false':
                        on_project += 1
                    else:
                        off_project += 1
                text = texts['project_stats_admin'].format(all_project=all_project, on_project=on_project, off_project=off_project)
                bot.send_message(cid, text, reply_markup=markup)
            else:
                bot.send_message(cid,texts['no_active_projects'])
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())




# Callback handling dispatcher routine interface 
@bot.callback_query_handler(func=lambda call: True)
def all_callback_query_handler(call):
    call_id = call.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    if check_black_list(cid) == True:
        data = 'black list'
    print(f'call={call.message.from_user.first_name} [{cid}]:{data}')

    if data.startswith('contact us'):
        _, answer = data.split('_')
        if answer == 'true':
            user_step_contact_us[cid] = 'A'
            bot.answer_callback_query(call_id, '✔️')
            bot.edit_message_text(texts['ask_send_phone'], cid, mid)
        elif answer == 'false':
            bot.answer_callback_query(call_id, '✖️')
            try:
                bot.delete_message(cid, mid)
            except:
                pass
    
    elif data.startswith('response contact'):
        _, customer_id = data.split('_')
        user_step_contact_us[cid] = 'B'
        contact_us_data[cid] = customer_id
        bot.edit_message_text(texts['enter_message_to_send'], cid, mid)

    elif data.startswith('check-project-request'):
        _, DATA, id = data.split('_')
        if DATA == 'true':
            bot.answer_callback_query(call_id, '✔️')
            amt = creat_bot_data[int(id)]['total_cost'] / 2
            bot.send_message(id, texts['admin_approved_pay'].format(amount=amt), parse_mode='HTML')
            user_step_creat_bot[int(id)] = 'E'
            bot.delete_message(cid, mid)
        elif DATA == 'false':
            bot.answer_callback_query(call_id, '✖️')
            bot.send_message(id, texts['admin_rejected_retry'])
            user_step_creat_bot.pop(int(id))
            bot.delete_message(cid, mid)

    elif data.startswith('check-deposit'): 
        _, call_data, customer_id = data.split("_")
        if call_data == 'true':
            bot.answer_callback_query(call_id, '✔️')
            customer_id = int(customer_id)
            file_name = str(time.time()).replace('.', '')
            project_id = add_new_product(None,
                                         creat_bot_data[customer_id]['token'],
                                         int(creat_bot_data[customer_id]['time_give']),
                                         int(file_name), 
                                         creat_bot_data[customer_id]['total_cost'],
                                         int(creat_bot_data[customer_id]['FEE_PAID']),
                                         'false')
            sale_id = take_random_karakter()
            add_sale(sale_id, customer_id)
            add_sale_row(sale_id, project_id)
            # download_voice(customer_id ,creat_bot_data[customer_id]['voice_file_id'] , str(file_name))
            user_step_creat_bot.pop(customer_id, None)
            creat_bot_data.pop(customer_id, None)
            bot.send_message(customer_id, texts['order_registered'].format(id=sale_id), reply_markup=customer_markup())
        elif call_data == 'false':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['btn_wrong_amount'], callback_data=f'entered_wrong {customer_id}'))
            markup.add(InlineKeyboardButton(texts['btn_not_receipt'], callback_data=f'photo_not_receipt {customer_id}'))
            markup.add(InlineKeyboardButton('کامل لغو شود' , callback_data=f'cancel_project {customer_id}'))
            bot.send_message(cid, texts['ask_reject_reason'], reply_markup=markup)
            bot.answer_callback_query(call_id, '✖️')
        bot.delete_message(cid, mid)

    elif data.startswith('entered_wrong'):
        _, id = data.split()
        user_step_creat_bot[cid] = 'F'
        creat_bot_data[cid] = id
        bot.edit_message_text(texts['ask_actual_paid'], cid, mid)

    elif data.startswith('photo_not_receipt'):
        _, customer_id = data.split()
        user_step_creat_bot[customer_id] = 'G'
        bot.send_message(customer_id, texts['err_invalid_receipt'])
        bot.edit_message_text(texts['msg_sent_to_user_notif'], cid, mid)
    
    elif data.startswith('cancel_project'):
        _, customer_id=data.split()
        user_step_creat_bot.pop(customer_id , None)
        bot.send_message(customer_id,texts['project_cancelled_user'] ,reply_markup=customer_markup())
        bot.send_message(cid , texts['project_cancelled_admin'])

    elif data == 'change_information':
        markup = InlineKeyboardMarkup()
        if get_customer_data(cid)['phone'] != None:
            markup.add(InlineKeyboardButton(texts['change_name'], callback_data='change_customer_name'),
                    InlineKeyboardButton(texts['change_phone_number'], callback_data='change_customer_phone_number'))
            markup.add(InlineKeyboardButton(texts["back"], callback_data='back_profile-button'))
            bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
        else:
            markup.add(InlineKeyboardButton(texts['btn_enter_info'], callback_data='send_info'))

    elif data == 'send_info':
        send_message(cid, texts['enter_name'])
        user_step_profile[cid] = 'A'    

    elif data == ('change_customer_phone_number'):
        send_message(cid, texts['enter_phone'] , reply_markup=back_meno())
        user_step_profile[cid] = 'B'

    elif data == "change_customer_name":
        bot.send_message(cid, texts['enter_name'] , reply_markup=back_meno())
        user_step_profile[cid] = 'A'

    elif data == 'my_bots':
        markup = InlineKeyboardMarkup()
        sale_id = get_sale_id_b_cid(cid)
        if sale_id != []:       
            for uid in sale_id:
                markup.add(InlineKeyboardButton(uid, callback_data=f'bot data_{uid}'))
            markup.add(InlineKeyboardButton(texts['back'], callback_data='back_mybots'))
            bot.edit_message_text(texts['my_bots_list'], cid, mid)
            bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
        else:
            markup.add(InlineKeyboardButton(texts['back'], callback_data='back_mybots'))
            bot.edit_message_text(texts['no_bots_registered'],cid,mid,reply_markup=markup)

    elif data.startswith('bot data'):
        _, sale_id = data.split('_')
        product_id = get_product_id_f_sale_row(sale_id)['PRODUCT_ID']
        product_data = get_product_data(product_id)
        customer_id = get_customer_id(sale_id)
        markup = InlineKeyboardMarkup()
        if product_data['STATUS'] == 'false':
            status = 'در حال انجام'
        elif product_data['STATUS'] == 'true':
            status = 'انجام شده'
        else:
            markup.add(InlineKeyboardButton('پرداخت' , callback_data=f'payment {sale_id}'))
            status = 'پرداخت نشده'
        text = texts['customer_bot_data_details'].format(
            id=sale_id, token=product_data['BOT_TOKEN'], total_cost=product_data['TOTAL_COST'],
            paid=product_data['FEE_PAID'] , status=status
        )
        bot.edit_message_text(text, cid, mid, parse_mode='HTML' , reply_markup=markup)

    elif data.startswith('payment'):
        _ , sale_id = data.split()
        product_id = get_product_id_f_sale_row(sale_id)["PRODUCT_ID"]
        product_data = get_product_data(product_id)
        user_step_creat_bot[cid] = 'G'
        admin_send_location_data[ADMIN[0]] = sale_id
        bot.send_message(cid , texts['pay_remaining'].format(amount = product_data['TOTAL_COST']-product_data['FEE_PAID']))

    elif data.startswith('check-projects'):
        _, status = data.split('_')
        markup = InlineKeyboardMarkup()  
        for i in get_sale_row_data():
            product_id = get_product_id_f_sale_row(i)
            product_data = get_product_data(product_id['PRODUCT_ID'])
            if product_data != None and product_data['STATUS'] == status:
                markup.add(InlineKeyboardButton(f"{i}", callback_data=f'show_project_data {i}'))
        markup.add(InlineKeyboardButton(texts['back'], callback_data='back_check-project'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)

    elif data.startswith('show_project_data'):
        _, sale_id = data.split()
        product_id = get_product_id_f_sale_row(sale_id)
        product_data = get_product_data(product_id['PRODUCT_ID'])
        customer_id = get_customer_id(sale_id)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['btn_see_voice'] , callback_data=f'see_customer_voice {product_id["PRODUCT_ID"]}'))
        if get_file_address(product_id['PRODUCT_ID']) !=None:
            markup.add(InlineKeyboardButton(texts['btn_github_address'] , callback_data=f'see_file_id {product_id["PRODUCT_ID"]}'))
        text = texts['admin_bot_data_details'].format(
            id=sale_id, token=product_data['BOT_TOKEN'], total_cost=product_data['TOTAL_COST'],
            paid=product_data['FEE_PAID'],customer_id=customer_id
        )
        markup.add(InlineKeyboardButton(texts['back'], callback_data='back_check-project'))
        bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode='HTML')

    elif data.startswith('see_customer_voice'):
        _ , product_id = data.split()
        sale_id = get_sale_id(product_id)['SALE_ID']
        customer_id = get_customer_id(sale_id)
        send_voice(cid , customer_id , 'hello ' , product_id)

    elif data.startswith('see_file_id'):
        _ , product_id = data.split()
        project_id = get_file_address(product_id)
        text = "آدرس گیت هاب"+"\n"+f'github.com/{project_id}'
        bot.send_message(cid , text)

    elif data.startswith('send-lcn-file'):
        _, sale_id = data.split('_')
        bot.edit_message_text(texts['enter_github_link'], cid, mid)
        admin_step_send_location_file[cid] = 'A'
        admin_send_location_data[cid] = sale_id

    elif data.startswith('send file'):
        _, status = data.split('_')
        if status == 'all':
            admin_send_message_to_customer[cid] = 'A'
            bot.edit_message_text(texts['enter_message_to_send'], cid, mid)
        elif status == 'one':
            markup = InlineKeyboardMarkup()
            for i in get_all_customer_data():
                if i['PHONE'] == None:
                    phone = texts['not_registered']
                    name = i['NAME']
                else:
                    name = i['NAME']
                    phone = i['PHONE']
                markup.add(InlineKeyboardButton(str(i['ID']), callback_data=f"send message_{i['ID']}"),
                           InlineKeyboardButton(name, callback_data=f"send message_{i['ID']}"),
                           InlineKeyboardButton(str(phone), callback_data=f"send message_{i['ID']}")
                           )
            bot.edit_message_text(texts['choose_user_to_msg'], cid, mid, reply_markup=markup)
            
    elif data.startswith('send message'):
        _, customer_id = data.split('_')
        admin_send_message_to_customer_data[cid] = customer_id
        admin_send_message_to_customer[cid] = 'B'
        bot.edit_message_text(texts['enter_message_to_send'], cid, mid)

    elif data == 'customer_data':
        markup = InlineKeyboardMarkup()
        for i in get_all_customer_data():
            if i['PHONE'] == None:
                phone = texts['not_registered']
                name = i['NAME']
            else:
                name = i['NAME']
                phone = i['PHONE']
            markup.add(InlineKeyboardButton(str(i['ID']), callback_data=f"see customer_{i['ID']}"),
                        InlineKeyboardButton(name, callback_data=f"see customer_{i['ID']}"),
                        InlineKeyboardButton(str(phone), callback_data=f"see customer_{i['ID']}")
                        )
        bot.edit_message_text(texts['choose_user_to_msg'], cid, mid, reply_markup=markup)

    elif data.startswith('see customer'):
        _, customer_id = data.split('_')
        customer_data = get_customer_data(customer_id)
        markup = InlineKeyboardMarkup()
        if check_black_list(customer_id) == False:
            markup.add(InlineKeyboardButton(texts['btn_ban_user'], callback_data=f'closed customer_{customer_data['id']}'),
                       InlineKeyboardButton(texts['btn_delete_user'], callback_data=f'delete customer_{customer_data['id']}')
                       )
        else:
            markup.add(InlineKeyboardButton(texts['btn_unban_user'], callback_data=f'unclosed customer_{customer_data['id']}'),
                       InlineKeyboardButton(texts['btn_delete_user'], callback_data=f'delete customer_{customer_data['id']}')
                       )
        markup.add(InlineKeyboardButton(texts['back'], callback_data='customer_data'))
        project_num = 0
        for i in get_sale_id_b_cid(customer_id):
            project_num += 1
        
        status_string = texts['status_banned'] if check_black_list(customer_id) == True else texts['status_not_banned']
        name_string = customer_data['name'] if customer_data['name'] != None else texts['not_registered_user']
        phone_string = customer_data['phone'] if customer_data['phone'] != None else texts['not_registered_user']
        
        text = texts['customer_detail_admin'].format(id=customer_data['id'], name=name_string, phone=phone_string, project_num=project_num, status=status_string)
        bot.edit_message_text(text, cid, mid, reply_markup=markup)

    elif data.startswith('closed customer'):
        _, customer_id = data.split('_')
        add_customer_black_list(customer_id, None, 3)
        bot.send_message(cid, texts['user_banned_success'])
        logging.info(f"Admin manually banned user {customer_id}.")
    
    elif data.startswith('unclosed customer'):
        _, customer_id = data.split('_')
        came_customer_black_list(customer_id,1)
        bot.send_message(cid, texts['user_unbanned_success'])
        bot.send_message(customer_id,texts['unbanned_message'])
        find_spam_data.pop(int(customer_id) , None)
        logging.info(f"Admin manually unbanned user {customer_id}.")

    elif data.startswith('delete customer'):
        _, customer_id = data.split('_')
        try:
            bot.delete_message(cid, mid)
            purge_customer_entirely(customer_id)
            bot.send_message(cid, texts['user_deleted_success'])
            logging.info(f"Admin manually deleted user {customer_id} account from system.")
        except:
            bot.answer_callback_query(call_id , 'این دکمه منغضی شده')

    elif data.startswith('check-lcn'):
        _ , status , sale_id =data.split("_")
        customer_id = int(get_customer_id(sale_id))
        if status == 'true':
            change_product_status('true', get_product_id_f_sale_row(sale_id)['PRODUCT_ID'])
            bot.send_message(customer_id , texts['project_available_soon'])
            bot.send_message(cid , f'پروژه {sale_id} را ران کنید')
        elif status == 'false':
            admin_send_location_data[ADMIN[0]] = customer_id
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('مبلغ وارد شده اشتباه بود' ,callback_data=f'enter-wrong-lcn {customer_id}'))
            markup.add(InlineKeyboardButton('cancel', callback_data=f'cancel-lcn {sale_id} {customer_id}'))
            bot.send_message(cid , texts['cancel_lcn_reason'] ,reply_markup=markup)
        bot.delete_message(cid , mid)

    elif data.startswith('enter-wrong-lcn'):
        _ , customer_id = data.split()
        user_step_creat_bot[customer_id] = 'G'
        bot.send_message(customer_id , 'مابغی مبلغ  را وارد کنید')

    elif data.startswith('cancel-lcn'):
        _ , sale_id , customer_id = data.split()
        customer_id = int(customer_id)
        change_product_status('not pay' ,get_product_id_f_sale_row(sale_id)['PRODUCT_ID'] )
        bot.send_message(customer_id ,texts['receipt_wrong_notify'])
        bot.send_message(cid , 'برای کاربر ارسال شد')

    elif data.startswith('back'):
        _, to = data.split('_')
        if to == 'profile-button':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['edit_bot'], callback_data='change_information'))
            markup.add(InlineKeyboardButton(texts['my_bots'], callback_data='my_bots'))
            bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
        elif to == 'mybots':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['edit_bot'], callback_data='change_information'))
            markup.add(InlineKeyboardButton(texts['my_bots'], callback_data='my_bots'))
            text = texts['profile_info'].format(name=get_customer_data(cid)['name'], phone=get_customer_data(cid)['phone'])
            bot.edit_message_text(text, cid, mid, reply_markup=markup, parse_mode='HTML')
        elif to == 'check-project':
            if get_all_product_data()!=[]:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(texts['active_projects'], callback_data='check-projects_false'))
                markup.add(InlineKeyboardButton(texts['finished_projects'], callback_data='check-projects_true'))
                markup.add(InlineKeyboardButton(texts['btn_not_paid_projects'] , callback_data=f'check-projects_not pay'))
                all_project = 0
                on_project = 0
                off_project = 0
                for project in get_all_product_data():
                    all_project += 1
                    if project['STATUS'] == 'false':
                        on_project += 1
                    else:
                        off_project += 1
                text = texts['project_stats_admin'].format(all_project=all_project, on_project=on_project, off_project=off_project)
                bot.edit_message_text(chat_id=cid, text=text, reply_markup=markup,message_id=mid)
            else:
                bot.edit_message_text(chat_id=cid,text=texts['no_active_projects'],message_id=mid)



# Universal message handler fallback 
@bot.message_handler(func=lambda message: True)
def all_message_handler(message):
    cid = message.chat.id
    if check_black_list(cid) == False:
        if cid in ADMIN:
            send_message(cid, texts['invalid_command'], reply_markup=admin_markup())
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())




#_______________________________________thread___________________________________________

# Thread tracking function to check deadline registrations daily
def check_time(day, sleep):
    bans_time = []
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        for id, (times, time_give) in get_all_regester_date().items():
            hundred_days_delta = datetime.timedelta(days=time_give - day)
            previous_date = times + hundred_days_delta
            previous_date = previous_date.strftime('%Y-%m-%d')
            if now == previous_date and id not in bans_time:
                for ad in ADMIN:
                    time.sleep(2)
                    bot.send_message(ad,times)
                    logging.info(f"Alert notification sent to Admin {ad} regarding user {id} timeline threshold.")
        bans_time.clear()
        time.sleep(sleep)

t1 = threading.Thread(target=check_time, args=(3, 3600 * 24))
t1.start()


# Runtime monitor process running over unban states dynamically
def check_find_spam_status(warning_1=60 * 15, warning_2=3600, sleep_time=60):
    regester_time=time.time()   
    while True:
        now = time.time()
        for cid in get_black_list_list():
            data = get_customer_black(cid) 
            if data['STAGE'] == 1 and data['DON'] == 'false':
                if int(now - data['TIME']) >= warning_1:
                    came_customer_black_list(cid,1)
                    bot.send_message(cid, texts['unbanned_message'])
                    find_spam_data.pop(int(cid) , None)                   
                    logging.info(f"User {cid} has been auto-unbanned from Stage 1 spam restrictions.")

            elif data['STAGE'] == 2 and data['DON'] == 'false':
                if int(now - data['TIME']) >= warning_2:
                    came_customer_black_list(cid,2)
                    find_spam_data.pop(int(cid) , None )
                    logging.info(f"User {cid} has been auto-unbanned from Stage 2 spam restrictions.")
        if now-regester_time >= 3600:
            regester_time=time.time()
            for all in get_black_list_list():
                find_spam_data.pop(int(all) , None)
        time.sleep(sleep_time)

t2 = threading.Thread(target=check_find_spam_status, args=())
t2.start()


#_____________________________________polling____________________________________________

# Operational startup setup polling 
print('System is running...')
logging.info('System is running...')
bot.infinity_polling()
logging.warning('System stopped!')
