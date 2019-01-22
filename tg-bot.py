#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import os, sys
import logging
import time
import telepot
import argparse
import urllib3
import requests

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from bs4 import BeautifulSoup


debug = False

# Import your users here!
users=[]

status_url="http://127.0.0.1/nagios/cgi-bin/status.cgi"
cgi_url="http://127.0.0.1/nagios/cgi-bin/cmd.cgi"

reload(sys)
sys.setdefaultencoding('utf-8')
logo={"WARNING": u'\U0001f536', "CRITICAL": u'\U0001f534', "Unmute": u'\U0001f50a', "Mute": u'\U0001f507'   }

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)


def process_status(chat_id):

    status_list=[]
    ANS="Services with problem: \n"

    data = {
         "host" : "all",
         "servicestatustypes" : "28" ,
         "limit" : "0"
         }

### You input the basic auth for the nagios here or make it as variable if you like
    resp = requests.post(status_url, data=data, auth=('AC', 'PW'))

    soup = BeautifulSoup(resp.text, "html.parser")
    status_table = soup.find("table", class_="status")
    rows = status_table.find_all("tr")
    rows.pop(0)

    last=""
    for one in rows :
        temp = one.find_all("td")
        if len(temp)<9 :
            continue
        if len(temp)>12 :
            last = temp[0].text.strip()
            if len(temp) == 14:
                news = {
                         "status"   : temp[9].text.strip(),
                         "time"     : temp[10].text.strip(),
                         "hostname" : temp[0].text.strip(),
                         "srvname"  : temp[4].text.strip(),
                         "detail"   : temp[13].text.strip(),
                         "notice"   : False
                }
            else :
                news = {
                         "status"   : temp[8].text.strip(),
                         "time"     : temp[9].text.strip(),
                         "hostname" : temp[0].text.strip(),
                         "srvname"  : temp[5].text.strip(),
                         "detail"   : temp[12].text.strip(),
                         "notice"   : True
                }

        else:
            if len(temp) == 11:
                news = {
                         "status"   : temp[6].text.strip(),
                         "time"     : temp[7].text.strip(),
                         "hostname" : last,
                         "srvname"  : temp[1].text.strip(),
                         "detail"   : temp[10].text.strip(),
                         "notice"   : False
                }
            else :
                news = {
                         "status"   : temp[5].text.strip(),
                         "time"     : temp[6].text.strip(),
                         "hostname" : last,
                         "srvname"  : temp[1].text.strip(),
                         "detail"   : temp[9].text.strip(),
                         "notice"   : True
                }
        status_list.append(news)

    status_keyboard=[]
    row=[]
    button_info=""
    for i in range(len(status_list)):
        if  status_list[i]["notice"] is False:
            ANS = ANS + logo["Mute"]
            button_info="{} {}".format(logo["Unmute"],i)
            callback_info="enable;{};{}".format(status_list[i]["hostname"],status_list[i]["srvname"])
        else:
            button_info="{} {}".format(logo["Mute"],i)
            callback_info="disable;{};{}".format(status_list[i]["hostname"],status_list[i]["srvname"])
        ANS="{}{} {}. {} - {} : {}\n".format(ANS, logo[status_list[i]["status"]], i,  status_list[i]["hostname"], status_list[i]["srvname"], status_list[i]["detail"] )
        row.append(InlineKeyboardButton(text=button_info, callback_data=callback_info))
        if ( i % 5 == 4) :
            status_keyboard.append(row)
            row=[]
    if  ( len(status_list) % 5 != 0 ) :
        status_keyboard.append(row)
    keyboard = InlineKeyboardMarkup(inline_keyboard=status_keyboard)

    if debug:
        print(ANS)

    bot.sendMessage(chat_id,ANS, reply_markup=keyboard)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == "text":
        content = msg["text"]
        if (str(chat_id) not in users) :
            bot.sendMessage(chat_id, content)
            return
        if "entities" in msg:
            if msg["entities"][0]["type"] == "bot_command":
                if content == "/list":
                    process_status(chat_id)





def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    logger.info('Callback Query:', query_id, from_id, query_data)

    if str(from_id) in users:
        cmd, host, service = query_data.split(";")
#        logger.info("User: {}, cmd: {} , host: {}, service: {}".format(from_id, cmd, host, service ))

        if cmd == "disable":
            data = {
                "cmd_typ" : "23",
                "cmd_mod" : 2,
                "host" : host,
                "service" : service ,
                "btnSubmit" : "Commit"
            }


        if cmd == "enable":
           data = {
               "cmd_typ" : "22",
               "cmd_mod" : 2,
               "host" : host ,
               "service" : service ,
               "btnSubmit" : "Commit"
           }


        bot.answerCallbackQuery(query_id, text='{} service "{}" at "{}"'.format(cmd, service, host))

        resp = requests.post(cgi_url, data=data, auth=('nmcadmin', 'mncadmin123'))

        for one in users:
            bot.sendMessage(one,"Service - {} of {} {}d - {}".format(service, host, cmd, resp))


### If you use proxy, uncomment the following
##proxy_url = "<URL>:<PORT>"
##telepot.api._pools = {'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),}
##telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))


bot = telepot.Bot('222222222:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')


MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()

while 1:
    time.sleep(10)
