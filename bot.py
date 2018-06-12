from config import *
import telebot
import logging
from telebot import types
from parser import *
import time

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(token)

message_box = {
    'welcome':
        u'Привет! Наш бот поможет тебе узнать прогнозы прибытия общественного транспорта на нужную остановку в городе Архангельск.',
    'info':
        u'Информация предоставляется только по транспорту, оборудованному системой спутникового слежения ГЛОНАСС. Если транспорт неактивен в течение 5 минут и более, то он не отслеживается',
    'error':
        u'Прогноз пуст! Попробуйте чуть позже.',
    'invalid-input':
    	u'Такой остановки не существует! Попробуйте еще.',
	'invalid-input-bus':
    	u'Такого автобуса не существует! Попробуйте еще.',    
    'bus':
    	u'Введите номер автобуса.',
    'help':
    	u'При выборе команды /search_station требуется ввести название остановки и из предложенного списка выбрать нужную остановку.\nПри выборе команды /search_bus требуется ввести номер автобуса(только число) и затем выбрать нужный вариант с учетом направления движения.',
    'input-station':
    	u'Введите остановку.',
    'select-station':
    	u'Выберите остановку.',
	'select-route':
    	u'Выберите автобус.',  
    'select-end':
    	u'Выберите станцию.',  	
    'data':
    	u'\n \U0001F68C Номер автобуса:{}\n \U0001F552 Время прибытия:{}\n \U0000270F Текущая остановка:{}\n'    
}

@bot.message_handler(commands=['start']) 
def start(message):
	bot.send_message(message.chat.id,message_box['welcome'])

@bot.message_handler(commands=['info']) 
def info(message):
	bot.send_message(message.chat.id,message_box['info'])

@bot.message_handler(commands=['help']) 
def help(message):
	bot.send_message(message.chat.id,message_box['help'])

@bot.message_handler(func=lambda message: message.chat.type == "private" ,commands=['search_station']) 
def search(message):
	bot.send_message(message.chat.id,message_box['input-station'])
	bot.register_next_step_handler(message, get_search)

def get_search(message):
	stations=[];hrefs=[]
	stations,hrefs=getSearchList(message.text) #parse buttons+their hrefs
	if stations:
		keyboard = types.InlineKeyboardMarkup()
		for i in range(len(stations)):
			keyboard.add(types.InlineKeyboardButton(text="№"+str(i+1)+" "+str(stations[i]), callback_data=str(hrefs[i])))
		bot.reply_to(message, message_box['select-station'], reply_markup=keyboard)
	else: 
		bot.reply_to(message, message_box['invalid-input'])


@bot.callback_query_handler(lambda call: call.message.chat.type == "private")
def callback_inline(call):
	if call.message.text== message_box['select-station']:
		table=[]
		table=splitList(getTable(call.data)[3:],3) #parse->split
		if table:
			for item in table:
				bot.send_message(call.message.chat.id,message_box['data'].format(*item))
		else:
			bot.send_message(call.message.chat.id,message_box['error'])	
		bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
	elif call.message.text== message_box['select-route']:
		routes=[];hrefs=[]
		routes,hrefs=getRouteTables(call.data)
		keyboard = types.InlineKeyboardMarkup()
		for i in range(len(routes)):
			keyboard.add(types.InlineKeyboardButton(text=str(routes[i]), callback_data=str(hrefs[i])))
		bot.reply_to(call.message, message_box['select-end'], reply_markup=keyboard)			
	elif call.message.text== message_box['select-end']:
		table=[]
		table=splitList(getTable(call.data)[3:],3) #parse->split
		if table:
			for item in table:
				bot.send_message(call.message.chat.id,message_box['data'].format(*item))
		else:
			bot.send_message(call.message.chat.id,message_box['error'])	
		bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
	
		
@bot.message_handler(func=lambda message: message.chat.type == "private" ,commands=['search_bus']) 
def route(message):
	bot.send_message(message.chat.id,message_box['bus'])
	bot.register_next_step_handler(message,get_route)

def get_route(message):
	if message.text.isdigit():
		routes=[];hrefs=[]
		routes,hrefs=getRouteList(message.text)
		if routes:
			keyboard = types.InlineKeyboardMarkup()
			for i in range(len(routes)):
				keyboard.add(types.InlineKeyboardButton(text=str(routes[i]), callback_data=str(hrefs[i])))
			bot.reply_to(message, message_box['select-route'], reply_markup=keyboard)
		else:
			bot.send_message(message.chat.id,message_box['invalid-input-bus'])	
			bot.edit_message_reply_markup(message.chat.id, message.message_id)			
	else:
		bot.send_message(message.chat.id,message_box['invalid-input-bus'])	

if __name__ == '__main__':
	while True:
	    try:
	        bot.polling(none_stop=True)
	    except Exception as e:
	        logger.error(e)
	        time.sleep(10)