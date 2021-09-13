#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 13:18:20 2021

@author: yifan wu
"""
import telegram.utils.request
# Import necessary modules
import logging
import re
import random
import ast
import json
import http.client
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import telepot

global bot
bot = telepot.Bot('1993196016:AAEo5g1X8yxRbCYYdM6qJ-O42JrcIr4GxWE')
"""
A chat robot that can help you find information of the Covid-19 all over the world.
The bot has been deployed on github
"""

"""
Usage: 
Send /start to initiate the conversation.
Run "updater.stop()" to stop the bot.
"""

# 连接各个国家的covid19数据查询api
conn = http.client.HTTPSConnection("covid-19-coronavirus-statistics.p.rapidapi.com")
headers = {
    'x-rapidapi-host': "covid-19-coronavirus-statistics.p.rapidapi.com",
    'x-rapidapi-key': "b5bc781b03msh74d4cf95a728b4bp198edbjsnbaa29715a04f"
    }
# 连接covid19疫苗新闻数据查询api
conn1 = http.client.HTTPSConnection("vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com")
headers1 = {
    'x-rapidapi-host': "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com",
    'x-rapidapi-key': "b5bc781b03msh74d4cf95a728b4bp198edbjsnbaa29715a04f"
    }

# 训练rasa解释器
trainer = Trainer(config.load("config_spacy.yml"))
# Load the training data
training_data = load_data('fan-rasa.md')
# Create an interpreter by training the model
interpreter = trainer.train(training_data)


# 全局变量声明
params = []
dude = None
# 不懂回复
default = "What does that mean? I don't understand...:("
# 闲聊回复
rules = {'i wish (.*)': ['What would it mean if {0}',
                         'Why do you wish {0}',
                         "What's stopping you from realising {0}"
                        ],
         'do you remember (.*)': ['Did you think I would forget {0}',
                                  "Why haven't you been able to forget {0}",
                                  'What about {0}',
                                  'Yes .. and?'
                                 ],
         'do you think (.*)': ['if {0}? Absolutely.',
                               'No chance.'
                              ],
         'if (.*)': ["Do you really think it's likely that {0}",
                     'Do you wish that {0}',
                     'What do you think about {0}',
                     'Really--if {0}'
                    ]
        }

# 定义回复规则
response = [
    "I'm sorry, I couldn't find anything like that. ",
    "Great! Here are some brief information about {}:",
    "Bingo! I found the following items: ",
]

#proxy = telegram.utils.request.Request(proxy_url='https://127.0.0.1:1080')
#bot = telegram.Bot('1993196016:AAEo5g1X8yxRbCYYdM6qJ-O42JrcIr4GxWE', request=proxy);

updater = Updater(token='1993196016:AAEo5g1X8yxRbCYYdM6qJ-O42JrcIr4GxWE', request_kwargs={'proxy_url': 'http://127.0.0.1:1200'})
#updater = Updater(token='1993196016:AAEo5g1X8yxRbCYYdM6qJ-O42JrcIr4GxWE', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
mlogger = logging.getLogger('matplotlib')
mlogger.setLevel(logging.WARNING)
# start命令
def start(update, context):
     update.message.reply_text(
        "Hi! My name is fan. I can help you search for information about epidemic covid-19.\n\n"
        "You can also ask latest death or affection information of any country, "
        "including update time, total cases, death case, recovered cases.\n"
        "For example 'tell me UK', 'can you tell me about France'.\n\n"
        "Welcome to chat with me! "
        )
     context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('C:/Users/Administrator/Desktop/covid19.jpg', 'rb'))
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# 大小写转换命令
def caps(update, context):
    print(type(context.args))
    text_caps = ' '.join(context.args).upper()
    return text_caps

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

# 未知命令
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=default)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# 替换人称
def replace_pronouns(message):
    message = message.lower()

    if 'me' in message:
        # Replace 'me' with 'you'
        return re.sub('me', 'you', message)
    if 'my' in message:
        # Replace 'my' with 'your'
        return re.sub('my', 'your', message)
    if 'your' in message:
        # Replace 'your' with 'my'
        return re.sub('your', 'my', message)
    if 'you' in message:
        # Replace 'you' with 'me'
        return re.sub('you', 'me', message)

    return message

# 匹配回复规则
def match_rule(update, context, message):
    for pattern, value in rules.items():
        # Create a match object
        match = re.search(pattern, message)
        # 如果匹配成功
        if match is not None:
            # Choose a random response
            response = random.choice(rules[pattern])
            # 如果需要人称替换
            if '{0}' in response:
                phrase = re.search(pattern, message).group(1)
                phrase = replace_pronouns(phrase)
                # 回复消息
                update.message.reply_text(response.format(phrase))
            else:
                # 回复消息
                update.message.reply_text(response)
            return True

    return False

#一周的数据显示
def find_one_week(message):
    name2 = None
    name_words2 = []

    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")

    # Get the matching words in the string
    name_words2 += name_pattern.findall(message)

    # Create a pattern for checking if the keywords occur

    name_keyword2 = re.compile("a week|one week|week|weak", re.I)

    if len(name_words2) > 0:
        if name_keyword2.findall(message):
         # Return the name if the keywords are present
         name2 = name_words2[0]

    return name2

#一个月的数据显示
def find_one_month(message):
    name3 = None
    name_words3 = []

    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")

    # Get the matching words in the string
    name_words3 += name_pattern.findall(message)

    # Create a pattern for checking if the keywords occur

    name_keyword3 = re.compile("a month|one month|for a month", re.I)

    if len(name_words3) > 0:
        if name_keyword3.findall(message):
         # Return the name if the keywords are present
         name3 = name_words3[0]

    return name3

#三个月的数据显示
def find_three_month(message):
    name4 = None
    name_words4 = []

    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")

    # Get the matching words in the string
    name_words4 += name_pattern.findall(message)

    # Create a pattern for checking if the keywords occur

    name_keyword4 = re.compile("3 months|three months|for 3 months", re.I)

    if len(name_words4) > 0:
        if name_keyword4.findall(message):
         # Return the name if the keywords are present
         name4 = name_words4[0]

    return name4

#六个月的数据显示
def find_six_month(message):
    name5 = None
    name_words5 = []

    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")

    # Get the matching words in the string
    name_words5 += name_pattern.findall(message)

    # Create a pattern for checking if the keywords occur

    name_keyword5 = re.compile("3 months|three months|for 3 months", re.I)

    if len(name_words5) > 0:
        if name_keyword5.findall(message):
          # Return the name if the keywords are present
          name5 = name_words5[0]
        else:
            name5 = None
    return name5

# 提取国家名
def find_name(message):
    name = None
    name_words = []

    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")

    # Get the matching words in the string
    name_words += name_pattern.findall(message)

    # Create a pattern for checking if the keywords occur
    name_keyword = re.compile("total|tell|show|cases|covid|", re.I)

    if len(name_words) > 0:
        # Return the name if the keywords are present
        name = name_words[0]

    return name

# 自动将国家名转换大写
def turn_name(message):
    if "name*" in message:
        index = message.index("name*") + len("name*")
        name = message[index:].upper()
        name_list = name.split(' ')

        for i in range(len(name_list)):
            if name_list[i] == '':
                continue
            else:
                index = i
                break

        newname = name_list[index:]
        return newname

#搜索各个国家的Covid19的各类数据
def search_work(update, context, name):
    if name == None:
        update.message.reply_text(default)
        return name

    print(name)
    conn.request("GET", "/v1/total?country="+name, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    data = json.loads(data)
    params = data["data"]

    update.message.reply_text("here is the total situation in {}:".format(params["location"]))
    update.message.reply_text('recovered number:{}'.format(params["recovered"]))
    update.message.reply_text('deaths number:{}'.format(params["deaths"]))
    update.message.reply_text('confirmed number:{}'.format(params["confirmed"]))
    update.message.reply_text('current report time:{}'.format(params["lastReported"]))
    return params

# 提取疫苗信息
def find_vaccine(message):
    name1= None
    name_words1 = []
    name_keyword1 = re.compile("Vaccine|NEWS|News|vaccine|vaccination", re.I)
    if name_keyword1.search(message):
        name1 = name_words1

    return name1

# vaccine_search
def search_vaccine(update, context, name1):
    if name1 == None:
        update.message.reply_text(default)
        return name1

    # 获得api数据
    conn1.request("GET", "/api/news/get-vaccine-news/0", headers=headers1)
    res = conn1.getresponse()
    data = res.read().decode("utf-8")
    # 将字符串转换为字典格式
    data = json.loads(data)

    # params存放搜索结果
    params = data["news"]
    # rename存放搜索结果名
    rename = [r['title'] for r in params]

    # 根据检索到的数目选择回复
    update.message.reply_text(response[2].format(*rename))

    # 得到检索到信息的长度
    lenth = len(rename)
    for i in range(lenth):
        update.message.reply_text("{}. {}".format(i + 1, rename[i]))

    update.message.reply_text("Tell me the index of which to view specific information.\n"
                                  "For example 'the third one', '5'")

    return params

# number_work
def number_work(update, context, message, params):
    name1 = message
    global id
    if "1" in name1:
        if "1" in name1:
            if name1.find("0") < 0:
                id = 1
            else:
                id = 10
    elif "one" in name1 or "first" in name1:
            id = 1
    elif "2" in name1 or "two" in name1 or "second" in name1:
            id = 2
    elif "3" in name1 or "three" in name1 or "third" in name1:
            id = 3
    elif "4" in name1 or "four" in name1 or "fourth" in name1:
            id = 4
    elif "5" in name1 or "five" in name1 or "fifth" in name1:
            id = 5
    elif "6" in name1 or "six" in name1 or "sixth" in name1:
            id = 6
    elif "7" in name1 or "seven" in name1 or "seventh" in name1:
            id = 7
    elif "8" in name1 or "eight" in name1 or "eighth" in name1:
            id = 8
    elif "9" in name1 or "nine" in name1 or "ninth" in name1:
            id = 9
    elif "10" in name1 or "ten" in name1 or "tenth" in name1:
            id = 10
    else:
            id = None

    # 索引错误时返回
    if id == None:
        update.message.reply_text("Please give me right index. (๑• . •๑)")
        return params

    print(params)
    # 索引正确时更新params并给出news信息
    params = params[id - 1]
    update.message.reply_text("Here are some brief information about {}:".format(params["title"]))
    for key in params:
        if key == "urlToImage":
            update.message.reply_text("urlToImage:")
            #############################################################
            update.message.reply_photo(params[key])
            continue
        update.message.reply_text("{}: {}".format(key, params[key]))

    return params


def one_week_search(update, context, name2, name3, name4, name5):
    if name2 == None:
        update.message.reply_text(default)
        return name2

    photo_send(name2,name3,name4,name5)
    update.message.reply_text("Here is the information you want:")
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open('D:/chatbot_covid/pic/pic1.jpg', 'rb'))

def one_month_search(update, context, name2, name3, name4, name5):

    if name3 == None:
        update.message.reply_text(default)
        return name3

    photo_send(name2, name3, name4, name5)
    update.message.reply_text("Here is the information you want:")
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open('D:/chatbot_covid/pic/pic1.jpg', 'rb'))


def three_months_search(update, context, name2, name3, name4, name5):
    if name4 == None:
        update.message.reply_text(default)
        return name4

    photo_send(name2, name3, name4, name5)
    update.message.reply_text("Here is the information you want:")
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open('D:/chatbot_covid/pic/pic1.jpg', 'rb'))


def six_months_search(update, context, name2, name3, name4, name5):
    if name5 == None:
        update.message.reply_text(default)
        return name5

    photo_send(name2, name3, name4, name5)
    update.message.reply_text("Here is the information you want:")
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open('D:/chatbot_covid/pic/pic1.jpg', 'rb'))

# 理解消息并回复
def respond(update, context, message):
    target = interpreter.parse(message)
    print(target)
    global params

    # 去掉消息中所有标点
    r = '[’!"#$%&\'()+,-./:;<=>?@[\\]^_`{|}~]+'
    message = re.sub(r, '', message)
    print(message)
    # params test
    print(params)


    # name5存放消息
    name5 = find_six_month(message)
    # name4存放消息
    name4 = find_three_month(message)
    # name3存放消息
    name3 = find_one_month(message)
    # name2存放信息
    name2 = find_one_week(message)
    # name1存放用户消息中的国家名
    name1 = find_vaccine(message)
    # name存放用户消息中的名
    name = find_name(message)
        #if name == None:
            #name = turn_name(message)
    #print(name)

    message = message.lower()

    print(target['intent']['name'])

    # 判断意图进行检索
    if target['intent']['name'] == 'work_search':
        if name == None:
           update.message.reply_text("can you tell me the specific country name?")
        else:
           params = search_work(update, context, name)

    elif target['intent']['name'] == 'work_number':
        params = number_work(update, context, message, params)

    elif target['intent']['name'] == 'vaccine_news_search':
        params = search_vaccine(update, context, name1)

    elif target['intent']['name'] == 'one_week_search':
        if name2 == None:
            update.message.reply_text("would you like to me the specific country name?")
            # here replace chat_id and test.jpg with real things
        else:
            params = one_week_search(update, context, name2, name3, name4, name5)

    elif target['intent']['name'] == 'one_month_search':
        if name3 ==None:
            update.message.reply_text("would you like to me the specific country name?")
        else:
            params = one_month_search(update, context, name2, name3, name4, name5)

    elif target['intent']['name'] == 'three_months_search':
        if name4 ==None:
            update.message.reply_text("would you like to me the specific country name?")
        else:
            params = three_months_search(update, context, name2, name3, name4, name5)

    elif target['intent']['name'] == 'six_months_search':
        if name5 ==None:
            update.message.reply_text("would you like to me the specific country name?")
        else:
            params = six_months_search(update, context, name2, name3, name4, name5)

    elif target['intent']['name'] == 'greet':
        # greet消息
        greet = [
            "Hello~",
            "Hey!",
            "Hi~",
            "Hey there~"
        ]
        update.message.reply_text(random.choice(greet))

    elif target['intent']['name'] == 'bot_challenge':
        # bot challenge消息
        bot = [
            "I'm Robot Fan. I can help you find information about the covid-19",
            "My name is Robot Fan. I can help you find information about the covid-19. (๑•ᴗ•๑)♡",
            "My name is Robot Fan, you can call me Fan. I can help you find information about the covid-19. (๑•ᴗ•๑)♡"
        ]
        update.message.reply_text(random.choice(bot))

    elif target['intent']['name'] == 'mood_great':
        # mood great消息
        great = [
            "Great! o(^▽^)o",
            "Yeah! o(^▽^)o",
            "Cheers! o(^▽^)o"
        ]
        update.message.reply_text(random.choice(great))

    elif target['intent']['name'] == 'thanks':
        # thank消息
        thank = [
            "I am glad I can help. (ฅ◑ω◑ฅ)",
            "You are welcome. (ฅ◑ω◑ฅ)",
            "So kind of you. (ฅ◑ω◑ฅ)",
            "It is my pleasure. (ฅ◑ω◑ฅ)"
        ]
        update.message.reply_text(random.choice(thank))

    elif target['intent']['name'] == 'goodbye':
        # goodbye消息
        bye = [
            "bye ~",
            "goodbye ~",
            "see you around ~",
            "see you later ~",
            "see you ~"
        ]
        update.message.reply_text(random.choice(bye))

    else:
        update.message.reply_text(default)


def photo_send(name2, name3, name4, name5):
    if name2 !=None:
        # 获得api数据
        conn1.request("GET", "/api/covid-ovid-data/sixmonth/{}".format(name2), headers=headers1)
        res = conn1.getresponse()
        data = res.read().decode("utf-8")
        # 将字符串转换为字典格式
        data = ast.literal_eval(data)
        global year
        global x, y
        year = None
        x = []
        y = []
        for i in range(len(data)):
            if i < 7:
                params = data[i]["date"]
                year = params[:4]
                params = params[5:]
                x.append(params)
        for i in range(len(data)):
            if i < 7:
                params = data[i]["total_cases"]
                y.append(params)
        list.reverse(x)
        list.reverse(y)
        # 显示最新1周的情况
        # 修改标签文字和线条粗细
        fig, axs = plt.subplots()
        plt.plot(x, y, label='Frist line', linewidth=2, color='c', marker='o', markerfacecolor='blue', markersize=10)
        plt.xlabel('Date')
        plt.ylabel('Total Cases Number')
        plt.title('The total cases of {} in {} of a week'.format(name2, str(year)))
        axs.spines['right'].set_visible(False)
        axs.spines['top'].set_visible(False)
        plt.savefig('D:/chatbot_covid/pic/pic1.jpg', dpi=200)

    elif name3 != None:
        # 获得api数据
        conn1.request("GET", "/api/covid-ovid-data/sixmonth/{}".format(name3), headers=headers1)
        res = conn1.getresponse()
        data = res.read().decode("utf-8")
        # 将字符串转换为字典格式
        data = ast.literal_eval(data)
        year = None
        x = []
        y = []
        for i in range(len(data)):
            if i < 23:
                params = data[i]["date"]
                year = params[:4]
                params = params[5:]
                x.append(params)
        for i in range(len(data)):
            if i < 23:
                params = data[i]["total_cases"]
                y.append(params)
        list.reverse(x)
        list.reverse(y)
        # 显示最新1个月的情况
        # 修改标签文字和线条粗细
        fig, axs = plt.subplots()
        plt.plot(x, y, label='Frist line', linewidth=2, color='c', marker='o', markerfacecolor='blue', markersize=10)
        plt.xlabel('Date')
        plt.ylabel('Total Cases Number')
        plt.title('The total cases of {} in {} of a month'.format(name3, str(year)))
        axs.spines['right'].set_visible(False)
        axs.spines['top'].set_visible(False)
        plt.xticks(range(0, 24, 1), rotation=70)
        plt.savefig('D:/chatbot_covid/pic/pic1.jpg', dpi=200)

    elif name4 != None:
        conn1.request("GET", "/api/covid-ovid-data/sixmonth/{}".format(name4), headers=headers1)
        res = conn1.getresponse()
        data = res.read().decode("utf-8")
        # 将字符串转换为字典格式
        data = ast.literal_eval(data)
        year = None
        x = []
        y = []
        for i in range(len(data)):
            if i < 55:
                params = data[i]["date"]
                year = params[:4]
                params = params[5:]
                x.append(params)
        for i in range(len(data)):
            if i < 55:
                params = data[i]["total_cases"]
                if params == 0:
                    params = np.NAN
                    y.append(params)
                else:
                    y.append(params)
        list.reverse(x)
        list.reverse(y)
        y = np.array(y)
        # 显示最新3个月的情况
        # 修改标签文字和线条粗细
        fig, axs = plt.subplots()
        plt.plot(x, y, label='Frist line', linewidth=2, color='c', marker='o', markerfacecolor='blue', markersize=10)
        plt.xlabel('Date')
        plt.ylabel('Total Cases Number')
        plt.title('The total cases of {} in {} of 3 months'.format(name4, str(year)))
        axs.spines['right'].set_visible(False)
        axs.spines['top'].set_visible(False)
        plt.xticks(range(0, 55, 3), rotation=70)
        plt.savefig('D:/chatbot_covid/pic/pic1.jpg', dpi=200)

    elif name5 != None:
        conn1.request("GET", "/api/covid-ovid-data/sixmonth/{}".format(name5), headers=headers1)
        res = conn1.getresponse()
        data = res.read().decode("utf-8")
        # 将字符串转换为字典格式
        data = ast.literal_eval(data)
        year = None
        x = []
        y = []
        for i in range(len(data)):
            params = data[i]["date"]
            year = params[:4]
            params = params[5:]
            x.append(params)
        for i in range(len(data)):
            params = data[i]["total_cases"]
            if params == 0:
                params = np.NAN
                y.append(params)
            else:
                y.append(params)
        list.reverse(x)
        list.reverse(y)
        y = np.array(y)
        # 显示最新6个月的情况
        # 修改标签文字和线条粗细
        fig, axs = plt.subplots()
        plt.plot(x, y, label='Frist line', linewidth=2, color='c', marker='o', markerfacecolor='blue', markersize=10)
        plt.xlabel('Date')
        plt.ylabel('Total Cases Number')
        plt.title('The total cases of {} in {} of 6 months'.format(name5, str(year)))
        axs.spines['right'].set_visible(False)
        axs.spines['top'].set_visible(False)
        plt.xticks(range(0, 105, 5), rotation=70)
        plt.savefig('D:/chatbot_covid/pic/pic1.jpg', dpi=200)

# 消息回复功能
def msg(update, context):
    message = update.message.text

    result = match_rule(update, context, message)

    if result == False:
        respond(update, context, message)


msg_handler = MessageHandler(Filters.text, msg)
dispatcher.add_handler(msg_handler)
# ****************************************

# 启停
updater.start_polling()
# updater.idle()

# inline
from telegram import InlineQueryResultArticle, InputTextMessageContent


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


from telegram.ext import InlineQueryHandler

inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

