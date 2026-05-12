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





creat_bot_data = dict()
user_step_creat_bot =dict() # {cid: {'user_step':..., 'bot_token':..., 'total_cost:...'}, ...
user_step_profile = dict()
user_step_ai=dict()
user_step_profile_mid = dict()
creat_bot_data_total_cost=dict()
admin_step_send_location_file=dict()
admin_send_location_data=dict()
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
    markup.add(texts['about_us'],texts['contact_us'])
    return markup



def admin_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(texts['send_location_file'],texts['check project'])
    markup.add(texts['send_message_to_customer'])
    markup.add(texts['ai for admin'])
    return markup



def back_creat_bot():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(('رفتن به صفحه اصلی'))
    return markup



def check_token(token):
    url = f"http://tapi.bale.ai/bot{token}/getMe"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            print("The token is valid!")
            print("Bot Details:")
            print(f"ID: {data['result']['id']}")
            print(f"Name: {data['result']['first_name']}")
            print(f"Username: {data['result']['username']}")
            return [True,data['result']['username']]
        else:
            print("The token is invalid!")
            if 'description' in data:
                print(f"Error: {data['description']}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False





def listener(messages):
    for m in messages:
        # print(m)
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
    if cid in ADMIN:
        text='سلام ادمین'+'\n'
        text+="از منوی زیر انتخاب کن"+":"
        send_message(cid,text,reply_markup=admin_markup())
    else:    
        # bot.copy_message(cid,'')
        bot.send_message(cid,'hello',reply_markup=customer_markup())



@bot.message_handler(func=lambda message:message.text=='ارسال فایل')
def admin_handler(message):
    cid =message.chat.id
    text=''
    send_message(cid,text)



@bot.message_handler(func=lambda message:message.text==texts['contact_us'])
def message_contact_us_handler(message):
    cid=message.chat.id
    text=' \n لطفا  برای تماس با ما با شماره زیر تماس بگیرید'
    text+='\n 09339798695        آرین پناهی'
    send_message(cid,text)



@bot.message_handler(func=lambda message:message.text==texts['about_us'])
def message_contact_us_handler(message):
    cid=message.chat.id
    number=0
    text='لیست ربات هایی که درست کردیم'+'\n'
    for token in get_all_token():
        number+=1
        text+=number+':'+'@'+check_token(token)[1]+'\n'
    send_message(cid,text)



@bot.message_handler(func=lambda message:message.text=='رفتن به صفحه اصلی')
def back_to_home_handler(message):
    cid=message.chat.id
    user_step_creat_bot.pop(cid)
    bot.send_message(cid,'از منوی زیر انتخاب کنید',reply_markup=customer_markup())



@bot.message_handler(func=lambda message:message.text==texts['ai for admin'])
def ai_handler(message):
    cid = message.chat.id
    if cid in ADMIN:
        bot.send_message(cid,'لطفا پیام خود را وارد کنید'+':')
        user_step_ai[cid]='A'
    else:
        send_message(cid,'✖'+'دستور یافت نشد'+','+'از منوی زیر انتخاب کنید'+':',reply_markup=customer_markup())



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
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله',callback_data='run server_yes'))
    markup.add(InlineKeyboardButton('خیر',callback_data='run server_no'))
    if get_customer_data(cid) == None:
        send_message(cid, ':لطفا نام خود را وارد کنید ')
        creat_bot_data[cid]={'name':None,'bot_token':None,'total_cost':None,'time_give':None,'run_server':None,'voice_file_id':None,'photo_file_id':None,'email':None,'password':None}
        user_step_creat_bot[cid]='A'
    else:
        text='آیا میخواهید پروژه شما روی سرور باشد'
        bot.send_message(cid,text,reply_markup=markup)
        creat_bot_data[cid]={'name':None,'bot_token':None,'total_cost':None,'time_give':None,'run_server':None,'voice_file_id':None,'photo_file_id':None,'email':None,'password':None}



@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id) == 'A')
def create_bot_handler_A(message):
    cid=message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('ارسال شماره تلگرام خودم', request_contact=True))
    send_message(cid,texts['enter phone'],reply_markup=markup)
    user_step_creat_bot[cid]='B'
    creat_bot_data[cid]["name"] = message.text



@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id)== 'B',content_types=['contact'])
def create_bot_handler_B(message):
    cid=message.chat.id
    phone=message.contact.phone_number
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله',callback_data='run server_yes'))
    markup.add(InlineKeyboardButton('خیر',callback_data='run server_no'))
    if get_customer_data(cid) == None:
        if cid==message.contact.user_id:
            phone=phone[2:]
            add_customer(cid,creat_bot_data[cid]['name'],phone)
    text='آیا میخواهید پروژه شما روی سرور باشد'    
    bot.send_message(cid,text,reply_markup=markup)



@bot.message_handler(func=lambda message: user_step_creat_bot.get(message.chat.id)== 'B')
def create_bot_handler_B(message):
    cid=message.chat.id
    phone=message.text
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله',callback_data='run server_yes'))
    markup.add(InlineKeyboardButton('خیر',callback_data='run server_no'))
    if get_customer_data(cid) == None:
        if phone[:2]=='98':
            phone=phone[2:]
        elif phone[:1]=='0':
            phone=phone[1:]
        add_customer(cid,creat_bot_data[cid]['name'],phone)
    text='آیا میخواهید پروژه شما روی سرور باشد'
    bot.send_message(cid,text,reply_markup=markup)
    


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
            text='لطفا ویژگی های ربات خود را به صورت یک فایل صوتی  یا صدای ضبط شده ارسال کنید'
            bot.send_message(cid,text,reply_markup=back_creat_bot())
        elif creat_bot_data[cid]['run_server']==True:
            email,password,token,total_cost,time_give,*other=message.text.split()
            creat_bot_data[cid]['email']=email
            creat_bot_data[cid]['password']=password
            creat_bot_data[cid]['token']=token
            creat_bot_data[cid]['total_cost']=int(total_cost)
            creat_bot_data[cid]['time_give']=int(time_give)
            creat_bot_data[cid]['FEE_PAID']=int(total_cost)/2
            add_email_password(cid,email,password) 
            text='لطفا ویژگی های ربات خود را به صورت یک فایل صوتی  یا صدای ضبط شده ارسال کنید'
            bot.send_message(cid,text,reply_markup=back_creat_bot())
            user_step_creat_bot[cid]='D'
        else:
            bot.send_message(cid,"توکن وارد شده درست  نمی باشد"+"\n"+'لطفا یک بار دیگه اطلاعات زیر را وارد کنید')
            user_step_creat_bot[cid]='B'
    except Exception as e:
        logging.error('error to split token')
        print('eroror', e)
        user_step_creat_bot[cid]='B'



@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='D',content_types=['voice','document'])
def create_bot_handler_D(message):
    cid = message.chat.id
    send_message(cid,'اطلاعات شما برای ادمین ارسال شد لطفا کمی صبر کنید تا اطلاعات شما توسط ادمین تایید شود')
    file_id = message.voice.file_id
    creat_bot_data[cid]['voice_file_id']=file_id
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('✔',callback_data=f'voice_yes_{cid}'),InlineKeyboardButton('✖',callback_data=f'voice_no_{cid}'))
    for ad in ADMIN:
        text='کاربر'+':'+ get_customer_data(cid)['name']+'\n'
        text+=f'درخواست ساخت یک ربات داده است با قیمت پیشنهادی :{creat_bot_data[cid]['total_cost']}\n'
        text+="و تاریخ تحویل"+":"+str(creat_bot_data[cid]['time_give'])+"\n"
        text+='این هم توکن ربات '+':'+creat_bot_data[cid]['token']+'\n'
        voice=bot.send_voice(ad,file_id,text,reply_markup=markup)



@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='E',content_types=['photo'])
def user_step_create_bot_handler_E(message):
    cid=message.chat.id
    file_id = message.photo[-1].file_id
    creat_bot_data[cid]['photo_file_id']=file_id
    bot.send_message(cid,'عکس شما برای ادمین ارسال شد')
    for ad in ADMIN:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('تایید',callback_data=f'photo_true_{cid}'),InlineKeyboardButton('لغو',callback_data=f'photo_false_{cid}'))
        text=get_customer_data(cid)['name']
        text+=' مبلغ '
        text+=f'{creat_bot_data[cid]['total_cost']/2}'
        text+='را واریز کرد '
        bot.send_photo(ad,file_id,text,reply_markup=markup)



@bot.message_handler(func=lambda message:user_step_creat_bot.get(message.chat.id)=='admin_F')
def create_bot_handler_F(message):
    cid=message.chat.id
    if cid in ADMIN:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('text',callback_data=f'customer_true_{user_step_creat_bot.get(cid)['cid']}'),
                   InlineKeyboardButton('text',callback_data=f'customer_false_{user_step_creat_bot.get(cid)['cid']}'))
        send_message(cid,'pass')
        send_message(user_step_creat_bot.get(cid)['cid'],message.text,reply_markup=markup)
        creat_bot_data[cid]['total_cost']=message.text.split("_")[-1]

    

@bot.message_handler(func=lambda message:message.text==texts['profile'])
def profile_handler(message):
    cid=message.chat.id
    if get_customer_data(cid)==None:
        bot.send_message(cid,'اطلاعاتی برای شما ثبت نشده')
    else:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('تغییر اطلاعات',callback_data='change_information'))
        markup.add(InlineKeyboardButton("ربات های من",callback_data='my_bots'))
        text='نام'+':'+get_customer_data(cid)['name']+'\n'
        text+="شماره"+':'+get_customer_data(cid)['phone']
        message=send_message(cid,text,reply_markup=markup)
        user_step_profile[cid] = 'A'
        user_step_profile_mid[cid]=message



@bot.message_handler(func=lambda message:user_step_profile.get(message.chat.id)=='A')
def user_step_profile_A(message):
    cid=message.chat.id
    edit_customer_name(message.text,cid)
    text='نام'+':'+get_customer_data(cid)['name']+'\n'
    text+="شماره"+':'+get_customer_data(cid)['phone']
    bot.edit_message_text(text,cid,user_step_profile_mid[cid].message_id)
    user_step_profile.pop(cid)



@bot.message_handler(func=lambda message:user_step_profile.get(message.chat.id)=='B')
def user_step_profile_B(message):
    cid=message.chat.id
    edit_customer_phone(message.text,cid)
    text='نام'+':'+get_customer_data(cid)['name']+'\n'
    text+="شماره"+':'+get_customer_data(cid)['phone']
    bot.edit_message_text(text,cid,user_step_profile_mid[cid].message_id)
    user_step_profile.pop(cid)



@bot.message_handler(func=lambda message:message.text==texts['check project'])
def check_project_handler_admin(message):
    cid = message.chat.id
    if cid in ADMIN:
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('پروژه های فعال ',callback_data='projects_on'))
        markup.add(InlineKeyboardButton('پروژه های تمام',callback_data='projects_off'))
        text='از منوی زیر انتخاب کن'+":"
        bot.send_message(cid,text,reply_markup=markup)
    else:
        send_message(cid,'✖'+'دستور یافت نشد'+','+'از منوی زیر انتخاب کنید'+':',reply_markup=customer_markup())



@bot.message_handler(func=lambda message:message.text==texts['send_location_file'])
def send_location_file_handler(message):
    cid=message.chat.id
    if cid in ADMIN:
        markup=InlineKeyboardMarkup()
        for i in get_sale_row_data():
            product_id=get_product_id_f_sale_row(i)
            product_data=get_product_data(product_id['PRODUCT_ID'])
            if product_data != None:
                if product_data['STATUS']=='no':
                    markup.add(InlineKeyboardButton(f"{i}" ,callback_data=f"file id_{i}"))
        bot.send_message(cid,'لیست پروژه هایی که فایل آنها ارسال نشده'+':',reply_markup=markup)
    else:
        send_message(cid,'✖'+'دستور یافت نشد'+','+'از منوی زیر انتخاب کنید'+':',reply_markup=customer_markup())







@bot.message_handler(func=lambda message:admin_step_send_location_file.get(message.chat.id)=='A')
def send_location_file_handler_A(message):
    try:
        cid=message.chat.id
        id=admin_send_location_data[cid]
        github_id='github.com/'+message.text
        add_file_project(github_id,get_product_id_f_sale_row(id)['PRODUCT_ID'])
        chenge_status_product('yes',get_product_id_f_sale_row(id)['PRODUCT_ID'])
        bot.send_message(cid,'آدرس فایل با موفقیت ثبت شد')
        customer_id=get_customer_id(id)
        bot.send_message(int(customer_id),'پروژه شما با موفقیت به پایان رسید',reply_markup=customer_markup())
    except Exception as e:
        bot.send_message(cid,"✖"+'خطا در ارسال فایل دوباره تلاش کنید')
        logging.error(f'error in send location file handler A :{e}')
    admin_step_send_location_file.pop(cid)
    admin_send_location_data.pop(cid)



@bot.message_handler(func=lambda message:message.text==texts['send_message_to_customer'])
def admin_send_file_to_customer_handler(message):
    cid=message.chat.id
    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("ارسال پیام به همه",callback_data='send file_all'))
    markup.add(InlineKeyboardButton("ارسال پیام به یک نفر",callback_data="send file_one"))
    bot.send_message(cid,'text',reply_markup=markup)
    
@bot.message_handler(func=lambda message:admin_send_message_to_customer.get(message.chat.id)=='A')
def admin_send_message_to_customer_handler_A(message):
    cid=message.chat.id
    number=0
    for i in get_all_customer_data():
        number+=1
        if number/20==int(number/20):
            time.sleep(2)
        bot.send_message(i['ID'],message.text)
    text=' ✔ ' + 'پیام شما با موفقیت ارسال شد'
    bot.send_message(cid,text)

    
@bot.message_handler(func=lambda message:admin_send_message_to_customer.get(message.chat.id)=='B')
def admin_send_message_to_customer_handler_A(message):
    cid=message.chat.id
    customer_id=admin_send_message_to_customer_data[cid]
    bot.send_message(customer_id,message.text)
    text=' ✔ ' + 'پیام شما با موفقیت ارسال شد'
    bot.send_message(cid,text)



@bot.callback_query_handler(func=lambda call:True)
def all_callback_query_handler(call):
    call_id=call.id
    cid=call.message.chat.id
    mid = call.message.message_id
    data = call.data
    if data=='make_token_bot':
        pass
    elif data.startswith('run server'):
        _,run_server=data.split('_')
        if run_server=='yes':
            bot.answer_callback_query(call_id,'✔')
            creat_bot_data[cid]['run_server']=True
            text='لطفا موارد زیر راا به همین شکل را وارد کنید'+':'+'\n'
            if have_email(creat_bot_data[cid]['email'])==None:
                text+='ایمیل'+':'+'\n'
                text+='رمز عبور'+':'+'\n'
            text+="توکن ربات" + ":" + '\n'
            text+='قیمت پیشنهادی'+ "(به تومان)" + ':'+'\n'
            text+='زمان تحویل پروژه' + '(به تعداد روز وارد کنید)' + ':'
            bot.edit_message_text(chat_id=cid,message_id=mid,text=text)
            user_step_creat_bot[cid]='C'
        elif run_server=='no':
            bot.answer_callback_query(call_id,'✖')
            creat_bot_data[cid]['run_server']=None
            text='لطفا موارد زیر راا به همین شکل را وارد کنید'+':'+'\n'
            text+='توکن ربات'+':'+'\n'
            text+='قیمت پیشنهادی'+ "(به تومان)" + ':'+'\n'
            text+='زمان تحویل پروژه' + '(به تعداد روز وارد کنید)' + ':'
            bot.edit_message_text(chat_id=cid,message_id=mid,text=text)
            user_step_creat_bot[cid]='C'
    elif data.startswith('voice'):
        _,DATA,id=data.split('_')
        if DATA=='yes':
            bot.answer_callback_query(call_id,'✔')
            text='ادمین درخواست شما را تایید کرد لطفا مبلغ '
            text+=f'{creat_bot_data[int(id)]['total_cost']/2}\n'
            text+='ریال را به این شماره کارت'+'\n'
            text+='آرین پناهی'+"       "+'`6219861856616676`'+'\n'
            text+='واریز کرده و عکس آن را ارسال کنید'
            bot.send_message(id,text)
            user_step_creat_bot[int(id)]='E'
            bot.delete_message(cid,mid)
        elif DATA=='no':
            bot.answer_callback_query(call_id,'✖')
            user_step_creat_bot[cid]='admin_F'
            user_step_creat_bot['cid']=id
    elif data.startswith('photo'): 
        _,call_data,id=data.split("_")
        if call_data=='true':
            bot.answer_callback_query(call_id,'✔')
            id=int(id)
            bot.send_message(id,'درخواست شما با موفقت ثبت شد',reply_markup=customer_markup())
            file_name = str(time.time()).replace('.', '')
            project_id=add_new_product(None,creat_bot_data[int(id)]['token'],
                                       int(creat_bot_data[int(id)]['time_give']),
                                       int(file_name),creat_bot_data[int(id)]['total_cost'],
                                       int(creat_bot_data[id]['FEE_PAID']),
                                       creat_bot_data[id]['run_server'],
                                       'no')
            random=take_random_karckter()
            add_sale(random,int(id))
            add_sale_row(random,project_id)
            # photo_save_path=os.path.join('Data','voice',str(id))
            # os.makedirs('Data',exist_ok=True)
            # os.makedirs(os.path.join('Data','voice'),exist_ok=True)
            # os.makedirs(photo_save_path,exist_ok=True)
            # file_id =creat_bot_data[id]['voice_file_id']
            # file_info = bot.get_file(file_id)
            # print(file_info)
            # # extension = file_info.file_path.split('.')[-1]
            # file_name=file_name+'.'+'ogg'#extension
            # file_path = file_info.file_path
            # content = bot.download_file(file_path)
            # with open(os.path.join(photo_save_path, file_name), 'wb') as f:
            #     f.write(content)

            # voice_save_path=os.path.join('Data',id)
            # file_id =creat_bot_data[id]['photo_file_id']
            # file_info = bot.get_file(file_id)
            # extension = file_info.file_path.split('.')[-1]
            # file_name=file_name+'.'+extension
            # print(extension)
            # file_path = file_info.file_path
            # content = bot.download_file(file_path)
            # with open(os.path.join(voice_save_path, file_name), 'wb') as f:
            #     f.write(content)
            user_step_creat_bot.pop(id)
            creat_bot_data.pop(id)
        elif call_data=='false':
            bot.answer_callback_query(call_id,'✖')
            pass
        bot.delete_message(cid,mid)
    elif data=='change_information':
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['change_name'],callback_data='change_name'),InlineKeyboardButton(texts['change_phone_number'],callback_data='change_phone_number'))
        markup.add(InlineKeyboardButton(texts["back"],callback_data='back_profile'))
        bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
    elif data==('change_phone_number'):
        text= ':' + "لطفا شماره تماس خود را وارد کنید "
        send_message(cid,text)
        user_step_profile[cid]='B'
    elif data=="change_name":
        text= ':' + "لطفا نام خود را وارد کنید "
        bot.send_message(cid,text)
        user_step_profile[cid]='A'
    elif data=='my_bots':
        markup = InlineKeyboardMarkup()
        ids=get_sale_id_b_cid(cid)
        for id in ids:
            markup.add(InlineKeyboardButton(id, callback_data=f'bot data_{id}'))
        markup.add(InlineKeyboardButton('بازگشت به قبل',callback_data='back_mybots'))
        bot.edit_message_text('لیست ربات های من'+":",cid,mid)
        bot.edit_message_reply_markup(cid,mid,reply_markup=markup)

    elif data.startswith('customer'):
        _,react,ID=data.split("_")
        if react=='true':
            text=f' ریال را به این شماره کارت:`6219861856616676` واریز کرده و عکس آن را ارسال کنید {user_step_creat_bot['total_cost']/2}  لطفا مبلغ  '
            send_message(cid,text)
            user_step_creat_bot.get(cid)['user_step']='C'
        elif react=='false':
            send_message(cid,'لطفا یک بار دیگه تلاش کنید و برای مبلغ پیشنهادی با این شماره تماس بگیرید:09339798695',reply_markup=customer_markup())
            user_step_creat_bot.pop(cid)
        
    elif data.startswith('bot data'):
        _,id=data.split('_')
        product_id=get_product_id_f_sale_row(id)
        product_data=get_product_data(product_id)
        text='کد'+' ربات '+":"+id+'\n'
        text+='توکن ربات'+':'+product_data['BOT_TOKEN']+'\n'
        text+= "مبلغ کل" + ':' + str(product_data['TOTAL_COST']) + '\n'
        text+="مبلغ پرداخت شده"+':'+str(product_data['FEE_PAID'])+'\n'
        if product_data['RAN_IN_SERSER']==None:
            text+='ران شود رو سرور'+':'+'✖'
        else:
            text+='ران شود رو سرور'+':'+'✔'
        bot.edit_message_text(text,cid,mid)
    elif data=='run_server':
        bot.answer_callback_query(call_id,'✔')
        creat_bot_data[cid]['run_server']=True
    elif data.startswith('projects'):
        _,status=data.split('_')
        markup=InlineKeyboardMarkup()
        if status=='on':
            for i in get_sale_row_data():
                product_id=get_product_id_f_sale_row(i)
                product_data=get_product_data(product_id['PRODUCT_ID'])
                if product_data != None:
                    if product_data['STATUS']=='no':
                        markup.add(InlineKeyboardButton(f"{i}" ,callback_data=f'show_project_data {i}'))
            markup.add(InlineKeyboardButton('بازگشت به قبل',callback_data='back_check-project'))
            bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
        elif status=='off':
            for i in get_sale_row_data():
                product_id=get_product_id_f_sale_row(i)
                product_data=get_product_data(product_id['PRODUCT_ID'])
                if product_data != None:
                    if product_data['STATUS']=='yes':
                        markup.add(InlineKeyboardButton(f"{i}" ,callback_data=f'show_project_data {i}')) 
            markup.add(InlineKeyboardButton('بازگشت به قبل',callback_data='back_check-project'))         
            bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
    elif data.startswith('show_project_data'):
        _,id=data.split()
        product_id=get_product_id_f_sale_row(id)
        product_data=get_product_data(product_id['PRODUCT_ID'])
        text='کد'+' ربات '+":"+id+'\n'
        text+='توکن ربات'+':'+product_data['BOT_TOKEN']+'\n'
        text+= "مبلغ کل" + ':' + str(product_data['TOTAL_COST']) + '\n'
        text+="مبلغ پرداخت شده"+':'+str(product_data['FEE_PAID'])+'\n'
        if product_data['RAN_IN_SERSER']==None:
            text+='ران شود رو سرور'+':'+'✖'
        else:
            text+='ران شود رو سرور'+':'+'✔'
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('بازگشت به قبل',callback_data='back_check-project'))
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data.startswith('file id'):
        _,id=data.split('_')
        bot.edit_message_text('لطفا آدرس گیت هاب را  وارد کنید'+":",cid,mid)
        admin_step_send_location_file[cid]='A'
        admin_send_location_data[cid]=id
    elif data.startswith('send message'):
        _,customer_id=data.split('_')
        admin_send_message_to_customer_data[cid]=customer_id
        admin_send_message_to_customer[cid]='B'
        text='لطفا پیام خود را وارد کنید' + ':'
        bot.edit_message_text(text,cid,mid)

    elif data.startswith('send file'):
        _,status=data.split('_')
        if status=='all':
            admin_send_message_to_customer[cid]='A'
            text='لطفا پیام خود را وارد کنید' + ':'
            bot.edit_message_text(text,cid,mid)
        elif status=='one':
            markup=InlineKeyboardMarkup()
            for i in get_all_customer_data():
                markup.add(InlineKeyboardButton(i['NAME'],callback_data=f'send message_{i['ID']}'),
                           InlineKeyboardButton(i['PHONE'],callback_data=f'send message_{i['ID']}'))
            text='لطفا انتخاب کنید به چه کسی می خواهید پیام دهید' + ':'
            bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data.startswith('back'):
        _,to=data.split('_')
        if to=='profile':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('تغییر اطلاعات',callback_data='change_information'))
            markup.add(InlineKeyboardButton("ربات های من",callback_data='my_bots'))
            bot.edit_message_reply_markup(cid,mid,reply_markup=markup)
        elif to=='mybots':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('تغییر اطلاعات',callback_data='change_information'))
            markup.add(InlineKeyboardButton("ربات های من",callback_data='my_bots'))
            text='نام'+':'+get_customer_data(cid)['name']+'\n'
            text+="شماره"+':'+get_customer_data(cid)['phone']
            bot.edit_message_text(text,cid,mid,reply_markup=markup)
            bot.edit_message_text('','',)
        elif to=='check-project':
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('پروژه های فعال ',callback_data='projects_on'))
            markup.add(InlineKeyboardButton('پروژه های تمام',callback_data='projects_off'))
            text='از منوی زیر انتخاب کن'+":"
            bot.edit_message_text(text,cid,mid,reply_markup=markup)





@bot.message_handler(func=lambda message: True)
def all_message_handler(message):
    cid=message.chat.id
    if cid in ADMIN :
        send_message(cid, '✖'+'دستور یافت نشد'+','+'از منوی زیر انتخاب کنید'+':',reply_markup=admin_markup())
    else:
        send_message(cid,'✖'+'دستور یافت نشد'+','+'از منوی زیر انتخاب کنید'+':',reply_markup=customer_markup())

        

print('code running...')
logging.info('code running...')
bot.infinity_polling()