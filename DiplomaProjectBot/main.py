import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import hotels_api as ns
import json
from redis_base import database
import datetime
from datetime import date, datetime
from typing import Any

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
bot = telebot.TeleBot("*********", parse_mode=None)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Main Menu"),
    telebot.types.BotCommand("/lowprice", "Affordable Hotels "),
    telebot.types.BotCommand("/highprice", "High Priced Hotels "),
    telebot.types.BotCommand("/bestdeal", "Filters"),
    telebot.types.BotCommand("/history", "History ")])


@bot.message_handler(commands=['start'])
def start_command(message, *args, **kwargs) -> Any:
    """
    This function provides with information.
    :param message: command 'start'
    :return: None
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        'Hello, I  can help you t0 find you best hotels\n'
        '1) To find information about cheap hotels press /lowprice\n'
        '2) To find information about high priced hotels press /highprice\n'
        '3) To choose visit time, distance from center '
        'and prices press /bestdeal\n'
        '4) To see the history press /history',
        reply_markup=keyboard)


@bot.message_handler(commands=['delbase'])
def help_command(message) -> Any:
    """
    This function deletes database.

    :param message: command delbase
    :return: None
    """
    database.flushdb()
    print(database.keys())


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def getting_town_code(message, *args, **kwargs) -> Any:
    """
    This function gets command,
    returns question, fills in database
    :param message: message with one of bot commands
    :return: None
    """

    chat_id = message.chat.id
    comm_name = message.text
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if database.hget(str(chat_id), "num") is None:
        database.hset(str(chat_id), "num", 0)
        n = database.hget(str(chat_id), "num")
        database.hset(str(chat_id) + " " + str(n), "command", comm_name)
        database.hset(str(chat_id) + " " + str(n), "call_time", current_time)
    else:
        database.hincrby(str(chat_id), "num", 1)
        n = database.hget(str(chat_id), "num")
        database.hset(str(chat_id) + " " + str(n), "command", comm_name)
        database.hset(str(chat_id) + " " + str(n), "call_time", current_time)
    msg = bot.send_message(message.from_user.id, "Enter town "
                                                 "which you want to visit")

    bot.register_next_step_handler(msg, getting_town_info)


def getting_town_info(message):
    """
    This function gets name of town,
    checks up the presence of town information
    on the server
    returns question, fills in database
    :param message: message from user
    :return: None
    """
    chat_id = message.chat.id
    destination = message.text
    n = database.hget(str(chat_id), "num")
    if destination.startswith("/"):
        bot.send_message(message.chat.id, "Input error press /start")
        database.hset(str(chat_id) + " " + str(n), 'answer1', 'NoResult')
    else:
        hot_code = ns.get_destination_id(destination)
        msg1 = ""
        if hot_code is not None:
            prop_list = ns.get_properties_list(hot_code)
            if prop_list:
                msg1 = bot.send_message(message.from_user.id, "Enter "
                                                              "how many results "
                                                              "you want to see (No more than 12)")
                database.hset(str(chat_id) + " " + str(n), 'city', destination)

                bot.register_next_step_handler(msg1, getting_res_num)

            else:
                bot.send_message(message.from_user.id, "This town is not in the list, press /start")
                database.hset(str(chat_id) + " " + str(n), 'city', destination)
                database.hset(str(chat_id) + " " + str(n), "answer", "NoResult")
        else:
            bot.send_message(message.from_user.id, "This town is not in the list, press /start")
            database.hset(str(chat_id) + " " + str(n), 'city', destination)
            database.hset(str(chat_id) + " " + str(n), "answer", "NoResult")


def getting_res_num(message):
    """
    This function gets the number of results,
    checks up the correctness of user input
    returns question, fills in database
    :param message: message
    :return: None
    """

    chat_id = message.chat.id
    n = database.hget(str(chat_id), "num")
    result = []
    res_number = message.text
    if not res_number.isdigit():
        bot.send_message(message.from_user.id, "Error, enter numbers, press /start ")
        database.hset(str(chat_id) + " " + str(n), 'numbers', "NumError")
    else:
        if int(res_number) > 12:
            bot.send_message(message.from_user.id, "Too many results to show"
                                                   " press/start ")
            database.hset(str(chat_id) + " " + str(n), 'numbers', "NumError")

        else:
            database.hset(str(chat_id) + " " + str(n), 'res_number', res_number)
            if database.hget(str(chat_id) + " " + str(n), 'command') != "/bestdeal":
                need_of_photo(message)
            else:
                msg = bot.send_message(message.from_user.id, "Enter "
                                                             "one night price, $")
                bot.register_next_step_handler(msg, best_price)


def best_price(message):
    """
    This function for bestdeal command,
    checks up the correctness of user input
    returns question, fills in database
    :param message: message
    :return: None
    """
    user_price = message.text
    chat_id = message.chat.id
    n = database.hget(str(chat_id), "num")
    if not user_price.isdigit():
        bot.send_message(message.from_user.id, "Enter numbers please"
                                               "press /bestdeal ")
        database.hset(str(chat_id) + " " + str(n), 'numbers', "NumError")
    else:

        database.hset(str(chat_id) + " " + str(n), 'user_price', user_price)
        msg1 = bot.send_message(message.from_user.id, "Enter distance from "
                                                      "center, miles")

        bot.register_next_step_handler(msg1, best_destination)


def best_destination(message):
    """
    This function for user destination,
    checks up the correctness of user input
    returns question, fills in database
    :param message: message
    :return: None
    """
    user_distance = message.text
    chat_id = message.chat.id
    n = database.hget(str(chat_id), "num")
    if not user_distance.isdigit():
        bot.send_message(message.from_user.id, "Enter numbers,"
                                               "press /bestdeal ")
        database.hset(str(chat_id) + " " + str(n), 'numbers', "NumError")
    else:
        database.hset(str(chat_id) + " " + str(n), 'user_distance', user_distance)

        bot.send_message(message.chat.id, "Check in and check out dates /calendar")
        run_calendar(message)


@bot.message_handler(commands=['calendar'])
def run_calendar(message):
    """
    This function turns on calendar keyboard twice

    :param1 message: calendar keyboard
    :param2 message: calendar keyboard
    :return: None
    """

    now = datetime.now()
    msg1, msg2 = bot.send_message(
        message.chat.id,
        "Choose check in date",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    ), bot.send_message(
        message.chat.id,
        "Choose check out date",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery):
    """
    Function processing inline callback requests,
    checking the corectness of user input,
    returns question, fills in database
    :param1 call: calendar keyboard
    :return: None

    """
    lst = []
    period = 0
    msg = ""
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )

    if action == "DAY":
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        answer = bot.send_message(
            chat_id=call.from_user.id,
            text=f"You choose {date.strftime('%d.%m.%Y')}",
            reply_markup=InlineKeyboardMarkup(), )

        n = database.hget(str(call.from_user.id), 'num')
        chat_id = call.from_user.id
        dt = date.strftime('%d.%m.%Y')
        new_id = str(chat_id) + " " + str(n)
        if database.hget(new_id, 'date1') is None or database.hget(new_id, 'date1') == "":
            database.hset(new_id, 'date1', str(dt))
            bot.send_message(call.from_user.id, "Choose next date")
        else:
            database.hset(new_id, 'date2', str(dt))
        if database.hget(new_id, 'date1') is not None and database.hget(new_id, 'date2') != "" \
                and database.hget(new_id, 'date2') is not None:
            new_id = str(chat_id) + " " + str(n)
            lst = [database.hget(new_id, 'date1'), database.hget(new_id, 'date2')]
            period = ns.date_count(lst[0], lst[1])
            if int(period) < 0:
                database.hset(new_id, 'date1', "")
                database.hset(new_id, 'date2', "")
                bot.send_message(chat_id, "Wrong dates, first later date was chosen,"
                                          "press /calendar ")
            else:
                database.hset(new_id, 'period', period)
                if 20 < int(period) and 1 < int(period) % 10 <= 4:
                    bot.send_message(chat_id, "Visit time is " + str(period)
                                     + " days")
                    need_of_photo(call)
                elif int(period) < 10 and int(period) % 10 == 1:
                    bot.send_message(chat_id, "Visit time is " + str(period)
                                     + " days")
                    need_of_photo(call)
                else:
                    bot.send_message(chat_id, "VIsit time is " + str(period)
                                     + " days")
                    need_of_photo(call)
    if action == "CANCEL":
        answer = bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )


def need_of_photo(message):
    """
    This function to check for photo necessity
    :param message: keyboard type
    :return: None
    """
    question0 = bot.send_message(message.from_user.id, "Do you want to see images of hotels? ")
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='No', callback_data='no')
    keyboard.add(key_no)
    question = 'Press "yes" or "No" buttons'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def callback_answer_yes(call):
    """
    Function processes callback query
    :param call: keyboard type object answer 'yes'
    :return: None
    """
    if call.data == "yes":
        msg = bot.send_message(call.from_user.id, 'Enter number '
                                                  'of photos to upload (No more than 9)')
        bot.register_next_step_handler(msg, result_photo)


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_answer_no(call):
    """
    Function processes callback query,
    checking the correctness of user input,
    returns question, fills in database
    :param call: keyboard type object answer 'no'
    :return: None
    """
    chat_id = call.from_user.id
    n = database.hget(str(chat_id), "num")
    new_id = str(chat_id) + " " + str(n)
    command = database.hget(new_id, 'command')
    destination = database.hget(new_id, 'city')
    res_num = database.hget(new_id, 'res_number')
    lst = []
    user_price = ''
    user_dist = ''
    period = ''
    text = ''
    if command == "/lowprice" or command == "/highprice":
        lst = ns.get_hotels(command, destination, res_num, 0)
        if lst:
            lst = ns.deal_with_none(lst)
            to_save = json.dumps(lst)
            database.hset(new_id, 'answer', to_save)
            for hotel in lst:
                text = f'Name of hotel: {hotel["hotel_name"]}, ' \
                       f' Address {hotel["address"]}' \
                       f' Price: {hotel["price"]} ,' \
                       f' Rating: {hotel["hotel_rating"]}'

                bot.send_message(call.from_user.id, text)
        else:
            bot.send_message(call.from_user.id, "There wasn't found any hotels in this town, "
                                                "press  /start")
            database.hset(new_id, 'answer', "NoResult")
    else:
        user_price = database.hget(new_id, 'user_price')
        user_dist = database.hget(new_id, 'user_distance')
        period = database.hget(new_id, 'period')
        lst = ns.get_hotels2(destination, res_num, user_price, user_dist, period, 0)
        if lst:
            lst = ns.deal_with_none(lst)
            to_save = json.dumps(lst)
            database.hset(new_id, 'answer', to_save)
            for hotel in lst:
                text = f'Name of hotel: {hotel["hotel_name"]}, ' \
                       f' Price per night: {hotel["price"]} , ' \
                       f' Total price {hotel["total_price"]},' \
                       f' Address {hotel["address"]}' \
                       f' Distance from center {hotel["distance"]}' \
                       f' Rating: {hotel["hotel_rating"]}'
                bot.send_message(call.from_user.id, text)
        else:
            bot.send_message(call.from_user.id, "There wasn't found any hotels in this town, with selected filters "
                                                "press  /start")
            database.hset(new_id, 'answer', "NoUserResult")
        print(database.hgetall(new_id))


def result_photo(message, *args, **kwargs):
    """
    Function processes information from database,
    returns final answer to user.
    checks the correctness of user input,
    fills in database for history
    :param message: message
    :return: None
    """
    img_num = message.text
    chat_id = message.chat.id
    n = database.hget(str(chat_id), "num")
    new_id = str(chat_id) + " " + str(n)
    if not img_num.isdigit():
        bot.send_message(message.from_user.id, "Enter numbers, press /start ")
        database.hset(new_id, 'numbers', "NumError")
    elif int(img_num) > 9:
        bot.send_message(message.from_user.id, "You entered wrong photos number,"
                                               "lets start from the beginning, press \n"
                                               " /lowprice\n/highprice\n/bestdeal")
        database.hset(new_id, 'numbers', "NumError")
    else:
        database.hset(new_id, "photo_num", img_num)
        command = database.hget(new_id, 'command')
        city = database.hget(new_id, 'city')
        res_num = database.hget(new_id, 'res_number')
        user_price = database.hget(new_id, 'user_price')
        user_dist = database.hget(new_id, 'user_distance')
        period = database.hget(new_id, 'period')
        print(database.hgetall(new_id))
        lst = []
        if command == "/lowprice" or command == "/highprice":
            lst = ns.get_hotels(command, city, res_num, img_num)
            if lst:
                lst = ns.deal_with_none(lst)
                to_save = json.dumps(lst)
                database.hset(new_id, 'answer', to_save)
                for hotel in lst:
                    text = f' Name of hotel: {hotel["hotel_name"]}, ' \
                           f' Price per night: {hotel["price"]} , ' \
                           f' Address {hotel["address"]}' \
                           f' Rating: {hotel["hotel_rating"]}'

                    media_group = []
                    for i in range(len(hotel['hotel_images'])):
                        media_group.append(InputMediaPhoto(hotel['hotel_images'][i], caption=text if i == 0 else ''))

                    bot.send_media_group(chat_id=chat_id, media=media_group)
            else:
                bot.send_message(message.chat.id, "Отелей в данном городе не найдено, "
                                                  "нажмите  /start")
                database.hset(new_id, 'answer', "NoResult")

        else:
            lst = ns.get_hotels2(city, res_num, user_price, user_dist, period, img_num)

            if lst:
                lst = ns.deal_with_none(lst)
                to_save = json.dumps(lst)
                database.hset(new_id, 'answer', to_save)
                for hotel in lst:
                    text = f'Name of hotel: {hotel["hotel_name"]}, ' \
                           f' Price per day: {hotel["price"]} , ' \
                           f' Total price {hotel["total_price"]},' \
                           f' Address {hotel["address"]}' \
                           f' Distance from center {hotel["distance"]}' \
                           f' Rating: {hotel["hotel_rating"]}'
                    media_group = []
                    for i in range(len(hotel['hotel_images'])):
                        media_group.append(InputMediaPhoto(hotel['hotel_images'][i], caption=text if i == 0 else ''))

                    bot.send_media_group(chat_id=chat_id, media=media_group)
            else:
                bot.send_message(message.chat.id, "There wasn't found any hotels in this town  "
                                                  "press  /start")
                database.hset(new_id, 'answer', "NoUserResult")
            print(database.hgetall(new_id))


@bot.message_handler(commands=["history"])
def getting_history(message, *args, **kwargs):
    """
    Function returns history of commands actions
    :return: None
    """
    chat_id = message.chat.id
    n = database.hget(str(chat_id), "num")
    print(n)
    for i in range(int(n) + 1):
        new_id = str(chat_id) + " " + str(i)
        if new_id.startswith(str(chat_id)):
            command = database.hget(new_id, 'command')
            city = database.hget(new_id, 'city')
            if database.hget(new_id, 'answer1') == "NoResult":
                text = f'Error in town input, ' \
                       f' request in {city} was started from the beginning'
                bot.send_message(chat_id, text)
            elif database.hget(new_id, 'numbers') == "NumError":
                text = f'Numbers error, ' \
                       f' request in {city} was started from the beginning'
                bot.send_message(chat_id, text)
            elif database.hget(new_id, 'answer') == "NoResult":
                text = f'Command pressed {command}, ' \
                       f' There wasnt information about {city}'
                bot.send_message(chat_id, text)
            elif database.hget(new_id, 'answer') == "NoUserResult":
                text = f'Command pressed {command}, ' \
                       f' There wasnt information about {city} with selected filters'
                bot.send_message(chat_id, text)

            else:
                res_num = database.hget(new_id, 'res_number')
                user_price = database.hget(new_id, 'user_price')
                user_distance = database.hget(new_id, 'user_distance')
                call_time = database.hget(new_id, 'call_time')
                date1 = database.hget(new_id, 'date1')
                date2 = database.hget(new_id, 'date2')
                for hotel in json.loads(database.hget(new_id, 'answer')):
                    if command != "/bestdeal":
                        text = f'Entered command {command}, ' \
                               f' Town name {city.capitalize()}, ' \
                               f' Number of results to show {res_num}, ' \
                               f' Hotels name: {hotel["hotel_name"]}, ' \
                               f' Price per night: {hotel["price"]}, ' \
                               f' Address {hotel["address"]}, ' \
                               f' Rating: {hotel["hotel_rating"]}, time of request {call_time}'
                        if hotel['hotel_images']:
                            media_group = []
                            for j in range(len(hotel['hotel_images'])):
                                media_group.append(
                                    InputMediaPhoto(hotel['hotel_images'][j], caption=text if j == 0 else ''))
                            bot.send_media_group(chat_id=chat_id, media=media_group)

                        else:
                            bot.send_message(chat_id, text)
                    else:
                        text = f'Entered command {command}, ' \
                               f' Town name {city}, ' \
                               f' Number of results to show {res_num}, ' \
                               f' Price {user_price}, ' \
                               f' Distance from center {user_distance}, ' \
                               f' Name of hotel: {hotel["hotel_name"]}, ' \
                               f' Price per night: {hotel["price"]}, ' \
                               f' Address {hotel["address"]},' \
                               f' Distance from center {hotel["distance"]},' \
                               f' Rating: {hotel["hotel_rating"]}, Время вызова команды {call_time}'
                        if hotel['hotel_images']:
                            media_group = []
                            for j in range(len(hotel['hotel_images'])):
                                media_group.append(
                                    InputMediaPhoto(hotel['hotel_images'][j], caption=text if j == 0 else ''))
                            bot.send_media_group(chat_id=chat_id, media=media_group)

                        else:
                            bot.send_message(chat_id, text)


if __name__ == '__main__':
    bot.infinity_polling()
