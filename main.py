import telebot
from telebot import types
from os import listdir, getcwd


#Создаем экземпляр бота
bot = telebot.TeleBot('TOKEN')


#глобальные переменные для хранения данных
name = '' #имя
phone = '' #номер
date = '' #когда позвонить
life = [] #объявления для жизни
investment = [] #объявления для инвестиций
chosen = -1 #выбранный вариант
category = '' #выбранная категория
ad_name = '' #название объявления
managers_id = [] #айди менеджеров
from_menu = True #вызов из меню


#генерируем маркап
def generate_markup(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for text in buttons:
        item1 = types.KeyboardButton(text)
        markup.add(item1)
    return markup


#главное меню
def main_menu(message):
    markup = generate_markup(['1. Надежные объекты Сочи', '2. Хочу что-то особенное', '3. О Сочи',
                             '4. Заказать обратный звонок'])
    bot.send_message(message.chat.id, 'Доброго времени суток, {}. Выберите нужный пункт в меню'.format(name),
                     reply_markup=markup)


#объявления
def ads(message, category):
    global chosen
    global life
    global investment
    global ad_name

    if category == 'life':
        markup = generate_markup(['1.1.1. Ещё вариант', '1.1.2. Перезвоните мне', '1.1.3. Назад'])
    else:
        markup = generate_markup(['1.2.1. Ещё вариант', '1.2.2. Перезвоните мне', '1.2.3. Назад'])
    adslist = []

    if category == 'life':
        life = listdir('ads/{}'.format(category))
        adslist = life
    else:
        investment = listdir('ads/{}'.format(category))
        adslist = investment

    if len(adslist) > 0:
        chosen = chosen + 1
        if chosen >= len(adslist):
            chosen = 0

    bot.send_message(message.from_user.id, 'Предложение {}'.format(chosen + 1), reply_markup=markup)

    variant = adslist[chosen]
    ad_name = variant

    adfolder = listdir('ads/{}/{}'.format(category, variant))
    text = ''
    photos = []
    videos = []
    for ad in adfolder:
        if ad.find('text') >= 0:
            text = ad
        elif ad.find('photo') >= 0:
            photos.append(ad)
        elif ad.find('video') >= 0:
            videos.append(ad)

    if text != '':
        textfile = open('ads/life/{}/{}'.format(variant, text), 'rb')
        textlines = textfile.readlines()
        bot.send_message(message.from_user.id, textlines, reply_markup=markup)
        textfile.close()
    if len(photos) >= 0:
        for photoname in photos:
            photo = open('ads/life/{}/{}'.format(variant, photoname), 'rb')
            bot.send_photo(message.from_user.id, photo)
            photo.close()
    if len(videos) >= 0:
        for videoname in videos:
            video = open('ads/life/{}/{}'.format(variant, videoname), 'rb')
            bot.send_video(message.from_user.id, video)
            video.close()


#обновляем данные о менеджерах
def update_managers():
    global managers_id
    managers_id.clear()

    managers = open('managers_id.txt', 'r')
    managerslines = managers.readlines()
    for manager in managerslines:
        managers_id.append(manager)

    managers.close()


#отправка сообщения менеджерам
def send_message_to_managers(from_main_menu = True):
    global managers_id
    global date
    global name
    global phone
    global category
    global ad_name

    for manager_id in managers_id:
        if from_main_menu:
            bot.send_message(manager_id, 'ФИО - {}\nТелефон - {}\nКогда позвонить - {}'.format(name, phone, date))
        else:
            bot.send_message(manager_id, 'ФИО - {}\nТелефон - {}\nВыбранная категория - {}\nВыбранный вариант - {}\n'
                                         'Когда позвонить - {}'.format(name, phone, category, ad_name, date))


#выполнение текстовых команд
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        markup = generate_markup(['Авторизоваться'])
        bot.send_message(message.from_user.id, 'Приветственное сообщение')
        dircontent = listdir()
        print(dircontent)
        photoname = ''
        for file in dircontent:
            print(file)
            print(file.find('hello'))
            print('\n')
            if file.find('hello') >= 0:
                photoname = file
                break
        if photoname == '':
            bot.send_message(message.from_user.id, 'Не удалось загрузить картинку. '
                                                   'Убедитесь, что в её названии присутствует слово hello')
        else:
            photo = open(photoname, 'rb')
            bot.send_photo(message.from_user.id, photo)
            photo.close()
        bot.send_message(message.from_user.id, 'Для продолжения авторизируйтесь', reply_markup=markup)

    elif message.text == 'Авторизоваться':
        if name == '':
            bot.send_message(message.from_user.id, 'Укажите ваше ФИО')
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.from_user.id, '{}, авторизация уже выполнена!'.format(name))
            main_menu(message)

    elif message.text == '1. Надежные объекты Сочи':
        markup = generate_markup(['1.1. Для жизни', '1.2. Для инвестиций'])
        bot.send_message(message.from_user.id, 'Укажите цель приобретения', reply_markup=markup)

    elif message.text == '1.1. Для жизни':
        global category
        global chosen

        chosen = -1
        category = message.text

        markup = generate_markup(['1.1.1. Ещё вариант', '1.1.2. Перезвоните мне', '1.1.3. Назад'])
        bot.send_message(message.from_user.id, 'Надежные предложения для жизни в Сочи', reply_markup=markup)

        ads(message, 'life')

    elif message.text == '1.1.1. Ещё вариант':
        ads(message, 'life')

    elif message.text == '1.2. Для инвестиций':
        markup = generate_markup(['1.2.1. Ещё вариант', '1.2.2. Перезвоните мне', '1.2.3. Назад'])
        bot.send_message(message.from_user.id, 'Надежные предложения для инвестиций в Сочи', reply_markup=markup)

        ads(message, 'investment')

    elif message.text == '1.1.2. Перезвоните мне' or message.text == '1.2.2. Перезвоните мне':
        global from_menu
        from_menu = False
        update_managers()

        markup = generate_markup(['4.1. Сегодня', '4.2. Завтра', '4.3. Другое время', '4.4. Вернуться в меню'])
        bot.send_message(message.from_user.id, 'Выберите удобное время', reply_markup=markup)

    elif message.text == '1.2.1. Ещё вариант':
        ads(message, 'investment')

    elif message.text == '1.1.3. Назад' or message.text == '1.2.3. Назад':
        main_menu(message)

    elif message.text == '2. Хочу что-то особенное':
        markup = generate_markup(['2.1. Вернуться в меню'])
        bot.send_message(message.from_user.id, 'Наш менеджер внимательно выслушает ваш запрос и предложит '
                                               'самые надежные объекты из доступных сейчас.', reply_markup=markup)

    elif message.text == '2.1. Вернуться в меню':
        main_menu(message)

    elif message.text == '3. О Сочи':
        markup = generate_markup(['3.1. Вернуться в меню'])

        dircontent = listdir('about')

        text_start = ''
        text_end = ''
        photos = []
        videos = []

        for data in dircontent:
            if data.find('text_start') >= 0:
                text_start = data
            if data.find('text_end') >= 0:
                text_end = data
            elif data.find('photo') >= 0:
                photos.append(data)
            elif data.find('video') >= 0:
                videos.append(data)

        if text_start != '':
            textfile = open('about/{}'.format(text_start), 'r')
            text = textfile.readlines()
            bot.send_message(message.from_user.id, text)
            textfile.close()

        if len(photos) > 0:
            for data in photos:
                photo = open('about/{}'.format(data), 'rb')
                bot.send_photo(message.from_user.id, photo)
                photo.close()

        if len(videos) > 0:
            for data in videos:
                video = open('about/{}'.format(data), 'rb')
                bot.send_video(message.from_user.id, video)
                video.close()

        if text_end != '':
            textfile = open('about/{}'.format(text_end), 'r')
            text = textfile.readlines()
            bot.send_message(message.from_user.id, text)
            textfile.close()

    elif message.text == '3.1. Вернуться в меню':
        main_menu(message)

    elif message.text == '4. Заказать обратный звонок':
        from_menu = True
        update_managers()

        markup = generate_markup(['4.1. Сегодня', '4.2. Завтра', '4.3. Другое время', '4.4. Вернуться в меню'])
        bot.send_message(message.from_user.id, 'Выберите удобное время', reply_markup=markup)

    elif message.text == '4.4. Вернуться в меню':
        main_menu(message)

    elif message.text == '4.1. Сегодня' or message.text == '4.2. Завтра':
        global date
        date = message.text[4:]
        bot.send_message(message.from_user.id, 'Наш менеджер свяжется с вами в выбранное вами время')
        send_message_to_managers(from_menu)
        main_menu(message)

    elif message.text == '4.3. Другое время':
        bot.send_message(message.from_user.id, 'Напишите, когда вам удобно будет ответить на звонок?')
        bot.register_next_step_handler(message, get_date)


    elif message.text == '4.1. Вернуться в меню':
        main_menu(message)

    elif message.text == '/myid':
        bot.send_message(message.from_user.id, message.from_user.id)

    else:
        bot.send_message(message.from_user.id, 'Неизвестная команда!')
        main_menu(message)


#узнаём имя
def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Укажите ваш номер телефона')
    bot.register_next_step_handler(message, get_phone)


#узнаём телефон
def get_phone(message):
    global phone
    phone = message.text
    main_menu(message)


#узнаём, когда позвонить
def get_date(message):
    global date
    date = message.text
    bot.send_message(message.from_user.id, 'Наш менеджер свяжется с вами в выбранное вами время')
    send_message_to_managers(from_menu)
    main_menu(message)


#основная функция запуска бота в цикле
bot.polling(none_stop=True, interval=0)