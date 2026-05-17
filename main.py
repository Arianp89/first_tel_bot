from confing import ai_token,proxy_2,proxy_1,API_TOKEN,ADMIN
from DQL import *
from DML import *
# from requests_forwarder import setup_proxy
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardMarkup, InlineKeyboardButton,KeyboardButton
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

telebot.apihelper.API_URL = 'http://tapi.bale.ai/bot{0}/{1}'
bot=telebot.TeleBot(API_TOKEN)

user_step_ai=dict()
creat_bot_data = dict()
user_step_profile = dict()
user_step_creat_bot =dict() 
user_step_profile_mid = dict()
admin_send_location_data=dict()
creat_bot_data_total_cost=dict()
admin_step_send_location_file=dict()
admin_send_message_to_customer=dict()
admin_send_message_to_customer_data=dict()

def ai(message):
    client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=ai_token)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":message}
        ]
    )

    return response.choices[0].message.content



def send_message(*args, **kwargs):
    try:
        return bot.send_message(*args, **kwargs)
    except Exception as e:
        logging.error(f'send message error:{e}')



def customer_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['create_bot'])
    markup.add(texts['profile'])
    markup.add(texts['about_us'], texts['contact_us'])
    return markup



def admin_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['check_customer'], texts['check_project'])
    markup.add(texts['send_location_file'],texts['send_message_to_customer'])
    markup.add(texts['ai_for_admin'])
    return markup



def back_creat_bot():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['go_home'])
    return markup



def check_token(token):
    url = f"http://tapi.bale.ai/bot{token}/getMe"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            return [True, data['result']['username']]
        else:
            print("The token is invalid!")
            if 'description' in data:
                print(f"Error: {data['description']}")
            return False
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False






def listener(messages):
    for m in messages:
        # print(m)
        register_user(m.chat.id, m.chat.first_name)
        if m.content_type == 'text':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: {m.text}")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: {m.text}")
        elif m.content_type == 'photo':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New photo recieved")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New photo recieved")
        elif m.content_type == 'document':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New document recieved")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New document recieved")
        elif m.content_type == 'voice':
            print(f"{m.chat.first_name} [{str(m.chat.id)}]: New voice recieved")
            logging.info(f"{m.chat.first_name} [{str(m.chat.id)}]: New voice recieved")
bot.set_update_listener(listener)  



@bot.message_handler(commands=['start'])
def message_start_handler(message):
    cid=message.chat.id
    register_user(cid,message.chat.first_name)
    if check_black_list(cid)==False:
        if cid in ADMIN:
            send_message(cid, texts['admin_welcome'], reply_markup=admin_markup())
        else:
            bot.send_message(cid, texts['user_welcome'], reply_markup=customer_markup())

@bot.message_handler(func=lambda message:message.text==texts['contact_us'])
def message_contact_us_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        send_message(cid, texts['contact_info'])

@bot.message_handler(func=lambda message:message.text==texts['about_us'])
def message_about_us_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        number=0
        text = texts['bot_list_header']
        for token in get_all_token():
            number+=1
            check_res = check_token(token)
            if check_res:
                text += f"{number}: @{check_res[1]}\n"
        send_message(cid, text)

@bot.message_handler(func=lambda message:message.text==texts['go_home'])
def back_to_home_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        if cid in user_step_creat_bot:
            user_step_creat_bot.pop(cid)
        bot.send_message(cid, texts['choose_from_menu'], reply_markup=customer_markup())

@bot.message_handler(func=lambda message:message.text==texts['ai_for_admin'])
def ai_handler(message):
    cid = message.chat.id
    if check_black_list(cid)==False:
        if cid in ADMIN:
            bot.send_message(cid, texts['enter_ai_prompt'])
            user_step_ai[cid]='A'
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())



@bot.message_handler(func=lambda message:user_step_ai.get(message.chat.id)=='A')
def ai_handler_A(message):
    cid=message.chat.id
    bot.send_chat_action(cid, 'typing', timeout=5)
    text=ai(message.text)
    time.sleep(5)
    bot.send_message(cid,text)
    user_step_ai.pop(cid)



@bot.message_handler(func=lambda message: message.text==texts['create_bot'])
def creat_bot_handler(message):
    cid = message.chat.id
    if check_black_list(cid)==False:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['yes'], callback_data='run server_yes'))
        markup.add(InlineKeyboardButton(texts['no'], callback_data='run server_no'))
        if get_customer_data(cid)['phone'] == None:
            send_message(cid, texts['enter_name'])
            creat_bot_data[cid]={'name':None,'bot_token':None,'total_cost':None,'time_give':None,'run_server':None,'voice_file_id':None,'photo_file_id':None,'email':None,'password':None}
            user_step_creat_bot[cid]='A'
        else:
            bot.send_message(cid, texts['ask_run_server'], reply_markup=markup)
            creat_bot_data[cid]={'name':None,'bot_token':None,'total_cost':None,'time_give':None,'run_server':None,'voice_file_id':None,'photo_file_id':None,'email':None,'password':None}

@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id) == 'A')
def create_bot_handler_A(message):
    cid=message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(texts['send_contact_btn'], request_contact=True))
    send_message(cid, texts['enter_phone'], reply_markup=markup)
    user_step_creat_bot[cid]='B'
    creat_bot_data[cid]["name"] = message.text

@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id)== 'B',content_types=['contact'])
def create_bot_handler_B_contact(message):
    cid=message.chat.id
    phone=message.contact.phone_number
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts['yes'], callback_data='run server_yes'))
    markup.add(InlineKeyboardButton(texts['no'], callback_data='run server_no'))
    if get_customer_data(cid)['phone'] == None:
        if cid==message.contact.user_id:
            if phone.startswith('98') :
                phone=phone[2:] 
        add_customer(cid,creat_bot_data[cid]['name'],int(phone))
    bot.send_message(cid, texts['ask_run_server'], reply_markup=markup)

@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id)== 'B')
def create_bot_handler_B_text(message):
    cid=message.chat.id
    phone=message.text
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts['yes'], callback_data='run server_yes'))
    markup.add(InlineKeyboardButton(texts['no'], callback_data='run server_no'))
    if get_customer_data(cid)['phone'] == None:
        if phone[:2]=='98':
            phone=phone[2:]
        elif phone[:1]=='0':
            phone=phone[1:]
        add_customer(cid,creat_bot_data[cid]['name'],int(phone))
    bot.send_message(cid, texts['ask_run_server'], reply_markup=markup)

@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id)== 'C')
def create_bot_hadler_C(message):
    cid=message.chat.id
    try:
        if creat_bot_data[cid]['run_server']==None:
            token,total_cost,time_give=message.text.split()
            creat_bot_data[cid]['token']=token
            creat_bot_data[cid]['total_cost']=int(total_cost)
            creat_bot_data[cid]['time_give']=int(time_give)
            creat_bot_data[cid]['FEE_PAID']=int(total_cost)/2
            bot.send_message(cid, texts['send_voice_features'], reply_markup=back_creat_bot())
            user_step_creat_bot[cid]='D'
        elif creat_bot_data[cid]['run_server']==True:
            email,password,token,total_cost,time_give,*other=message.text.split()
            creat_bot_data[cid]['email']=email
            creat_bot_data[cid]['password']=password
            creat_bot_data[cid]['token']=token
            creat_bot_data[cid]['total_cost']=int(total_cost)
            creat_bot_data[cid]['time_give']=int(time_give)
            creat_bot_data[cid]['FEE_PAID']=int(total_cost)/2
            add_email_password(cid,email,password) 
            bot.send_message(cid, texts['send_voice_features'], reply_markup=back_creat_bot())
            user_step_creat_bot[cid]='D'
        else:
            bot.send_message(cid, texts['invalid_token_retry'])
            user_step_creat_bot[cid]='B'
    except Exception as e:
        logging.error('error to split token')
        logging.error('eroror', e)
        user_step_creat_bot[cid]='B'



@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='D',content_types=['voice','document'])
def create_bot_handler_D(message):
    cid = message.chat.id
    send_message(cid, texts['data_sent_to_admin'])
    file_id = message.voice.file_id
    creat_bot_data[cid]['voice_file_id']=file_id
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts['confirm'],callback_data=f'voice_yes_{cid}'), InlineKeyboardButton(texts['cancel'],callback_data=f'voice_no_{cid}'))
    for ad in ADMIN:
        text = texts['admin_new_order'].format(
            name=get_customer_data(cid)['name'],
            cost=creat_bot_data[cid]['total_cost'],
            time=creat_bot_data[cid]['time_give'],
            token=creat_bot_data[cid]['token']
        )
        bot.send_voice(ad, file_id, text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='E',content_types=['photo'])
def user_step_create_bot_handler_E(message):
    cid=message.chat.id
    file_id = message.photo[-1].file_id
    creat_bot_data[cid]['photo_file_id']=file_id
    bot.send_message(cid, texts['photo_sent_to_admin'])
    for ad in ADMIN:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['confirm'],callback_data=f'photo_true_{cid}'),InlineKeyboardButton(texts['cancel'],callback_data=f'photo_false_{cid}'))
        text = texts['admin_payment_received'].format(name=get_customer_data(cid)['name'], amount=creat_bot_data[cid]['total_cost']/2)
        bot.send_photo(ad, file_id, text, reply_markup=markup)


@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='F')
def user_step_create_bot_handler_F(message):
    cid=message.chat.id
    customer_id=int(creat_bot_data[cid])
    file_name = str(time.time()).replace('.', '')
    project_id=add_new_product(None,creat_bot_data[customer_id]['token'],
                                int(creat_bot_data[customer_id]['time_give']),
                                int(file_name),creat_bot_data[customer_id]['total_cost'],
                                int(message.text),
                                creat_bot_data[customer_id]['run_server'],
                                'no')
    sale_id=take_random_karckter()
    add_sale(sale_id,customer_id)
    add_sale_row(sale_id,project_id)
    user_step_creat_bot.pop(cid, None)
    creat_bot_data.pop(cid, None)
    bot.send_message(customer_id, texts['order_registered'].format(id=sale_id), reply_markup=customer_markup())
    bot.send_message(cid,'پروژه شما با موفقیت ثبت شد و استارت خورد', reply_markup=admin_markup())


@bot.message_handler(func=lambda message:message.text==texts['profile'])
def profile_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        if get_customer_data(cid)==None:
            bot.send_message(cid, texts['no_info_found'])
        else:
            markup=InlineKeyboardMarkup()
            if get_customer_data(cid)['phone']==None:
                name='ثبت نشده'
                phone='ثبت نشده'
                markup.add(InlineKeyboardButton('وارد کردن اطلاعات',callback_data='send_info'))
            else:
                name=get_customer_data(cid)['name']
                phone=get_customer_data(cid)['phone']
                markup.add(InlineKeyboardButton(texts['edit_bot'], callback_data='change_information'))
                markup.add(InlineKeyboardButton(texts['my_bots'], callback_data='my_bots'))
            text = texts['profile_info'].format(name=name, phone=phone)
            msg=send_message(cid, text, reply_markup=markup, parse_mode='HTML')
            user_step_profile[cid] = 'A'
            user_step_profile_mid[cid] = msg

@bot.message_handler(func=lambda message:user_step_profile.get(message.chat.id)=='A')
def user_step_profile_A(message):
    cid=message.chat.id
    if get_customer_data(cid)['phone']!=None:
        edit_customer_name(message.text,cid)
        text = texts['profile_info'].format(name=get_customer_data(cid)['name'], phone=get_customer_data(cid)['phone'])
        bot.edit_message_text(text, cid, user_step_profile_mid[cid].message_id, parse_mode='HTML')
        user_step_profile.pop(cid)
    else:
        edit_customer_name(message.text,cid)
        user_step_profile[cid]='B'
        markup=ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton('ارسال شماره تلفن', request_contact=True))
        bot.send_message(cid, 'لطفا شماره تلفن خود را ارسال کنید', reply_markup=markup)



@bot.message_handler(func=lambda message:user_step_profile.get(message.chat.id)=='B',content_types=['contact'])
def user_step_profile_B(message):
    cid=message.chat.id
    if get_customer_data(cid)['phone']!=None:
        edit_customer_phone(message.text,cid)
        text = texts['profile_info'].format(name=get_customer_data(cid)['name'], phone=get_customer_data(cid)['phone'])
        bot.edit_message_text(text, cid, user_step_profile_mid[cid].message_id, parse_mode='HTML')
        user_step_profile.pop(cid)
    else:
        phone_number=message.contact.phone_number
        if message.contact.user_id==cid:
            if phone_number.startswith('98') :
                phone_number=phone_number[2:]
            elif phone_number.startswith('0'):
                phone_number=phone_number[1:]
            edit_customer_phone(phone_number,cid)
            user_step_profile.pop(cid)
            bot.send_message(cid, 'اطلاعات شما با موفقیت ثبت شد', reply_markup=customer_markup())


@bot.message_handler(func=lambda message:user_step_profile.get(message.chat.id)=='B')
def user_step_profile_B(message):
    cid=message.chat.id
    if get_customer_data(cid)['phone']!=None:
        edit_customer_phone(message.text,cid)
        text = texts['profile_info'].format(name=get_customer_data(cid)['name'], phone=get_customer_data(cid)['phone'])
        bot.edit_message_text(text, cid, user_step_profile_mid[cid].message_id, parse_mode='HTML')
        user_step_profile.pop(cid)
    else:
        edit_customer_phone(message.text,cid)
        user_step_profile.pop(cid)
        bot.send_message(cid, 'اطلاعات شما با موفقیت ثبت شد', reply_markup=customer_markup())

@bot.message_handler(func=lambda message:message.text==texts['check_project'])
def check_project_handler_admin(message):
    cid = message.chat.id
    if check_black_list(cid)==False:
        if cid in ADMIN :
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['active_projects'], callback_data='projects_on'))
            markup.add(InlineKeyboardButton(texts['finished_projects'], callback_data='projects_off'))
            all_project=0
            on_project=0
            off_project=0
            for project in get_all_product_data():
                all_project+=1
                if project['STATUS']=='no':
                    on_project+=1
                else:
                    off_project+=1
            text=f"""کل پروژه ها :{all_project}
پروژه های فعال :{on_project}
پروژه های انجام شده :{off_project}
"""
            bot.send_message(cid, text, reply_markup=markup)
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())

@bot.message_handler(func=lambda message:message.text==texts['send_location_file'])
def send_location_file_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        if cid in ADMIN:
            no=0
            for i in get_all_product_data():
                if i['STATUS']=='no':
                    no+=1
            if no!=0:
                markup=InlineKeyboardMarkup()
                for i in get_sale_row_data():
                    product_id=get_product_id_f_sale_row(i)
                    product_data=get_product_data(product_id['PRODUCT_ID'])
                    if product_data != None:
                        if product_data['STATUS']=='no':
                            markup.add(InlineKeyboardButton(f"{i}" ,callback_data=f"file id_{i}"))
                bot.send_message(cid, texts['missing_file_projects'], reply_markup=markup)
            else:
                bot.send_message(cid,'هیچ پروژه فعالی ندارید')
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())

@bot.message_handler(func=lambda message:admin_step_send_location_file.get(message.chat.id)=='A')
def send_location_file_handler_A(message):
    cid=message.chat.id
    try:
        id=admin_send_location_data[cid]
        github_id='github.com/'+message.text
        add_file_project(github_id,get_product_id_f_sale_row(id)['PRODUCT_ID'])
        chenge_status_product('yes',get_product_id_f_sale_row(id)['PRODUCT_ID'])
        bot.send_message(cid, texts['file_link_saved'])
        customer_id=get_customer_id(id)
        bot.send_message(int(customer_id), texts['project_finished_user'], reply_markup=customer_markup())
    except Exception as e:
        bot.send_message(cid, texts['file_send_error'])
        logging.error(f'error in send location file: {e}')
    admin_step_send_location_file.pop(cid)
    admin_send_location_data.pop(cid)



@bot.message_handler(func=lambda message:message.text==texts['send_message_to_customer'])
def admin_send_file_to_customer_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['send_to_all'], callback_data='send file_all'))
        markup.add(InlineKeyboardButton(texts['send_to_one'], callback_data="send file_one"))
        bot.send_message(cid, texts['admin_choose_menu'], reply_markup=markup)
    
@bot.message_handler(func=lambda message:admin_send_message_to_customer.get(message.chat.id) in ['A', 'B'])
def admin_send_message_to_customer_handler_A_B(message):
    cid=message.chat.id
    step = admin_send_message_to_customer.get(cid)
    if step == 'A':
        number=0
        unsuccessful=0
        successful=0
        for i in get_all_customer_data():
            number+=1
            if number % 20 == 0: time.sleep(2)
            try:
                bot.send_message(i['ID'], message.text)
                successful+=1
            except:
                    unsuccessful+=1
        text=f"""✅ارسال تمام شد
📤موفق:{successful}
❌ناموفق:{unsuccessful}        
        """
        bot.send_message(cid,text)
    elif step == 'B':
        customer_id=admin_send_message_to_customer_data[cid]
        bot.send_message(customer_id, message.text)
        bot.send_message(cid, texts['message_sent_success'])
    admin_send_message_to_customer.pop(cid)



@bot.message_handler(func=lambda message:message.text==texts['check_customer'])
def check_customer_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        customer_num=0
        yes_black_list=0
        no_black_list=0
        for i in get_all_customer_data():
            customer_num+=1
            if i["BLACK_LIST"]==None:
                no_black_list+=1
            else:
                yes_black_list+=1
        text=f"""تعداد کل کاربران:{customer_num}
تعداد کاربران مسدود شده :{yes_black_list}
تعداد کاربران مسدود نه شده :{no_black_list}
"""
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('مشاهده کاربران',callback_data='customer_data'))
        bot.send_message(cid,text,reply_markup=markup)





@bot.callback_query_handler(func=lambda call:True)
def all_callback_query_handler(call):
    call_id=call.id
    cid=call.message.chat.id
    mid = call.message.message_id
    data = call.data

    if data.startswith('run server'):
        _,run_server=data.split('_')
        if run_server=='yes':
            bot.answer_callback_query(call_id,'✔')
            creat_bot_data[cid]['run_server']=True
            text = texts['enter_bot_details_server'] if have_email(creat_bot_data[cid].get('email'))==None else texts['enter_bot_details_no_server']
            bot.edit_message_text(chat_id=cid,message_id=mid,text=text)
            user_step_creat_bot[cid]='C'
        elif run_server=='no':
            bot.answer_callback_query(call_id,'✖')
            creat_bot_data[cid]['run_server']=None
            bot.edit_message_text(chat_id=cid,message_id=mid,text=texts['enter_bot_details_no_server'])
            user_step_creat_bot[cid]='C'
            
    elif data.startswith('voice'):
        _,DATA,id=data.split('_')
        if DATA=='yes':
            bot.answer_callback_query(call_id,'✔')
            amt = creat_bot_data[int(id)]['total_cost']/2
            bot.send_message(id, texts['admin_approved_pay'].format(amount=amt),
                              parse_mode='HTML')
            user_step_creat_bot[int(id)]='E'
            bot.delete_message(cid,mid)
        elif DATA=='no':
            bot.answer_callback_query(call_id,'✖')
            bot.send_message(id, texts['admin_rejected_retry'])
            user_step_creat_bot.pop(int(id), None)
            bot.delete_message(cid,mid)

    elif data.startswith('photo'): 
        _,call_data,id=data.split("_")
        if call_data=='true':
            bot.answer_callback_query(call_id,'✔')
            id=int(id)
            file_name = str(time.time()).replace('.', '')
            project_id=add_new_product(None,creat_bot_data[id]['token'],
                                       int(creat_bot_data[id]['time_give']),
                                       int(file_name),creat_bot_data[id]['total_cost'],
                                       int(creat_bot_data[id]['FEE_PAID']),
                                       creat_bot_data[id]['run_server'],
                                       'no')
            sale_id=take_random_karckter()
            add_sale(sale_id,id)
            add_sale_row(sale_id,project_id)
            user_step_creat_bot.pop(id, None)
            creat_bot_data.pop(id, None)
            bot.send_message(id, texts['order_registered'].format(id=sale_id), reply_markup=customer_markup())
        elif call_data=='false':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('مبلغ وارد شده اشتباه بود',callback_data=f'entered_wrong {id}'))
            markup.add(InlineKeyboardButton(' عکس فیش نبود',callback_data=f'photo_not_receipt {id}'))
            bot.send_message(cid,' چرا این کاربر تایید نشد',reply_markup=markup)
            bot.answer_callback_query(call_id,'✖')
        bot.delete_message(cid,mid)

    elif data.startswith('entered_wrong'):
        _,id=data.split()
        user_step_creat_bot[cid]='F'
        creat_bot_data[cid]=id
        bot.edit_message_text('کاربر چقدر از این مبلغ را پرداخت کرد',cid,mid)
    elif data.startswith('photo_not_receipt'):
        _,customer_id=data.split()
        user_step_creat_bot[customer_id]='D'
        bot.send_message(customer_id,'لطفا عکس فیش را درست ارسال کنید')
        bot.edit_message_text('پیام برای کاربر ارسال شد',cid,mid)


    elif data=='change_information':
        markup=InlineKeyboardMarkup()
        if get_customer_data(cid)['phone']!=None:
            markup.add(InlineKeyboardButton(texts['change_name'],callback_data='change_name'),
                    InlineKeyboardButton(texts['change_phone_number'],callback_data='change_phone_number'))
            markup.add(InlineKeyboardButton(texts["back"],callback_data='back_profile'))
            bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
        else:
            markup.add(InlineKeyboardButton('وارد کردن اطلاعات',callback_data='send_info'))

    elif data=='send_info':
        send_message(cid, texts['enter_name'])
        user_step_profile[cid]='A'    

    elif data==('change_phone_number'):
        send_message(cid, texts['enter_phone'])
        user_step_profile[cid]='B'

    elif data=="change_name":
        bot.send_message(cid, texts['enter_name'])
        user_step_profile[cid]='A'

    elif data=='my_bots':
        markup = InlineKeyboardMarkup()
        ids=get_sale_id_b_cid(cid)
        for uid in ids:
            markup.add(InlineKeyboardButton(uid, callback_data=f'bot data_{uid}'))
        markup.add(InlineKeyboardButton(texts['back'],callback_data='back_mybots'))
        bot.edit_message_text(texts['my_bots_list'], cid, mid)
        bot.edit_message_reply_markup(cid,mid,reply_markup=markup)

    elif data.startswith('bot data'):
        _,id=data.split('_')
        product_id=get_product_id_f_sale_row(id)['PRODUCT_ID']
        product_data=get_product_data(product_id)
        svr = texts['yes'] if product_data['RAN_IN_SERSER'] else texts['no']
        text = texts['bot_data_details'].format(
            id=id, token=product_data['BOT_TOKEN'], total_cost=product_data['TOTAL_COST'],
              paid=product_data['FEE_PAID'], server=svr
        )
        bot.edit_message_text(text,cid,mid, parse_mode='HTML')

    elif data.startswith('projects'):
        _,status=data.split('_')
        markup=InlineKeyboardMarkup()
        target_status = 'no' if status == 'on' else 'yes'
        for i in get_sale_row_data():
            product_id=get_product_id_f_sale_row(i)
            product_data=get_product_data(product_id['PRODUCT_ID'])
            if product_data != None and product_data['STATUS'] == target_status:
                markup.add(InlineKeyboardButton(f"{i}" ,callback_data=f'show_project_data {i}'))
        markup.add(InlineKeyboardButton(texts['back'],callback_data='back_check-project'))
        bot.edit_message_reply_markup(cid,mid,reply_markup=markup)

    elif data.startswith('show_project_data'):
        _,id=data.split()
        product_id=get_product_id_f_sale_row(id)
        product_data=get_product_data(product_id['PRODUCT_ID'])
        svr = texts['yes'] if product_data['RAN_IN_SERSER'] else texts['no']
        text = texts['bot_data_details'].format(
            id=id, token=product_data['BOT_TOKEN'], total_cost=product_data['TOTAL_COST'],
              paid=product_data['FEE_PAID'], server=svr
        )
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['back'],callback_data='back_check-project'))
        bot.edit_message_text(text,cid,mid,reply_markup=markup, parse_mode='HTML')

    elif data.startswith('file id'):
        _,id=data.split('_')
        bot.edit_message_text(texts['enter_github_link'],cid,mid)
        admin_step_send_location_file[cid]='A'
        admin_send_location_data[cid]=id

    elif data.startswith('send file'):
        _,status=data.split('_')
        if status=='all':
            admin_send_message_to_customer[cid]='A'
            bot.edit_message_text(texts['enter_message_to_send'],cid,mid)
        elif status=='one':
            markup=InlineKeyboardMarkup()
            for i in get_all_customer_data():
                if i['PHONE']==None:
                    phone='ثبت نشوده'
                else:
                    name=i['NAME']
                    phone=i['PHONE']
                markup.add(InlineKeyboardButton(str(i['ID']),callback_data=f"send message_{i['ID']}"),
                           InlineKeyboardButton(name,callback_data=f"send message_{i['ID']}"),
                           InlineKeyboardButton(phone,callback_data=f"send message_{i['ID']}")
                           )
            bot.edit_message_text(texts['choose_user_to_msg'],cid,mid,reply_markup=markup)
            
    elif data.startswith('send message'):
        _,customer_id=data.split('_')
        admin_send_message_to_customer_data[cid]=customer_id
        admin_send_message_to_customer[cid]='B'
        bot.edit_message_text(texts['enter_message_to_send'],cid,mid)

    elif data=='customer_data':
        markup=InlineKeyboardMarkup()
        for i in get_all_customer_data():
            if i['PHONE']==None:
                phone='ثبت نشوده'
                name=i['NAME']
            else:
                name=i['NAME']
                phone=i['PHONE']
            markup.add(InlineKeyboardButton(str(i['ID']),callback_data=f"see customer_{i['ID']}"),
                        InlineKeyboardButton(name,callback_data=f"see customer_{i['ID']}"),
                        InlineKeyboardButton(str(phone),callback_data=f"see customer_{i['ID']}")
                        )
        text='لطفا کاربر مورد نظر را از منوی زیر انتخاب کنید'
        bot.edit_message_text(text,cid,mid,reply_markup=markup)

    elif data.startswith('see customer'):
        _,customer_id=data.split('_')
        customer_data=get_customer_data(customer_id)
        markup=InlineKeyboardMarkup()
        if check_black_list(customer_id)==False:
            markup.add(InlineKeyboardButton(' مسدود کردن کاربر',callback_data=f'closed customer_{customer_data['id']}'))
        else:
            markup.add(InlineKeyboardButton('برداشتن از مسدودیت',callback_data=f'unclosed customer_{customer_data['id']}'))
        project_num=0
        for i in get_sale_id_b_cid(customer_id):
            project_num+=1
        text=f"""آیدی کاربر :{customer_data['id']}
نام کاربر :{customer_data['name'] if customer_data['name']!=None else 'ثبت نام نشده'}
شماره تماس :{customer_data['phone'] if customer_data['phone']!=None else 'ثبت نام نشده'}
تعداد پروژه ها: {project_num}
 وضعیت مسدودیت :{'مسدود شده' if check_black_list(customer_id)==True else 'مسدود نشده'}
"""
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data.startswith('closed customer'):
        _,customer_id=data.split('_')
        add_customer_black_list(customer_id)
        bot.send_message(cid,'کاربر مورد نظر با موفقیت مسدود شد')
    
    elif data.startswith('unclosed customer'):
        _,customer_id=data.split('_')
        came_customer_black_list(customer_id)
        bot.send_message(cid,'کاربر مورد نظر  با موفقیت لغو مسدودیت شد')

    elif data.startswith('back'):
        _,to=data.split('_')
        if to=='profile':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['edit_bot'],callback_data='change_information'))
            markup.add(InlineKeyboardButton(texts['my_bots'],callback_data='my_bots'))
            bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
        elif to=='mybots':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['edit_bot'],callback_data='change_information'))
            markup.add(InlineKeyboardButton(texts['my_bots'],callback_data='my_bots'))
            text = texts['profile_info'].format(name=get_customer_data(cid)['name'], phone=get_customer_data(cid)['phone'])
            bot.edit_message_text(text,cid,mid,reply_markup=markup, parse_mode='HTML')
        elif to=='check-project':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts['active_projects'],callback_data='projects_on'))
            markup.add(InlineKeyboardButton(texts['finished_projects'],callback_data='projects_off'))
            bot.edit_message_text(texts['admin_choose_menu'],cid,mid,reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def all_message_handler(message):
    cid=message.chat.id
    if check_black_list(cid)==False:
        if cid in ADMIN:
            send_message(cid, texts['invalid_command'], reply_markup=admin_markup())
        else:
            send_message(cid, texts['invalid_command'], reply_markup=customer_markup())


def check_time(day,sleep):#one time in a day check for users that their 100 days is coming to end and send message to admin to check if they have registered project or not
    bans_time=[]
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        for id, (times, time_give) in get_all_regester_date().items():
            hundred_days_delta = datetime.timedelta(days=time_give-day)
            previous_date = times + hundred_days_delta
            previous_date = previous_date.strftime('%Y-%m-%d')
            if now == previous_date and id not in bans_time:
                for ad in ADMIN:
                    time.sleep(2)
                    bot.send_message(ad,texts['new_user_registered'].format(sale_id=get_sale_id(id)['SALE_ID'], time=times))
        time.sleep(sleep)

t1 = threading.Thread(target=check_time, args=(3,3600*24))#one time in a day check for users that their 100 days is coming to end and send message to admin to check if they have registered project or not
t1.start()


print('System is running...')
logging.info('System is running...')
bot.infinity_polling()
logging.warning('System stopped!')