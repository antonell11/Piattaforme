#-*- coding: utf-8 -*-
#importo le librerie
from settings import token, start_msg
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from pprint import pprint
import json
import os
import requests
import sys
import telepot

#for user
utente = {}

#definizione della funzione on_chat_message
def on_chat_message(msg):

	content_type, chat_type, chat_id = telepot.glance(msg)
	name = msg["from"]["first_name"]

	# Check user state
    	try:
        	utente[chat_id] = utente[chat_id]
    	except:
        	utente[chat_id] = 0
	# start command
    	if 'text' in msg and msg['text'] == '/start':
		bot.sendMessage(chat_id, 'ciao {}'.format(name))
		bot.sendMessage(chat_id, "/help  --> per visualizzare comandi.\n")

    	elif 'text' in msg and msg['text'] == '/cerca':
        	msg = "clicca o digita una citta per trovare gli alberghi oppure /digita per cercare un albergo per il nome" 
        	markup = ReplyKeyboardMarkup(keyboard=[["Bergamo", "Milano"], ["Monza", "Rho"], ["Mantova","Brescia", "Livigno"]])
        	bot.sendMessage(chat_id, msg, reply_markup=markup)
       		utente[chat_id] = 1

    	elif 'text' in msg and msg['text'] == '/help':
		bot.sendMessage(chat_id, "Ecco i comandi eseguibili:\n"+ 
					 "/cerca  --> per cercare una città italiana.\n"+
					"/cercaGPS  --> per cercare tramite posizione.\n"+
					"/digita  --> per cercare il nome di un hotel.\n")

	elif 'text' in msg and msg['text'] == '/cercaGPS':
        	msg = "Inviami la tua posizione"
        	bot.sendMessage(chat_id, msg)
        	utente[chat_id] = 1

	elif 'text' in msg and msg['text'] == '/digita':
                msg ="Inserisci il nome dell'albergo richiesto:"
		bot.sendMessage(chat_id, msg,reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                utente[chat_id] = 2
	
		

	
		

    	elif utente[chat_id] == 1:

    		if content_type == 'text':
			bot.sendMessage(chat_id,msg['text'])
	    		try:	
				r = requests.get(
                			url="https://www.dati.lombardia.it/resource/7n8z-rsk5.json?nome_comune="+str(msg['text']))
                		json_data = r.json()
		
				#estraggo i dati JSON

				count=0
				for i in json_data[0:len(json_data[0])]:
					nome_comune = json_data [count]["nome_comune"] 
					denominazione_struttura = json_data[count]["denominazione_struttura"]
					indirizzo=json_data[count]["indirizzo"]
				        count=count+1
					bot.sendMessage(chat_id, "comune: {}.\ndenominazione: {}.\nindirizzo: {}.\n".
						format(nome_comune,denominazione_struttura,indirizzo))
				bot.sendMessage(chat_id, "/digita il nome di un hotel che hai visto, altrimenti /cerca o /cercaGPS per effettuare 									un altra ricerca",reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
				utente[chat_id] = 0
				
	    		except:
				bot.sendMessage(chat_id, "Errore API")

		elif content_type == 'location':
			google_api = True
            		while (google_api == True):
                		try:
                    			# send location
                    			response = requests.get('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(
                       				msg['location']['latitude']) + ',' + str(msg['location']['longitude']))
                    			resp_json_payload = response.json()
                    			a = str(resp_json_payload['results'][0]
                            			['address_components'][2]['long_name'])
                    			google_api = False

                		except:
                    			pass

            		bot.sendMessage(chat_id, "Cerco Hotel a "+ a)
			
			try:	
		        	r = requests.get(
                	        	url='https://www.dati.lombardia.it/resource/7n8z-rsk5.json?nome_comune='+a)
                	        json_data = r.json()

			    	#estraggo i dati JSON

				count=0
				for i in json_data[0:len(json_data[0])]:
					nome_comune = json_data [count]["nome_comune"] 
					denominazione_struttura = json_data[count]["denominazione_struttura"]
					indirizzo=json_data[count]["indirizzo"]
                                        count=count+1
					bot.sendMessage(chat_id, "comune: {}.\ndenominazione: {}.\nindirizzo: {}.\n".
						format(nome_comune,denominazione_struttura,indirizzo))
				bot.sendMessage(chat_id, "/digita il nome di un hotel che hai visto, altrimenti /cerca o"+
                                                        " /cercaGPS per effettuare un altra 									ricerca",reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
				utente[chat_id] = 0
            		except:
                               	bot.sendMessage(chat_id, a +" non in lista",reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
              			

	
        elif utente[chat_id] == 2:

    	    if content_type == 'text':
		bot.sendMessage(chat_id,msg['text']) 
		try:	
			r = requests.get(
                		url='https://www.dati.lombardia.it/resource/7n8z-rsk5.json?denominazione_struttura='+str(msg['text']))
                	json_data = r.json()
			#estraggo i dati JSON
			count=0
			presente=0
			for i in json_data[0:len(json_data[0])]:
				nome_comune = json_data [count]["nome_comune"]
				denominazione_struttura = json_data[count]["denominazione_struttura"]		
				indirizzo=json_data[count]["indirizzo"]
				presente=presente+1
				latitude = json_data [count]["location"]["latitude"] 
				longitude= json_data[count]["location"]["longitude"]
				bot.sendLocation(chat_id,latitude,longitude)	
				bot.sendMessage(chat_id, "comune: {}.\ndenominazione: {}.\nindirizzo: {}.\n".
						format(nome_comune,denominazione_struttura,indirizzo))	
                                count=count+1
					
					
				
			bot.sendMessage(chat_id, "/digita il nome di un hotel che hai visto, altrimenti /cerca o /cercaGPS per effettuare 								un altra ricerca",reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
			utente[chat_id] = 0
		
	    	except:
			if (count==0 and presente == 0):
				bot.sendMessage(chat_id, "Errore API, non esiste l'albergo ricercato ", 								reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
			else: 	
				bot.sendMessage(chat_id, "NON DISPONIBILE LA MAPPA PER QUESTO HOTEL \ncomune: {}.\ndenominazione: {}.	\nindirizzo:{}.\n". format(nome_comune,denominazione_struttura,indirizzo))

	
# Main
print("Avvio Albergo_bot!")

# Start working
try:
	bot = telepot.Bot(token)
    	bot.message_loop(on_chat_message)
    	while(1):
        	sleep(10)
finally:
	print("Esci")



